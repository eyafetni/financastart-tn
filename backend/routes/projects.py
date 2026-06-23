import json
from fastapi import APIRouter, HTTPException, Depends
from database import get_db
from models import ProjectCreate, F1Update, F2Update, F3Update
from auth import get_current_user

router = APIRouter(prefix="/projects", tags=["Projects"])


def row_to_project(row) -> dict:
    """Convertit une ligne SQLite en dict avec JSONs parsés."""
    d = dict(row)
    for field in ["f1_diagnostic", "f2_scoring", "f3_roadmap"]:
        if d.get(field):
            d[field] = json.loads(d[field])
    return d


# ── CRÉER UN PROJET ───────────────────────────────
@router.post("/")
def create_project(data: ProjectCreate, user=Depends(get_current_user)):
    conn = get_db()
    cursor = conn.cursor()
    cursor.execute(
        "INSERT INTO projects (user_id, project_name, sector) VALUES (?, ?, ?)",
        (user["user_id"], data.project_name, data.sector)
    )
    conn.commit()
    project_id = cursor.lastrowid
    conn.close()
    return {"id": project_id, "message": "Projet créé avec succès"}


# ── LISTER MES PROJETS ────────────────────────────
@router.get("/")
def list_projects(user=Depends(get_current_user)):
    conn = get_db()
    rows = conn.execute(
        "SELECT * FROM projects WHERE user_id = ? ORDER BY updated_at DESC",
        (user["user_id"],)
    ).fetchall()
    conn.close()
    return [row_to_project(r) for r in rows]


# ── RÉCUPÉRER UN PROJET ───────────────────────────
@router.get("/{project_id}")
def get_project(project_id: int, user=Depends(get_current_user)):
    conn = get_db()
    row = conn.execute(
        "SELECT * FROM projects WHERE id = ? AND user_id = ?",
        (project_id, user["user_id"])
    ).fetchone()
    conn.close()
    if not row:
        raise HTTPException(status_code=404, detail="Projet non trouvé")
    return row_to_project(row)


# ── SAUVEGARDER F1 (Diagnostic) ───────────────────
@router.put("/{project_id}/f1")
def save_f1(project_id: int, data: F1Update, user=Depends(get_current_user)):
    conn = get_db()
    conn.execute(
        """UPDATE projects 
           SET f1_diagnostic = ?, updated_at = CURRENT_TIMESTAMP 
           WHERE id = ? AND user_id = ?""",
        (json.dumps(data.f1_diagnostic, ensure_ascii=False), project_id, user["user_id"])
    )
    conn.commit()
    conn.close()
    return {"message": "F1 sauvegardé ✅"}


# ── SAUVEGARDER F2 (Scoring AHP) ──────────────────
@router.put("/{project_id}/f2")
def save_f2(project_id: int, data: F2Update, user=Depends(get_current_user)):
    conn = get_db()
    conn.execute(
        """UPDATE projects 
           SET f2_scoring = ?, updated_at = CURRENT_TIMESTAMP 
           WHERE id = ? AND user_id = ?""",
        (json.dumps(data.f2_scoring, ensure_ascii=False), project_id, user["user_id"])
    )
    conn.commit()
    conn.close()
    return {"message": "F2 sauvegardé ✅"}


# ── SAUVEGARDER F3 (Roadmap RAG) ──────────────────
@router.put("/{project_id}/f3")
def save_f3(project_id: int, data: F3Update, user=Depends(get_current_user)):
    conn = get_db()
    conn.execute(
        """UPDATE projects 
           SET f3_roadmap = ?, updated_at = CURRENT_TIMESTAMP 
           WHERE id = ? AND user_id = ?""",
        (json.dumps(data.f3_roadmap, ensure_ascii=False), project_id, user["user_id"])
    )
    conn.commit()
    conn.close()
    return {"message": "F3 sauvegardé ✅"}


# ── DASHBOARD COMPLET (F1+F2+F3) ──────────────────
@router.get("/{project_id}/dashboard")
def get_dashboard(project_id: int, user=Depends(get_current_user)):
    conn = get_db()
    row = conn.execute(
        "SELECT * FROM projects WHERE id = ? AND user_id = ?",
        (project_id, user["user_id"])
    ).fetchone()
    conn.close()
    if not row:
        raise HTTPException(status_code=404, detail="Projet non trouvé")

    project = row_to_project(row)

    # Résumé dashboard pour le frontend
    return {
        "project_id": project_id,
        "project_name": project["project_name"],
        "sector": project["sector"],
        "status": project["status"],
        "maturity_stage": project["f1_diagnostic"].get("stage") if project["f1_diagnostic"] else None,
        "perception_gap": project["f1_diagnostic"].get("perception_gap") if project["f1_diagnostic"] else None,
        "scores": project["f2_scoring"].get("scores") if project["f2_scoring"] else None,
        "blockers": project["f1_diagnostic"].get("blockers") if project["f1_diagnostic"] else None,
        "roadmap_summary": project["f3_roadmap"].get("roadmap") if project["f3_roadmap"] else None,
        "full_data": project
    }
