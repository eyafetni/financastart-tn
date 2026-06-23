from fastapi import APIRouter, HTTPException
from database import get_db
from models import UserRegister, UserLogin, TokenResponse
from auth import hash_password, verify_password, create_token

router = APIRouter(prefix="/auth", tags=["Authentication"])

@router.post("/register", response_model=TokenResponse)
def register(user: UserRegister):
    conn = get_db()
    cursor = conn.cursor()

    # Vérifier si email existe déjà
    existing = cursor.execute("SELECT id FROM users WHERE email = ?", (user.email,)).fetchone()
    if existing:
        conn.close()
        raise HTTPException(status_code=400, detail="Email déjà utilisé")

    # Créer l'utilisateur
    hashed = hash_password(user.password)
    cursor.execute(
        "INSERT INTO users (email, password_hash, name) VALUES (?, ?, ?)",
        (user.email, hashed, user.name)
    )
    conn.commit()
    user_id = cursor.lastrowid
    conn.close()

    token = create_token(user_id, user.email)
    return TokenResponse(access_token=token, user_id=user_id, name=user.name)


@router.post("/login", response_model=TokenResponse)
def login(credentials: UserLogin):
    conn = get_db()
    cursor = conn.cursor()

    row = cursor.execute("SELECT * FROM users WHERE email = ?", (credentials.email,)).fetchone()
    conn.close()

    if not row or not verify_password(credentials.password, row["password_hash"]):
        raise HTTPException(status_code=401, detail="Email ou mot de passe incorrect")

    token = create_token(row["id"], row["email"])
    return TokenResponse(access_token=token, user_id=row["id"], name=row["name"])
