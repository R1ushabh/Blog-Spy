import asyncio
import json
import logging
from fastapi import APIRouter
from fastapi.responses import StreamingResponse
from app.workers.scheduler import sse_subscribers

logger = logging.getLogger("sse_events")
router = APIRouter(prefix="/events", tags=["Real-Time SSE Events"])

@router.get("/sse")
async def sse_event_stream():
    """
    Server-Sent Events endpoint delivering real-time notifications,
    monitoring health updates, and scale test metrics to the dashboard without page refresh.
    """
    queue = asyncio.Queue(maxsize=50)
    sse_subscribers.append(queue)

    async def event_generator():
        try:
            # Send initial connection event
            yield f"event: connected\ndata: {json.dumps({'message': 'Real-Time SSE Stream Active'})}\n\n"
            
            while True:
                try:
                    payload = await asyncio.wait_for(queue.get(), timeout=15.0)
                    event_type = payload.get("event", "message")
                    data_json = json.dumps(payload.get("data", {}))
                    yield f"event: {event_type}\ndata: {data_json}\n\n"
                except asyncio.TimeoutError:
                    yield ": keep-alive ping\n\n"
        except Exception:
            pass
        finally:
            if queue in sse_subscribers:
                try:
                    sse_subscribers.remove(queue)
                except ValueError:
                    pass

    return StreamingResponse(event_generator(), media_type="text/event-stream")
