from datetime import datetime, timedelta, timezone
from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException, Request
from sqlalchemy import select
from sqlalchemy.orm import Session, selectinload

from app.config import get_settings
from app.database import get_db
from app.dependencies import get_current_user
from app.models import TrackingSession, User
from app.schemas import SessionCreate, SessionDetail, SessionResponse
from app.security import new_share_token, token_hash


router = APIRouter(prefix="/sessions", tags=["sessions"])


@router.post("/start", response_model=SessionResponse, status_code=201)
def start_tracking(
    payload: SessionCreate,
    request: Request,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
) -> SessionResponse:
    settings = get_settings()
    raw_share_token = new_share_token()
    expires_in_hours = payload.expires_in_hours or settings.share_link_hours
    session = TrackingSession(
        owner_id=current_user.id,
        share_token_hash=token_hash(raw_share_token),
        expires_at=datetime.now(timezone.utc) + timedelta(hours=expires_in_hours),
    )
    db.add(session)
    db.commit()
    db.refresh(session)
    base_url = str(request.base_url).rstrip("/")
    return SessionResponse(
        session_id=session.id,
        share_token=raw_share_token,
        share_url=f"{base_url}/track/{raw_share_token}",
        expires_at=session.expires_at,
    )


@router.get("", response_model=list[SessionDetail])
def list_sessions(current_user: User = Depends(get_current_user), db: Session = Depends(get_db)) -> list[TrackingSession]:
    return list(
        db.scalars(
            select(TrackingSession)
            .where(TrackingSession.owner_id == current_user.id)
            .order_by(TrackingSession.created_at.desc())
        ).all()
    )


@router.get("/{session_id}", response_model=SessionDetail)
def get_session(
    session_id: UUID,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
) -> TrackingSession:
    session = db.scalar(
        select(TrackingSession)
        .where(TrackingSession.id == session_id, TrackingSession.owner_id == current_user.id)
        .options(selectinload(TrackingSession.locations))
    )
    if session is None:
        raise HTTPException(status_code=404, detail="Session not found")
    return session


@router.post("/{session_id}/stop", response_model=SessionDetail)
def stop_session(
    session_id: UUID,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
) -> TrackingSession:
    session = db.scalar(select(TrackingSession).where(TrackingSession.id == session_id, TrackingSession.owner_id == current_user.id))
    if session is None:
        raise HTTPException(status_code=404, detail="Session not found")
    session.active = False
    db.commit()
    db.refresh(session)
    return session
