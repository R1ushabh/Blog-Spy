from typing import List, Optional
from fastapi import APIRouter, Depends, HTTPException, Query, BackgroundTasks
from sqlalchemy.orm import Session
from app.core.database import get_db
from app.models.models import Competitor, MonitoringSource, MonitoringEvent
from app.schemas.schemas import CompetitorCreate, CompetitorResponse, CompetitorUpdate, WebsiteAnalysisResult
from app.services.analyzer import analyze_website
from app.services.strategy_engine import execute_competitor_check
from app.services.deduplicator import normalize_url

router = APIRouter(prefix="/competitors", tags=["Competitor Management"])

@router.get("", response_model=List[CompetitorResponse])
@router.get("/", response_model=List[CompetitorResponse])
def list_competitors(
    search: Optional[str] = None,
    status: Optional[str] = None,
    skip: int = Query(0, ge=0),
    limit: int = Query(100, ge=1, le=500),
    db: Session = Depends(get_db)
):
    query = db.query(Competitor)
    if search:
        query = query.filter(Competitor.name.ilike(f"%{search}%") | Competitor.website_url.ilike(f"%{search}%"))
    if status:
        query = query.filter(Competitor.status == status)
    return query.order_by(Competitor.created_at.desc()).offset(skip).limit(limit).all()

@router.post("", response_model=CompetitorResponse)
@router.post("/", response_model=CompetitorResponse)
async def create_competitor(
    payload: CompetitorCreate,
    background_tasks: BackgroundTasks,
    db: Session = Depends(get_db)
):
    normalized = normalize_url(payload.website_url)
    existing = db.query(Competitor).filter(Competitor.website_url == normalized).first()
    if existing:
        raise HTTPException(status_code=400, detail="Competitor website already registered.")

    competitor = Competitor(
        name=payload.name,
        website_url=normalized,
        blog_url=normalize_url(payload.blog_url) if payload.blog_url else None,
        feed_url=normalize_url(payload.feed_url) if payload.feed_url else None,
        sitemap_url=normalize_url(payload.sitemap_url) if payload.sitemap_url else None,
        monitoring_enabled=payload.monitoring_enabled,
        monitoring_interval=payload.monitoring_interval,
        status="DISCOVERING",
        health_status="ONLINE"
    )
    db.add(competitor)
    db.commit()
    db.refresh(competitor)

    # Automatically analyze website sources upon creation
    analysis = await analyze_website(
        website_url=competitor.website_url,
        blog_url=competitor.blog_url,
        feed_url=competitor.feed_url,
        sitemap_url=competitor.sitemap_url
    )

    # Save discovered sources
    for rss in analysis["rss_feeds"] + analysis["atom_feeds"]:
        db.add(MonitoringSource(competitor_id=competitor.id, source_type="RSS", source_url=rss, priority=1))
    for sm in analysis["sitemaps"]:
        db.add(MonitoringSource(competitor_id=competitor.id, source_type="SITEMAP", source_url=sm, priority=2))
    
    # Always add Direct Page fallback source
    db.add(MonitoringSource(competitor_id=competitor.id, source_type="DIRECT_PAGE", source_url=competitor.blog_url or competitor.website_url, priority=3))

    competitor.status = "ACTIVE"
    competitor.strategy_summary = analysis["strategy_reason"]
    competitor.strategy_confidence = analysis["confidence_scores"]
    
    db.commit()
    db.refresh(competitor)

    # Trigger immediate initial check in background
    background_tasks.add_task(execute_competitor_check, db, competitor.id)

    return competitor

@router.get("/{competitor_id}", response_model=CompetitorResponse)
def get_competitor(competitor_id: int, db: Session = Depends(get_db)):
    comp = db.query(Competitor).filter(Competitor.id == competitor_id).first()
    if not comp:
        raise HTTPException(status_code=404, detail="Competitor not found")
    return comp

@router.put("/{competitor_id}", response_model=CompetitorResponse)
def update_competitor(competitor_id: int, payload: CompetitorUpdate, db: Session = Depends(get_db)):
    comp = db.query(Competitor).filter(Competitor.id == competitor_id).first()
    if not comp:
        raise HTTPException(status_code=404, detail="Competitor not found")
        
    for k, v in payload.dict(exclude_unset=True).items():
        setattr(comp, k, v)
        
    db.commit()
    db.refresh(comp)
    return comp

@router.delete("/{competitor_id}")
def delete_competitor(competitor_id: int, db: Session = Depends(get_db)):
    comp = db.query(Competitor).filter(Competitor.id == competitor_id).first()
    if not comp:
        raise HTTPException(status_code=404, detail="Competitor not found")
    db.delete(comp)
    db.commit()
    return {"status": "deleted", "id": competitor_id}

@router.post("/{competitor_id}/analyze", response_model=WebsiteAnalysisResult)
async def analyze_competitor_endpoint(competitor_id: int, db: Session = Depends(get_db)):
    comp = db.query(Competitor).filter(Competitor.id == competitor_id).first()
    if not comp:
        raise HTTPException(status_code=404, detail="Competitor not found")
        
    res = await analyze_website(comp.website_url, comp.blog_url, comp.feed_url, comp.sitemap_url)
    return res

@router.post("/{competitor_id}/check-now")
async def check_competitor_now(competitor_id: int, db: Session = Depends(get_db)):
    """Triggers an immediate production monitoring check for this competitor."""
    comp = db.query(Competitor).filter(Competitor.id == competitor_id).first()
    if not comp:
        raise HTTPException(status_code=404, detail="Competitor not found")
        
    result = await execute_competitor_check(db, competitor_id)
    return result

@router.post("/{competitor_id}/pause")
def pause_competitor(competitor_id: int, db: Session = Depends(get_db)):
    comp = db.query(Competitor).filter(Competitor.id == competitor_id).first()
    if not comp:
        raise HTTPException(status_code=404, detail="Competitor not found")
    comp.status = "PAUSED"
    comp.health_status = "PAUSED"
    db.commit()
    return {"status": "paused", "competitor_id": competitor_id}

@router.post("/{competitor_id}/resume")
def resume_competitor(competitor_id: int, db: Session = Depends(get_db)):
    comp = db.query(Competitor).filter(Competitor.id == competitor_id).first()
    if not comp:
        raise HTTPException(status_code=404, detail="Competitor not found")
    comp.status = "ACTIVE"
    comp.health_status = "ONLINE"
    db.commit()
    return {"status": "resumed", "competitor_id": competitor_id}
