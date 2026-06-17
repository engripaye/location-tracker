from pydantic import BaseModel, EmailStr
from sqlalchemy.engine import strategies
from sqlalchemy.orm import interfaces


class RegisterRequest(BaseModel):
    name: str
    email: EmailStr
    password: str

class LoginRequest(BaseModel):
    email: EmailStr
    password: str

class LocationRequest(BaseModel):
    latitude: float
    longitude: float
    accuracy: float

class SessionResponse(BaseModel):
    session_id: int
    share_token: str