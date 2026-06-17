from fastapi import APIRouter
from sqlalchemy.orm import Session
from fastapi import Depends
from uuid import uuid4

from app.models import TrackingSession
from app.dependencies import get_db

router = APIRouter(
    prefix="/sessions",
    tags=["sessions"],
)

@router.post("/start")
def start_tracking(
        db: Session = Depends(get_db)
):
    session = TrackingSession(
        owner_id = 1,
        share_token = str(uuid4())
    )

    db.add(session)
    db.commit()
    db.refresh(session)

    return {
        "session_id": session.id,
        "share_token": session.share_token
    }