from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from app.core.database import get_db
from app.workers.scale_engine import scale_engine
from app.schemas.schemas import ScaleTestStatus

router = APIRouter(prefix="/scale-test", tags=["100-Website Scale Engine"])

@router.post("/seed")
def seed_100_competitors_endpoint(db: Session = Depends(get_db)):
    return scale_engine.seed_100_competitors(db)

@router.post("/start")
def start_scale_test_endpoint():
    scale_engine.start_scale_test()
    return {"status": "started"}

@router.post("/stop")
def stop_scale_test_endpoint():
    scale_engine.stop_scale_test()
    return {"status": "stopped"}

@router.post("/clear")
def clear_scale_test_endpoint(db: Session = Depends(get_db)):
    return scale_engine.clear_scale_test_data(db)

@router.get("/status", response_model=ScaleTestStatus)
def get_scale_test_status_endpoint(db: Session = Depends(get_db)):
    return scale_engine.get_status(db)
