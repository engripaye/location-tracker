from datetime import datetime, timedelta, timezone

from fastapi import APIRouter, Depends, HTTPException, Request, status
from sqlalchemy import select
from sqlalchemy.orm import Session

from app.config import get_settings
from app.database import get_db
from app.dependencies import get_current_user
from app.models import RefreshToken, User
from app.schemas import LoginRequest, RefreshRequest, RegisterRequest, TokenResponse, UserResponse
from app.security import (
    create_access_token,
    fingerprint_hash,
    hash_password,
    new_refresh_token,
    token_hash,
    verify_password,
)


router = APIRouter(prefix="/auth", tags=["auth"])


@router.post("/register", response_model=TokenResponse, status_code=201)
def register(request_body: RegisterRequest, request: Request, db: Session = Depends(get_db)) -> TokenResponse:
    existing = db.scalar(select(User).where(User.email == request_body.email.lower()))
    if existing:
        raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail="Email already registered")

    user = User(
        name=request_body.name,
        email=request_body.email.lower(),
        password_hash=hash_password(request_body.password),
    )
    db.add(user)
    db.flush()
    refresh_token = _create_refresh_token(user, request, db)
    db.commit()
    return TokenResponse(access_token=create_access_token(user.id), refresh_token=refresh_token)


@router.post("/login", response_model=TokenResponse)
def login(request_body: LoginRequest, request: Request, db: Session = Depends(get_db)) -> TokenResponse:
    user = db.scalar(select(User).where(User.email == request_body.email.lower()))
    if user is None or not verify_password(request_body.password, user.password_hash):
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid email or password")

    refresh_token = _create_refresh_token(user, request, db)
    db.commit()
    return TokenResponse(access_token=create_access_token(user.id), refresh_token=refresh_token)


@router.post("/refresh", response_model=TokenResponse)
def refresh(request_body: RefreshRequest, request: Request, db: Session = Depends(get_db)) -> TokenResponse:
    now = datetime.now(timezone.utc)
    stored = db.scalar(select(RefreshToken).where(RefreshToken.token_hash == token_hash(request_body.refresh_token)))
    if stored is None or stored.revoked_at is not None or stored.expires_at <= now:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid refresh token")

    stored.revoked_at = now
    refresh_token = _create_refresh_token(stored.user, request, db)
    db.commit()
    return TokenResponse(access_token=create_access_token(stored.user_id), refresh_token=refresh_token)


@router.post("/logout", status_code=204)
def logout(request_body: RefreshRequest, db: Session = Depends(get_db)) -> None:
    stored = db.scalar(select(RefreshToken).where(RefreshToken.token_hash == token_hash(request_body.refresh_token)))
    if stored and stored.revoked_at is None:
        stored.revoked_at = datetime.now(timezone.utc)
        db.commit()


@router.get("/me", response_model=UserResponse)
def me(current_user: User = Depends(get_current_user)) -> User:
    return current_user


def _create_refresh_token(user: User, request: Request, db: Session) -> str:
    refresh_token = new_refresh_token()
    db.add(
        RefreshToken(
            user_id=user.id,
            token_hash=token_hash(refresh_token),
            device_fingerprint=fingerprint_hash(request.headers.get("X-Device-Fingerprint")),
            user_agent=request.headers.get("User-Agent"),
            expires_at=datetime.now(timezone.utc) + timedelta(days=get_settings().refresh_token_days),
        )
    )
    return refresh_token
