import httpx
import feedparser
from datetime import datetime
from typing import List, Dict, Any, Optional
from app.services.extractor import parse_iso_or_human_date
from app.services.deduplicator import normalize_url
from app.api.demo_site import get_demo_rss_feed

async def fetch_and_parse_rss(feed_url: str, timeout: int = 15) -> Dict[str, Any]:
    """
    Fetches an RSS or Atom feed and extracts normalized article items.
    Supports pubDate, dc:date, published, updated, created date variants.
    Bypasses network loopback for internal demo-site endpoints to prevent Uvicorn self-deadlock.
    """
    status_code = 200
    if "demo-site/rss.xml" in feed_url or "/api/demo-site" in feed_url:
        resp = get_demo_rss_feed()
        raw_xml = resp.body.decode("utf-8")
    else:
        headers = {
            "User-Agent": "CompetitorSpyBot/1.0 (+http://competitorspy.local/bot)",
            "Accept": "application/rss+xml, application/atom+xml, application/xml, text/xml, */*"
        }
        async with httpx.AsyncClient(timeout=timeout, follow_redirects=True, headers=headers) as client:
            response = await client.get(feed_url)
            response.raise_for_status()
            raw_xml = response.text
            status_code = response.status_code
        
    parsed = feedparser.parse(raw_xml)
    items: List[Dict[str, Any]] = []
    
    for entry in parsed.entries:
        title = getattr(entry, "title", "Untitled").strip()
        link = getattr(entry, "link", None)
        if not link and hasattr(entry, "links") and len(entry.links) > 0:
            link = entry.links[0].get("href")
        if not link:
            continue
            
        normalized_link = normalize_url(link)
        
        raw_date = None
        if hasattr(entry, "published"):
            raw_date = entry.published
        elif hasattr(entry, "updated"):
            raw_date = entry.updated
        elif hasattr(entry, "pubDate"):
            raw_date = entry.pubDate
        elif hasattr(entry, "dc_date"):
            raw_date = entry.dc_date
        elif hasattr(entry, "created"):
            raw_date = entry.created

        parsed_pub_time = parse_iso_or_human_date(raw_date) if raw_date else None
        author = getattr(entry, "author", None)
        summary = getattr(entry, "summary", getattr(entry, "description", None))
        
        items.append({
            "title": title,
            "url": normalized_link,
            "original_url": link,
            "publication_time": parsed_pub_time,
            "author": author,
            "summary": summary,
            "method": "ATOM" if "atom" in feed_url.lower() or getattr(parsed, "version", "").startswith("atom") else "RSS"
        })
        
    return {
        "status": status_code,
        "feed_title": getattr(parsed.feed, "title", ""),
        "items": items
    }
