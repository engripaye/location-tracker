from datetime import datetime
from uuid import UUID

from pydantic import BaseModel, EmailStr, Field


class RegisterRequest(BaseModel):
    name: str = Field(min_length=1, max_length=120)
    email: EmailStr
    password: str = Field(min_length=8, max_length=128)


class LoginRequest(BaseModel):
    email: EmailStr
    password: str


class RefreshRequest(BaseModel):
    refresh_token: str


class TokenResponse(BaseModel):
    access_token: str
    refresh_token: str
    token_type: str = "bearer"


class UserResponse(BaseModel):
    id: UUID
    name: str
    email: EmailStr

    model_config = {"from_attributes": True}


class SessionCreate(BaseModel):
    expires_in_hours: int | None = Field(default=None, ge=1, le=720)


class SessionResponse(BaseModel):
    session_id: UUID
    share_token: str
    share_url: str
    expires_at: datetime


class SessionDetail(BaseModel):
    id: UUID
    active: bool
    expires_at: datetime
    created_at: datetime

    model_config = {"from_attributes": True}


class LocationRequest(BaseModel):
    latitude: float = Field(ge=-90, le=90)
    longitude: float = Field(ge=-180, le=180)
    accuracy: float | None = Field(default=None, ge=0)


class LocationResponse(BaseModel):
    id: UUID
    session_id: UUID
    latitude: float
    longitude: float
    accuracy: float | None
    address: str | None
    device_fingerprint: str | None
    created_at: datetime

    model_config = {"from_attributes": True}


class SosRequest(BaseModel):
    session_id: UUID | None = None
    latitude: float | None = Field(default=None, ge=-90, le=90)
    longitude: float | None = Field(default=None, ge=-180, le=180)
    message: str | None = Field(default=None, max_length=1000)


class SosResponse(BaseModel):
    id: UUID
    session_id: UUID | None
    latitude: float | None
    longitude: float | None
    message: str | None
    status: str
    created_at: datetime

    model_config = {"from_attributes": True}
