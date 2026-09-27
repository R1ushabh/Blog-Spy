from datetime import datetime, timezone
from sqlalchemy import Column, Integer, String, Boolean, DateTime, Text, Float, ForeignKey, Index, JSON
from sqlalchemy.orm import relationship
from app.core.database import Base

def utcnow():
    return datetime.now(timezone.utc)

class User(Base):
    __tablename__ = "users"
    
    id = Column(Integer, primary_key=True, index=True)
    email = Column(String(255), unique=True, nullable=False, index=True)
    password_hash = Column(String(255), nullable=False)
    role = Column(String(50), default="admin")
    created_at = Column(DateTime, default=utcnow)
    updated_at = Column(DateTime, default=utcnow, onupdate=utcnow)

class Competitor(Base):
    __tablename__ = "competitors"
    
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(255), nullable=False)
    website_url = Column(String(1024), nullable=False)
    blog_url = Column(String(1024), nullable=True)
    feed_url = Column(String(1024), nullable=True)
    sitemap_url = Column(String(1024), nullable=True)
    
    monitoring_enabled = Column(Boolean, default=True)
    status = Column(String(50), default="ACTIVE")  # DISCOVERING, ACTIVE, PAUSED, DEGRADED, OFFLINE, ERROR
    health_status = Column(String(50), default="ONLINE")  # ONLINE, DEGRADED, OFFLINE, PAUSED
    monitoring_interval = Column(Integer, default=60)  # seconds
    
    last_checked_at = Column(DateTime, nullable=True)
    last_success_at = Column(DateTime, nullable=True)
    last_detection_at = Column(DateTime, nullable=True)
    next_check_at = Column(DateTime, nullable=True)
    consecutive_failures = Column(Integer, default=0)
    
    strategy_summary = Column(Text, nullable=True)
    strategy_confidence = Column(JSON, nullable=True)
    
    created_at = Column(DateTime, default=utcnow)
    updated_at = Column(DateTime, default=utcnow, onupdate=utcnow)
    
    # Relationships
    sources = relationship("MonitoringSource", back_populates="competitor", cascade="all, delete-orphan")
    articles = relationship("Article", back_populates="competitor", cascade="all, delete-orphan")
    checks = relationship("MonitoringCheck", back_populates="competitor", cascade="all, delete-orphan")
    events = relationship("MonitoringEvent", back_populates="competitor", cascade="all, delete-orphan")

class MonitoringSource(Base):
    __tablename__ = "monitoring_sources"
    
    id = Column(Integer, primary_key=True, index=True)
    competitor_id = Column(Integer, ForeignKey("competitors.id", ondelete="CASCADE"), nullable=False, index=True)
    source_type = Column(String(50), nullable=False)  # RSS, ATOM, SITEMAP, SITEMAP_INDEX, DIRECT_PAGE, PLAYWRIGHT_FALLBACK
    source_url = Column(String(1024), nullable=False)
    status = Column(String(50), default="ACTIVE")  # ACTIVE, INACTIVE, ERROR
    priority = Column(Integer, default=1)  # 1 = highest
    
    discovered_at = Column(DateTime, default=utcnow)
    last_success_at = Column(DateTime, nullable=True)
    last_error_at = Column(DateTime, nullable=True)
    configuration_json = Column(JSON, nullable=True)
    
    competitor = relationship("Competitor", back_populates="sources")

class Article(Base):
    __tablename__ = "articles"
    
    id = Column(Integer, primary_key=True, index=True)
    competitor_id = Column(Integer, ForeignKey("competitors.id", ondelete="CASCADE"), nullable=False, index=True)
    
    title = Column(String(1024), nullable=False)
    body = Column(Text, nullable=True)
    excerpt = Column(Text, nullable=True)
    featured_image = Column(String(1024), nullable=True)
    author = Column(String(255), nullable=True)
    
    publication_time = Column(DateTime, nullable=True, index=True)
    detected_at = Column(DateTime, default=utcnow, index=True)
    detection_delay_seconds = Column(Float, nullable=True)
    detection_delay_display = Column(String(100), nullable=True)
    detection_method = Column(String(50), nullable=False, index=True)  # RSS, ATOM, SITEMAP, DIRECT_PAGE, PLAYWRIGHT
    
    source_url = Column(String(1024), nullable=False, index=True)
    original_url = Column(String(1024), nullable=True)
    canonical_url = Column(String(1024), nullable=True, index=True)
    
    meta_description = Column(Text, nullable=True)
    categories = Column(JSON, nullable=True)  # List of strings
    tags = Column(JSON, nullable=True)  # List of strings
    relevant_links = Column(JSON, nullable=True)  # List of link dicts/strings
    content_hash = Column(String(64), nullable=False, index=True)
    
    status = Column(String(50), default="STORED")  # DETECTED, EXTRACTED, STORED, NOTIFIED, FAILED_EXTRACTION
    within_target = Column(Boolean, default=True)  # detection_delay_seconds <= 300
    
    created_at = Column(DateTime, default=utcnow)
    updated_at = Column(DateTime, default=utcnow, onupdate=utcnow)
    
    competitor = relationship("Competitor", back_populates="articles")
    images = relationship("ArticleImage", back_populates="article", cascade="all, delete-orphan")
    notifications = relationship("Notification", back_populates="article", cascade="all, delete-orphan")

class ArticleImage(Base):
    __tablename__ = "article_images"
    
    id = Column(Integer, primary_key=True, index=True)
    article_id = Column(Integer, ForeignKey("articles.id", ondelete="CASCADE"), nullable=False, index=True)
    image_url = Column(String(1024), nullable=False)
    image_type = Column(String(50), default="inline")  # featured, og, twitter, inline
    alt_text = Column(String(512), nullable=True)
    position = Column(Integer, default=0)
    
    article = relationship("Article", back_populates="images")

class MonitoringCheck(Base):
    __tablename__ = "monitoring_checks"
    
    id = Column(Integer, primary_key=True, index=True)
    competitor_id = Column(Integer, ForeignKey("competitors.id", ondelete="CASCADE"), nullable=False, index=True)
    source_id = Column(Integer, ForeignKey("monitoring_sources.id", ondelete="SET NULL"), nullable=True)
    
    started_at = Column(DateTime, default=utcnow, index=True)
    completed_at = Column(DateTime, nullable=True)
    duration_ms = Column(Float, default=0.0)
    success = Column(Boolean, default=True)
    http_status = Column(Integer, nullable=True)
    articles_found = Column(Integer, default=0)
    new_articles_found = Column(Integer, default=0)
    error_type = Column(String(100), nullable=True)
    error_message = Column(Text, nullable=True)
    retry_count = Column(Integer, default=0)
    
    competitor = relationship("Competitor", back_populates="checks")

class Notification(Base):
    __tablename__ = "notifications"
    
    id = Column(Integer, primary_key=True, index=True)
    article_id = Column(Integer, ForeignKey("articles.id", ondelete="CASCADE"), nullable=False, index=True)
    notification_type = Column(String(50), default="DASHBOARD")  # DASHBOARD, EMAIL, WEBSOCKET
    status = Column(String(50), default="SENT")  # PENDING, SENT, FAILED
    created_at = Column(DateTime, default=utcnow)
    sent_at = Column(DateTime, nullable=True)
    error_message = Column(Text, nullable=True)
    
    article = relationship("Article", back_populates="notifications")

class MonitoringEvent(Base):
    __tablename__ = "monitoring_events"
    
    id = Column(Integer, primary_key=True, index=True)
    competitor_id = Column(Integer, ForeignKey("competitors.id", ondelete="CASCADE"), nullable=False, index=True)
    event_type = Column(String(100), nullable=False)  # HEALTH_CHANGE, STRATEGY_CHANGE, STRUCTURE_WARN, RETRY, FAILURE
    timestamp = Column(DateTime, default=utcnow, index=True)
    payload_json = Column(JSON, nullable=True)
    
    competitor = relationship("Competitor", back_populates="events")

class SystemMetric(Base):
    __tablename__ = "system_metrics"
    
    id = Column(Integer, primary_key=True, index=True)
    timestamp = Column(DateTime, default=utcnow, index=True)
    active_competitors = Column(Integer, default=0)
    active_workers = Column(Integer, default=0)
    checks_per_minute = Column(Float, default=0.0)
    articles_detected = Column(Integer, default=0)
    failed_checks = Column(Integer, default=0)
    average_detection_delay = Column(Float, default=0.0)

# Indexes for explicit mandatory performance requirements
Index("idx_articles_competitor_pubtime", Article.competitor_id, Article.publication_time)
Index("idx_articles_canonical_hash", Article.canonical_url, Article.content_hash)
