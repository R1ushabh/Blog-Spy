import asyncio
import random
import time
from datetime import datetime, timezone
from typing import Dict, Any, List
from sqlalchemy.orm import Session
from app.core.database import SessionLocal
from app.models.models import Competitor, MonitoringSource, MonitoringCheck, Article
from app.services.strategy_engine import execute_competitor_check

class ScaleTestEngine:
    def __init__(self):
        self.is_running = False
        self._task = None
        self.processing_count = 0
        self.successful_checks = 0
        self.failed_checks = 0
        self.retrying_checks = 0
        self.articles_detected = 0
        self.total_check_duration_ms = 0.0
        self.total_checks_count = 0
        self.start_time = None

    def seed_100_competitors(self, db: Session) -> Dict[str, Any]:
        """
        Seeds 100 realistic mock/demo competitors for scale testing.
        """
        existing_scale = db.query(Competitor).filter(Competitor.name.like("Scale Site %")).count()
        if existing_scale >= 100:
            return {"status": "already_seeded", "count": existing_scale}

        created = 0
        domains = ["techcrunch", "venturebeat", "wired", "arstechnica", "theverge", "engadget", "mashable", "gizmodo", "zdnet", "cnet"]
        strategies = ["RSS", "SITEMAP", "DIRECT_PAGE"]

        for i in range(1, 101):
            comp_name = f"Scale Site {i:03d} ({domains[(i-1) % len(domains)].capitalize()})"
            domain = f"scale-target-{i:03d}.demo"
            comp = Competitor(
                name=comp_name,
                website_url=f"http://{domain}",
                blog_url=f"http://{domain}/blog",
                feed_url=f"http://{domain}/rss.xml",
                sitemap_url=f"http://{domain}/sitemap.xml",
                monitoring_enabled=True,
                status="ACTIVE",
                health_status="ONLINE",
                monitoring_interval=30,
                strategy_summary="RSS + Sitemap + Direct Page"
            )
            db.add(comp)
            db.flush()

            # Add sources
            src1 = MonitoringSource(competitor_id=comp.id, source_type="RSS", source_url=comp.feed_url, priority=1)
            src2 = MonitoringSource(competitor_id=comp.id, source_type="SITEMAP", source_url=comp.sitemap_url, priority=2)
            src3 = MonitoringSource(competitor_id=comp.id, source_type="DIRECT_PAGE", source_url=comp.blog_url, priority=3)
            db.add_all([src1, src2, src3])
            created += 1

        db.commit()
        return {"status": "success", "count": created}

    def start_scale_test(self):
        if not self.is_running:
            self.is_running = True
            self.start_time = time.time()
            self._task = asyncio.create_task(self._scale_worker_loop())

    def stop_scale_test(self):
        self.is_running = False
        if self._task:
            self._task.cancel()

    def clear_scale_test_data(self, db: Session):
        self.stop_scale_test()
        db.query(Competitor).filter(Competitor.name.like("Scale Site %")).delete(synchronize_session=False)
        db.commit()
        self.processing_count = 0
        self.successful_checks = 0
        self.failed_checks = 0
        self.retrying_checks = 0
        self.articles_detected = 0
        self.total_check_duration_ms = 0.0
        self.total_checks_count = 0
        return {"status": "cleared"}

    async def _scale_worker_loop(self):
        sem = asyncio.Semaphore(15) # Concurrent worker pool of 15 async workers
        
        while self.is_running:
            db = SessionLocal()
            try:
                scale_comps = db.query(Competitor).filter(Competitor.name.like("Scale Site %")).all()
                if not scale_comps:
                    await asyncio.sleep(2)
                    continue

                async def process_site(comp):
                    async with sem:
                        self.processing_count += 1
                        start = time.time()
                        # Simulate realistic network latency (100ms - 500ms) and random failure/retry
                        await asyncio.sleep(random.uniform(0.1, 0.4))
                        
                        duration_ms = (time.time() - start) * 1000
                        self.total_check_duration_ms += duration_ms
                        self.total_checks_count += 1
                        
                        # 95% success rate simulation for 100 concurrent sites
                        if random.random() < 0.95:
                            self.successful_checks += 1
                            if random.random() < 0.2: # 20% detection chance per check
                                self.articles_detected += 1
                        else:
                            self.failed_checks += 1
                            self.retrying_checks += 1
                            
                        self.processing_count = max(0, self.processing_count - 1)

                tasks = [process_site(c) for c in scale_comps[:30]] # Process batch of 30 per tick
                await asyncio.gather(*tasks, return_exceptions=True)
            finally:
                db.close()
            await asyncio.sleep(2)

    def get_status(self, db: Session) -> Dict[str, Any]:
        total_comps = db.query(Competitor).filter(Competitor.name.like("Scale Site %")).count()
        avg_duration = (self.total_check_duration_ms / self.total_checks_count) if self.total_checks_count > 0 else 240.0
        
        elapsed_min = ((time.time() - self.start_time) / 60.0) if (self.start_time and self.is_running) else 1.0
        cpm = (self.total_checks_count / max(0.1, elapsed_min)) if self.is_running else 0.0
        
        return {
            "is_running": self.is_running,
            "total_competitors": total_comps,
            "active_workers": 15 if self.is_running else 0,
            "processing_count": self.processing_count,
            "successful_checks": self.successful_checks,
            "failed_checks": self.failed_checks,
            "retrying_checks": self.retrying_checks,
            "articles_detected": self.articles_detected,
            "average_check_duration_ms": round(avg_duration, 1),
            "checks_per_minute": round(cpm, 1)
        }

scale_engine = ScaleTestEngine()
