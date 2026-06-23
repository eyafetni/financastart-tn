import hashlib
import secrets
import jwt
from datetime import datetime, timedelta
from database import get_db

SECRET_KEY = "financastart-tn-secret-2026"  # change en prod
ALGORITHM = "HS256"
TOKEN_EXPIRE_HOURS = 24

# ── MOT DE PASSE ──────────────────────────────────
def hash_password(password: str) -> str:
    return hashlib.sha256(password.encode()).hexdigest()

def verify_password(password: str, hashed: str) -> bool:
    return hash_password(password) == hashed

# ── JWT ───────────────────────────────────────────
def create_token(user_id: int, email: str) -> str:
    payload = {
        "user_id": user_id,
        "email": email,
        "exp": datetime.utcnow() + timedelta(hours=TOKEN_EXPIRE_HOURS)
    }
    return jwt.encode(payload, SECRET_KEY, algorithm=ALGORITHM)

def decode_token(token: str) -> dict:
    try:
        return jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
    except jwt.ExpiredSignatureError:
        raise ValueError("Token expiré")
    except jwt.InvalidTokenError:
        raise ValueError("Token invalide")

# ── MIDDLEWARE : récupérer user courant ───────────
from fastapi import Header, HTTPException

def get_current_user(authorization: str = Header(...)):
    if not authorization.startswith("Bearer "):
        raise HTTPException(status_code=401, detail="Format token invalide")
    token = authorization.split(" ")[1]
    try:
        payload = decode_token(token)
        return payload  # {"user_id": ..., "email": ...}
    except ValueError as e:
        raise HTTPException(status_code=401, detail=str(e))
