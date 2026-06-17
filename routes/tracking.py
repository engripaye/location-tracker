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