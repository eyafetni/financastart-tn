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
from ai.f1_diagnostic.part2 import run_diagnostic_from_json
from ai.f3_rag.rag_engine import run_rag
import tempfile

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

# ── ANALYSER LE PROJET (F1 + F2) ──────────────────
def map_raw_answers_to_f1_input(raw_payload: dict) -> dict:
    """Helper pour mapper les réponses brutes du questionnaire vers l'entrée F1."""
    # Le frontend envoie déjà un payload structuré, mais on peut ajuster ici si besoin
    return raw_payload

# ── GÉNÉRER F1 (Diagnostic) ──────────────────
@router.post("/{project_id}/generate-f1")
def generate_f1(project_id: int, payload: dict, user=Depends(get_current_user)):
    conn = get_db()
    row = conn.execute("SELECT id FROM projects WHERE id = ? AND user_id = ?", (project_id, user["user_id"])).fetchone()
    if not row:
        conn.close()
        raise HTTPException(status_code=404, detail="Projet non trouvé")

    f1_input = map_raw_answers_to_f1_input(payload)
    
    with tempfile.NamedTemporaryFile(mode='w', suffix='.json', delete=False, encoding='utf-8') as tmp_file:
        json.dump(f1_input, tmp_file, ensure_ascii=False)
        tmp_filepath = tmp_file.name

    try:
        f1_result = run_diagnostic_from_json(tmp_filepath)
        if not f1_result:
            raise HTTPException(status_code=500, detail="Erreur F1")
            
        conn.execute(
            "UPDATE projects SET f1_diagnostic = ?, updated_at = CURRENT_TIMESTAMP WHERE id = ? AND user_id = ?",
            (json.dumps(f1_result, ensure_ascii=False), project_id, user["user_id"])
        )
        conn.commit()
    finally:
        conn.close()
        if os.path.exists(tmp_filepath):
            os.remove(tmp_filepath)
            
    return {"message": "F1 généré ✅", "f1_diagnostic": f1_result}

# ── GÉNÉRER F3 (Roadmap RAG) ──────────────────
@router.post("/{project_id}/generate-f3")
def generate_f3(project_id: int, user=Depends(get_current_user)):
    conn = get_db()
    row = conn.execute("SELECT f1_diagnostic, f2_scoring FROM projects WHERE id = ? AND user_id = ?", (project_id, user["user_id"])).fetchone()
    if not row or not row["f1_diagnostic"] or not row["f2_scoring"]:
        conn.close()
        raise HTTPException(status_code=400, detail="Projet non trouvé ou F1/F2 manquants")
        
    f1_data = json.loads(row["f1_diagnostic"])
    f2_data = json.loads(row["f2_scoring"])
    
    # Fusionner f1 et f2 pour RAG
    combined_data = {**f1_data, **f2_data}
    
    try:
        f3_result = run_rag(combined_data)
        conn.execute(
            "UPDATE projects SET f3_roadmap = ?, updated_at = CURRENT_TIMESTAMP WHERE id = ? AND user_id = ?",
            (json.dumps(f3_result, ensure_ascii=False), project_id, user["user_id"])
        )
        conn.commit()
    finally:
        conn.close()
        
    return {"message": "F3 généré ✅", "f3_roadmap": f3_result}

# ── ANALYSER LE PROJET (F1 + F2 + F3) ──────────────────
@router.post("/{project_id}/analyse")
def analyse_project(project_id: int, payload: dict, user=Depends(get_current_user)):
    conn = get_db()
    row = conn.execute("SELECT id FROM projects WHERE id = ? AND user_id = ?", (project_id, user["user_id"])).fetchone()
    if not row:
        conn.close()
        raise HTTPException(status_code=404, detail="Projet non trouvé")

    f1_input = map_raw_answers_to_f1_input(payload)

    with tempfile.NamedTemporaryFile(mode='w', suffix='.json', delete=False, encoding='utf-8') as tmp_file:
        json.dump(f1_input, tmp_file, ensure_ascii=False)
        tmp_filepath = tmp_file.name

    try:
        # F1
        f1_result = run_diagnostic_from_json(tmp_filepath)
        if not f1_result:
            raise HTTPException(status_code=500, detail="Erreur F1")

        # F2
        f2_result = process_entrepreneur_profile(f1_result)

        # F3
        combined_data = {**f1_result, **f2_result}
        f3_result = run_rag(combined_data)

        conn.execute(
            """UPDATE projects 
               SET f1_diagnostic = ?, f2_scoring = ?, f3_roadmap = ?, 
                   project_name = ?, sector = ?, updated_at = CURRENT_TIMESTAMP 
               WHERE id = ? AND user_id = ?""",
            (
                json.dumps(f1_result, ensure_ascii=False),
                json.dumps(f2_result, ensure_ascii=False),
                json.dumps(f3_result, ensure_ascii=False),
                payload.get("nom_entreprise", "Projet sans nom"),
                payload.get("secteur", ""),
                project_id,
                user["user_id"]
            )
        )
        conn.commit()
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Erreur d'analyse: {str(e)}")
    finally:
        conn.close()
        if os.path.exists(tmp_filepath):
            os.remove(tmp_filepath)

    return {
        "status": "success",
        "message": "Diagnostic complet (F1 + F2 + F3) terminé ✅",
        "f1_diagnostic": f1_result,
        "f2_scoring": f2_result,
        "f3_roadmap": f3_result
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

    # Map f2_scoring into the nested shape expected by dataAdapter.js
    scores_obj = None
    if project.get("f2_scoring") and "scores" in project["f2_scoring"]:
        f2_scores = project["f2_scoring"]["scores"]
        scores_obj = {
            "scores_f2": {
                "market": f2_scores.get("market_score", {}).get("valeur", 0),
                "commercial_offer": f2_scores.get("commercial_offer_score", {}).get("valeur", 0),
                "innovation": f2_scores.get("innovation_score", {}).get("valeur", 0),
                "scalability": f2_scores.get("scalability_score", {}).get("valeur", 0),
                "green": f2_scores.get("green_score", {}).get("valeur", 0),
            },
            "detail": f2_scores
        }

    return {
        "project_id": project_id,
        "startup_name": project["project_name"],
        "sector": project["sector"],
        "location": project["f1_diagnostic"].get("localisation", "Tunisie") if project["f1_diagnostic"] else "Tunisie",
        "real_stage": project["f1_diagnostic"].get("stade_reel") if project["f1_diagnostic"] else None,
        "perceived_stage": project["f1_diagnostic"].get("stade_percu") if project["f1_diagnostic"] else None,
        "gap_detected": project["f1_diagnostic"].get("gap_detecte") if project["f1_diagnostic"] else False,
        "gap_explanation": project["f1_diagnostic"].get("gap_explication") if project["f1_diagnostic"] else "",
        "divergence_signals": project["f1_diagnostic"].get("signaux_divergence", []) if project["f1_diagnostic"] else [],
        "blockers": project["f1_diagnostic"].get("blockers", []) if project["f1_diagnostic"] else [],
        "scores_data": scores_obj,
        "detected_anomalies": project["f2_scoring"].get("anomalies_detectees", []) if project["f2_scoring"] else [],
        "recommended_resources": project["f3_roadmap"].get("ressources_recommandees", []) if project["f3_roadmap"] else [],
        "roadmap_data": project["f3_roadmap"].get("roadmap", {}) if project["f3_roadmap"] else {},
        "financing_readiness_index": project["f2_scoring"].get("financing_readiness_index") if project["f2_scoring"] else 0,
        "is_financeable": project["f2_scoring"].get("is_financeable") if project["f2_scoring"] else False,
        "fri_interpretation": project["f2_scoring"].get("fri_interpretation") if project["f2_scoring"] else ""
    }
