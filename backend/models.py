from pydantic import BaseModel, EmailStr
from typing import Optional, Any, Dict

# ── AUTH ──────────────────────────────────────────
class UserRegister(BaseModel):
    email: EmailStr
    password: str
    name: Optional[str] = None

class UserLogin(BaseModel):
    email: EmailStr
    password: str

class TokenResponse(BaseModel):
    access_token: str
    token_type: str = "bearer"
    user_id: int
    name: Optional[str]

# ── PROJETS ───────────────────────────────────────
class ProjectCreate(BaseModel):
    project_name: str
    sector: Optional[str] = None

class F1Update(BaseModel):
    f1_diagnostic: Dict[str, Any]  # JSON complet du diagnostic F1

class F2Update(BaseModel):
    f2_scoring: Dict[str, Any]     # JSON scores AHP F2

class F3Update(BaseModel):
    f3_roadmap: Dict[str, Any]     # JSON roadmap F3

class ProjectResponse(BaseModel):
    id: int
    user_id: int
    project_name: str
    sector: Optional[str]
    f1_diagnostic: Optional[Dict[str, Any]]
    f2_scoring: Optional[Dict[str, Any]]
    f3_roadmap: Optional[Dict[str, Any]]
    status: str
    created_at: str
    updated_at: str
