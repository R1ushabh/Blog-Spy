import os
import sys
import asyncio
from datetime import datetime, timezone

sys.path.insert(0, os.path.abspath("backend"))

from app.core.database import SessionLocal
from app.models.models import Competitor, Article, MonitoringSource, MonitoringCheck
from app.services.analyzer import analyze_website
from app.services.strategy_engine import execute_competitor_check
from app.services.deduplicator import normalize_url

REAL_COMPETITORS = [
    {
        "name": "GitHub Blog",
        "website_url": "https://github.blog",
        "blog_url": "https://github.blog",
        "feed_url": "https://github.blog/feed/",
        "sitemap_url": "https://github.blog/sitemap.xml"
    },
    {
        "name": "TechCrunch",
        "website_url": "https://techcrunch.com",
        "blog_url": "https://techcrunch.com",
        "feed_url": "https://techcrunch.com/feed/",
        "sitemap_url": "https://techcrunch.com/sitemap.xml"
    },
    {
        "name": "DEV Community",
        "website_url": "https://dev.to",
        "blog_url": "https://dev.to",
        "feed_url": "https://dev.to/feed",
        "sitemap_url": "https://dev.to/sitemap.xml"
    }
]

async def add_and_test_real_blogs():
    db = SessionLocal()
    print("=== TESTING POPULAR REAL-WORLD BLOGS & WEBSITES ===")

    for item in REAL_COMPETITORS:
        print(f"\n--------------------------------------------------")
        print(f"Target Competitor: {item['name']} ({item['website_url']})")
        
        # 1. Check if competitor already exists
        comp = db.query(Competitor).filter(Competitor.website_url == item["website_url"]).first()
        if not comp:
            print("1. Registering competitor in database...")
            comp = Competitor(
                name=item["name"],
                website_url=item["website_url"],
                blog_url=item["blog_url"],
                feed_url=item["feed_url"],
                sitemap_url=item["sitemap_url"],
                monitoring_enabled=True,
                status="ACTIVE",
                health_status="ONLINE",
                monitoring_interval=60
            )
            db.add(comp)
            db.commit()
            db.refresh(comp)

            # Analyze website sources automatically
            analysis = await analyze_website(comp.website_url, comp.blog_url, comp.feed_url, comp.sitemap_url)
            print(f"   [Discovered Strategy]: {analysis['strategy_reason']}")

            # Save discovered sources
            for rss in analysis["rss_feeds"] + analysis["atom_feeds"]:
                db.add(MonitoringSource(competitor_id=comp.id, source_type="RSS", source_url=rss, priority=1))
            for sm in analysis["sitemaps"]:
                db.add(MonitoringSource(competitor_id=comp.id, source_type="SITEMAP", source_url=sm, priority=2))
            db.add(MonitoringSource(competitor_id=comp.id, source_type="DIRECT_PAGE", source_url=comp.blog_url or comp.website_url, priority=3))
            
            comp.strategy_summary = analysis["strategy_reason"]
            db.commit()
        else:
            print(f"1. Competitor '{comp.name}' already registered (ID={comp.id}).")

        # 2. Execute Monitoring Check Cycle
        print(f"2. Executing real-time monitoring check for {item['name']}...")
        check_res = await execute_competitor_check(db, comp.id)
        print(f"   Check Status: {check_res.get('status')}")
        print(f"   New Articles Discovered: {check_res.get('new_articles')}")
        print(f"   Duration: {check_res.get('duration_ms'):.1f}ms")

        # 3. Query Articles Discovered for this Competitor
        articles = db.query(Article).filter(Article.competitor_id == comp.id).order_by(Article.detected_at.desc()).limit(5).all()
        print(f"3. Sample Articles Stored for {item['name']} (Total = {db.query(Article).filter(Article.competitor_id == comp.id).count()}):")
        for idx, art in enumerate(articles, 1):
            print(f"   [{idx}] {art.title[:60]}")
            print(f"       Method: {art.detection_method} | Delay: {art.detection_delay_display} | Author: {art.author or 'Unknown'}")
            print(f"       URL: {art.canonical_url or art.source_url}")

    db.close()
    print("\n=== REAL-WORLD BLOG TESTING COMPLETE ===")

if __name__ == "__main__":
    asyncio.run(add_and_test_real_blogs())
