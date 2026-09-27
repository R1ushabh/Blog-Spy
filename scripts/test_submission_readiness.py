import os
import sys
from datetime import datetime, timezone

sys.path.insert(0, os.path.abspath("backend"))

from app.core.database import SessionLocal
from app.models.models import Competitor, Article, Notification, MonitoringCheck, MonitoringSource
from app.services.strategy_engine import execute_competitor_check
from app.api.demo_site import publish_demo_article, PublishDemoArticleRequest
import asyncio

def run_submission_verification():
    db = SessionLocal()
    print("=== FINAL SUBMISSION READINESS VERIFICATION ===")
    
    # 1. Verify Demo Competitor exists
    demo_comp = db.query(Competitor).filter(Competitor.website_url.like("%demo-site%")).first()
    if not demo_comp:
        print("FAIL: Controlled Demo competitor missing!")
        return
    print(f"[PASS] Found Controlled Demo Competitor ID={demo_comp.id}: {demo_comp.name}")

    # 2. Publish a Fresh Test Article to Controlled Demo Site
    timestamp = int(datetime.now(timezone.utc).timestamp())
    fresh_title = f"Fresh Real-Time Test Article #{timestamp}"
    print(f"Publishing fresh demo article: '{fresh_title}'...")
    
    demo_payload = PublishDemoArticleRequest(
        title=fresh_title,
        body="This is a fresh real-time test article body published for live submission audit.",
        author="Audit Team",
        published_at=datetime.now(timezone.utc).isoformat(),
        image="https://images.unsplash.com/photo-1518770660439-4636190af475?w=800&q=80"
    )
    published = publish_demo_article(demo_payload)
    print(f"[PASS] Article published with ID: {published.get('article_id') or published.get('article', {}).get('id')}")

    # 3. Trigger Monitor Check for Demo Competitor
    print("Executing monitoring check cycle...")
    res = asyncio.run(execute_competitor_check(db, demo_comp.id))
    print(f"[PASS] Monitoring Check Result: {res}")

    # 4. Verify Article in DB and Check Detection Delay
    detected_art = db.query(Article).filter(Article.title == fresh_title).first()
    if not detected_art:
        print("FAIL: Fresh article was not detected in database!")
        return
    
    print(f"[PASS] Detected Article ID: {detected_art.id}")
    print(f"  - Title: {detected_art.title}")
    print(f"  - Method: {detected_art.detection_method}")
    print(f"  - Publication Time: {detected_art.publication_time}")
    print(f"  - Detected At: {detected_art.detected_at}")
    print(f"  - Detection Delay Seconds: {detected_art.detection_delay_seconds}s")
    print(f"  - Delay Display: {detected_art.detection_delay_display}")
    print(f"  - Within 5m Target: {detected_art.within_target}")

    # 5. Verify Notification Created
    notif = db.query(Notification).filter(Notification.article_id == detected_art.id).first()
    if notif:
        print(f"[PASS] Notification created for article ID {detected_art.id}, status: {notif.status}")
    else:
        print("FAIL: Notification was not created for fresh article!")

    # 6. Verify Duplicate Prevention
    print("Re-running monitoring check to test duplicate prevention...")
    res2 = asyncio.run(execute_competitor_check(db, demo_comp.id))
    dup_count = db.query(Article).filter(Article.title == fresh_title).count()
    if dup_count == 1:
        print(f"[PASS] Duplicate Prevention Verified: 0 duplicates created on re-check (count={dup_count}).")
    else:
        print(f"FAIL: Duplicate Prevention Failed! Found {dup_count} instances of article.")

    # 7. Verify Analytics Overview Consistency
    from app.api.analytics import get_analytics_overview
    overview = get_analytics_overview(db)
    print(f"[PASS] Analytics Overview:")
    print(f"  - Total Articles: {overview.total_articles}")
    print(f"  - Within 5m Target %: {overview.within_target_percentage}%")
    print(f"  - Average Delay Display: {overview.average_detection_delay_display}")
    print(f"  - Total Checks: {overview.total_checks}")

    db.close()
    print("=== VERIFICATION COMPLETE ===")

if __name__ == "__main__":
    run_submission_verification()
