from fastapi import APIRouter
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