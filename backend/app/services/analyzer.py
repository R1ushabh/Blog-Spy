import re
import httpx
from bs4 import BeautifulSoup
from urllib.parse import urljoin, urlparse
from typing import Dict, Any, List

from app.services.deduplicator import normalize_url

async def analyze_website(
    website_url: str,
    blog_url: str = None,
    feed_url: str = None,
    sitemap_url: str = None,
    timeout: int = 3
) -> Dict[str, Any]:
    """
    Automatically investigates a competitor website to discover RSS/Atom feeds,
    sitemaps, article URL patterns, metadata schema, date signals, and recommended strategies.
    """
    normalized_website = normalize_url(website_url)
    target_blog = blog_url or website_url
    
    rss_feeds = []
    atom_feeds = []
    sitemaps = []
    sitemap_indexes = []
    article_patterns = []
    pub_date_signals = []
    canonical_signals = []
    structured_metadata = []
    
    if feed_url:
        rss_feeds.append(feed_url)
    if sitemap_url:
        sitemaps.append(sitemap_url)

    headers = {
        "User-Agent": "CompetitorSpyBot/1.0 (+http://competitorspy.local/bot)",
        "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8"
    }

    try:
        async with httpx.AsyncClient(timeout=timeout, follow_redirects=True, headers=headers) as client:
            # 1. Inspect robots.txt for Sitemap references
            try:
                robots_url = urljoin(normalized_website, "/robots.txt")
                robots_resp = await client.get(robots_url)
                if robots_resp.status_code == 200:
                    for line in robots_resp.text.splitlines():
                        if line.lower().startswith("sitemap:"):
                            discovered_sm = line.split(":", 1)[1].strip()
                            if discovered_sm not in sitemaps:
                                sitemaps.append(discovered_sm)
            except Exception:
                pass

            # 2. Check Common Sitemap Endpoints if none found
            if not sitemaps:
                common_sitemaps = ["/sitemap.xml", "/sitemap_index.xml", "/post-sitemap.xml"]
                for sm_path in common_sitemaps:
                    test_sm = urljoin(normalized_website, sm_path)
                    try:
                        resp = await client.head(test_sm)
                        if resp.status_code == 200:
                            sitemaps.append(test_sm)
                    except Exception:
                        pass

            # 3. Fetch Main/Blog Page HTML
            resp = await client.get(target_blog)
            if resp.status_code == 200:
                html = resp.text
                soup = BeautifulSoup(html, "lxml")

                # Look for RSS/Atom <link> elements
                for link in soup.find_all("link", rel=lambda r: r and "alternate" in r.lower()):
                    ltype = link.get("type", "").lower()
                    href = link.get("href")
                    if href:
                        full_feed = urljoin(target_blog, href)
                        if "rss" in ltype and full_feed not in rss_feeds:
                            rss_feeds.append(full_feed)
                        elif "atom" in ltype and full_feed not in atom_feeds:
                            atom_feeds.append(full_feed)

                # Look for common feed URLs if none found
                if not rss_feeds and not atom_feeds:
                    for feed_path in ["/feed", "/rss", "/rss.xml", "/feed.xml", "/atom.xml", "/blog/rss"]:
                        test_feed = urljoin(normalized_website, feed_path)
                        try:
                            fresp = await client.head(test_feed)
                            if fresp.status_code == 200:
                                rss_feeds.append(test_feed)
                        except Exception:
                            pass

                # Inspect Canonical tags
                canonical = soup.find("link", rel=lambda r: r and "canonical" in r.lower())
                if canonical and canonical.get("href"):
                    canonical_signals.append("HTML canonical link element")

                # Inspect Schema.org / JSON-LD
                json_ld = soup.find_all("script", type="application/ld+json")
                if json_ld:
                    structured_metadata.append("JSON-LD Article Metadata")
                if soup.find("meta", property=re.compile(r"^og:")):
                    structured_metadata.append("OpenGraph Metadata")

                # Inspect Date signals
                if soup.find("time"):
                    pub_date_signals.append("Semantic <time> HTML tag")
                if soup.find("meta", property=re.compile(r"published_time|date", re.I)):
                    pub_date_signals.append("Meta publication date property")

                # Article pattern inspection
                article_tags = soup.find_all("article")
                if article_tags:
                    article_patterns.append("Semantic <article> container pattern")
                
                # Check link paths
                for a in soup.find_all("a", href=True):
                    href = a["href"]
                    if re.search(r'/(blog|post|article|news)/\w+', href, re.I):
                        article_patterns.append("URL subpath matching blog/post pattern")
                        break
    except Exception as e:
        pass

    # Strategy Selection Logic
    confidence = {}
    recommended = []
    
    if rss_feeds or atom_feeds:
        confidence["RSS"] = "High"
        recommended.append("RSS")
    else:
        confidence["RSS"] = "Unavailable"

    if sitemaps:
        confidence["Sitemap"] = "High" if len(sitemaps) > 0 else "Medium"
        recommended.append("Sitemap")
    else:
        confidence["Sitemap"] = "Low"

    confidence["Direct Page"] = "Medium" if article_patterns else "Low"
    recommended.append("Direct Page")

    if not recommended:
        recommended.append("Direct Page")
        
    reason = ""
    if "RSS" in recommended:
        reason = "RSS/Atom feed auto-detected with high precision. Retaining Sitemap and Direct Page as secondary verification sources."
    elif "Sitemap" in recommended:
        reason = "XML Sitemap auto-detected. Direct Page monitoring retained as secondary verification."
    else:
        reason = "Direct Page pattern fallback selected because no RSS feed or Sitemap was exposed."

    return {
        "website": normalized_website,
        "blog_section": target_blog,
        "rss_feeds": rss_feeds,
        "atom_feeds": atom_feeds,
        "sitemaps": sitemaps,
        "sitemap_indexes": sitemap_indexes,
        "article_patterns": list(set(article_patterns)),
        "publication_date_signals": list(set(pub_date_signals)),
        "canonical_signals": canonical_signals,
        "structured_metadata": list(set(structured_metadata)),
        "recommended_strategies": recommended,
        "confidence_scores": confidence,
        "strategy_reason": reason
    }
