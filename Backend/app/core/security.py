from datetime import datetime, timedelta, timezone
import bcrypt
from jose import jwt, JWTError

from app.config import settings


def hash_password(password: str) -> str:
    pw = password.encode("utf-8")[:72]  # bcrypt only uses the first 72 bytes
    return bcrypt.hashpw(pw, bcrypt.gensalt()).decode("utf-8")


def verify_password(plain_password: str, hashed_password: str) -> bool:
    pw = plain_password.encode("utf-8")[:72]
    try:
        return bcrypt.checkpw(pw, hashed_password.encode("utf-8"))
    except ValueError:
        return False  # malformed hash in the database


def create_access_token(data: dict) -> str:
    to_encode = data.copy()
    expire = datetime.now(timezone.utc) + timedelta(
        minutes=settings.jwt_access_token_expire_minutes
    )
    to_encode.update({"exp": expire})
    return jwt.encode(to_encode, settings.jwt_secret_key, algorithm=settings.jwt_algorithm)


def decode_access_token(token: str) -> dict | None:
    try:
        return jwt.decode(token, settings.jwt_secret_key, algorithms=[settings.jwt_algorithm])
    except JWTError:
        return None