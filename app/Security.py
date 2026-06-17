from jose import jwt
from passlib.context import CryptContext
from datetime import datetime, timedelta
import os

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

SECRET_KEY = os.getenv("SECRET_KEY")
ALGORITHMS = os.getenv("ALGORITHMS")

def hash_password(password):
    return pwd_context.hash(password)

def verify_password(
        plain_password,
        hashed_password): return pwd_context.verify(plain_password, hashed_password)

def create_access_token(
        data: dict
):
    payload = data.copy()

    payload["exp"] = datetime.utcnow() + timedelta(hours=1)