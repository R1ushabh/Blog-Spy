import httpx
from bs4 import BeautifulSoup
from datetime import datetime
from typing import List, Dict, Any, Optional
from urllib.parse import urljoin
from app.services.extractor import parse_iso_or_human_date
from app.services.deduplicator import normalize_url
from app.api.demo_site import get_demo_sitemap

async def fetch_and_parse_sitemap(sitemap_url: str, depth: int = 0, max_depth: int = 1, timeout: int = 3) -> Dict[str, Any]:
    """
    Parses sitemap.xml or sitemap_index.xml recursively up to max_depth.
    Extracts article URLs, lastmod timestamps, changefreq, and priority.
    Bypasses network loopback for internal demo-site endpoints to prevent Uvicorn self-deadlock.
    """
    if depth > max_depth:
        return {"status": 200, "urls": []}
        
    status_code = 200
    if "demo-site/sitemap.xml" in sitemap_url or "/api/demo-site" in sitemap_url:
        resp = get_demo_sitemap()
        content = resp.body.decode("utf-8")
    else:
        headers = {
            "User-Agent": "CompetitorSpyBot/1.0 (+http://competitorspy.local/bot)",
            "Accept": "text/xml, application/xml, */*"
        }
        async with httpx.AsyncClient(timeout=timeout, follow_redirects=True, headers=headers) as client:
            response = await client.get(sitemap_url)
            response.raise_for_status()
            content = response.text
            status_code = response.status_code

    soup = BeautifulSoup(content, "xml")
    urls: List[Dict[str, Any]] = []

    # Handle Sitemap Index (<sitemapindex><sitemap><loc>...)
    sitemap_tags = soup.find_all("sitemap")
    if sitemap_tags and len(sitemap_tags) > 0:
        for sm in sitemap_tags[:2]:
            loc = sm.find("loc")
            if loc and loc.text:
                child_res = await fetch_and_parse_sitemap(loc.text.strip(), depth=depth+1, max_depth=max_depth, timeout=timeout)
                urls.extend(child_res.get("urls", []))
        return {
            "status": status_code,
            "type": "SITEMAP_INDEX",
            "urls": urls
        }

    # Handle URL set (<urlset><url><loc><lastmod>...)
    url_tags = soup.find_all("url")
    for u in url_tags:
        loc = u.find("loc")
        if not loc or not loc.text:
            continue
        raw_url = loc.text.strip()
        lastmod = u.find("lastmod")
        pub_time = parse_iso_or_human_date(lastmod.text.strip()) if lastmod and lastmod.text else None
        
        normalized = normalize_url(raw_url)
        urls.append({
            "url": normalized,
            "original_url": raw_url,
            "lastmod": pub_time,
            "method": "SITEMAP"
        })

    return {
        "status": status_code,
        "type": "SITEMAP",
        "urls": urls[:20]
    }
