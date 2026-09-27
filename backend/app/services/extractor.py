import re
import json
from datetime import datetime, timezone
from typing import Optional, Dict, Any, List
from urllib.parse import urljoin, urlparse
from bs4 import BeautifulSoup
import trafilatura
from dateparser import parse as parse_date

from app.services.deduplicator import normalize_url

def parse_iso_or_human_date(date_str: Optional[str]) -> Optional[datetime]:
    if not date_str or not isinstance(date_str, str):
        return None
    cleaned = date_str.strip()
    if not cleaned:
        return None
    try:
        dt = parse_date(cleaned, settings={'TIMEZONE': 'UTC', 'RETURN_AS_TIMEZONE_AWARE': True})
        if dt:
            return dt.astimezone(timezone.utc).replace(tzinfo=None)
    except Exception:
        pass
    return None

def extract_article_details(html_content: str, url: str) -> Dict[str, Any]:
    """
    Extracts full article metadata & body content from HTML using a multi-tiered pipeline:
    1. JSON-LD / schema.org metadata
    2. OpenGraph / Twitter metadata
    3. Trafilatura content extraction
    4. BeautifulSoup semantic HTML fallback
    """
    soup = BeautifulSoup(html_content, "lxml")
    
    extracted = {
        "title": None,
        "body": None,
        "excerpt": None,
        "featured_image": None,
        "author": None,
        "publication_time": None,
        "canonical_url": None,
        "meta_description": None,
        "categories": [],
        "tags": [],
        "relevant_links": [],
        "images": []
    }

    # Extract Canonical URL
    canonical_link = soup.find("link", attrs={"rel": lambda r: r and "canonical" in r.lower()})
    if canonical_link and canonical_link.get("href"):
        extracted["canonical_url"] = normalize_url(urljoin(url, canonical_link["href"]))
    else:
        extracted["canonical_url"] = normalize_url(url)

    # 1. JSON-LD parsing
    json_ld_scripts = soup.find_all("script", attrs={"type": "application/ld+json"})
    for script in json_ld_scripts:
        if not script.string:
            continue
        try:
            data = json.loads(script.string)
            items = data if isinstance(data, list) else [data]
            for item in items:
                if isinstance(item, dict) and "@graph" in item:
                    items.extend(item["@graph"])
                    continue
                if not isinstance(item, dict):
                    continue
                type_name = str(item.get("@type", ""))
                if any(t in type_name for t in ["Article", "BlogPosting", "NewsArticle", "WebPage"]):
                    if not extracted["title"] and item.get("headline"):
                        extracted["title"] = str(item["headline"])
                    if not extracted["publication_time"]:
                        pub_str = item.get("datePublished") or item.get("dateCreated")
                        if pub_str:
                            extracted["publication_time"] = parse_iso_or_human_date(str(pub_str))
                    if not extracted["author"]:
                        auth = item.get("author")
                        if isinstance(auth, dict):
                            extracted["author"] = auth.get("name")
                        elif isinstance(auth, list) and len(auth) > 0:
                            extracted["author"] = auth[0].get("name") if isinstance(auth[0], dict) else str(auth[0])
                        elif isinstance(auth, str):
                            extracted["author"] = auth
                    if not extracted["featured_image"]:
                        img = item.get("image")
                        if isinstance(img, dict):
                            extracted["featured_image"] = img.get("url")
                        elif isinstance(img, list) and len(img) > 0:
                            extracted["featured_image"] = img[0] if isinstance(img[0], str) else img[0].get("url")
                        elif isinstance(img, str):
                            extracted["featured_image"] = img
                    if not extracted["meta_description"] and item.get("description"):
                        extracted["meta_description"] = str(item["description"])
        except Exception:
            continue

    # 2. OpenGraph / Twitter Fallbacks
    if not extracted["title"]:
        og_title = soup.find("meta", attrs={"property": "og:title"}) or soup.find("meta", attrs={"name": "twitter:title"})
        if og_title and og_title.get("content"):
            extracted["title"] = og_title["content"].strip()

    if not extracted["meta_description"]:
        og_desc = soup.find("meta", attrs={"property": "og:description"}) or soup.find("meta", attrs={"name": "description"})
        if og_desc and og_desc.get("content"):
            extracted["meta_description"] = og_desc["content"].strip()

    if not extracted["featured_image"]:
        og_img = soup.find("meta", attrs={"property": "og:image"}) or soup.find("meta", attrs={"name": "twitter:image"})
        if og_img and og_img.get("content"):
            extracted["featured_image"] = urljoin(url, og_img["content"].strip())

    if not extracted["publication_time"]:
        og_time = (
            soup.find("meta", attrs={"property": "article:published_time"}) or
            soup.find("meta", attrs={"property": "og:published_time"}) or
            soup.find("meta", attrs={"name": "pubdate"}) or
            soup.find("meta", attrs={"name": "publishdate"})
        )
        if og_time and og_time.get("content"):
            extracted["publication_time"] = parse_iso_or_human_date(og_time["content"].strip())

    if not extracted["author"]:
        meta_author = soup.find("meta", attrs={"name": "author"}) or soup.find("meta", attrs={"property": "article:author"})
        if meta_author and meta_author.get("content"):
            extracted["author"] = meta_author["content"].strip()

    # 3. HTML BeautifulSoup Fallback for Title
    if not extracted["title"]:
        h1 = soup.find("h1")
        if h1:
            extracted["title"] = h1.get_text().strip()
        elif soup.title and soup.title.string:
            extracted["title"] = soup.title.string.strip()
        else:
            extracted["title"] = "Untitled Article"

    # HTML <time> tag fallback for publication date
    if not extracted["publication_time"]:
        time_tag = soup.find("time")
        if time_tag:
            datetime_attr = time_tag.get("datetime") or time_tag.get_text()
            if datetime_attr:
                extracted["publication_time"] = parse_iso_or_human_date(datetime_attr)

    # 4. Body Content Extraction with Trafilatura
    try:
        traf_text = trafilatura.extract(html_content, include_images=True, include_links=True, output_format="xml")
        if traf_text:
            traf_soup = BeautifulSoup(traf_text, "xml")
            extracted["body"] = traf_soup.get_text(separator="\n\n").strip()
    except Exception:
        pass

    if not extracted["body"]:
        article_elem = soup.find("article") or soup.find("main") or soup.find("div", attrs={"class": re.compile(r"content|post|entry", re.I)})
        if article_elem:
            paragraphs = [p.get_text().strip() for p in article_elem.find_all("p") if len(p.get_text().strip()) > 20]
            extracted["body"] = "\n\n".join(paragraphs)
        else:
            paragraphs = [p.get_text().strip() for p in soup.find_all("p") if len(p.get_text().strip()) > 20]
            extracted["body"] = "\n\n".join(paragraphs[:10])

    # Generate Excerpt
    if extracted["body"]:
        extracted["excerpt"] = extracted["body"][:250].replace("\n", " ") + "..."
    elif extracted["meta_description"]:
        extracted["excerpt"] = extracted["meta_description"]

    # Extract Inline Images
    images = []
    if extracted["featured_image"]:
        images.append({
            "image_url": extracted["featured_image"],
            "image_type": "featured",
            "alt_text": extracted["title"],
            "position": 0
        })
        
    pos = 1
    for img in soup.find_all("img"):
        src = img.get("src") or img.get("data-src")
        if src and not src.startswith("data:"):
            full_img_url = urljoin(url, src)
            if full_img_url != extracted["featured_image"] and pos <= 5:
                images.append({
                    "image_url": full_img_url,
                    "image_type": "inline",
                    "alt_text": img.get("alt", ""),
                    "position": pos
                })
                pos += 1
    extracted["images"] = images

    # Extract Categories / Tags
    tags = set()
    for cat_meta in soup.find_all("meta", attrs={"property": "article:tag"}):
        if cat_meta.get("content"):
            tags.add(cat_meta["content"].strip())
    extracted["tags"] = list(tags)

    return extracted
