# f2_scoring/demo_scoring.py
"""
Démonstration complète du pipeline de scoring Feature 2 (Contrat F2).
Utilise calculer_scores() de calcul_scores.py et affiche un rapport terminal formaté.
"""

import sys
import os
import json

# Résolution du chemin
_THIS_DIR   = os.path.dirname(os.path.abspath(__file__))
_PARENT_DIR = os.path.dirname(_THIS_DIR)
if _PARENT_DIR not in sys.path:
    sys.path.insert(0, _PARENT_DIR)

from f2_scoring.calcul_scores import calculer_scores
from f2_scoring.matrice_coeff import ANOMALY_RULES, evaluate_condition

# ─────────────────────────────────────────────────────────────────────────────
#  PROFIL DE DÉMONSTRATION — Startup AgriTech, Sfax
# ─────────────────────────────────────────────────────────────────────────────
PROFIL = {
    "nom":    "AgroSmart TN",
    "sector": "agritech",
    "stage":  "Market Validation",

    # ── 20 sous-scores (0-100) ─────────────────────────────────────────────
    "MS1": 85,  # TAM large — potentiel export
    "MS2": 15,  # Concurrence peu documentée
    "MS3": 75,  # Nombreuses LOI signées
    "MS4": 15,  # Modèle de revenus non finalisé

    "CO1": 80,  # Proposition de valeur claire
    "CO2": 30,  # Prototype fonctionnel (Seed)
    "CO3": 15,  # Tarification non définie
    "CO4": 70,  # Bon alignement offre-besoins

    "IN1": 75,  # Nouveauté locale forte
    "IN2": 25,  # Technologie IoT basique
    "IN3": 15,  # Peu de barrières à l'entrée
    "IN4": 65,  # Rupture modérée

    "SC1": 50,  # Réplicabilité moyenne
    "SC2": 45,  # Dépendance manuelle modérée
    "SC3": 60,  # Coûts déploiement corrects
    "SC4": 40,  # Expansion régionale envisagée

    "GS1": 40,  # Énergie standard (pas ENR)
    "GS2": 85,  # Revendique gestion eau irréprochable
    "GS3": 50,  # Impact biodiversité modéré
    "GS4": 55,  # Déchets partiellement gérés

    # ── Données de contexte (pour l'évaluation des anomalies) ─────────────
    "has_client_interviews":    True,
    "has_patent_deposit_art12": False,
    "has_water_data":           False,  # Déclenchera ANOM_GS_2 !
    "saas_physical_specified":  True,
    "has_eie_document":         False,
    "has_online_presence":      True,
    "has_b2b_clients":          True,
    "has_user_tests":           True,
    "price_benchmarked_vs_distrib": False,  # Déclenchera ANOM_CO_6 si secteur Agroalimentaire et CO3 >= 70
    "has_tech_stack":           True,
    "is_identical_model":       False,
    "has_production_capacity":  True,
    "is_remotely_adaptable":    True,
    "packaging_logistics_documented": True,
    "green_hosting_policy":     True,
}

SUB_SCORES = {k: PROFIL[k] for k in PROFIL if len(k) == 3 and k[:2] in ("MS","CO","IN","SC","GS")}

# ─────────────────────────────────────────────────────────────────────────────
#  DÉTECTION DES ANOMALIES (à partir de matrice_coeff.ANOMALY_RULES)
# ─────────────────────────────────────────────────────────────────────────────
def detect_anomalies(profil: dict) -> list[dict]:
    triggered = []
    for rule in ANOMALY_RULES:
        ok = True
        for cond in rule["conditions"]:
            val = profil.get(cond["variable"], False if isinstance(cond["value"], bool) else 0)
            if not evaluate_condition(val, cond["operator"], cond["value"]):
                ok = False
                break
        if ok:
            triggered.append(rule)
    return triggered

from f2_scoring.matrice_coeff import SECTOR_ALIASES

sector_raw = PROFIL["sector"]
sector_resolved = SECTOR_ALIASES.get(sector_raw.lower(), sector_raw)

ANOMALIES_DETECTEES = detect_anomalies({
    **SUB_SCORES,
    **{k: PROFIL[k] for k in PROFIL if isinstance(PROFIL[k], bool)},
    "sector": sector_resolved,
    "stage":  PROFIL["stage"],
    # scores composites initiaux (estimés avant pénalités pour les règles globales)
    "market_score": 40, "commercial_offer_score": 58, "innovation_score": 57,
    "scalability_score": 48, "green_score": 64,
})

BLOCKERS = [
    {"domaine": "Marché",    "description": "Modèle de revenus non finalisé (MS4=15/100)",    "niveau": "rouge"},
    {"domaine": "Financier", "description": "Aucun état financier formel disponible",           "niveau": "rouge"},
    {"domaine": "Légal",     "description": "Statuts juridiques non encore déposés (RNE)",     "niveau": "orange"},
    {"domaine": "Vert",      "description": "Données hydriques non documentées en AgriTech",   "niveau": "orange"},
]

# ─────────────────────────────────────────────────────────────────────────────
#  AFFICHAGE FORMATÉ
# ─────────────────────────────────────────────────────────────────────────────
LINE  = "=" * 70
SEP   = "-" * 70
BARRE = {"rouge": "[!!!]", "orange": "[!! ]", "jaune": "[!  ]"}
NIVEAUX_FRI = [(70,"BANCABLE","**"), (50,"POTENTIELLEMENT BANCABLE","* "), (40,"INSUFFISANT","  "), (0,"NON BANCABLE","XX")]

def barre_score(val: float, width: int = 30) -> str:
    filled = int(round(val / 100 * width))
    return "[" + "#" * filled + "." * (width - filled) + f"] {val:.1f}/100"

def couleur_val(val: float) -> str:
    if val >= 70: return f"[OK]  {val:.1f}"
    if val >= 45: return f"[MOY] {val:.1f}"
    return            f"[BAS] {val:.1f}"

def print_rapport(res: dict, profil: dict):
    print()
    print(LINE)
    print(f"  RAPPORT DE SCORING — {profil['nom']}  |  Secteur : {res['secteur_applique']}")
    print(f"  Stade déclaré : {profil['stage']}")
    print(LINE)

    # ── Financing Readiness Index ─────────────────────────────────────────
    fri = res["financing_readiness_index"]
    for seuil, label, icn in NIVEAUX_FRI:
        if fri >= seuil:
            fri_label = label
            fri_icn   = icn
            break
    print(f"\n  FINANCING READINESS INDEX : {barre_score(fri, 40)}")
    print(f"  Statut : [{fri_icn}] {fri_label}")
    print(f"  {res['fri_interpretation']}")
    print(SEP)

    # ── Les 5 scores ─────────────────────────────────────────────────────
    print("\n  LES 5 SCORES COMPOSITES\n")
    NOMS = {
        "market_score":           "Market Score         ",
        "commercial_offer_score": "Commercial Offer     ",
        "innovation_score":       "Innovation Score     ",
        "scalability_score":      "Scalability Score    ",
        "green_score":            "Green Score          ",
    }
    for key, label in NOMS.items():
        s = res["scores"][key]
        penalite_val = s.get("penalite_appliquee", 0)
        penalite_str = f"  (penalite: -{penalite_val})" if penalite_val else ""
        print(f"  {label}  {barre_score(s['valeur'])}{penalite_str}")

        # Sous-scores
        for ss_name, ss_val in s["sous_scores"].items():
            poids_dict = s.get("poids_ahp")
            poids_str = f"   (poids {poids_dict[ss_name]:.1f}%)" if poids_dict and ss_name in poids_dict else ""
            label_ss = ss_name.replace("_", " ").capitalize()
            print(f"    |-- {label_ss:<28} {couleur_val(ss_val)}{poids_str}")

        # Justification et action
        print(f"    >> {s['justification']}")
        print(f"    >> ACTION : {s['action']}")
        anoms = s.get("anomalies_declenchees")
        if anoms:
            print(f"    >> Anomalies : {', '.join(anoms)}")
        print()

    # ── Anomalies ─────────────────────────────────────────────────────────
    print(SEP)
    print(f"\n  ANOMALIES DETECTEES : {len(res['anomalies_detectees'])}\n")
    for a in res["anomalies_detectees"]:
        print(f"  [!] {a['id']:<16} Penalite : -{a['penalite']} pts sur '{a['dimension_impactee']}'")
        print(f"      {a['description']}")
        print()

    # ── Blockers ──────────────────────────────────────────────────────────
    print(SEP)
    print(f"\n  BLOCKERS PRIORITAIRES : {len(res['blockers_actifs'])}\n")
    for b in res["blockers_actifs"]:
        icn = BARRE.get(b["niveau"], "[?  ]")
        print(f"  {icn} [{b['domaine']}]  {b['description']}")

    # ── Résumé exécutif ───────────────────────────────────────────────────
    print()
    print(SEP)
    print("\n  RESUME EXECUTIF\n")
    # Découpage en lignes de ~65 caractères pour lisibilité
    texte = res["resume_executif"]
    mots = texte.split()
    ligne, lignes = "", []
    for mot in mots:
        if len(ligne) + len(mot) + 1 > 65:
            lignes.append(ligne)
            ligne = mot
        else:
            ligne = f"{ligne} {mot}".strip()
    if ligne:
        lignes.append(ligne)
    for l in lignes:
        print(f"  {l}")

    print()
    print(LINE)
    print(f"  JSON COMPLET (contrat F2) ci-dessous :")
    print(LINE)
    print(json.dumps(res, ensure_ascii=False, indent=2))


# ─────────────────────────────────────────────────────────────────────────────
if __name__ == "__main__":
    resultat = calculer_scores(
        sub_scores = SUB_SCORES,
        anomalies  = ANOMALIES_DETECTEES,
        blockers   = BLOCKERS,
        secteur    = PROFIL["sector"],
    )
    print_rapport(resultat, PROFIL)

    # Extraire et sauvegarder le contrat F2 au format JSON
    output_path = os.path.join(_PARENT_DIR, "contrat_f2_output.json")
    with open(output_path, "w", encoding="utf-8") as f:
        json.dump(resultat, f, ensure_ascii=False, indent=2)
    print(f"\n[INFO] Fichier JSON exporté avec succès dans : {output_path}")
