from typing import List, Optional
from fastapi import APIRouter, Depends, Query
from sqlalchemy.orm import Session
from app.core.database import get_db
from app.models.models import MonitoringCheck, MonitoringSource, Competitor, Notification
from app.schemas.schemas import MonitoringCheckResponse, MonitoringSourceResponse, NotificationResponse

router = APIRouter(prefix="/monitoring", tags=["Monitoring Logs & Sources"])

@router.get("/checks", response_model=List[MonitoringCheckResponse])
def get_monitoring_checks(
    competitor_id: Optional[int] = None,
    success: Optional[bool] = None,
    skip: int = Query(0, ge=0),
    limit: int = Query(100, ge=1, le=500),
    db: Session = Depends(get_db)
):
    query = db.query(MonitoringCheck)
    if competitor_id:
        query = query.filter(MonitoringCheck.competitor_id == competitor_id)
    if success is not None:
        query = query.filter(MonitoringCheck.success == success)
        
    checks = query.order_by(MonitoringCheck.started_at.desc()).offset(skip).limit(limit).all()
    for c in checks:
        if c.competitor:
            c.competitor_name = c.competitor.name
    return checks

@router.get("/sources", response_model=List[MonitoringSourceResponse])
def get_monitoring_sources(competitor_id: Optional[int] = None, db: Session = Depends(get_db)):
    query = db.query(MonitoringSource)
    if competitor_id:
        query = query.filter(MonitoringSource.competitor_id == competitor_id)
    return query.all()

@router.get("/notifications", response_model=List[NotificationResponse])
def get_notifications(skip: int = Query(0, ge=0), limit: int = Query(50, ge=1, le=200), db: Session = Depends(get_db)):
    notifs = db.query(Notification).order_by(Notification.created_at.desc()).offset(skip).limit(limit).all()
    for n in notifs:
        if n.article:
            n.article_title = n.article.title
            if n.article.competitor:
                n.competitor_name = n.article.competitor.name
    return notifs
