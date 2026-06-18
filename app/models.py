from datetime import datetime, timezone
from uuid import UUID
from uuid import uuid4

from sqlalchemy import Boolean, DateTime, Float, ForeignKey, Index, String, Text, Uuid
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.database import Base


def utc_now() -> datetime:
    return datetime.now(timezone.utc)


class User(Base):
    __tablename__ = "users"

    id: Mapped[UUID] = mapped_column(Uuid(as_uuid=True), primary_key=True, default=uuid4)
    name: Mapped[str] = mapped_column(String(120), nullable=False)
    email: Mapped[str] = mapped_column(String(255), nullable=False, unique=True, index=True)
    password_hash: Mapped[str] = mapped_column(String(255), nullable=False)
    is_active: Mapped[bool] = mapped_column(Boolean, nullable=False, default=True)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False, default=utc_now)

    sessions: Mapped[list["TrackingSession"]] = relationship(back_populates="owner", cascade="all, delete-orphan")
    refresh_tokens: Mapped[list["RefreshToken"]] = relationship(back_populates="user", cascade="all, delete-orphan")
    sos_events: Mapped[list["SosEvent"]] = relationship(back_populates="user")


class RefreshToken(Base):
    __tablename__ = "refresh_tokens"

    id: Mapped[UUID] = mapped_column(Uuid(as_uuid=True), primary_key=True, default=uuid4)
    user_id: Mapped[UUID] = mapped_column(Uuid(as_uuid=True), ForeignKey("users.id", ondelete="CASCADE"), nullable=False)
    token_hash: Mapped[str] = mapped_column(String(128), nullable=False, unique=True, index=True)
    device_fingerprint: Mapped[str | None] = mapped_column(String(128))
    user_agent: Mapped[str | None] = mapped_column(Text)
    expires_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False)
    revoked_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True))
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False, default=utc_now)

    user: Mapped[User] = relationship(back_populates="refresh_tokens")


class TrackingSession(Base):
    __tablename__ = "tracking_sessions"

    id: Mapped[UUID] = mapped_column(Uuid(as_uuid=True), primary_key=True, default=uuid4)
    owner_id: Mapped[UUID] = mapped_column(Uuid(as_uuid=True), ForeignKey("users.id", ondelete="CASCADE"), nullable=False)
    share_token_hash: Mapped[str] = mapped_column(String(128), nullable=False, unique=True)
    active: Mapped[bool] = mapped_column(Boolean, nullable=False, default=True)
    expires_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False, default=utc_now)

    owner: Mapped[User] = relationship(back_populates="sessions")
    locations: Mapped[list["LocationPoint"]] = relationship(back_populates="session", cascade="all, delete-orphan")
    sos_events: Mapped[list["SosEvent"]] = relationship(back_populates="session")

    __table_args__ = (
        Index("idx_tracking_sessions_owner_created", "owner_id", "created_at"),
        Index("idx_tracking_sessions_share_token_hash", "share_token_hash"),
    )


class LocationPoint(Base):
    __tablename__ = "location_points"

    id: Mapped[UUID] = mapped_column(Uuid(as_uuid=True), primary_key=True, default=uuid4)
    session_id: Mapped[UUID] = mapped_column(Uuid(as_uuid=True), ForeignKey("tracking_sessions.id", ondelete="CASCADE"), nullable=False)
    latitude: Mapped[float] = mapped_column(Float, nullable=False)
    longitude: Mapped[float] = mapped_column(Float, nullable=False)
    accuracy: Mapped[float | None] = mapped_column(Float)
    address: Mapped[str | None] = mapped_column(Text)
    device_fingerprint: Mapped[str | None] = mapped_column(String(128))
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False, default=utc_now)

    session: Mapped[TrackingSession] = relationship(back_populates="locations")

    __table_args__ = (Index("idx_location_points_session_created", "session_id", "created_at"),)


class SosEvent(Base):
    __tablename__ = "sos_events"

    id: Mapped[UUID] = mapped_column(Uuid(as_uuid=True), primary_key=True, default=uuid4)
    user_id: Mapped[UUID] = mapped_column(Uuid(as_uuid=True), ForeignKey("users.id", ondelete="CASCADE"), nullable=False)
    session_id: Mapped[UUID | None] = mapped_column(Uuid(as_uuid=True), ForeignKey("tracking_sessions.id", ondelete="SET NULL"))
    latitude: Mapped[float | None] = mapped_column(Float)
    longitude: Mapped[float | None] = mapped_column(Float)
    message: Mapped[str | None] = mapped_column(Text)
    status: Mapped[str] = mapped_column(String(32), nullable=False, default="open")
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False, default=utc_now)

    user: Mapped[User] = relationship(back_populates="sos_events")
    session: Mapped[TrackingSession | None] = relationship(back_populates="sos_events")

    __table_args__ = (Index("idx_sos_events_user_created", "user_id", "created_at"),)
