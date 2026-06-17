# f2_scoring/calcul_scores.py
"""
Feature 2 — Moteur de scoring multi-dimensionnel (Contrat F2).

Conforme à :
- AI_for_Entrepreneurship.pdf  §2.4 (5 scores, poids documentés, anomalies, guidance)
- Briefings_Equipe.docx        §Membre 2 (format JSON de sortie F2, Financing Readiness Index,
                                logique bloquante : Market < 30 OU Commercial < 25 => FRI <= 40)

ENTRÉES (JSON / dict) :
    sub_scores  : dict avec les 20 sous-scores  (MS1-MS4, CO1-CO4, IN1-IN4, SC1-SC4, GS1-GS4), 0-100
    anomalies   : list de dicts  {"id": "ANOM_XX_Y", "description": "...", "penalty_points": N, "target_score": "..."}
    blockers    : list de dicts  {"domaine": "...", "description": "...", "niveau": "rouge|orange|jaune"}
    secteur     : str  (ex. "AgriTech / Agroalimentaire" ou alias "agritech")

SORTIE (dict sérialisable JSON) — Contrat F2 :
    {
      "financing_readiness_index": int,         # 0-100, plafonné si critique
      "fri_interpretation":  str,               # label lisible + statut bancabilité
      "is_financeable": bool,                   # signal binaire pour le dashboard
      "secteur_applique": str,                  # secteur après résolution d'alias
      "scores": {
          "market_score": {
              "valeur": float,                  # score final de la dimension 0-100
              "sous_scores": {                  # 4 sous-scores nominatifs
                  "taille_marche": float,
                  "concurrence": float,
                  "validation_client": float,
                  "modele_revenus": float
              },
              "poids_ahp": {...},               # poids AHP ajustés au secteur (%)
              "penalite_appliquee": int,        # points déduits par anomalies
              "justification": str,             # explication naturelle du score
              "action": str,                    # action prioritaire pour améliorer le score
              "anomalies_declenchees": [...]    # ids des anomalies concernant cette dimension
          },
          "commercial_offer_score": {...},
          "innovation_score": {...},
          "scalability_score": {...},
          "green_score": {...}
      },
      "blockers_actifs": [...],                 # liste transmise depuis F1 enrichie
      "anomalies_detectees": [...],             # liste complète des anomalies déclenchées
      "resume_executif": str                    # paragraphe de synthèse complet
    }
"""

from __future__ import annotations
import sys
import os
import numpy as np
from typing import Any

# Résolution du chemin : fonctionne que le script soit lancé depuis AINS/ ou depuis f2_scoring/
_THIS_DIR   = os.path.dirname(os.path.abspath(__file__))   # …/AINS/f2_scoring
_PARENT_DIR = os.path.dirname(_THIS_DIR)                    # …/AINS
if _PARENT_DIR not in sys.path:
    sys.path.insert(0, _PARENT_DIR)

# Imports internes — ne modifie rien dans ces fichiers
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

# Plafond du Financing Readiness Index si une dimension critique est trop faible
# (Briefings_Equipe §Membre 2 — Logique non-linéaire bloquante)
FRI_PLAFOND_CRITIQUE = 40          # Si Market < 30 OU Commercial < 25 → FRI <= 40
MARKET_SEUIL_BLOQUANT = 30
COMMERCIAL_SEUIL_BLOQUANT = 25

# Noms lisibles pour l'affichage (clé interne → label)
DIMENSION_LABELS = {
    "market":           "Market Score",
    "commercial_offer": "Commercial Offer Score",
    "innovation":       "Innovation Score",
    "scalability":      "Scalability Score",
    "green":            "Green Score",
}

# Correspondance dimension → préfixe des 4 sous-scores
DIM_PREFIX = {
    "market":           "MS",
    "commercial_offer": "CO",
    "innovation":       "IN",
    "scalability":      "SC",
    "green":            "GS",
}

# Noms lisibles des sous-scores par dimension
SOUS_SCORE_LABELS = {
    "market":           ["taille_marche", "concurrence", "validation_client", "modele_revenus"],
    "commercial_offer": ["proposition_valeur", "maturite_produit", "strategie_prix", "alignement_besoins"],
    "innovation":       ["nouveaute_locale", "intensite_tech", "barrieres_entree", "degre_rupture"],
    "scalability":      ["replicabilite", "independance_manuelle", "couts_deploiement", "potentiel_geo"],
    "green":            ["climat_air", "eau", "sols_biodiversite", "ressources_dechets"],
}

# Poids globaux AHP inter-scores (Matrice 5x5 pré-calculée, CR=0.29%, conforme)
GLOBAL_WEIGHTS_ORDERED = {
    "market":           0.2976,
    "commercial_offer": 0.1579,
    "innovation":       0.2976,
    "scalability":      0.1579,
    "green":            0.0889,
}

# =========================================================================
# MOTEUR DE CALCUL INTERNE (ne dépend que de AHPEngine et matrice_coeff)
# =========================================================================

def _resolve_sector(secteur: str) -> str:
    """Résout les alias de secteur vers le nom complet."""
    secteur_lower = secteur.strip().lower()
    if secteur_lower in SECTOR_ALIASES:
        return SECTOR_ALIASES[secteur_lower]
    # Tentative par correspondance partielle (insensible à la casse)
    for alias, full in SECTOR_ALIASES.items():
        if alias in secteur_lower or secteur_lower in full.lower():
            return full
    return secteur  # Retourne tel quel si non trouvé


def _get_adjusted_weights(dimension: str, secteur_full: str) -> dict[str, float]:
    """
    Applique les ajustements sectoriels sur les poids AHP de base, puis
    renormalise pour que la somme = 1.0.
    Retourne {sous_score_label: poids_ajuste}.
    """
    prefix = DIM_PREFIX[dimension]
    base_w = AHP_WEIGHTS[dimension]  # {"MS1": 0.1205, ...}
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
    """
    Calcule le score final d'une dimension :
    1. Récupère les 4 sous-scores bruts (MS1..MS4, etc.)
    2. Applique les poids AHP ajustés au secteur
    3. Déduit les pénalités liées aux anomalies de cette dimension
    4. Construit le bloc de résultat attendu dans le contrat F2

    Retourne un dict complet pour la clé de cette dimension dans "scores".
    """
    prefix  = DIM_PREFIX[dimension]
    labels  = SOUS_SCORE_LABELS[dimension]
    engine  = AHPEngine()

    # --- Sous-scores bruts ---
    ss_values = {}
    for i, lbl in enumerate(labels):
        key_in = f"{prefix}{i+1}"
        ss_values[lbl] = float(sub_scores_raw.get(key_in, 0))

    # --- Poids AHP ajustés ---
    poids = _get_adjusted_weights(dimension, secteur_full)

    # --- Score brut pondéré ---
    score_brut = sum(poids[lbl] * ss_values[lbl] for lbl in labels)

    # --- Pénalités ---
    target_keys = {
        "market":           ["market", "both_market_commercial"],
        "commercial_offer": ["commercial_offer", "both_market_commercial", "both_commercial_innovation"],
        "innovation":       ["innovation", "both_commercial_innovation"],
        "scalability":      ["scalability"],
        "green":            ["green"],
    }
    anoms_dim = [a for a in anomalies if a.get("target_score") in target_keys[dimension]]
    penalite  = sum(a.get("penalty_points", 0) for a in anoms_dim)
    ids_anoms = [a.get("id", "?") for a in anoms_dim]

    score_final = round(max(0.0, score_brut - penalite), 1)

    # --- Justification et action (texte naturel) ---
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
    """
    Génère une justification textuelle et une action prioritaire
    pour chaque dimension en fonction des valeurs réelles des sous-scores.
    La logique est déterministe et tracée — pas de LLM.
    """
    labels  = SOUS_SCORE_LABELS[dimension]

    # Identifier le sous-score le plus fort et le plus faible
    faible_lbl = min(labels, key=lambda l: sous_scores[l])
    fort_lbl   = max(labels, key=lambda l: sous_scores[l])
    faible_val = sous_scores[faible_lbl]
    fort_val   = sous_scores[fort_lbl]

    # Etiquettes lisibles (remplace les underscores par des espaces)
    def human(lbl): return lbl.replace("_", " ").capitalize()

    # Niveau global du score
    if score_final >= 70:
        niveau = "solide"
    elif score_final >= 45:
        niveau = "modere"
    else:
        niveau = "critique"

    # Templates par dimension et niveau
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

    just = justifications[dimension][niveau]
    act  = actions[dimension][niveau]
    return just, act


def _compute_fri(scores_dict: dict[str, float], global_penalty: int = 0) -> tuple[int, str, bool]:
    """
    Calcule le Financing Readiness Index (FRI) sur 100.
    Applique la logique bloquante du Briefings_Equipe :
      Si Market Score < 30 OU Commercial Score < 25 → FRI plafonné à 40.
    Retourne : (fri_valeur, interpretation_texte, is_financeable)
    """
    market_val = scores_dict.get("market", 0)
    commercial_val = scores_dict.get("commercial_offer", 0)

    # Score global brut : somme pondérée AHP inter-scores
    fri_brut = sum(GLOBAL_WEIGHTS_ORDERED[dim] * val for dim, val in scores_dict.items())
    fri_brut = round(fri_brut, 1)

    # Déduction de la pénalité globale
    fri_brut = max(0.0, fri_brut - global_penalty)

    # Application du plafond critique (logique non-linéaire bloquante)
    plafond_actif = (market_val < MARKET_SEUIL_BLOQUANT or commercial_val < COMMERCIAL_SEUIL_BLOQUANT)
    fri_final = int(min(fri_brut, FRI_PLAFOND_CRITIQUE)) if plafond_actif else int(fri_brut)

    # Interprétation
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
) -> str:
    """Génère un paragraphe de synthèse exécutif complet."""
    dim_faible = min(scores_dict, key=scores_dict.get)
    dim_forte  = max(scores_dict, key=scores_dict.get)
    status     = "est bancable" if is_fin else "n'est PAS encore bancable"
    label_faible = DIMENSION_LABELS[dim_faible]
    label_forte  = DIMENSION_LABELS[dim_forte]

    return (
        f"Analyse pour le secteur '{secteur}' : le projet {status} avec un Financing Readiness Index de {fri}/100. "
        f"Le point fort du profil est le {label_forte} ({scores_dict[dim_forte]:.1f}/100). "
        f"Le principal frein est le {label_faible} ({scores_dict[dim_faible]:.1f}/100), "
        f"qui doit etre traite en priorite. "
        f"{nb_anomalies} anomalie(s) detectee(s) et {nb_blockers} blocker(s) identifie(s). "
        f"Les actions prioritaires sont detaillees par dimension dans la section 'scores'."
    )


# =========================================================================
# POINT D'ENTRÉE PUBLIC
# =========================================================================

def calculer_scores(
    sub_scores: dict[str, float],
    anomalies: list[dict],
    blockers: list[dict],
    secteur: str,
) -> dict[str, Any]:
    """
    Calcule les 5 scores composites + le Financing Readiness Index
    et retourne le contrat F2 complet au format JSON-compatible.

    Paramètres
    ----------
    sub_scores : dict
        Les 20 sous-scores : {"MS1": float, "MS2": float, ..., "GS4": float}
        Chaque valeur est comprise entre 0 et 100.
    anomalies : list[dict]
        Anomalies détectées (ex. issues de matrice_coeff.check_anomalies).
        Chaque anomalie : {"id": str, "description": str,
                           "penalty_points": int, "target_score": str}
    blockers : list[dict]
        Blockers identifiés par le module F1 (Diagnostic) ou détectés localement.
        Format : {"domaine": str, "description": str, "niveau": "rouge|orange|jaune"}
    secteur : str
        Secteur de l'entreprise (nom complet ou alias court).

    Retourne
    --------
    dict sérialisable JSON — Contrat F2 complet.
    """
    # --- Résolution du secteur ---
    secteur_full = _resolve_sector(secteur)

    # --- Enrichissement des anomalies avec les templates de matrice_coeff.py ---
    from f2_scoring.matrice_coeff import ANOMALY_RULES
    rules_dict = {rule["id"]: rule for rule in ANOMALY_RULES}
    
    enriched_anomalies = []
    for anom in anomalies:
        rule = rules_dict.get(anom.get("id"))
        if rule:
            merged = {**rule, **anom}
            enriched_anomalies.append(merged)
        else:
            enriched_anomalies.append(anom)

    # --- Calcul des 5 scores de dimension ---
    DIMS = ["market", "commercial_offer", "innovation", "scalability", "green"]
    scores_detail: dict[str, dict] = {}
    scores_valeurs: dict[str, float] = {}

    for dim in DIMS:
        result = _compute_dimension_score(dim, sub_scores, secteur_full, enriched_anomalies)
        scores_detail[f"{dim}_score"] = result
        scores_valeurs[dim] = result["valeur"]

    # --- Formatage des templates d'anomalies et application aux justifications ---
    class SafeDict(dict):
        def __missing__(self, key):
            return f"{{{key}}}"

    fmt_context = SafeDict({
        **sub_scores,
        "sector": secteur_full,
        "stage": "Ideation",  # Valeur par défaut
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
        
        justification_text = ""
        if "justification_template" in a:
            try:
                justification_text = a["justification_template"].format_map(fmt_context)
            except Exception:
                justification_text = a.get("description", "")
        else:
            justification_text = a.get("description", "")
            
        action_text = ""
        if "action_template" in a:
            try:
                action_text = a["action_template"].format_map(fmt_context)
            except Exception:
                action_text = ""
                
        if justification_text:
            a_copy["description"] = justification_text
            if action_text:
                a_copy["description"] += " ACTION : " + action_text
                
        formatted_anomalies.append(a_copy)
        
        # Surcharge de la justification et de l'action de la dimension impactée
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

    # --- Résumé exécutif ---
    resume = _build_resume_executif(
        secteur_full, fri, is_fin,
        scores_valeurs,
        len(formatted_anomalies),
        len(blockers),
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
