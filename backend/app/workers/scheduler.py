import asyncio
import logging
from datetime import datetime, timezone
from typing import List
from sqlalchemy.orm import Session
from app.core.database import SessionLocal
from app.models.models import Competitor
from app.services.strategy_engine import execute_competitor_check

logger = logging.getLogger("scheduler")

# SSE event broadcast subscribers queue
sse_subscribers: List[asyncio.Queue] = []

async def broadcast_event(event_type: str, data: dict):
    """
    Broadcasts real-time events (new_article, system_health) to all connected SSE clients.
    """
    payload = {"event": event_type, "data": data, "timestamp": datetime.now(timezone.utc).isoformat()}
    for queue in list(sse_subscribers):
        try:
            queue.put_nowait(payload)
        except Exception:
            pass

def run_sync_competitor_check(competitor_id: int) -> dict:
    """Runs a competitor check in an isolated synchronous thread session."""
    db = SessionLocal()
    try:
        return asyncio.run(execute_competitor_check(db, competitor_id))
    except Exception as e:
        logger.error(f"Sync check error for competitor {competitor_id}: {e}")
        return {"status": "error", "new_articles": 0, "error": str(e)}
    finally:
        db.close()

class BackgroundScheduler:
    def __init__(self):
        self.is_running = False
        self._task = None

    def start(self):
        if not self.is_running:
            self.is_running = True
            self._task = asyncio.create_task(self._run_loop())
            logger.info("Continuous Background Scheduler started.")

    def stop(self):
        self.is_running = False
        if self._task:
            self._task.cancel()
            logger.info("Continuous Background Scheduler stopped.")

    async def _run_loop(self):
        while self.is_running:
            try:
                await self._process_due_competitors()
            except Exception as e:
                logger.error(f"Scheduler loop error: {e}")
            await asyncio.sleep(5) # Poll every 5 seconds

    async def _process_due_competitors(self):
        due_ids = await asyncio.to_thread(self._get_due_competitor_ids)
        if not due_ids:
            return

        sem = asyncio.Semaphore(10)
        async def sem_task(cid):
            async with sem:
                await self._run_single_check(cid)

        await asyncio.gather(*(sem_task(cid) for cid in due_ids), return_exceptions=True)

    def _get_due_competitor_ids(self) -> List[int]:
        db = SessionLocal()
        try:
            now = datetime.now(timezone.utc).replace(tzinfo=None)
            due_comps = db.query(Competitor).filter(
                Competitor.monitoring_enabled == True,
                Competitor.status != "PAUSED",
                ~Competitor.name.like("Scale Site %")
            ).all()

            due_ids = []
            for comp in due_comps:
                if not comp.last_checked_at or (now - comp.last_checked_at).total_seconds() >= comp.monitoring_interval:
                    due_ids.append(comp.id)
            return due_ids
        finally:
            db.close()

    async def _run_single_check(self, competitor_id: int):
        # Run network checks off the main Uvicorn event loop thread!
        res = await asyncio.to_thread(run_sync_competitor_check, competitor_id)
        if res.get("new_articles", 0) > 0:
            db = SessionLocal()
            try:
                comp = db.query(Competitor).filter(Competitor.id == competitor_id).first()
                await broadcast_event("new_article", {
                    "competitor_id": competitor_id,
                    "competitor_name": comp.name if comp else "",
                    "new_articles": res.get("new_articles")
                })
            finally:
                db.close()

scheduler = BackgroundScheduler()
