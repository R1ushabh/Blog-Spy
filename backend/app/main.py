import logging
from contextlib import asynccontextmanager
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.core.config import settings
from app.core.database import engine, Base, SessionLocal
from app.api import auth, competitors, articles, monitoring, analytics, scale_test, evidence, events, demo_site
from app.workers.scheduler import scheduler
from app.models.models import Competitor, MonitoringSource

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("main")

@asynccontextmanager
async def lifespan(app: FastAPI):
    # 1. Create DB Tables
    logger.info("Creating database tables if not existing...")
    Base.metadata.create_all(bind=engine)
    
    # 2. Seed Default Controlled Demo Competitor if DB empty
    db = SessionLocal()
    try:
        if db.query(Competitor).count() == 0:
            logger.info("Seeding default controlled demo competitor...")
            demo_comp = Competitor(
                name="Acme Corp Demo Blog",
                website_url="http://127.0.0.1:8000/api/demo-site",
                blog_url="http://127.0.0.1:8000/api/demo-site",
                feed_url="http://127.0.0.1:8000/api/demo-site/rss.xml",
                sitemap_url="http://127.0.0.1:8000/api/demo-site/sitemap.xml",
                monitoring_enabled=True,
                status="ACTIVE",
                health_status="ONLINE",
                monitoring_interval=30,
                strategy_summary="RSS + Sitemap + Direct Page (Controlled Environment)"
            )
            db.add(demo_comp)
            db.flush()
            
            src1 = MonitoringSource(competitor_id=demo_comp.id, source_type="RSS", source_url=demo_comp.feed_url, priority=1)
            src2 = MonitoringSource(competitor_id=demo_comp.id, source_type="SITEMAP", source_url=demo_comp.sitemap_url, priority=2)
            src3 = MonitoringSource(competitor_id=demo_comp.id, source_type="DIRECT_PAGE", source_url=demo_comp.blog_url, priority=3)
            db.add_all([src1, src2, src3])
            db.commit()
    except Exception as e:
        logger.error(f"Error seeding demo competitor: {e}")
    finally:
        db.close()

    # 3. Start Background Scheduler
    scheduler.start()
    
    yield
    
    # Shutdown
    scheduler.stop()

app = FastAPI(
    title=settings.PROJECT_NAME,
    openapi_url="/api/openapi.json",
    docs_url="/api/docs",
    redoc_url="/api/redoc",
    lifespan=lifespan
)

# CORS Middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_origin_regex=r"https?://.*",
    allow_credentials=False,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Health endpoint
@app.get("/health", tags=["Health Check"])
def health_check():
    return {"status": "ok", "service": "CompetitorSpy API", "version": "1.0.0"}

# Include Routers
app.include_router(auth.router, prefix=settings.API_V1_STR)
app.include_router(competitors.router, prefix=settings.API_V1_STR)
app.include_router(articles.router, prefix=settings.API_V1_STR)
app.include_router(monitoring.router, prefix=settings.API_V1_STR)
app.include_router(analytics.router, prefix=settings.API_V1_STR)
app.include_router(scale_test.router, prefix=settings.API_V1_STR)
app.include_router(evidence.router, prefix=settings.API_V1_STR)
app.include_router(events.router, prefix=settings.API_V1_STR)
app.include_router(demo_site.router, prefix=settings.API_V1_STR)
