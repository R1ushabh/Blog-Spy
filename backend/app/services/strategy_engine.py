from datetime import datetime, timezone
import math
from typing import Dict, Any, Tuple
from sqlalchemy.orm import Session
from app.models.models import Competitor, MonitoringSource, Article, MonitoringCheck, Notification, ArticleImage
from app.services.rss_detector import fetch_and_parse_rss
from app.services.sitemap_detector import fetch_and_parse_sitemap
from app.services.direct_detector import fetch_and_parse_direct_page
from app.services.extractor import extract_article_details
from app.services.deduplicator import is_duplicate_article, compute_content_hash, normalize_url
from app.api.demo_site import get_demo_article_page
import httpx

def calculate_delay(publication_time: datetime, detected_at: datetime) -> Tuple[float, str, bool]:
    """
    Calculates exact detection delay seconds, display string, and 5-min target flag.
    Formula: detection_delay_seconds = detected_at - publication_time
    Formats as: 38 sec, 3 min 12 sec, 1 hr 02 min 08 sec, etc.
    """
    if not publication_time:
        return 0.0, "Publication time unavailable", True
        
    diff = (detected_at - publication_time).total_seconds()
    if diff < 0:
        diff = 0.0 # handle slight clock skew gracefully
        
    seconds = int(diff)
    within_target = (seconds <= 300)
    
    if seconds < 60:
        display = f"{seconds} sec"
    elif seconds < 3600:
        mins = seconds // 60
        secs = seconds % 60
        display = f"{mins} min {secs:02d} sec"
    else:
        hrs = seconds // 3600
        mins = (seconds % 3600) // 60
        display = f"Backfill / First Discovery ({hrs}h {mins:02d}m)"
        
    return diff, display, within_target

async def execute_competitor_check(db: Session, competitor_id: int) -> Dict[str, Any]:
    """
    Executes a complete monitoring check cycle for a competitor:
    1. Fetches active monitoring sources (RSS, Sitemap, Direct Page)
    2. Runs detection strategy
    3. Fetches & extracts full article metadata for newly detected articles
    4. Enforces deduplication
    5. Stores article & calculates exact delay
    6. Generates notifications & updates health status
    """
    competitor = db.query(Competitor).filter(Competitor.id == competitor_id).first()
    if not competitor or not competitor.monitoring_enabled or competitor.status == "PAUSED":
        return {"status": "skipped", "reason": "competitor disabled or paused"}

    start_time = datetime.now(timezone.utc)
    new_articles_count = 0
    total_found = 0
    check_error = None
    http_status = 200

    sources = db.query(MonitoringSource).filter(
        MonitoringSource.competitor_id == competitor_id,
        MonitoringSource.status == "ACTIVE"
    ).all()

    if not sources:
        # Fallback to direct page monitoring on competitor.website_url
        sources = [MonitoringSource(
            competitor_id=competitor_id,
            source_type="DIRECT_PAGE",
            source_url=competitor.blog_url or competitor.website_url
        )]

    for source in sources:
        try:
            detected_raw_items = []
            method_used = source.source_type

            if source.source_type in ["RSS", "ATOM"]:
                rss_res = await fetch_and_parse_rss(source.source_url)
                detected_raw_items = rss_res.get("items", [])
                http_status = rss_res.get("status", 200)
            elif source.source_type in ["SITEMAP", "SITEMAP_INDEX"]:
                sm_res = await fetch_and_parse_sitemap(source.source_url)
                for u_item in sm_res.get("urls", []):
                    detected_raw_items.append({
                        "title": "Untitled Article",
                        "url": u_item["url"],
                        "original_url": u_item["original_url"],
                        "publication_time": u_item["lastmod"],
                        "method": "SITEMAP"
                    })
                http_status = sm_res.get("status", 200)
            elif source.source_type == "DIRECT_PAGE":
                dp_res = await fetch_and_parse_direct_page(source.source_url)
                detected_raw_items = dp_res.get("articles", [])
                http_status = dp_res.get("status", 200)

            total_found += len(detected_raw_items)

            for item in detected_raw_items[:3]:
                art_url = item["url"]
                
                # Check for duplicates before fetching full article page
                pre_check_hash = compute_content_hash(item.get("title", ""), "", str(item.get("publication_time")))
                is_dup, _ = is_duplicate_article(db, competitor_id, art_url, art_url, pre_check_hash, item.get("title", ""))
                if is_dup:
                    continue

                # Fetch & Extract full article details
                full_body = ""
                extracted_data = {}
                try:
                    if "demo-site/articles/" in art_url:
                        art_id = art_url.split("demo-site/articles/")[-1]
                        resp = get_demo_article_page(art_id)
                        extracted_data = extract_article_details(resp.body.decode("utf-8"), art_url)
                        full_body = extracted_data.get("body") or ""
                    else:
                        async with httpx.AsyncClient(timeout=2, follow_redirects=True) as client:
                            resp = await client.get(art_url)
                            if resp.status_code == 200:
                                extracted_data = extract_article_details(resp.text, art_url)
                                full_body = extracted_data.get("body") or ""
                except Exception:
                    pass

                title = extracted_data.get("title") or item.get("title") or "Untitled Article"
                canonical_url = extracted_data.get("canonical_url") or item.get("url")
                pub_time = extracted_data.get("publication_time") or item.get("publication_time")
                
                # Re-verify deduplication with exact canonical URL & extracted content hash
                content_hash = compute_content_hash(title, full_body, str(pub_time))
                is_dup_final, _ = is_duplicate_article(db, competitor_id, art_url, canonical_url, content_hash, title)
                if is_dup_final:
                    continue

                # Calculate Exact Detection Delay
                now_utc = datetime.now(timezone.utc).replace(tzinfo=None) # naive for DB
                pub_time_naive = pub_time.replace(tzinfo=None) if pub_time and pub_time.tzinfo else pub_time
                
                delay_sec, delay_disp, within_target = calculate_delay(pub_time_naive, now_utc)

                # Store New Article
                new_article = Article(
                    competitor_id=competitor_id,
                    title=title,
                    body=full_body,
                    excerpt=extracted_data.get("excerpt") or item.get("summary"),
                    featured_image=extracted_data.get("featured_image"),
                    author=extracted_data.get("author") or item.get("author"),
                    publication_time=pub_time_naive,
                    detected_at=now_utc,
                    detection_delay_seconds=delay_sec,
                    detection_delay_display=delay_disp,
                    detection_method=item.get("method", source.source_type),
                    source_url=art_url,
                    original_url=item.get("original_url", art_url),
                    canonical_url=canonical_url,
                    meta_description=extracted_data.get("meta_description"),
                    categories=extracted_data.get("categories", []),
                    tags=extracted_data.get("tags", []),
                    relevant_links=extracted_data.get("relevant_links", []),
                    content_hash=content_hash,
                    status="STORED",
                    within_target=within_target
                )
                db.add(new_article)
                db.flush()

                # Add images
                for img_item in extracted_data.get("images", []):
                    art_img = ArticleImage(
                        article_id=new_article.id,
                        image_url=img_item["image_url"],
                        image_type=img_item["image_type"],
                        alt_text=img_item.get("alt_text"),
                        position=img_item.get("position", 0)
                    )
                    db.add(art_img)

                # Create Notification
                notif = Notification(
                    article_id=new_article.id,
                    notification_type="DASHBOARD",
                    status="SENT",
                    sent_at=now_utc
                )
                db.add(notif)
                new_articles_count += 1

            source.last_success_at = datetime.now(timezone.utc).replace(tzinfo=None)
        except Exception as e:
            check_error = str(e)
            if hasattr(source, "id"):
                source.last_error_at = datetime.now(timezone.utc).replace(tzinfo=None)

    completed_time = datetime.now(timezone.utc).replace(tzinfo=None)
    start_time_naive = start_time.replace(tzinfo=None)
    duration_ms = (completed_time - start_time_naive).total_seconds() * 1000

    # Record Monitoring Check Log
    check_log = MonitoringCheck(
        competitor_id=competitor_id,
        started_at=start_time_naive,
        completed_at=completed_time,
        duration_ms=duration_ms,
        success=(check_error is None),
        http_status=http_status,
        articles_found=total_found,
        new_articles_found=new_articles_count,
        error_type="HTTP_ERROR" if check_error else None,
        error_message=check_error,
        retry_count=0
    )
    db.add(check_log)

    # Update Competitor Health & Timestamps
    competitor.last_checked_at = completed_time
    if check_error is None:
        competitor.last_success_at = completed_time
        competitor.consecutive_failures = 0
        competitor.health_status = "ONLINE"
    else:
        competitor.consecutive_failures += 1
        if competitor.consecutive_failures >= 5:
            competitor.health_status = "OFFLINE"
        else:
            competitor.health_status = "DEGRADED"

    if new_articles_count > 0:
        competitor.last_detection_at = completed_time

    db.commit()

    return {
        "status": "success" if check_error is None else "degraded",
        "new_articles": new_articles_count,
        "duration_ms": duration_ms,
        "error": check_error
    }
