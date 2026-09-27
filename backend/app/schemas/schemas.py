from datetime import datetime
from typing import List, Optional, Any, Dict
from pydantic import BaseModel, HttpUrl, EmailStr, Field

# User Schemas
class UserBase(BaseModel):
    email: EmailStr
    role: str = "admin"

class UserCreate(UserBase):
    password: str

class UserResponse(UserBase):
    id: int
    created_at: datetime
    class Config:
        from_attributes = True

class Token(BaseModel):
    access_token: str
    token_type: str = "bearer"
    user: UserResponse

# Competitor Schemas
class CompetitorCreate(BaseModel):
    name: str = Field(..., description="Name of the competitor")
    website_url: str = Field(..., description="Main website URL")
    blog_url: Optional[str] = None
    feed_url: Optional[str] = None
    sitemap_url: Optional[str] = None
    monitoring_enabled: bool = True
    monitoring_interval: int = Field(60, ge=10, le=3600, description="Interval in seconds")

class CompetitorUpdate(BaseModel):
    name: Optional[str] = None
    website_url: Optional[str] = None
    blog_url: Optional[str] = None
    feed_url: Optional[str] = None
    sitemap_url: Optional[str] = None
    monitoring_enabled: Optional[bool] = None
    monitoring_interval: Optional[int] = None
    status: Optional[str] = None

class MonitoringSourceResponse(BaseModel):
    id: int
    competitor_id: int
    source_type: str
    source_url: str
    status: str
    priority: int
    discovered_at: datetime
    last_success_at: Optional[datetime] = None
    last_error_at: Optional[datetime] = None
    configuration_json: Optional[Any] = None
    class Config:
        from_attributes = True

class CompetitorResponse(BaseModel):
    id: int
    name: str
    website_url: str
    blog_url: Optional[str] = None
    feed_url: Optional[str] = None
    sitemap_url: Optional[str] = None
    monitoring_enabled: bool
    status: str
    health_status: str
    monitoring_interval: int
    last_checked_at: Optional[datetime] = None
    last_success_at: Optional[datetime] = None
    last_detection_at: Optional[datetime] = None
    next_check_at: Optional[datetime] = None
    consecutive_failures: int
    strategy_summary: Optional[str] = None
    strategy_confidence: Optional[Any] = None
    created_at: datetime
    updated_at: datetime
    sources: List[MonitoringSourceResponse] = []
    class Config:
        from_attributes = True

# Website Analysis Schema
class WebsiteAnalysisResult(BaseModel):
    website: str
    blog_section: Optional[str] = None
    rss_feeds: List[str] = []
    atom_feeds: List[str] = []
    sitemaps: List[str] = []
    sitemap_indexes: List[str] = []
    article_patterns: List[str] = []
    publication_date_signals: List[str] = []
    canonical_signals: List[str] = []
    structured_metadata: List[str] = []
    recommended_strategies: List[str] = []
    confidence_scores: Dict[str, str] = {}
    strategy_reason: str = ""

# Article Schemas
class ArticleImageResponse(BaseModel):
    id: int
    image_url: str
    image_type: str
    alt_text: Optional[str] = None
    position: int
    class Config:
        from_attributes = True

class ArticleResponse(BaseModel):
    id: int
    competitor_id: int
    competitor_name: Optional[str] = None
    title: str
    body: Optional[str] = None
    excerpt: Optional[str] = None
    featured_image: Optional[str] = None
    author: Optional[str] = None
    publication_time: Optional[datetime] = None
    detected_at: datetime
    detection_delay_seconds: Optional[float] = None
    detection_delay_display: Optional[str] = None
    detection_method: str
    source_url: str
    original_url: Optional[str] = None
    canonical_url: Optional[str] = None
    meta_description: Optional[str] = None
    categories: Optional[List[str]] = []
    tags: Optional[List[str]] = []
    relevant_links: Optional[Any] = []
    content_hash: str
    status: str
    within_target: bool
    created_at: datetime
    images: List[ArticleImageResponse] = []
    class Config:
        from_attributes = True

# Monitoring Check Schema
class MonitoringCheckResponse(BaseModel):
    id: int
    competitor_id: int
    competitor_name: Optional[str] = None
    source_id: Optional[int] = None
    started_at: datetime
    completed_at: Optional[datetime] = None
    duration_ms: float
    success: bool
    http_status: Optional[int] = None
    articles_found: int
    new_articles_found: int
    error_type: Optional[str] = None
    error_message: Optional[str] = None
    retry_count: int
    class Config:
        from_attributes = True

# Notification Schema
class NotificationResponse(BaseModel):
    id: int
    article_id: int
    article_title: Optional[str] = None
    competitor_name: Optional[str] = None
    notification_type: str
    status: str
    created_at: datetime
    sent_at: Optional[datetime] = None
    error_message: Optional[str] = None
    class Config:
        from_attributes = True

# Analytics Overview
class AnalyticsOverview(BaseModel):
    active_competitors: int
    active_monitors: int
    total_articles: int
    average_detection_delay_seconds: float
    average_detection_delay_display: str
    fastest_delay_display: str
    slowest_delay_display: str
    failed_checks_count: int
    within_target_percentage: float
    total_checks: int
    checks_per_minute: float

# Scale Test Schemas
class ScaleTestStatus(BaseModel):
    is_running: bool
    total_competitors: int
    active_workers: int
    processing_count: int
    successful_checks: int
    failed_checks: int
    retrying_checks: int
    articles_detected: int
    average_check_duration_ms: float
    checks_per_minute: float
