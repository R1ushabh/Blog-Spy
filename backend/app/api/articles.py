from typing import List, Optional
from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session
from app.core.database import get_db
from app.models.models import Article, Competitor
from app.schemas.schemas import ArticleResponse

router = APIRouter(prefix="/articles", tags=["Detected Articles"])

@router.get("", response_model=List[ArticleResponse])
@router.get("/", response_model=List[ArticleResponse])
def list_articles(
    competitor_id: Optional[int] = None,
    search: Optional[str] = None,
    method: Optional[str] = None,
    within_target: Optional[bool] = None,
    skip: int = Query(0, ge=0),
    limit: int = Query(50, ge=1, le=200),
    db: Session = Depends(get_db)
):
    query = db.query(Article)
    if competitor_id:
        query = query.filter(Article.competitor_id == competitor_id)
    if search:
        query = query.filter(
            Article.title.ilike(f"%{search}%") |
            Article.source_url.ilike(f"%{search}%") |
            Article.author.ilike(f"%{search}%")
        )
    if method:
        query = query.filter(Article.detection_method == method)
    if within_target is not None:
        query = query.filter(Article.within_target == within_target)

    articles = query.order_by(Article.detected_at.desc()).offset(skip).limit(limit).all()
    
    # Attach competitor name
    for a in articles:
        if a.competitor:
            a.competitor_name = a.competitor.name
            
    return articles

@router.get("/{article_id}", response_model=ArticleResponse)
def get_article(article_id: int, db: Session = Depends(get_db)):
    article = db.query(Article).filter(Article.id == article_id).first()
    if not article:
        raise HTTPException(status_code=404, detail="Article not found")
    if article.competitor:
        article.competitor_name = article.competitor.name
    return article
