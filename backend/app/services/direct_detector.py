import re
import httpx
from bs4 import BeautifulSoup
from typing import List, Dict, Any
from urllib.parse import urljoin, urlparse
from app.services.deduplicator import normalize_url
from app.services.extractor import parse_iso_or_human_date
from app.api.demo_site import get_demo_blog_home

async def fetch_and_parse_direct_page(page_url: str, timeout: int = 3) -> Dict[str, Any]:
    """
    Directly crawls a blog/news index page to extract potential article links and date signals.
    Employs semantic HTML inspection (<article>, article link regex, schema.org).
    Bypasses network loopback for internal demo-site endpoints to prevent Uvicorn self-deadlock.
    """
    status_code = 200
    if "demo-site" in page_url:
        resp = get_demo_blog_home()
        html = resp.body.decode("utf-8")
    else:
        headers = {
            "User-Agent": "CompetitorSpyBot/1.0 (+http://competitorspy.local/bot)",
            "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8"
        }
        async with httpx.AsyncClient(timeout=timeout, follow_redirects=True, headers=headers) as client:
            response = await client.get(page_url)
            response.raise_for_status()
            html = response.text
            status_code = response.status_code

    soup = BeautifulSoup(html, "lxml")
    parsed_base = urlparse(page_url)
    base_domain = parsed_base.netloc.lower()

    discovered_links: List[Dict[str, Any]] = []
    seen_urls = set()

    # Strategy A: Semantic <article> tags
    articles = soup.find_all("article")
    for art in articles:
        a_tag = art.find("a", href=True)
        if a_tag:
            full_url = urljoin(page_url, a_tag["href"])
            norm = normalize_url(full_url)
            if norm not in seen_urls and (not base_domain or urlparse(full_url).netloc.lower() == base_domain):
                seen_urls.add(norm)
                title = a_tag.get_text().strip() or art.find(["h1", "h2", "h3"]).get_text().strip() if art.find(["h1", "h2", "h3"]) else "Untitled"
                time_tag = art.find("time")
                pub_time = parse_iso_or_human_date(time_tag.get("datetime") or time_tag.get_text()) if time_tag else None
                
                discovered_links.append({
                    "title": title,
                    "url": norm,
                    "original_url": full_url,
                    "publication_time": pub_time,
                    "method": "DIRECT_PAGE"
                })

    # Strategy B: Common blog / post URL regex pattern matching in remaining links
    post_pattern = re.compile(r'/(blog|posts?|articles?|news|story|\d{4}/\d{2})/', re.I)
    for a in soup.find_all("a", href=True):
        href = a["href"]
        full_url = urljoin(page_url, href)
        norm = normalize_url(full_url)
        
        if norm not in seen_urls and (not base_domain or urlparse(full_url).netloc.lower() == base_domain):
            if post_pattern.search(href) or len(urlparse(full_url).path.strip("/").split("/")) >= 2:
                if not any(href.lower().endswith(ext) for ext in [".png", ".jpg", ".css", ".js", ".pdf", "#"]):
                    seen_urls.add(norm)
                    title = a.get_text().strip() or "Untitled Article"
                    discovered_links.append({
                        "title": title[:200],
                        "url": norm,
                        "original_url": full_url,
                        "publication_time": None,
                        "method": "DIRECT_PAGE"
                    })

    return {
        "status": status_code,
        "articles": discovered_links[:30]
    }
