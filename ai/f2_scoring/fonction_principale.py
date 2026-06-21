# f2_scoring/pipeline.py
"""
Orchestrateur Principal — API Backend.
Prend le profil brut de l'entrepreneur (JSON/Dict) et retourne le contrat F2 finalisé,
enrichi du contexte complet F1 (profil, gaps, stades).
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
    Exécute le pipeline de diagnostic, calcule les scores et formate l'output final
    en y intégrant tout le contexte F1 (profil complet, gaps, stades, signaux).

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

    # Récupération sécurisée du secteur et du contexte profil
    secteur = profil_data.get("secteur", "Général")
    profil_complet = profil_data.get("profil_complet", {}) or {}
    reponses_f2 = profil_data.get("reponses", {}) or {}

    # 3. Calcul des Scores et Enrichissement Phase 2
    #    On passe profil_complet et reponses_f2 pour que les ANOMALY_RULES
    #    puissent évaluer les conditions sur les champs du profil F1
    #    (rne, equipe, saisonnalite, intensite_concurrence, etc.) sans planter
    #    si un champ donné est absent du payload.
    contrat_f2 = calculer_scores(
        sub_scores=sub_scores_extraits,
        anomalies=anomalies_p1,
        blockers=blockers_extraits,
        secteur=secteur,
        profil_complet=profil_complet,
        reponses_f2=reponses_f2,
    )

    # 4. Post-processing : Transformation et mapping des clés d'anomalies
    if "anomalies_detectees" in contrat_f2:
        anomalies_modifiees = []
        for anom in contrat_f2["anomalies_detectees"]:
            nouvelle_anomalie = {
                "id": anom.get("id", "?"),
                "justification": anom.get("justification_template") or anom.get("description", ""),
                "penalite": anom.get("penalite", anom.get("penalty_points", 0)),
                "dimension_impactee": anom.get("dimension_impactee", anom.get("target_score", "")),
                "justification_template": anom.get("justification_template", ""),
                "action_template": anom.get("action_template", ""),
                "kb_link": anom.get("kb_link", "")
            }
            anomalies_modifiees.append(nouvelle_anomalie)

        contrat_f2["anomalies_detectees"] = anomalies_modifiees

    # 5. Enrichissement du contrat avec le contexte complet du diagnostic F1
    #    (id, timestamp, stade perçu vs réel, gaps, signaux de divergence)
    id_brut = profil_data.get("entrepreneur_id", "001")
    id_propre = f"PROF-{id_brut.split('-')[-1]}" if "-" in id_brut else f"PROF-{id_brut}"

    contrat_f2 = {
        "id": id_propre,
        "entrepreneur_id": profil_data.get("entrepreneur_id"),
        "timestamp": profil_data.get("timestamp"),

        # ── Contexte de diagnostic (stade perçu vs réel) ──
        "secteur": profil_data.get("secteur", "autre"),
        "secteur_label": profil_data.get("secteur_label"),
        "localisation": profil_data.get("localisation"),
        "stade_reel": profil_data.get("stade_reel"),
        "stade_percu": profil_data.get("stade_percu"),
        "gap_detecte": profil_data.get("gap_detecte", False),
        "gap_explication": profil_data.get("gap_explication"),
        "gaps": profil_data.get("gaps", []),
        "signaux_divergence": profil_data.get("signaux_divergence", []),
        "financement_recommande": profil_data.get("financement_recommande"),

        # ── Profil complet exposé tel quel ──
        "profil_complet": profil_complet,

        # ── Contrat F2 (scores, anomalies, FRI, résumé exécutif) ──
        **contrat_f2,
    }

    # 6. Retour du dictionnaire (Prêt pour un jsonify ou un return FastAPI)
    return contrat_f2