from fastapi import APIRouter
from sqlalchemy.orm import Session

from app.models import User
from app.schemas import (
    LocationRequest,
    LoginRequest
)

from app.security import (
    hash_password,
    verify_password,
    create_access_token
)

from app.dependency import get_db
from fastapi import Depends

router = APIRouter(
    prefix="/auth",
    tags=["auth"]
)