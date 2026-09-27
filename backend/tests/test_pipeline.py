import pytest
from datetime import datetime, timezone, timedelta
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from app.core.database import Base
from app.models.models import Competitor, Article, MonitoringSource
from app.services.deduplicator import normalize_url, compute_content_hash, is_duplicate_article
from app.services.strategy_engine import calculate_delay, execute_competitor_check
from app.services.extractor import extract_article_details

# Setup in-memory SQLite database for testing
engine = create_engine("sqlite:///:memory:", connect_args={"check_same_thread": False})
TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

@pytest.fixture(autouse=True)
def setup_db():
    Base.metadata.create_all(bind=engine)
    yield
    Base.metadata.drop_all(bind=engine)

def test_url_normalization():
    raw_url = "HTTPS://Example.COM/blog/post-1/?utm_source=twitter&utm_medium=cpc&ref=123#anchor"
    normalized = normalize_url(raw_url)
    assert normalized == "https://example.com/blog/post-1"

def test_detection_delay_math():
    pub_time = datetime(2026, 9, 27, 10, 0, 0)
    det_time = datetime(2026, 9, 27, 10, 3, 12)
    
    diff_sec, display, within_target = calculate_delay(pub_time, det_time)
    assert diff_sec == 192.0
    assert display == "3 min 12 sec"
    assert within_target is True

    # Test delay above 5 minutes
    det_late = datetime(2026, 9, 27, 10, 8, 43)
    diff_sec2, display2, within_target2 = calculate_delay(pub_time, det_late)
    assert diff_sec2 == 523.0
    assert display2 == "8 min 43 sec"
    assert within_target2 is False

def test_canonical_deduplication():
    db = TestingSessionLocal()
    comp = Competitor(name="Test Comp", website_url="https://test.com", monitoring_enabled=True)
    db.add(comp)
    db.commit()

    art_url = "https://test.com/blog/new-launch"
    content_hash = compute_content_hash("New Product Launch", "Body text content")

    # Check initially not duplicate
    is_dup, _ = is_duplicate_article(db, comp.id, art_url, art_url, content_hash, "New Product Launch")
    assert is_dup is False

    # Insert article
    art = Article(
        competitor_id=comp.id,
        title="New Product Launch",
        body="Body text content",
        publication_time=datetime.now(timezone.utc).replace(tzinfo=None),
        detected_at=datetime.now(timezone.utc).replace(tzinfo=None),
        detection_delay_seconds=120.0,
        detection_delay_display="2 min 00 sec",
        detection_method="RSS",
        source_url=art_url,
        canonical_url=art_url,
        content_hash=content_hash,
        within_target=True
    )
    db.add(art)
    db.commit()

    # Re-check deduplication -> should return True
    is_dup2, existing = is_duplicate_article(db, comp.id, art_url, art_url, content_hash, "New Product Launch")
    assert is_dup2 is True
    assert existing.id == art.id
    db.close()

def test_article_extractor_html():
    sample_html = """
    <!DOCTYPE html>
    <html>
    <head>
        <title>Sample Headline Post</title>
        <link rel="canonical" href="https://blog.example.com/posts/sample-headline" />
        <meta name="author" content="Jane Doe" />
        <meta property="article:published_time" content="2026-09-27T10:00:00Z" />
    </head>
    <body>
        <article>
            <h1>Sample Headline Post</h1>
            <p>This is paragraph one of the test article body with enough content text.</p>
        </article>
    </body>
    </html>
    """
    extracted = extract_article_details(sample_html, "https://blog.example.com/posts/sample-headline")
    assert extracted["title"] == "Sample Headline Post"
    assert extracted["canonical_url"] == "https://blog.example.com/posts/sample-headline"
    assert extracted["author"] == "Jane Doe"
    assert extracted["publication_time"] is not None
