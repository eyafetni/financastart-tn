# f2_scoring/pipeline.py
"""
Orchestrateur Principal — API Backend.
Prend le profil brut de l'entrepreneur (JSON/Dict) et retourne le contrat F2 finalisé.
"""
import json
from typing import Any

# Imports de tes modules d'extraction (Phase 1)
from extraction_donnees.extract_sub_scores import extract_sub_scores
from extraction_donnees.extract_anomalies_etapes_1 import extract_anomalies as extract_anomalies_p1
from extraction_donnees.extract_blockers import extract_blockers

# Import du moteur de calcul (Phase 2)
from calcul_scores import calculer_scores


def process_entrepreneur_profile(profil_input: str | dict[str, Any]) -> dict[str, Any]:
    """
    Point d'entrée unique pour le Backend.
    
    Prend en entrée le profil de l'entrepreneur (soit une chaîne JSON, soit un dict)
    Exécute le pipeline de diagnostic, calcule les scores et formate l'output final.
    
    :param profil_input: Données brutes du formulaire entrepreneur (Dict ou String JSON)
    :return: Contrat F2 finalisé et structuré (Dict) au format attendu par le front/BDD.
    """
    # 1. Parsing et sérialisation sécurisée
    if isinstance(profil_input, str):
        try:
            profil_data = json.loads(profil_input)
        except json.JSONDecodeError as e:
            raise ValueError(f"Le format JSON fourni est invalide : {str(e)}")
    elif isinstance(profil_input, dict):
        profil_data = profil_input
    else:
        raise TypeError("Le profil d'entrée doit être un dictionnaire ou une chaîne JSON valide.")

    # 2. Extraction Phase 1 (Indicateurs, Bloqueurs, Premières anomalies)
    sub_scores_extraits = extract_sub_scores(profil_data)
    anomalies_p1 = extract_anomalies_p1(profil_data)
    blockers_extraits = extract_blockers(profil_data)
    print(blockers_extraits)
    
    # Récupération sécurisée du secteur
    secteur = profil_data.get("secteur", "Général")

    # 3. Calcul des Scores et Enrichissement Phase 2
    contrat_f2 = calculer_scores(
        sub_scores=sub_scores_extraits,
        anomalies=anomalies_p1,
        blockers=blockers_extraits,
        secteur=secteur
    )

    # 4. Post-processing : Transformation et mapping des clés d'anomalies
    if "anomalies_detectees" in contrat_f2:
        anomalies_modifiees = []
        for anom in contrat_f2["anomalies_detectees"]:
            nouvelle_anomalie = {
                "id": anom.get("id", "?"),
                "justification": anom.get("description", ""),  # Mapping vers la clé finale
                "penalite": anom.get("penalite", 0),
                "dimension_impactee": anom.get("dimension_impactee", ""),
                "justification_template": anom.get("justification_template", ""),
                "action_template": anom.get("action_template", ""),
                "kb_link": anom.get("kb_link", "")
            }
            anomalies_modifiees.append(nouvelle_anomalie)
            
        contrat_f2["anomalies_detectees"] = anomalies_modifiees

    # 5. Retour du dictionnaire (Prêt pour un jsonify ou un return FastAPI)
    return contrat_f2