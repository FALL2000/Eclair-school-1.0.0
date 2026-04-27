from fastapi import HTTPException
import jwt
from datetime import datetime, timedelta, timezone
from typing import Optional

from config.settings import get_settings

settings = get_settings()

SECRET_KEY = settings.secret_key
ALGORITHM = settings.algorithm
ACCESS_TOKEN_EXPIRE_MINUTES = settings.access_token_expire_minutes
ACCESS_REFRESH_TOKEN_EXPIRE_DAYS = settings.access_refresh_token_expire_days


def create_tokens(user_id: int) -> dict:
    """Génère un Access Token et un Refresh Token."""
    now = datetime.now(timezone.utc)

    # Access Token (30 minutes)
    access_payload = {
        "sub": str(user_id),
        "exp": now + timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES),
        "iat": now,
        "type": "access"
    }
    access_token = jwt.encode(access_payload, SECRET_KEY, algorithm=ALGORITHM)

    # Refresh Token (1 jour)
    refresh_payload = {
        "sub": str(user_id),
        "exp": now + timedelta(days=ACCESS_REFRESH_TOKEN_EXPIRE_DAYS),
        "iat": now,
        "type": "refresh"
    }
    refresh_token = jwt.encode(
        refresh_payload, SECRET_KEY, algorithm=ALGORITHM)

    return {
        "access_token": access_token,
        "refresh_token": refresh_token,
        "token_type": "bearer"
    }


def decode_token(token: str) -> Optional[dict]:
    """Décode et valide un token JWT."""
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        return payload
    except jwt.ExpiredSignatureError:
        # Le token a expiré
        raise HTTPException(status_code=401, detail={
                            "error_code": "TOKEN_EXPIRED", "message": "Token expired"})
    except jwt.InvalidTokenError:
        # Le token est mal formé ou la clé est mauvaise
        raise HTTPException(status_code=401, detail={
                            "error_code": "INVALID_TOKEN", "message": "Invalid token"})
