from fastapi import APIRouter
from pyasn1 import error
from sqlalchemy import FromClause
from sqlalchemy.orm import Session
from fastapi import Depends


from app.models import (
TrackingSession,
LocationPoint
)

from app.schemas import (
LocationRequest
)

from app.dependencies import get_db
router = APIRouter(
    prefix="/track",
    tags=["Tracking"]
)

@router.post("/{session_id}/location")
def save_location(session_id: int, request: LocationRequest, db: Session = Depends(get_db)):
    location = LocationPoint(
        session_id=session_id,
        latitude=request.latitude,
        longitude=request.longitude,
        accuracy=request.accuracy,
    )

    db.add(location)
    db.commit()

    return {"message": "saved"}

@router.get("/{share_token}")
def latest_location(
        share_token: str,
        db: Session = Depends(get_db),
):
    session: db_query(
        TrackingSession,
    ).filter(
        TrackingSession.share_token
        == share_token
    ).first()

    if not session:
        return {"error": "Not found"}

    location = db.query(LocationPoint).filter(
        LocationPoint.session_id == session.id
    ).order_by(
        LocationPoint.created_at.desc()
    ).first()

    if not location:
        return {"error": "No Location"}

    return {
        "latitude":
            location.latitude,
        "longitude":
            location.longitude,
        "accuracy":
            location.accuracy,
        "timestamp":
            location.created_at
    }