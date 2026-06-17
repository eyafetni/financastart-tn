import json
from extract_sub_scores import extract_sub_scores
from extract_blockers import extract_blockers

def extract_all_scenario_data(payload):
    """Fonction principale orchestrant l'extraction globale."""
    # Base parsing
    data = json.loads(payload) if isinstance(payload, str) else payload
    profil = data.get("profil_complet", {})
    
    # 1. ADAPTATION : On passe directement 'data' (le dictionnaire complet)
    # car extract_sub_scores s'occupe déjà d'extraire .get("reponses_questionnaire", {})
    sub_scores = extract_sub_scores(data)
    
    # Pour les blockers, on continue de lui passer la liste dédiée
    blockers = extract_blockers(data.get("blockers", []))
    
    # 2. Extraction locale des anomalies (Règle CA vs RNE)
    anomalies = []
    if profil.get("chiffre_affaires", 0) > 1000000 and not profil.get("rne", True):
        anomalies.append({
            "id": "ANOM_GLOBAL_FRAUD",
            "description": "Incohérence majeure : Déclarations de revenus élevées contredites par l'absence de RNE.",
            "penalty_points": 35,
            "target_score": "global"
        })
        
    # Meta-formatting
    secteur_display = data.get("secteur", "Générique").capitalize()
    ville_display = data.get("localisation", "Tunis")
    id_brut = data.get("entrepreneur_id", "001")
    id_propre = f"PROF-{id_brut.split('-')[-1]}" if "-" in id_brut else f"PROF-{id_brut}"

    return {
        "id": id_propre,
        "nom_scenario": f"Cas Démo : {secteur_display} {ville_display} - Analyse Réelle complète",
        "secteur": data.get("secteur", "autre"),
        "sub_scores": sub_scores,
        "anomalies": anomalies,
        "blockers": blockers,
        "attendu": "FRI calculé selon les pondérations cibles du système expert."
    }