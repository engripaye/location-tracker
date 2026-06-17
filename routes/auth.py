from fastapi import APIRouter
from sqlalchemy.orm import Session

from app.models import User
from app.schemas import (
    LocationRequest,
    LoginRequest, RegisterRequest
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

@router.post("/register")
def register(
        request: RegisterRequest,
        db: Session = Depends(get_db),=
):
    user = User(
        name=request.name,
        email=request.email,
        password_hash=hash_password(
            request.password
        )
    )

    db.add(user)
    db.commit()

    return {"message": "Registered"}
