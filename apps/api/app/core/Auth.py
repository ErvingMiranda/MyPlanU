from datetime import datetime, timedelta
from typing import Optional
import os

from passlib.context import CryptContext
from jose import jwt, JWTError

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

ALGORITHM = "HS256"

def get_secret_key() -> str:
    key = os.getenv("SECRET_KEY")
    if not key:
        # Dev fallback (no usar en prod)
        key = "dev-secret-key-change-me"
    return key

def get_access_token_exp_minutes() -> int:
    try:
        return int(os.getenv("ACCESS_TOKEN_EXPIRE_MINUTES", "60"))
    except Exception:
        return 60

def hash_password(password: str) -> str:
    return pwd_context.hash(password)

def verify_password(password: str, hashed: str) -> bool:
    if not hashed:
        return False
    return pwd_context.verify(password, hashed)

def create_access_token(subject: str, extra: Optional[dict] = None) -> str:
    to_encode = {"sub": subject, "iat": datetime.utcnow()}
    if extra:
        to_encode.update(extra)
    expire = datetime.utcnow() + timedelta(minutes=get_access_token_exp_minutes())
    to_encode.update({"exp": expire})
    encoded_jwt = jwt.encode(to_encode, get_secret_key(), algorithm=ALGORITHM)
    return encoded_jwt

def decode_access_token(token: str) -> Optional[dict]:
    try:
        payload = jwt.decode(token, get_secret_key(), algorithms=[ALGORITHM])
        return payload
    except JWTError:
        return None
