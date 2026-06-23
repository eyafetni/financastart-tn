import json
import sys
import os
from fastapi import APIRouter, HTTPException, Depends
from database import get_db
from models import ProjectCreate, F1Update, F2Update, F3Update
from auth import get_current_user

# Ajout du dossier racine et f2_scoring au sys.path pour les imports de l'IA
parent_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", ".."))
if parent_dir not in sys.path:
    sys.path.insert(0, parent_dir)
f2_scoring_path = os.path.join(parent_dir, "ai", "f2_scoring")
if f2_scoring_path not in sys.path:
    sys.path.insert(0, f2_scoring_path)

from ai.f2_scoring.fonction_principale import process_entrepreneur_profile
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


# ── GÉNÉRER F2 DEPUIS F1 (Pipeline) ──────────────────
@router.post("/{project_id}/generate-f2")
def generate_f2(project_id: int, user=Depends(get_current_user)):
    """
    Récupère le diagnostic F1 existant en base de données, lance l'algorithme
    de scoring AHP (F2), et enregistre le résultat dans le projet.
    """
    conn = get_db()
    row = conn.execute(
        "SELECT f1_diagnostic FROM projects WHERE id = ? AND user_id = ?",
        (project_id, user["user_id"])
    ).fetchone()
    
    if not row:
        conn.close()
        raise HTTPException(status_code=404, detail="Projet non trouvé")
        
    f1_data_str = row["f1_diagnostic"]
    if not f1_data_str:
        conn.close()
        raise HTTPException(
            status_code=400, 
            detail="Le diagnostic F1 n'a pas encore été complété pour ce projet."
        )
        
    try:
        f1_data = json.loads(f1_data_str)
    except Exception as e:
        conn.close()
        raise HTTPException(status_code=500, detail=f"Données F1 invalides : {str(e)}")

    # Appel du pipeline de scoring F2
    try:
        f2_result = process_entrepreneur_profile(f1_data)
    except Exception as e:
        conn.close()
        raise HTTPException(
            status_code=500, 
            detail=f"Erreur lors de l'exécution du moteur F2 : {str(e)}"
        )

    # Sauvegarde des résultats F2
    conn.execute(
        """UPDATE projects 
           SET f2_scoring = ?, updated_at = CURRENT_TIMESTAMP 
           WHERE id = ? AND user_id = ?""",
        (json.dumps(f2_result, ensure_ascii=False), project_id, user["user_id"])
    )
    conn.commit()
    conn.close()

    return {
        "message": "Scoring F2 généré et sauvegardé avec succès ✅",
        "f2_scoring": f2_result
    }


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
