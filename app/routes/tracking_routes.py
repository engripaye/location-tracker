from datetime import datetime, timezone
from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException, Request, WebSocket, WebSocketDisconnect, status
from sqlalchemy import select
from sqlalchemy.orm import Session

from app.database import get_db
from app.dependencies import get_current_user
from app.models import LocationPoint, SosEvent, TrackingSession, User
from app.schemas import LocationRequest, LocationResponse, SosRequest, SosResponse
from app.security import fingerprint_hash, token_hash
from app.services.geocoding import reverse_geocode
from app.services.realtime import manager


router = APIRouter(tags=["tracking"])


@router.post("/track/{share_token}/location", response_model=LocationResponse, status_code=201)
async def save_location(
    share_token: str,
    request_body: LocationRequest,
    request: Request,
    db: Session = Depends(get_db),
) -> LocationPoint:
    session = _session_from_share_token(share_token, db)
    _ensure_session_available(session)
    location = LocationPoint(
        session_id=session.id,
        latitude=request_body.latitude,
        longitude=request_body.longitude,
        accuracy=request_body.accuracy,
        address=await reverse_geocode(request_body.latitude, request_body.longitude),
        device_fingerprint=fingerprint_hash(request.headers.get("X-Device-Fingerprint")),
    )
    db.add(location)
    db.commit()
    db.refresh(location)
    await manager.broadcast(session.id, LocationResponse.model_validate(location).model_dump(mode="json"))
    return location


@router.get("/track/{share_token}", response_model=LocationResponse)
def latest_location(share_token: str, db: Session = Depends(get_db)) -> LocationPoint:
    session = _session_from_share_token(share_token, db)
    _ensure_session_available(session)
    location = db.scalar(
        select(LocationPoint)
        .where(LocationPoint.session_id == session.id)
        .order_by(LocationPoint.created_at.desc())
    )
    if location is None:
        raise HTTPException(status_code=404, detail="No location yet")
    return location


@router.get("/sessions/{session_id}/locations", response_model=list[LocationResponse])
def session_locations(
    session_id: UUID,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
) -> list[LocationPoint]:
    session = db.scalar(select(TrackingSession).where(TrackingSession.id == session_id, TrackingSession.owner_id == current_user.id))
    if session is None:
        raise HTTPException(status_code=404, detail="Session not found")
    return list(
        db.scalars(
            select(LocationPoint)
            .where(LocationPoint.session_id == session.id)
            .order_by(LocationPoint.created_at.desc())
        ).all()
    )


@router.websocket("/ws/track/{share_token}")
async def live_tracking(websocket: WebSocket, share_token: str) -> None:
    db = next(get_db())
    try:
        session = _session_from_share_token(share_token, db)
        if not _session_is_available(session):
            await websocket.close(code=status.WS_1008_POLICY_VIOLATION)
            return
        await manager.connect(session.id, websocket)
        try:
            while True:
                await websocket.receive_text()
        except WebSocketDisconnect:
            manager.disconnect(session.id, websocket)
    finally:
        db.close()


@router.post("/sos", response_model=SosResponse, status_code=201)
def create_sos(
    request_body: SosRequest,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
) -> SosEvent:
    if request_body.session_id:
        session = db.scalar(
            select(TrackingSession).where(
                TrackingSession.id == request_body.session_id,
                TrackingSession.owner_id == current_user.id,
            )
        )
        if session is None:
            raise HTTPException(status_code=404, detail="Session not found")

    event = SosEvent(
        user_id=current_user.id,
        session_id=request_body.session_id,
        latitude=request_body.latitude,
        longitude=request_body.longitude,
        message=request_body.message,
    )
    db.add(event)
    db.commit()
    db.refresh(event)
    return event


@router.get("/sos", response_model=list[SosResponse])
def list_sos(current_user: User = Depends(get_current_user), db: Session = Depends(get_db)) -> list[SosEvent]:
    return list(
        db.scalars(
            select(SosEvent)
            .where(SosEvent.user_id == current_user.id)
            .order_by(SosEvent.created_at.desc())
        ).all()
    )


def _session_from_share_token(share_token: str, db: Session) -> TrackingSession:
    session = db.scalar(select(TrackingSession).where(TrackingSession.share_token_hash == token_hash(share_token)))
    if session is None:
        raise HTTPException(status_code=404, detail="Share link not found")
    return session


def _ensure_session_available(session: TrackingSession) -> None:
    if not _session_is_available(session):
        raise HTTPException(status_code=410, detail="Share link has expired or is inactive")


def _session_is_available(session: TrackingSession) -> bool:
    return session.active and session.expires_at > datetime.now(timezone.utc)
