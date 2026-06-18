# f2_scoring/calcul_scores.py
"""
Feature 2 — Moteur de scoring multi-dimensionnel (Contrat F2).

Conforme à :
- AI_for_Entrepreneurship.pdf  §2.4 (5 scores, poids documentés, anomalies, guidance)
- Briefings_Equipe.docx        §Membre 2 (format JSON de sortie F2, Financing Readiness Index,
                                logique bloquante : Market < 30 OU Commercial < 25 => FRI <= 40)
"""

from __future__ import annotations
import sys
import os
import numpy as np
from typing import Any

# Résolution du chemin
_THIS_DIR   = os.path.dirname(os.path.abspath(__file__))
_PARENT_DIR = os.path.dirname(_THIS_DIR)
if _PARENT_DIR not in sys.path:
    sys.path.insert(0, _PARENT_DIR)

# Imports internes
from f2_scoring.ahp_engine import AHPEngine
from f2_scoring.matrice_coeff import (
    AHP_MATRICES,
    AHP_WEIGHTS,
    SECTOR_ADJUSTMENTS,
    SECTOR_ALIASES,
)

# =========================================================================
# CONSTANTES MÉTIER
# =========================================================================

FRI_PLAFOND_CRITIQUE = 40
MARKET_SEUIL_BLOQUANT = 30
COMMERCIAL_SEUIL_BLOQUANT = 25

DIMENSION_LABELS = {
    "market":           "Market Score",
    "commercial_offer": "Commercial Offer Score",
    "innovation":       "Innovation Score",
    "scalability":      "Scalability Score",
    "green":            "Green Score",
}

DIM_PREFIX = {
    "market":           "MS",
    "commercial_offer": "CO",
    "innovation":       "IN",
    "scalability":      "SC",
    "green":            "GS",
}

SOUS_SCORE_LABELS = {
    "market":           ["taille_marche", "concurrence", "validation_client", "modele_revenus"],
    "commercial_offer": ["proposition_valeur", "maturite_produit", "strategie_prix", "alignement_besoins"],
    "innovation":       ["nouveaute_locale", "intensite_tech", "barrieres_entree", "degre_rupture"],
    "scalability":      ["replicabilite", "independance_manuelle", "couts_deploiement", "potentiel_geo"],
    "green":            ["climat_air", "eau", "sols_biodiversite", "ressources_dechets"],
}

GLOBAL_WEIGHTS_ORDERED = {
    "market":           0.2976,
    "commercial_offer": 0.1579,
    "innovation":       0.2976,
    "scalability":      0.1579,
    "green":            0.0889,
}

# =========================================================================
# MOTEUR DE CALCUL INTERNE
# =========================================================================

def _resolve_sector(secteur: str) -> str:
    secteur_lower = secteur.strip().lower()
    if secteur_lower in SECTOR_ALIASES:
        return SECTOR_ALIASES[secteur_lower]
    for alias, full in SECTOR_ALIASES.items():
        if alias in secteur_lower or secteur_lower in full.lower():
            return full
    return secteur


def _get_adjusted_weights(dimension: str, secteur_full: str) -> dict[str, float]:
    prefix = DIM_PREFIX[dimension]
    base_w = AHP_WEIGHTS[dimension]
    adj_rules = SECTOR_ADJUSTMENTS.get(secteur_full, {}).get(dimension, {})

    labels = SOUS_SCORE_LABELS[dimension]
    raw = []
    for i, lbl in enumerate(labels):
        key_ahp = f"{prefix}{i+1}"
        base = base_w[key_ahp]
        adj  = adj_rules.get(key_ahp, 0.0)
        raw.append(max(0.0, base + adj))

    total = sum(raw)
    normalized = [r / total if total > 0 else 0.0 for r in raw]
    return {lbl: round(normalized[i], 4) for i, lbl in enumerate(labels)}


def _compute_dimension_score(
    dimension: str,
    sub_scores_raw: dict[str, float],
    secteur_full: str,
    anomalies: list[dict],
) -> dict[str, Any]:
    prefix  = DIM_PREFIX[dimension]
    labels  = SOUS_SCORE_LABELS[dimension]

    ss_values = {}
    for i, lbl in enumerate(labels):
        key_in = f"{prefix}{i+1}"
        ss_values[lbl] = float(sub_scores_raw.get(key_in, 0))

    poids = _get_adjusted_weights(dimension, secteur_full)
    score_brut = sum(poids[lbl] * ss_values[lbl] for lbl in labels)

    target_keys = {
        "market":           ["market", "both_market_commercial"],
        "commercial_offer": ["commercial_offer", "both_market_commercial", "both_commercial_innovation"],
        "innovation":       ["innovation", "both_commercial_innovation"],
        "scalability":      ["scalability"],
        "green":            ["green"],
    }
    anoms_dim = [a for a in anomalies if a.get("target_score") in target_keys[dimension]]
    penalite  = sum(a.get("penalty_points", 0) for a in anoms_dim)

    score_final = round(max(0.0, score_brut - penalite), 1)
    justification, action = _generate_justification(dimension, ss_values, score_final, poids)

    return {
        "valeur": score_final,
        "sous_scores": {lbl: round(ss_values[lbl], 1) for lbl in labels},
        "justification_template": justification,
        "action_template": action,
        "kb_link": "",
    }


def _generate_justification(
    dimension: str,
    sous_scores: dict[str, float],
    score_final: float,
    poids: dict[str, float],
) -> tuple[str, str]:
    labels  = SOUS_SCORE_LABELS[dimension]
    faible_lbl = min(labels, key=lambda l: sous_scores[l])
    fort_lbl   = max(labels, key=lambda l: sous_scores[l])
    faible_val = sous_scores[faible_lbl]
    fort_val   = sous_scores[fort_lbl]

    def human(lbl): return lbl.replace("_", " ").capitalize()

    if score_final >= 70:
        niveau = "solide"
    elif score_final >= 45:
        niveau = "modere"
    else:
        niveau = "critique"

    justifications = {
        "market": {
            "solide":   f"Le marche est bien positionne : le critere '{human(fort_lbl)}' ({fort_val:.0f}/100) tire le score. Le marche adressable est credible et la traction validee.",
            "modere":   f"Le marche est partiellement valide. Point fort : '{human(fort_lbl)}' ({fort_val:.0f}/100). Faiblesse identifiee : '{human(faible_lbl)}' ({faible_val:.0f}/100) qui penalise la bancabilite.",
            "critique": f"Le Market Score est insuffisant ({score_final:.1f}/100). Le critere '{human(faible_lbl)}' ({faible_val:.0f}/100) constitue un bloqueur majeur pour toute demarche de financement.",
        },
        "commercial_offer": {
            "solide":   f"L'offre commerciale est differentiated et bien definie. La '{human(fort_lbl)}' ({fort_val:.0f}/100) constitue un avantage competitif clair.",
            "modere":   f"L'offre commerciale necessite des ajustements. Le critere '{human(faible_lbl)}' ({faible_val:.0f}/100) fragilise la proposition de valeur globale.",
            "critique": f"L'offre commerciale est trop fragile ({score_final:.1f}/100). La '{human(faible_lbl)}' ({faible_val:.0f}/100) doit etre refondee avant toute approche d'investisseur.",
        },
        "innovation": {
            "solide":   f"Le profil innovant est reconnu : '{human(fort_lbl)}' ({fort_val:.0f}/100) positionne favorablement le projet sur son marche.",
            "modere":   f"L'innovation est presente mais insuffisamment defenisble. Le critere '{human(faible_lbl)}' ({faible_val:.0f}/100) limite la protection competitive.",
            "critique": f"Le score d'innovation est trop faible ({score_final:.1f}/100). Sans '{human(faible_lbl)}' renforce, le projet ne repond pas au critere Startup Act Art. 3.",
        },
        "scalability": {
            "solide":   f"Le modele est fortement scalable. La '{human(fort_lbl)}' ({fort_val:.0f}/100) confirme la capacite de croissance sans augmentation lineaire des couts.",
            "modere":   f"La scalabilite est partielle. Le critere '{human(faible_lbl)}' ({faible_val:.0f}/100) limite la trajectoire de croissance attendue par les financeurs.",
            "critique": f"Le profil de scalabilite est insuffisant ({score_final:.1f}/100). Le critere '{human(faible_lbl)}' ({faible_val:.0f}/100) signale une dependance trop forte au modele manuel.",
        },
        "green": {
            "solide":   f"L'impact environnemental est bien maitrise. Le pilier '{human(fort_lbl)}' ({fort_val:.0f}/100) est un atout dans le contexte PNUD/ODD.",
            "modere":   f"La dimension green est partiellement couverte. Le pilier '{human(faible_lbl)}' ({faible_val:.0f}/100) necessite des actions correctives documentees.",
            "critique": f"Le Green Score est insuffisant ({score_final:.1f}/100). Le pilier '{human(faible_lbl)}' ({faible_val:.0f}/100) constitue un risque ESG pour les partenaires PNUD.",
        },
    }

    actions = {
        "market": {
            "solide":   f"Consolider la documentation de validation client (LOI, contrats) pour renforcer le dossier bancaire.",
            "modere":   f"Priorite : ameliorer '{human(faible_lbl)}' — obtenir 3 lettres d'intention clients ou preuves de traction payante avant tout depot de dossier.",
            "critique": f"ACTION URGENTE : '{human(faible_lbl)}' doit passer au-dessus de 30/100. Sans cela, aucun financement n'est envisageable.",
        },
        "commercial_offer": {
            "solide":   f"Formaliser le pricing dans un document de strategie commerciale pour les due diligences.",
            "modere":   f"Travailler '{human(faible_lbl)}' : rediger une fiche de proposition de valeur claire (1 page) et la tester avec 5 clients potentiels.",
            "critique": f"ACTION URGENTE : redefinir '{human(faible_lbl)}' (score {faible_val:.0f}/100). Engager un atelier job-to-be-done avec de vrais utilisateurs.",
        },
        "innovation": {
            "solide":   f"Initier une procedure de depot de brevet (Art. 12 Startup Act) pour securiser les barrieres a l'entree.",
            "modere":   f"Renforcer '{human(faible_lbl)}' : documenter la differentiation par rapport aux solutions existantes sur le marche tunisien.",
            "critique": f"ACTION URGENTE : justifier la nouveaute par une etude comparative de marche. Sans differentiation documentee, le label Startup Act est inaccessible.",
        },
        "scalability": {
            "solide":   f"Modeliser les economies d'echelle a 3 ans pour le dossier de levee de fonds.",
            "modere":   f"Reduire la dependance sur '{human(faible_lbl)}' : identifier 2 processus manuels a automatiser dans les 3 prochains mois.",
            "critique": f"ACTION URGENTE : repenser le modele operationnel pour que '{human(faible_lbl)}' depasse 30/100 — le projet ne peut pas scaler dans son etat actuel.",
        },
        "green": {
            "solide":   f"Formaliser le bilan carbone et l'aligner sur les ODD pour les dossiers de financement PNUD/AFD.",
            "modere":   f"Produire un plan d'action sur le pilier '{human(faible_lbl)}' : mesures correctives, calendrier, indicateurs suivis.",
            "critique": f"ACTION URGENTE : le pilier '{human(faible_lbl)}' ({faible_val:.0f}/100) doit faire l'objet d'un plan de mitigation ecrit avant toute soumission a des fonds verts.",
        },
    }

    return justifications[dimension][niveau], actions[dimension][niveau]


def _compute_fri(scores_dict: dict[str, float], global_penalty: int = 0) -> tuple[int, str, bool]:
    market_val = scores_dict.get("market", 0)
    commercial_val = scores_dict.get("commercial_offer", 0)

    fri_brut = sum(GLOBAL_WEIGHTS_ORDERED[dim] * val for dim, val in scores_dict.items())
    fri_brut = max(0.0, round(fri_brut, 1) - global_penalty)

    plafond_actif = (market_val < MARKET_SEUIL_BLOQUANT or commercial_val < COMMERCIAL_SEUIL_BLOQUANT)
    fri_final = int(min(fri_brut, FRI_PLAFOND_CRITIQUE)) if plafond_actif else int(fri_brut)

    if fri_final >= 70:
        interp = f"Excellent ({fri_final}/100) — Profil bancable. Le projet peut initier une demarche de financement formelle."
        is_fin = True
    elif fri_final >= 50:
        interp = f"Favorable ({fri_final}/100) — Profil potentiellement bancable avec des renforcements cibles."
        is_fin = True
    elif fri_final >= 40:
        interp = f"Insuffisant ({fri_final}/100) — Des blockers majeurs doivent etre resolus avant toute approche bancaire."
        is_fin = False
    else:
        if plafond_actif:
            raison = "Market Score < 30" if market_val < MARKET_SEUIL_BLOQUANT else "Commercial Score < 25"
            interp = f"Non bancable ({fri_final}/100) — Plafond active : {raison}. Ce projet ne peut PAS acceder a un financement dans son etat actuel."
        else:
            interp = f"Non bancable ({fri_final}/100) — Les scores cumulatifs sont trop faibles. Un accompagnement structurant est indispensable."
        is_fin = False

    return fri_final, interp, is_fin


def _build_resume_executif(
    secteur: str,
    fri: int,
    is_fin: bool,
    scores_dict: dict[str, float],
    nb_anomalies: int,
    nb_blockers: int,
    global_penalty: int = 0,  # Nouvelle variable passée au build
) -> str:
    dim_faible = min(scores_dict, key=scores_dict.get)
    dim_forte  = max(scores_dict, key=scores_dict.get)
    
    status = "est bancable" if is_fin else "n'est PAS encore bancable"
    
    # 1. Introduction globale
    debut = f"Analyse pour le secteur '{secteur}' : le projet {status} avec un Financing Readiness Index de {fri}/100. "
    
    # 2. Analyse des forces
    forces = f"Le point fort intrinsèque du profil est le {DIMENSION_LABELS[dim_forte]} ({scores_dict[dim_forte]:.1f}/100). "
    
    # 3. Détermination dynamique de la cause principale de l'échec / frein
    if global_penalty >= 40:
        freins = (
            f"Cependant, la viabilité financière est lourdement compromise par une alerte de conformité réglementaire majeure "
            f"(-{global_penalty} points appliqués au score global). "
        )
    elif nb_blockers > 0 and fri <= 40:
        freins = (
            f"Le profil est actuellement bloqué par {nb_blockers} critère(s) éliminatoire(s) actif(s) "
            f"(notamment sur le plan organisationnel ou légal), ce qui active automatiquement un plafond critique de vigilance. "
        )
    else:
        freins = f"Le principal levier d'amélioration est le {DIMENSION_LABELS[dim_faible]} ({scores_dict[dim_faible]:.1f}/100). "
        
    # 4. Conclusion / Appel à l'action
    if nb_anomalies > 0 or nb_blockers > 0:
        conclusion = (
            f"Au total, {nb_anomalies} anomalie(s) et {nb_blockers} bloqueur(s) requièrent une résolution immédiate. "
            f"Les actions correctives prioritaires sont détaillées dans les sections dédiées."
        )
    else:
        conclusion = "Le projet présente un profil régulier, les optimisations mineures sont disponibles dans la section 'scores'."

    return debut + forces + freins + conclusion

def _evaluer_condition(condition: dict, contexte: dict) -> bool:
    var = condition.get("variable")
    op = condition.get("operator")
    val_cible = condition.get("value")
    
    if var not in contexte:
        return False
        
    val_reelle = contexte[var]
    
    if op == "==": return val_reelle == val_cible
    if op == ">=": return val_reelle >= val_cible
    if op == "<=": return val_reelle <= val_cible
    if op == "in":
        if isinstance(val_reelle, str) and isinstance(val_cible, list):
            return val_reelle.lower() in [v.lower() for v in val_cible]
        return val_reelle in val_cible
    return False

def _detecter_anomalies_scoring(sub_scores: dict, secteur_full: str, anomalies_phase_1: list[dict]) -> list[dict]:
    from f2_scoring.matrice_coeff import ANOMALY_RULES
    
    contexte = {**sub_scores}
    contexte["sector"] = secteur_full
    
    ids_phase_1 = {a.get("id") for a in anomalies_phase_1}
    contexte["has_water_data"] = "ANOM_RECIPIENT_WATER_MISSING" not in ids_phase_1 
    contexte["saas_physical_specified"] = "ANOM_MODEL_NOT_SPECIFIED" not in ids_phase_1
    contexte["has_eie_document"] = "ANOM_EIE_MISSING" not in ids_phase_1

    anomalies_calculees = []
    for rule in ANOMALY_RULES:
        conditions = rule.get("conditions", [])
        if not conditions:
            continue
            
        if all(_evaluer_condition(cond, contexte) for cond in conditions):
            anomalies_calculees.append({
                "id": rule["id"],
                "penalty_points": rule["penalty_points"],
                "target_score": rule["target_score"],
                "description": rule.get("description", "")
            })
            
    return anomalies_calculees

# =========================================================================
# POINT D'ENTRÉE PUBLIC
# =========================================================================

def calculer_scores(
    sub_scores: dict[str, float],
    anomalies: list[dict],
    blockers: list[dict],
    secteur: str,
) -> dict[str, Any]:
    secteur_full = _resolve_sector(secteur)
    anomalies_scoring = _detecter_anomalies_scoring(sub_scores, secteur_full, anomalies)
    toutes_anomalies = anomalies + anomalies_scoring

    vu = set()
    anomalies_uniques = []
    for a in toutes_anomalies:
        if a.get("id") not in vu:
            vu.add(a.get("id"))
            anomalies_uniques.append(a)

    from f2_scoring.matrice_coeff import ANOMALY_RULES
    rules_dict = {rule["id"]: rule for rule in ANOMALY_RULES}
    
    enriched_anomalies = []
    for anom in anomalies_uniques:
        rule = rules_dict.get(anom.get("id"))
        if rule:
            merged = {**rule, **anom}
            enriched_anomalies.append(merged)
        else:
            enriched_anomalies.append(anom)

    DIMS = ["market", "commercial_offer", "innovation", "scalability", "green"]
    scores_detail: dict[str, dict] = {}
    scores_valeurs: dict[str, float] = {}

    for dim in DIMS:
        result = _compute_dimension_score(dim, sub_scores, secteur_full, enriched_anomalies)
        scores_detail[f"{dim}_score"] = result
        scores_valeurs[dim] = result["valeur"]

    # --- MODIFICATION ICI : Récupération et formatage flexible des templates ---
    class SafeDict(dict):
        def __missing__(self, key):
            return f"{{{key}}}"

    fmt_context = SafeDict({
        **sub_scores,
        "sector": secteur_full,
        "stage": "Ideation",
        "market_score": scores_valeurs.get("market", 0.0),
        "commercial_offer_score": scores_valeurs.get("commercial_offer", 0.0),
        "innovation_score": scores_valeurs.get("innovation", 0.0),
        "scalability_score": scores_valeurs.get("scalability", 0.0),
        "green_score": scores_valeurs.get("green", 0.0),
    })

    formatted_anomalies = []
    for a in enriched_anomalies:
        a_copy = a.copy()
        fmt_context["kb_link"] = a.get("kb_link", "")
        
        # Capture adaptative du texte de justification (gère 'justification' et 'justification_template')
        raw_just = a.get("justification") or a.get("justification_template") or a.get("description", "")
        justification_text = ""
        if raw_just:
            try:
                justification_text = raw_just.format_map(fmt_context)
            except Exception:
                justification_text = raw_just
        
        # Capture adaptative de l'action
        raw_action = a.get("action") or a.get("action_template", "")
        action_text = ""
        if raw_action:
            try:
                action_text = raw_action.format_map(fmt_context)
            except Exception:
                action_text = raw_action
                
        # Sauvegarde formelle pour l'output final
        a_copy["justification_template"] = justification_text
        a_copy["action_template"] = action_text

        if justification_text:
            a_copy["description"] = justification_text
            if action_text:
                a_copy["description"] += " ACTION : " + action_text
                
        formatted_anomalies.append(a_copy)
        
        # Surcharge des blocs dimensionnels
        target = a.get("target_score", "")
        target_keys = {
            "market":           ["market", "both_market_commercial"],
            "commercial_offer": ["commercial_offer", "both_market_commercial", "both_commercial_innovation"],
            "innovation":       ["innovation", "both_commercial_innovation"],
            "scalability":      ["scalability"],
            "green":            ["green"],
        }
        for dim in DIMS:
            if target in target_keys[dim]:
                if justification_text:
                    scores_detail[f"{dim}_score"]["justification_template"] = justification_text
                if action_text:
                    scores_detail[f"{dim}_score"]["action_template"] = action_text
                scores_detail[f"{dim}_score"]["kb_link"] = a.get("kb_link", "")

    # --- Financing Readiness Index ---
    global_penalty = sum(a.get("penalty_points", 0) for a in formatted_anomalies if a.get("target_score") == "global")
    fri, fri_interp, is_fin = _compute_fri(scores_valeurs, global_penalty)

    # --- MODIFICATION COMPATIBILITÉ : Ajout de global_penalty pour un résumé intelligent ---
    resume = _build_resume_executif(
        secteur_full, 
        fri, 
        is_fin, 
        scores_valeurs, 
        len(formatted_anomalies), 
        len(blockers), 
        global_penalty
    )

    # --- Construction du contrat F2 ---
    contrat_f2 = {
        "financing_readiness_index": fri,
        "fri_interpretation": fri_interp,
        "is_financeable": is_fin,
        "secteur_applique": secteur_full,
        "scores": scores_detail,
        "blockers_actifs": blockers,
        "anomalies_detectees": [
            {
                "id": a.get("id", "?"),
                "description": a.get("description", ""),
                "penalite": a.get("penalty_points", 0),
                "dimension_impactee": a.get("target_score", ""),
                "justification_template": a.get("justification_template", ""),
                "action_template": a.get("action_template", ""),
                "kb_link": a.get("kb_link", ""),
            }
            for a in formatted_anomalies
        ],
        "resume_executif": resume,
    }

    return contrat_f2

# =========================================================================
# DÉMO AUTONOME (exécutable directement)
# =========================================================================
if __name__ == "__main__":
    import json

    # Profil de test : startup AgriTech avec anomalies
    sub_scores_demo = {
        "MS1": 85, "MS2": 15, "MS3": 75, "MS4": 15,
        "CO1": 80, "CO2": 30, "CO3": 15, "CO4": 70,
        "IN1": 75, "IN2": 25, "IN3": 15, "IN4": 65,
        "SC1": 50, "SC2": 45, "SC3": 60, "SC4": 40,
        "GS1": 40, "GS2": 85, "GS3": 50, "GS4": 55,
    }

    anomalies_demo = [
        {
            "id": "ANOM_MS_1",
            "description": "Validation client elevee (MS3>=70) mais modele de revenus embryonnaire (MS4<=20).",
            "penalty_points": 8,
            "target_score": "market",
        },
        {
            "id": "ANOM_SC_1",
            "description": "Forte replicabilite revendiquee (SC1>=18) mais modele de revenus embryonnaire (MS4<=20).",
            "penalty_points": 10,
            "target_score": "scalability",
        },
        {
            "id": "ANOM_GS_2",
            "description": "Gestion de l'eau revendiquee (GS2>=70) en AgriTech sans donnee hydrique fournie.",
            "penalty_points": 10,
            "target_score": "green",
        },
    ]

    blockers_demo = [
        {"domaine": "Marche",    "description": "Modele de revenus non finalise",          "niveau": "rouge"},
        {"domaine": "Financier", "description": "Aucun document financier disponible",      "niveau": "orange"},
        {"domaine": "Legal",     "description": "Statuts juridiques non deposes",           "niveau": "jaune"},
    ]

    resultat = calculer_scores(
        sub_scores=sub_scores_demo,
        anomalies=anomalies_demo,
        blockers=blockers_demo,
        secteur="agritech",
    )

    print(json.dumps(resultat, ensure_ascii=False, indent=2))
