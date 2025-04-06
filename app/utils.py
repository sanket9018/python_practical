from fastapi import FastAPI, Depends, HTTPException, status, Request
from passlib.context import CryptContext

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

from datetime import datetime, timedelta, timezone
import jwt
import os

from dotenv import load_dotenv
load_dotenv()

BASE_URL = os.getenv("BASE_URL", "http://localhost:8000")


SECRET_KEY = os.getenv("SECRET_KEY")
ALGORITHM = os.getenv("ALGORITHM")

ACCESS_TOKEN_EXPIRE_MINUTES = 60  # 1 Minute

def create_access_token(data: dict, expires_delta: timedelta = None):
    to_encode = data.copy()
    expire = datetime.utcnow() + (expires_delta or timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES))
    to_encode.update({"exp": expire})
    encoded_jwt = jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)
    ttl_seconds = int((expire - datetime.utcnow()).total_seconds())
    return encoded_jwt, ttl_seconds


def decode_access_token(token: str):
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        return payload
    except Exception as e:
        print(f"Token decoding error: {e}")
        return None


def hash_password(password: str) -> str:
    """Hash plain password using bcrypt."""
    return pwd_context.hash(password)


def verify_password(plain_password: str, hashed_password: str) -> bool:
    """Verify the plain password with hashed password."""
    return pwd_context.verify(plain_password, hashed_password)


async def get_user_by_token(token: str, conn, cur):
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        user_id = payload.get("user_id")
        if user_id is None:
            return None
        await cur.execute("SELECT * FROM user WHERE id=%s AND deletedAt IS NULL", (user_id,))
        return await cur.fetchone()
    except Exception:
        return None
    

def format_user(user: dict):
    if user.get("profilepic"):
        filename = os.path.basename(user["profilepic"])
        user["profilepic"] = f"{BASE_URL}/uploads/{filename}"
    return user
