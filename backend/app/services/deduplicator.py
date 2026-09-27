import hashlib
import re
from urllib.parse import urlparse, urlunparse, parse_qsl, urlencode
from typing import Optional, Tuple
from sqlalchemy.orm import Session
from app.models.models import Article

def normalize_url(url: str) -> str:
    """
    Normalizes a URL by stripping tracking parameters (utm_*, ref, fbclid),
    converting scheme/host to lowercase, and removing trailing slashes.
    """
    if not url:
        return ""
    try:
        parsed = urlparse(url.strip())
        scheme = parsed.scheme.lower() or "http"
        netloc = parsed.netloc.lower()
        path = parsed.path.rstrip("/")
        if not path:
            path = ""
            
        # Filter out tracking query params
        ignored_params = {"utm_source", "utm_medium", "utm_campaign", "utm_term", "utm_content", "ref", "fbclid", "gclid"}
        query_pairs = parse_qsl(parsed.query)
        filtered_query = [(k, v) for k, v in query_pairs if k.lower() not in ignored_params]
        query = urlencode(filtered_query)
        
        normalized = urlunparse((scheme, netloc, path, parsed.params, query, ""))
        return normalized
    except Exception:
        return url.strip()

def compute_content_hash(title: str, body: Optional[str] = None, publication_time_str: Optional[str] = None) -> str:
    """
    Creates a unique SHA-256 hash representation of the article content.
    """
    raw_str = f"{title.strip().lower()}|{ (body or '').strip().lower()[:500] }|{publication_time_str or ''}"
    return hashlib.sha256(raw_str.encode('utf-8')).hexdigest()

def is_duplicate_article(
    db: Session,
    competitor_id: int,
    source_url: str,
    canonical_url: Optional[str],
    content_hash: str,
    title: str
) -> Tuple[bool, Optional[Article]]:
    """
    Checks if an article is already recorded using the canonical deduplication pipeline:
    1. Canonical URL match for competitor
    2. Normalized source URL match for competitor
    3. Content hash match for competitor
    4. Title exact match fallback
    """
    norm_source = normalize_url(source_url)
    norm_canonical = normalize_url(canonical_url) if canonical_url else None
    
    # 1. Canonical URL check
    if norm_canonical:
        existing = db.query(Article).filter(
            Article.competitor_id == competitor_id,
            Article.canonical_url == norm_canonical
        ).first()
        if existing:
            return True, existing
            
    # 2. Source URL check
    existing = db.query(Article).filter(
        Article.competitor_id == competitor_id,
        Article.source_url == norm_source
    ).first()
    if existing:
        return True, existing

    # 3. Content hash check
    existing = db.query(Article).filter(
        Article.competitor_id == competitor_id,
        Article.content_hash == content_hash
    ).first()
    if existing:
        return True, existing
        
    # 4. Title fallback check
    existing = db.query(Article).filter(
        Article.competitor_id == competitor_id,
        Article.title == title.strip()
    ).first()
    if existing:
        return True, existing

    return False, None
