from typing import Dict, Any, List
from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from sqlalchemy import func
from app.core.database import get_db
from app.models.models import Competitor, Article, MonitoringCheck, MonitoringSource
from app.schemas.schemas import AnalyticsOverview
from app.services.strategy_engine import calculate_delay

router = APIRouter(prefix="/analytics", tags=["Analytics & Health Metrics"])

@router.get("/overview", response_model=AnalyticsOverview)
def get_analytics_overview(db: Session = Depends(get_db)):
    active_competitors = db.query(Competitor).filter(Competitor.monitoring_enabled == True).count()
    active_monitors = db.query(MonitoringSource).filter(MonitoringSource.status == "ACTIVE").count()
    total_articles = db.query(Article).count()
    
    # Calculate delay metrics from DB
    realtime_avg = db.query(func.avg(Article.detection_delay_seconds)).filter(Article.detection_delay_seconds <= 3600).scalar()
    overall_avg = db.query(func.avg(Article.detection_delay_seconds)).scalar() or 0.0
    avg_delay_sec = realtime_avg if realtime_avg is not None else overall_avg
    
    min_delay_sec = db.query(func.min(Article.detection_delay_seconds)).scalar()
    max_delay_sec = db.query(func.max(Article.detection_delay_seconds)).scalar()
    
    avg_display = f"{int(avg_delay_sec)} sec" if avg_delay_sec < 60 else f"{int(avg_delay_sec // 60)} min {int(avg_delay_sec % 60):02d} sec"
    fastest_display = f"{int(min_delay_sec)} sec" if min_delay_sec is not None and min_delay_sec < 60 else f"{int(min_delay_sec // 60)} min {int(min_delay_sec % 60):02d} sec" if min_delay_sec else "N/A"
    slowest_display = "Backfill (Historical)" if max_delay_sec and max_delay_sec >= 3600 else f"{int(max_delay_sec // 60)} min {int(max_delay_sec % 60):02d} sec" if max_delay_sec else "N/A"
    
    failed_checks_count = db.query(MonitoringCheck).filter(MonitoringCheck.success == False).count()
    total_checks = db.query(MonitoringCheck).count()
    
    within_target_count = db.query(Article).filter(Article.within_target == True).count()
    within_target_pct = (within_target_count / total_articles * 100.0) if total_articles > 0 else 0.0

    return AnalyticsOverview(
        active_competitors=active_competitors,
        active_monitors=active_monitors,
        total_articles=total_articles,
        average_detection_delay_seconds=round(avg_delay_sec, 1),
        average_detection_delay_display=avg_display,
        fastest_delay_display=fastest_display,
        slowest_delay_display=slowest_display,
        failed_checks_count=failed_checks_count,
        within_target_percentage=round(within_target_pct, 1),
        total_checks=total_checks,
        checks_per_minute=round(total_checks / 10.0, 1) if total_checks > 0 else 0.0
    )

@router.get("/detection-delays")
def get_detection_delay_chart_data(db: Session = Depends(get_db)):
    articles = db.query(Article).order_by(Article.detected_at.asc()).limit(30).all()
    data = []
    for a in articles:
        data.append({
            "id": a.id,
            "title": a.title[:30] + "...",
            "competitor": a.competitor.name if a.competitor else "Unknown",
            "delay_seconds": round(a.detection_delay_seconds or 0, 1),
            "delay_display": a.detection_delay_display or "0 sec",
            "method": a.detection_method,
            "within_target": a.within_target,
            "detected_at": a.detected_at.isoformat()
        })
    return data

@router.get("/methods")
def get_detection_methods_breakdown(db: Session = Depends(get_db)):
    results = db.query(
        Article.detection_method,
        func.count(Article.id).label("article_count"),
        func.avg(Article.detection_delay_seconds).label("avg_delay")
    ).group_by(Article.detection_method).all()
    
    data = []
    for r in results:
        data.append({
            "method": r.detection_method,
            "article_count": r.article_count,
            "avg_delay_seconds": round(r.avg_delay or 0, 1)
        })
    return data
