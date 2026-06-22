"""
=======================================================================
PROTOCOLE D'ÉVALUATION v2 — Feature 2 : Explainable Multi-Dimensional Scoring
AINS Hackathon 2026
=======================================================================

Chaque profil de test est construit au format réel du pipeline :
  - profil_complet  : champs sectoriels issus de la Feature 1 (branche_*)
  - reponses        : réponses F2 avec index (0-4) et valeur textuelle
  - blockers        : liste avec domaine / description / niveau
  - expected        : valeurs attendues en sortie (fri_min/max, capped, anomalies)

4 métriques :
  1. Overall Pass Rate
  2. Score Consistency (monotonie ordinale P09 >= P01 >= P10)
  3. Anomaly Detection Rate
  4. Hard-Cap Compliance

Exécution : python eval_protocol_f2_v2.py
Output    : eval_report_f2_v2.json
=======================================================================
"""

import json
import math
from datetime import datetime

# ── Import réel (décommenter quand PYTHONPATH configuré) ──────────────
# from fonction_principale import process_entrepreneur_profile
# from extract_sub_scores import extract_sub_scores
# from calcul_scores import calculer_scores

# =========================================================================
# SCALE de conversion index → score (identique à extract_sub_scores.py)
# =========================================================================
SCALE = [10, 40, 60, 75, 90]

def index_to_score(index: int) -> int:
    return SCALE[index] if 0 <= index <= 4 else 60

def reponses_to_sub_scores(reponses: dict) -> dict:
    """Reproduit extract_sub_scores.py — mapping clé questionnaire → code sous-score."""
    mapping = {
        "potentiel_financier_marche": "MS1",
        "intensite_concurrence":      "MS2",
        "niveau_traction":            "MS3",
        "modele_revenu":              "MS4",
        "business_plan_f2":           "CO1",
        "maturite_produit":           "CO2",
        "strategie_prix":             "CO3",
        "alignement_besoins":         "CO4",
        "nouveaute_locale":           "IN1",
        "intensite_tech":             "IN2",
        "barrieres_entree":           "IN3",
        "degre_rupture":              "IN4",
        "replicabilite":              "SC1",
        "independance_manuelle":      "SC2",
        "couts_deploiement":          "SC3",
        "potentiel_geo":              "SC4",
        "climat_air":                 "GS1",
        "donnees_eau_fournies":       "GS2",
        "sols_biodiversite":          "GS3",
        "ressources_dechets":         "GS4",
    }
    sub_scores = {}
    for qid, code in mapping.items():
        rep = reponses.get(qid, {})
        idx = rep.get("index", 2) if isinstance(rep, dict) else 2
        sub_scores[code] = index_to_score(idx)
    return sub_scores

# =========================================================================
# MOCK calculer_scores — remplace par ton import réel
# =========================================================================
GLOBAL_W = {
    "market": 0.2976, "commercial_offer": 0.1579,
    "innovation": 0.2976, "scalability": 0.1579, "green": 0.0889,
}
AHP_W = {
    "market":           {"MS1":0.1205,"MS2":0.4542,"MS3":0.1826,"MS4":0.2427},
    "commercial_offer": {"CO1":0.2772,"CO2":0.1610,"CO3":0.0960,"CO4":0.4658},
    "innovation":       {"IN1":0.4231,"IN2":0.2272,"IN3":0.1225,"IN4":0.2272},
    "scalability":      {"SC1":0.4687,"SC2":0.2800,"SC3":0.1361,"SC4":0.1152},
    "green":            {"GS1":0.2772,"GS2":0.4658,"GS3":0.0960,"GS4":0.1610},
}
DIM_KEYS = {
    "market":           ["MS1","MS2","MS3","MS4"],
    "commercial_offer": ["CO1","CO2","CO3","CO4"],
    "innovation":       ["IN1","IN2","IN3","IN4"],
    "scalability":      ["SC1","SC2","SC3","SC4"],
    "green":            ["GS1","GS2","GS3","GS4"],
}

def calculer_scores_mock(sub_scores, anomalies, blockers, secteur,
                          profil_complet=None, reponses_f2=None):
    scores = {}
    for dim, keys in DIM_KEYS.items():
        w = AHP_W[dim]
        scores[dim] = round(sum(w[k] * sub_scores.get(k, 60) for k in keys), 1)

    fri_brut = sum(GLOBAL_W[d] * scores[d] for d in GLOBAL_W)
    SEV = {"rouge": 0.7, "orange": 0.25, "jaune": 0.1}
    lam = sum(SEV.get(b.get("niveau", ""), 0.1) for b in blockers)
    global_pen = sum(a.get("penalty_points", 0) for a in anomalies
                     if a.get("target_score") == "global")
    fri = int(max(0, min(100, round(fri_brut * math.exp(-lam) - global_pen, 1))))

    capped = False
    if scores.get("market", 100) < 30:
        fri = min(fri, 40); capped = True
    if scores.get("commercial_offer", 100) < 25:
        fri = min(fri, 40); capped = True

    return {
        "financing_readiness_index": fri,
        "is_financeable": fri >= 55,
        "scores": {d: {"valeur": scores[d]} for d in scores},
        "anomalies_detectees": anomalies,
        "_capped": capped,
    }

calculer_scores = calculer_scores_mock

# =========================================================================
# TEST SET v2 — 14 profils au format réel
# =========================================================================
# Légende index → score : 0=10, 1=40, 2=60, 3=75, 4=90

TEST_SET = [

    # ══════════════════════════════════════════════════════════════════════
    # SECTEUR : AGRICULTURE (branche_agriculture_sylviculture_peche)
    # ══════════════════════════════════════════════════════════════════════

    {
        "id": "P01",
        "description": "Agriculture Siliana — profil réel ENT-DBD323 — Market critique → hard-cap 40",
        "secteur": "agriculture_sylviculture_peche",
        "profil_complet": {
            "equipe":                  "solo",
            "certifications_sanitaires": False,
            "chaine_froid":            False,
            "saisonnalite":            "Partiellement",
            "acces_foncier":           "Oui, location court terme",
            "rne":                     True,
            "chiffre_affaires":        58852266.0,
            "anciennete_revenus":      "Plus de 3 ans",
            "business_plan":           "absent",
            "innovation_niveau":       "tres_faible",
            "accompagnement":          "jamais",
            "financement":             "aucun",
        },
        "reponses": {
            "potentiel_financier_marche": {"index": 0, "valeur": "marche_national_intermediaire"},
            "intensite_concurrence":      {"index": 0, "valeur": "marche_partage"},
            "niveau_traction":            {"index": 0, "valeur": "traction_initiale"},
            "modele_revenu":              {"index": 1, "valeur": "commission_marketplace"},
            "business_plan_f2":           {"index": 1, "valeur": "en_cours_de_validation"},
            "maturite_produit":           {"index": 1, "valeur": "mvp_valide"},
            "strategie_prix":             {"index": 1, "valeur": "alignement_concurrence"},
            "alignement_besoins":         {"index": 1, "valeur": "important_non_urgent"},
            "nouveaute_locale":           {"index": 4, "valeur": "adaptation_locale"},
            "intensite_tech":             {"index": 4, "valeur": "integration_avancee"},
            "barrieres_entree":           {"index": 4, "valeur": "moat_commercial"},
            "degre_rupture":              {"index": 4, "valeur": "transformation_process"},
            "replicabilite":              {"index": 4, "valeur": "deploiement_operationnel_modere"},
            "independance_manuelle":      {"index": 4, "valeur": "paliers_de_croissance"},
            "couts_deploiement":          {"index": 4, "valeur": "besoin_modere"},
            "potentiel_geo":              {"index": 4, "valeur": "national"},
            "climat_air":                 {"index": 4, "valeur": "neutralite_passive"},
            "donnees_eau_fournies":       {"index": 4, "valeur": "suivi_manuel_partiel"},
            "sols_biodiversite":          {"index": 4, "valeur": "preservation_passive"},
            "ressources_dechets":         {"index": 4, "valeur": "reduction_a_la_source"},
        },
        "blockers": [],
        "anomalies_injectees": [
            {"id":"ANOM_TEAM_SOLO_FATIGUE","penalty_points":10,"target_score":"commercial_offer"},
            {"id":"ANOM_ECO_REGIONAL_FUNDS_MISSED","penalty_points":10,"target_score":"commercial_offer"},
        ],
        # Market = 0.1205*10 + 0.4542*10 + 0.1826*10 + 0.2427*40 = 1.205+4.542+1.826+9.708 = 17.3 < 30 → cap
        "expected": {"fri_min": 0, "fri_max": 40, "is_financeable": False, "capped": True},
        "expected_anomaly_ids": ["ANOM_TEAM_SOLO_FATIGUE", "ANOM_ECO_REGIONAL_FUNDS_MISSED"],
    },

    {
        "id": "P02",
        "description": "Agriculture Sfax — certifications ok, chaine froid ok, équipe constituée → bancable",
        "secteur": "agriculture_sylviculture_peche",
        "profil_complet": {
            "equipe":                  "equipe_complete",
            "certifications_sanitaires": True,
            "chaine_froid":            True,
            "saisonnalite":            "Non, activité régulière toute l'année",
            "acces_foncier":           "Oui, propriété ou bail long terme",
            "rne":                     True,
            "chiffre_affaires":        1200000.0,
            "anciennete_revenus":      "Entre 1 et 3 ans",
            "business_plan":           "complet",
            "innovation_niveau":       "moyen",
            "accompagnement":          "programme_apii",
            "financement":             "credit_bancaire",
        },
        "reponses": {
            "potentiel_financier_marche": {"index": 3, "valeur": "marche_regional_fort"},
            "intensite_concurrence":      {"index": 2, "valeur": "marche_oligopolistique"},
            "niveau_traction":            {"index": 3, "valeur": "traction_forte"},
            "modele_revenu":              {"index": 3, "valeur": "abonnement_recurrent"},
            "business_plan_f2":           {"index": 3, "valeur": "valide_complet"},
            "maturite_produit":           {"index": 3, "valeur": "produit_marche"},
            "strategie_prix":             {"index": 2, "valeur": "premium_justifie"},
            "alignement_besoins":         {"index": 3, "valeur": "besoin_urgent_valide"},
            "nouveaute_locale":           {"index": 2, "valeur": "amelioration_notable"},
            "intensite_tech":             {"index": 2, "valeur": "tech_moderee"},
            "barrieres_entree":           {"index": 2, "valeur": "barrieres_moderees"},
            "degre_rupture":              {"index": 2, "valeur": "evolution_incrementale"},
            "replicabilite":              {"index": 3, "valeur": "replicabilite_elevee"},
            "independance_manuelle":      {"index": 3, "valeur": "semi_automatise"},
            "couts_deploiement":          {"index": 3, "valeur": "investissement_modere"},
            "potentiel_geo":              {"index": 3, "valeur": "maghreb"},
            "climat_air":                 {"index": 3, "valeur": "reduction_active"},
            "donnees_eau_fournies":       {"index": 3, "valeur": "gestion_raisonnee"},
            "sols_biodiversite":          {"index": 3, "valeur": "pratiques_durables"},
            "ressources_dechets":         {"index": 3, "valeur": "economie_circulaire"},
        },
        "blockers": [],
        "anomalies_injectees": [],
        "expected": {"fri_min": 60, "fri_max": 100, "is_financeable": True, "capped": False},
        "expected_anomaly_ids": [],
    },

    {
        "id": "P03",
        "description": "Agriculture — accès foncier incertain + saisonnalité forte + solo → blocker rouge",
        "secteur": "agriculture_sylviculture_peche",
        "profil_complet": {
            "equipe":                  "solo",
            "certifications_sanitaires": False,
            "chaine_froid":            False,
            "saisonnalite":            "Oui, fortement saisonnière",
            "acces_foncier":           "Non, accès incertain",
            "rne":                     False,
            "chiffre_affaires":        0,
            "anciennete_revenus":      "Moins d'un an",
            "business_plan":           "absent",
            "innovation_niveau":       "nul",
            "accompagnement":          "jamais",
            "financement":             "aucun",
        },
        "reponses": {
            "potentiel_financier_marche": {"index": 0, "valeur": "marche_local_faible"},
            "intensite_concurrence":      {"index": 0, "valeur": "marche_partage"},
            "niveau_traction":            {"index": 0, "valeur": "aucune_traction"},
            "modele_revenu":              {"index": 0, "valeur": "non_defini"},
            "business_plan_f2":           {"index": 0, "valeur": "absent"},
            "maturite_produit":           {"index": 0, "valeur": "idee"},
            "strategie_prix":             {"index": 0, "valeur": "non_definie"},
            "alignement_besoins":         {"index": 0, "valeur": "hypothetique"},
            "nouveaute_locale":           {"index": 0, "valeur": "copie_existant"},
            "intensite_tech":             {"index": 0, "valeur": "aucune_tech"},
            "barrieres_entree":           {"index": 0, "valeur": "aucune_barriere"},
            "degre_rupture":              {"index": 0, "valeur": "aucune_rupture"},
            "replicabilite":              {"index": 0, "valeur": "non_replicable"},
            "independance_manuelle":      {"index": 0, "valeur": "totalement_manuel"},
            "couts_deploiement":          {"index": 0, "valeur": "capex_prohibitif"},
            "potentiel_geo":              {"index": 0, "valeur": "local_seulement"},
            "climat_air":                 {"index": 0, "valeur": "impact_negatif"},
            "donnees_eau_fournies":       {"index": 0, "valeur": "aucune_gestion"},
            "sols_biodiversite":          {"index": 0, "valeur": "degradation_passive"},
            "ressources_dechets":         {"index": 0, "valeur": "aucune_gestion"},
        },
        "blockers": [
            {"domaine": "Réglementaire", "description": "Absence de certification sanitaire ou phytosanitaire", "niveau": "orange"},
        ],
        "anomalies_injectees": [],
        # Tous index 0 = score 10 → market ~10, commercial ~10 → double hard-cap
        "expected": {"fri_min": 0, "fri_max": 40, "is_financeable": False, "capped": True},
        "expected_anomaly_ids": [],
    },

    # ══════════════════════════════════════════════════════════════════════
    # SECTEUR : TECH / DIGITAL (branche_tech_services_entreprise)
    # ══════════════════════════════════════════════════════════════════════

    {
        "id": "P04",
        "description": "Tech Tunis — SaaS en production, MRR fort, équipe, IP protégée → profil bancable",
        "secteur": "tech",
        "profil_complet": {
            "equipe":                "equipe_complete",
            "rne":                   True,
            "forme_juridique":       "SUARL",
            "mvp_statut":            "production",
            "mrr":                   "fort",
            "propriete_intellectuelle": True,
            "scalabilite":           "Oui, fortement scalable (SaaS, plateforme)",
            "business_plan":         "complet",
            "accompagnement":        "incubateur",
            "financement":           "love_money",
            "chiffre_affaires":      85000.0,
            "anciennete_revenus":    "Entre 1 et 3 ans",
        },
        "reponses": {
            "potentiel_financier_marche": {"index": 4, "valeur": "marche_global"},
            "intensite_concurrence":      {"index": 3, "valeur": "marche_oligopolistique"},
            "niveau_traction":            {"index": 4, "valeur": "traction_forte"},
            "modele_revenu":              {"index": 4, "valeur": "abonnement_recurrent"},
            "business_plan_f2":           {"index": 4, "valeur": "valide_complet"},
            "maturite_produit":           {"index": 4, "valeur": "produit_marche"},
            "strategie_prix":             {"index": 4, "valeur": "premium_justifie"},
            "alignement_besoins":         {"index": 4, "valeur": "besoin_urgent_valide"},
            "nouveaute_locale":           {"index": 3, "valeur": "innovation_claire"},
            "intensite_tech":             {"index": 4, "valeur": "tech_avancee"},
            "barrieres_entree":           {"index": 3, "valeur": "barrieres_elevees"},
            "degre_rupture":              {"index": 3, "valeur": "rupture_moderee"},
            "replicabilite":              {"index": 4, "valeur": "replicabilite_elevee"},
            "independance_manuelle":      {"index": 4, "valeur": "full_automatise"},
            "couts_deploiement":          {"index": 4, "valeur": "marginal_cost_zero"},
            "potentiel_geo":              {"index": 4, "valeur": "global_born_global"},
            "climat_air":                 {"index": 3, "valeur": "reduction_active"},
            "donnees_eau_fournies":       {"index": 2, "valeur": "suivi_partiel"},
            "sols_biodiversite":          {"index": 2, "valeur": "neutre"},
            "ressources_dechets":         {"index": 3, "valeur": "reduction_structuree"},
        },
        "blockers": [],
        "anomalies_injectees": [],
        "expected": {"fri_min": 70, "fri_max": 100, "is_financeable": True, "capped": False},
        "expected_anomaly_ids": [],
    },

    {
        "id": "P05",
        "description": "Tech — traction forte (index 4) mais modèle revenu nul (index 0) → ANOM_MS_1",
        "secteur": "tech",
        "profil_complet": {
            "equipe":                "duo_fondateurs",
            "rne":                   True,
            "mvp_statut":            "test",
            "mrr":                   "zero_avec_users",
            "propriete_intellectuelle": False,
            "scalabilite":           "Partiellement scalable",
            "business_plan":         "en_cours",
            "accompagnement":        "jamais",
            "financement":           "aucun",
        },
        "reponses": {
            "potentiel_financier_marche": {"index": 2, "valeur": "marche_national_moyen"},
            "intensite_concurrence":      {"index": 2, "valeur": "marche_fragmente"},
            "niveau_traction":            {"index": 4, "valeur": "traction_forte"},   # ← contradiction
            "modele_revenu":              {"index": 0, "valeur": "non_defini"},        # ← contradiction
            "business_plan_f2":           {"index": 1, "valeur": "en_cours_de_validation"},
            "maturite_produit":           {"index": 2, "valeur": "beta"},
            "strategie_prix":             {"index": 1, "valeur": "freemium"},
            "alignement_besoins":         {"index": 2, "valeur": "besoin_confirme"},
            "nouveaute_locale":           {"index": 2, "valeur": "amelioration_notable"},
            "intensite_tech":             {"index": 3, "valeur": "tech_avancee"},
            "barrieres_entree":           {"index": 2, "valeur": "barrieres_moderees"},
            "degre_rupture":              {"index": 2, "valeur": "evolution_incrementale"},
            "replicabilite":              {"index": 3, "valeur": "replicabilite_elevee"},
            "independance_manuelle":      {"index": 2, "valeur": "semi_automatise"},
            "couts_deploiement":          {"index": 3, "valeur": "investissement_modere"},
            "potentiel_geo":              {"index": 2, "valeur": "national"},
            "climat_air":                 {"index": 2, "valeur": "neutralite_passive"},
            "donnees_eau_fournies":       {"index": 2, "valeur": "suivi_partiel"},
            "sols_biodiversite":          {"index": 2, "valeur": "neutre"},
            "ressources_dechets":         {"index": 2, "valeur": "reduction_a_la_source"},
        },
        "blockers": [],
        "anomalies_injectees": [
            {"id": "ANOM_MS_1", "penalty_points": 8, "target_score": "market"},
        ],
        "expected": {"fri_min": 30, "fri_max": 70, "is_financeable": None, "capped": False},
        "expected_anomaly_ids": ["ANOM_MS_1"],
    },

    {
        "id": "P06",
        "description": "Tech — scalabilité revendiquée (index 4) mais modèle revenu nul (index 0) → ANOM_SC_1",
        "secteur": "tech",
        "profil_complet": {
            "equipe":                "solo",
            "rne":                   False,
            "mvp_statut":            "dev",
            "mrr":                   "zero",
            "propriete_intellectuelle": False,
            "scalabilite":           "Oui, fortement scalable (SaaS, plateforme)",
            "business_plan":         "absent",
            "accompagnement":        "jamais",
            "financement":           "aucun",
        },
        "reponses": {
            "potentiel_financier_marche": {"index": 1, "valeur": "marche_local_faible"},
            "intensite_concurrence":      {"index": 1, "valeur": "marche_sature"},
            "niveau_traction":            {"index": 1, "valeur": "traction_initiale"},
            "modele_revenu":              {"index": 0, "valeur": "non_defini"},        # ← contradiction
            "business_plan_f2":           {"index": 0, "valeur": "absent"},
            "maturite_produit":           {"index": 1, "valeur": "prototype"},
            "strategie_prix":             {"index": 0, "valeur": "non_definie"},
            "alignement_besoins":         {"index": 1, "valeur": "hypothetique"},
            "nouveaute_locale":           {"index": 1, "valeur": "copie_amelioree"},
            "intensite_tech":             {"index": 2, "valeur": "tech_moderee"},
            "barrieres_entree":           {"index": 1, "valeur": "faibles_barrieres"},
            "degre_rupture":              {"index": 1, "valeur": "evolution_faible"},
            "replicabilite":              {"index": 4, "valeur": "deploiement_massif"}, # ← contradiction
            "independance_manuelle":      {"index": 1, "valeur": "semi_manuel"},
            "couts_deploiement":          {"index": 1, "valeur": "investissements_lourds"},
            "potentiel_geo":              {"index": 1, "valeur": "regional_tunisie"},
            "climat_air":                 {"index": 1, "valeur": "neutralite_passive"},
            "donnees_eau_fournies":       {"index": 1, "valeur": "aucune_gestion"},
            "sols_biodiversite":          {"index": 1, "valeur": "neutre"},
            "ressources_dechets":         {"index": 1, "valeur": "reduction_faible"},
        },
        "blockers": [
            {"domaine": "Juridique", "description": "Pas de RNE enregistré", "niveau": "rouge"},
        ],
        "anomalies_injectees": [
            {"id": "ANOM_SC_1", "penalty_points": 10, "target_score": "scalability"},
        ],
        "expected": {"fri_min": 0, "fri_max": 40, "is_financeable": False, "capped": True},
        "expected_anomaly_ids": ["ANOM_SC_1"],
    },

    # ══════════════════════════════════════════════════════════════════════
    # SECTEUR : INDUSTRIE (branche_industrie_construction)
    # ══════════════════════════════════════════════════════════════════════

    {
        "id": "P07",
        "description": "Industrie Sfax — équipements ok, ISO certifié, FOPRODI déposé → profil solide",
        "secteur": "industrie",
        "profil_complet": {
            "equipe":              "equipe_complete",
            "rne":                 True,
            "forme_juridique":     "SA",
            "equipements":         "operationnels",
            "certification_iso":   "certifie",
            "foprodi_apii":        True,
            "sous_traitance":      "Oui, contrats formels signés",
            "business_plan":       "complet",
            "accompagnement":      "programme_apii",
            "financement":         "credit_bancaire",
            "chiffre_affaires":    2500000.0,
            "anciennete_revenus":  "Plus de 3 ans",
        },
        "reponses": {
            "potentiel_financier_marche": {"index": 3, "valeur": "marche_regional_fort"},
            "intensite_concurrence":      {"index": 2, "valeur": "marche_oligopolistique"},
            "niveau_traction":            {"index": 3, "valeur": "traction_forte"},
            "modele_revenu":              {"index": 3, "valeur": "contrat_b2b"},
            "business_plan_f2":           {"index": 3, "valeur": "valide_complet"},
            "maturite_produit":           {"index": 3, "valeur": "produit_marche"},
            "strategie_prix":             {"index": 2, "valeur": "premium_justifie"},
            "alignement_besoins":         {"index": 3, "valeur": "besoin_urgent_valide"},
            "nouveaute_locale":           {"index": 2, "valeur": "amelioration_notable"},
            "intensite_tech":             {"index": 2, "valeur": "tech_moderee"},
            "barrieres_entree":           {"index": 3, "valeur": "barrieres_elevees"},
            "degre_rupture":              {"index": 2, "valeur": "evolution_incrementale"},
            "replicabilite":              {"index": 2, "valeur": "replicabilite_moderee"},
            "independance_manuelle":      {"index": 2, "valeur": "semi_automatise"},
            "couts_deploiement":          {"index": 2, "valeur": "investissement_modere"},
            "potentiel_geo":              {"index": 2, "valeur": "national"},
            "climat_air":                 {"index": 3, "valeur": "reduction_active"},
            "donnees_eau_fournies":       {"index": 2, "valeur": "suivi_partiel"},
            "sols_biodiversite":          {"index": 2, "valeur": "neutre"},
            "ressources_dechets":         {"index": 3, "valeur": "reduction_structuree"},
        },
        "blockers": [],
        "anomalies_injectees": [],
        "expected": {"fri_min": 55, "fri_max": 100, "is_financeable": True, "capped": False},
        "expected_anomaly_ids": [],
    },

    {
        "id": "P08",
        "description": "Industrie — équipements absents + aucun financement → blocker rouge + hard-cap probable",
        "secteur": "industrie",
        "profil_complet": {
            "equipe":              "solo",
            "rne":                 False,
            "equipements":         "absent",
            "certification_iso":   "absent",
            "foprodi_apii":        False,
            "sous_traitance":      "Non, clientèle directe uniquement",
            "business_plan":       "absent",
            "accompagnement":      "jamais",
            "financement":         "aucun",
            "chiffre_affaires":    0,
            "anciennete_revenus":  "Moins d'un an",
        },
        "reponses": {
            "potentiel_financier_marche": {"index": 0, "valeur": "marche_local_faible"},
            "intensite_concurrence":      {"index": 0, "valeur": "marche_partage"},
            "niveau_traction":            {"index": 0, "valeur": "aucune_traction"},
            "modele_revenu":              {"index": 0, "valeur": "non_defini"},
            "business_plan_f2":           {"index": 0, "valeur": "absent"},
            "maturite_produit":           {"index": 0, "valeur": "idee"},
            "strategie_prix":             {"index": 0, "valeur": "non_definie"},
            "alignement_besoins":         {"index": 0, "valeur": "hypothetique"},
            "nouveaute_locale":           {"index": 0, "valeur": "copie_existant"},
            "intensite_tech":             {"index": 0, "valeur": "aucune_tech"},
            "barrieres_entree":           {"index": 0, "valeur": "aucune_barriere"},
            "degre_rupture":              {"index": 0, "valeur": "aucune_rupture"},
            "replicabilite":              {"index": 0, "valeur": "non_replicable"},
            "independance_manuelle":      {"index": 0, "valeur": "totalement_manuel"},
            "couts_deploiement":          {"index": 0, "valeur": "capex_prohibitif"},
            "potentiel_geo":              {"index": 0, "valeur": "local_seulement"},
            "climat_air":                 {"index": 0, "valeur": "impact_negatif"},
            "donnees_eau_fournies":       {"index": 0, "valeur": "aucune_gestion"},
            "sols_biodiversite":          {"index": 0, "valeur": "degradation_passive"},
            "ressources_dechets":         {"index": 0, "valeur": "aucune_gestion"},
        },
        "blockers": [
            {"domaine": "Financier",   "description": "Besoin d'investissement équipements / matériel", "niveau": "rouge"},
            {"domaine": "Juridique",   "description": "Pas de RNE enregistré",                          "niveau": "rouge"},
        ],
        "anomalies_injectees": [],
        "expected": {"fri_min": 0, "fri_max": 40, "is_financeable": False, "capped": True},
        "expected_anomaly_ids": [],
    },

    # ══════════════════════════════════════════════════════════════════════
    # SECTEUR : COMMERCE (branche_commerce_transport_logistique)
    # ══════════════════════════════════════════════════════════════════════

    {
        "id": "P09",
        "description": "Commerce Tunis — réseau multi-canaux, e-commerce actif, stock géré → bancable",
        "secteur": "commerce",
        "profil_complet": {
            "equipe":               "equipe_complete",
            "rne":                  True,
            "forme_juridique":      "SARL",
            "reseau_distribution":  "Oui, réseau structuré multi-canaux",
            "capacite_logistique":  "Oui, parc propre opérationnel",
            "presence_digitale":    "Oui, e-commerce actif avec commandes",
            "gestion_stock":        "Oui, avec un système de gestion de stock",
            "business_plan":        "complet",
            "accompagnement":       "programme_apii",
            "financement":          "credit_bancaire",
            "chiffre_affaires":     450000.0,
            "anciennete_revenus":   "Plus de 3 ans",
        },
        "reponses": {
            "potentiel_financier_marche": {"index": 3, "valeur": "marche_regional_fort"},
            "intensite_concurrence":      {"index": 2, "valeur": "marche_fragmente"},
            "niveau_traction":            {"index": 3, "valeur": "traction_forte"},
            "modele_revenu":              {"index": 3, "valeur": "vente_directe_recurrente"},
            "business_plan_f2":           {"index": 3, "valeur": "valide_complet"},
            "maturite_produit":           {"index": 3, "valeur": "produit_marche"},
            "strategie_prix":             {"index": 3, "valeur": "premium_justifie"},
            "alignement_besoins":         {"index": 3, "valeur": "besoin_urgent_valide"},
            "nouveaute_locale":           {"index": 2, "valeur": "amelioration_notable"},
            "intensite_tech":             {"index": 2, "valeur": "tech_moderee"},
            "barrieres_entree":           {"index": 2, "valeur": "barrieres_moderees"},
            "degre_rupture":              {"index": 1, "valeur": "evolution_faible"},
            "replicabilite":              {"index": 3, "valeur": "replicabilite_elevee"},
            "independance_manuelle":      {"index": 2, "valeur": "semi_automatise"},
            "couts_deploiement":          {"index": 2, "valeur": "investissement_modere"},
            "potentiel_geo":              {"index": 2, "valeur": "national"},
            "climat_air":                 {"index": 2, "valeur": "neutralite_passive"},
            "donnees_eau_fournies":       {"index": 1, "valeur": "suivi_minimal"},
            "sols_biodiversite":          {"index": 1, "valeur": "neutre"},
            "ressources_dechets":         {"index": 2, "valeur": "reduction_a_la_source"},
        },
        "blockers": [],
        "anomalies_injectees": [],
        "expected": {"fri_min": 55, "fri_max": 100, "is_financeable": True, "capped": False},
        "expected_anomaly_ids": [],
    },

    # ══════════════════════════════════════════════════════════════════════
    # SECTEUR : SERVICES / TOURISME (branche_service_tourisme)
    # ══════════════════════════════════════════════════════════════════════

    {
        "id": "P10",
        "description": "Tourisme Djerba — classé, fidélisation, numérisé → profil solide",
        "secteur": "services",
        "profil_complet": {
            "equipe":               "equipe_complete",
            "rne":                  True,
            "classement_agree":     "obtenu",
            "fidelisation":         "Oui, base de données clients active et programme structuré",
            "numerisation_service": "Oui, plateforme de réservation / CRM opérationnel",
            "saisonnalite":         "Partiellement",
            "business_plan":        "complet",
            "accompagnement":       "incubateur",
            "financement":          "love_money",
            "chiffre_affaires":     320000.0,
            "anciennete_revenus":   "Entre 1 et 3 ans",
        },
        "reponses": {
            "potentiel_financier_marche": {"index": 3, "valeur": "marche_regional_fort"},
            "intensite_concurrence":      {"index": 2, "valeur": "marche_oligopolistique"},
            "niveau_traction":            {"index": 3, "valeur": "traction_forte"},
            "modele_revenu":              {"index": 3, "valeur": "abonnement_recurrent"},
            "business_plan_f2":           {"index": 3, "valeur": "valide_complet"},
            "maturite_produit":           {"index": 3, "valeur": "produit_marche"},
            "strategie_prix":             {"index": 2, "valeur": "premium_justifie"},
            "alignement_besoins":         {"index": 3, "valeur": "besoin_urgent_valide"},
            "nouveaute_locale":           {"index": 2, "valeur": "amelioration_notable"},
            "intensite_tech":             {"index": 2, "valeur": "tech_moderee"},
            "barrieres_entree":           {"index": 2, "valeur": "barrieres_moderees"},
            "degre_rupture":              {"index": 1, "valeur": "evolution_faible"},
            "replicabilite":              {"index": 2, "valeur": "replicabilite_moderee"},
            "independance_manuelle":      {"index": 2, "valeur": "semi_automatise"},
            "couts_deploiement":          {"index": 2, "valeur": "investissement_modere"},
            "potentiel_geo":              {"index": 2, "valeur": "national"},
            "climat_air":                 {"index": 2, "valeur": "neutralite_passive"},
            "donnees_eau_fournies":       {"index": 2, "valeur": "suivi_partiel"},
            "sols_biodiversite":          {"index": 2, "valeur": "neutre"},
            "ressources_dechets":         {"index": 2, "valeur": "reduction_a_la_source"},
        },
        "blockers": [],
        "anomalies_injectees": [],
        "expected": {"fri_min": 55, "fri_max": 100, "is_financeable": True, "capped": False},
        "expected_anomaly_ids": [],
    },

    # ══════════════════════════════════════════════════════════════════════
    # TESTS DE COHÉRENCE ORDINALE (monotonie)
    # ══════════════════════════════════════════════════════════════════════

    {
        "id": "P11",
        "description": "Consistency REF — Tech standard tous index 2 (score 60) → FRI de référence",
        "secteur": "tech",
        "profil_complet": {
            "equipe": "duo_fondateurs", "rne": True, "mvp_statut": "beta",
            "mrr": "faible", "business_plan": "en_cours",
        },
        "reponses": {k: {"index": 2, "valeur": "moyen"} for k in [
            "potentiel_financier_marche","intensite_concurrence","niveau_traction","modele_revenu",
            "business_plan_f2","maturite_produit","strategie_prix","alignement_besoins",
            "nouveaute_locale","intensite_tech","barrieres_entree","degre_rupture",
            "replicabilite","independance_manuelle","couts_deploiement","potentiel_geo",
            "climat_air","donnees_eau_fournies","sols_biodiversite","ressources_dechets",
        ]},
        "blockers": [],
        "anomalies_injectees": [],
        "expected": {"fri_min": 45, "fri_max": 75, "is_financeable": None, "capped": False},
        "expected_anomaly_ids": [],
        "_consistency_role": "ref",
    },

    {
        "id": "P12",
        "description": "Consistency HAUT — même profil que P11 mais tous index 3 → FRI >= FRI(P11)",
        "secteur": "tech",
        "profil_complet": {
            "equipe": "duo_fondateurs", "rne": True, "mvp_statut": "beta",
            "mrr": "faible", "business_plan": "en_cours",
        },
        "reponses": {k: {"index": 3, "valeur": "bon"} for k in [
            "potentiel_financier_marche","intensite_concurrence","niveau_traction","modele_revenu",
            "business_plan_f2","maturite_produit","strategie_prix","alignement_besoins",
            "nouveaute_locale","intensite_tech","barrieres_entree","degre_rupture",
            "replicabilite","independance_manuelle","couts_deploiement","potentiel_geo",
            "climat_air","donnees_eau_fournies","sols_biodiversite","ressources_dechets",
        ]},
        "blockers": [],
        "anomalies_injectees": [],
        "expected": {"fri_min": 60, "fri_max": 100, "is_financeable": None, "capped": False},
        "expected_anomaly_ids": [],
        "_consistency_role": "haut",
    },

    {
        "id": "P13",
        "description": "Consistency BAS — même profil que P11 mais tous index 1 → FRI <= FRI(P11)",
        "secteur": "tech",
        "profil_complet": {
            "equipe": "duo_fondateurs", "rne": True, "mvp_statut": "beta",
            "mrr": "faible", "business_plan": "en_cours",
        },
        "reponses": {k: {"index": 1, "valeur": "faible"} for k in [
            "potentiel_financier_marche","intensite_concurrence","niveau_traction","modele_revenu",
            "business_plan_f2","maturite_produit","strategie_prix","alignement_besoins",
            "nouveaute_locale","intensite_tech","barrieres_entree","degre_rupture",
            "replicabilite","independance_manuelle","couts_deploiement","potentiel_geo",
            "climat_air","donnees_eau_fournies","sols_biodiversite","ressources_dechets",
        ]},
        "blockers": [],
        "anomalies_injectees": [],
        "expected": {"fri_min": 0, "fri_max": 55, "is_financeable": None, "capped": False},
        "expected_anomaly_ids": [],
        "_consistency_role": "bas",
    },

    # ══════════════════════════════════════════════════════════════════════
    # TEST FRONTIÈRE BANCABILITÉ
    # ══════════════════════════════════════════════════════════════════════

    {
        "id": "P14",
        "description": "Frontière bancabilité — profil mixte index 1-2 avec 1 blocker orange → ~55",
        "secteur": "services",
        "profil_complet": {
            "equipe": "duo_fondateurs", "rne": True,
            "classement_agree": "en_cours", "business_plan": "en_cours",
            "accompagnement": "jamais", "financement": "aucun",
        },
        "reponses": {
            "potentiel_financier_marche": {"index": 2, "valeur": "national"},
            "intensite_concurrence":      {"index": 1, "valeur": "marche_sature"},
            "niveau_traction":            {"index": 2, "valeur": "traction_initiale"},
            "modele_revenu":              {"index": 2, "valeur": "commission"},
            "business_plan_f2":           {"index": 2, "valeur": "en_cours"},
            "maturite_produit":           {"index": 1, "valeur": "mvp"},
            "strategie_prix":             {"index": 2, "valeur": "alignement_marche"},
            "alignement_besoins":         {"index": 2, "valeur": "besoin_confirme"},
            "nouveaute_locale":           {"index": 2, "valeur": "amelioration"},
            "intensite_tech":             {"index": 1, "valeur": "faible"},
            "barrieres_entree":           {"index": 2, "valeur": "moderees"},
            "degre_rupture":              {"index": 1, "valeur": "faible"},
            "replicabilite":              {"index": 2, "valeur": "moderee"},
            "independance_manuelle":      {"index": 2, "valeur": "semi"},
            "couts_deploiement":          {"index": 1, "valeur": "lourds"},
            "potentiel_geo":              {"index": 2, "valeur": "national"},
            "climat_air":                 {"index": 2, "valeur": "neutre"},
            "donnees_eau_fournies":       {"index": 1, "valeur": "minimal"},
            "sols_biodiversite":          {"index": 2, "valeur": "neutre"},
            "ressources_dechets":         {"index": 2, "valeur": "reduction"},
        },
        "blockers": [
            {"domaine": "Commercial", "description": "Absence de stratégie de fidélisation client", "niveau": "orange"},
        ],
        "anomalies_injectees": [],
        "expected": {"fri_min": 30, "fri_max": 70, "is_financeable": None, "capped": False},
        "expected_anomaly_ids": [],
    },
]


# =========================================================================
# MOTEUR D'ÉVALUATION
# =========================================================================

def run_evaluation(test_set):
    results = []
    fri_by_id = {}

    print("\n" + "="*70)
    print("  PROTOCOLE D'ÉVALUATION F2 v2 — AINS Hackathon 2026")
    print("  Format : input réel (profil_complet + reponses F2 par secteur)")
    print("="*70)

    for profil in test_set:
        pid  = profil["id"]
        desc = profil["description"]

        # 1. Conversion reponses → sub_scores (comme extract_sub_scores.py)
        sub_scores = reponses_to_sub_scores(profil["reponses"])

        # 2. Appel moteur
        output = calculer_scores(
            sub_scores=sub_scores,
            anomalies=profil["anomalies_injectees"],
            blockers=profil["blockers"],
            secteur=profil["secteur"],
            profil_complet=profil["profil_complet"],
            reponses_f2=profil["reponses"],
        )

        fri    = output["financing_readiness_index"]
        is_fin = output["is_financeable"]
        capped = output.get("_capped", False)
        detected_ids = {a["id"] for a in output.get("anomalies_detectees", [])}
        fri_by_id[pid] = fri

        exp    = profil["expected"]
        checks = {}

        checks["fri_range"] = exp["fri_min"] <= fri <= exp["fri_max"]

        if exp["is_financeable"] is not None:
            checks["is_financeable"] = (is_fin == exp["is_financeable"])
        else:
            checks["is_financeable"] = None

        checks["hard_cap"] = (fri <= 40) if exp["capped"] else True

        exp_anoms = set(profil.get("expected_anomaly_ids", []))
        if exp_anoms:
            checks["anomaly_detection"] = exp_anoms.issubset(detected_ids)
            checks["anomaly_detail"] = {
                "expected": list(exp_anoms),
                "detected": list(detected_ids),
                "missing":  list(exp_anoms - detected_ids),
            }
        else:
            checks["anomaly_detection"] = None

        binary = [v for v in checks.values() if isinstance(v, bool)]
        passed = all(binary)

        status = "✅ PASS" if passed else "❌ FAIL"
        print(f"\n[{pid}] {status} — {desc}")
        sub_mkt = sub_scores.get("MS1",0)*0.1205 + sub_scores.get("MS2",0)*0.4542 + \
                  sub_scores.get("MS3",0)*0.1826 + sub_scores.get("MS4",0)*0.2427
        print(f"       Market AHP={sub_mkt:.1f} | FRI={fri}/100 | bancable={is_fin} | cap={capped}")
        print(f"       Plage : [{exp['fri_min']}, {exp['fri_max']}]")
        if not checks["fri_range"]:
            print(f"       ⚠ FRI hors plage!")
        if exp_anoms and not checks.get("anomaly_detection"):
            print(f"       ⚠ Anomalies manquantes : {checks.get('anomaly_detail',{}).get('missing')}")

        results.append({
            "profil_id": pid,
            "description": desc,
            "secteur": profil["secteur"],
            "sub_scores_calcules": sub_scores,
            "fri_obtenu": fri,
            "fri_attendu": f"[{exp['fri_min']}, {exp['fri_max']}]",
            "is_financeable": is_fin,
            "capped": capped,
            "checks": checks,
            "passed": passed,
        })

    # ── Consistency ordinale P11 (ref) / P12 (haut) / P13 (bas) ────────
    fri_ref  = fri_by_id.get("P11", 0)
    fri_haut = fri_by_id.get("P12", 0)
    fri_bas  = fri_by_id.get("P13", 0)
    consistency_ok = (fri_haut >= fri_ref) and (fri_bas <= fri_ref)

    # ── Métriques ────────────────────────────────────────────────────────
    anom_checks = [r["checks"].get("anomaly_detection") for r in results
                   if r["checks"].get("anomaly_detection") is not None]
    anomaly_rate = (sum(anom_checks) / len(anom_checks) * 100) if anom_checks else 0.0
    cap_rate     = sum(r["checks"]["hard_cap"] for r in results) / len(results) * 100
    overall      = sum(r["passed"] for r in results) / len(results) * 100

    summary = {
        "date": datetime.now().isoformat(),
        "nb_profils": len(test_set),
        "secteurs_couverts": ["Agriculture", "Tech/Digital", "Industrie", "Commerce", "Services"],
        "metrics": {
            "overall_pass_rate":        round(overall, 1),
            "score_consistency":        consistency_ok,
            "anomaly_detection_rate":   round(anomaly_rate, 1),
            "hard_cap_compliance_rate": round(cap_rate, 1),
            "fri_bas_P13": fri_bas, "fri_ref_P11": fri_ref, "fri_haut_P12": fri_haut,
        },
        "results": results,
    }

    print("\n" + "="*70)
    print("  RÉSUMÉ DES MÉTRIQUES")
    print("="*70)
    print(f"  Taux réussite global       : {overall:.1f}%  ({sum(r['passed'] for r in results)}/{len(results)})")
    print(f"  Cohérence ordinale (P13≤P11≤P12) : {'✅ OUI' if consistency_ok else '❌ NON'}")
    print(f"     FRI P13(bas)={fri_bas} | P11(ref)={fri_ref} | P12(haut)={fri_haut}")
    print(f"  Détection anomalies        : {anomaly_rate:.1f}%")
    print(f"  Conformité hard-cap        : {cap_rate:.1f}%")
    print("="*70 + "\n")

    return summary


if __name__ == "__main__":
    rapport = run_evaluation(TEST_SET)
    path = "eval_report_f2_v2.json"
    with open(path, "w", encoding="utf-8") as f:
        json.dump(rapport, f, indent=2, ensure_ascii=False)
    print(f"Rapport sauvegardé : {path}")