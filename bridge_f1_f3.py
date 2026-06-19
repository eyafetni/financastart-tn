"""
============================================================
bridge_f1_f3.py — Pont FINAL F1 + F2 → RAG F3
AINS Hackathon 2026 — Version finale complète
============================================================

FLUX COMPLET:
    diagnostic_engine.py (F1) → diagnostic_ENT-XXX.json
    scoring_engine.py    (F2) → contrat_f2_output.json
                ↓
    bridge_f1_f3.py  (CE FICHIER)
        ↓
    search_kb_no_api.py (RAG F3)
        ↓
    Dashboard Membre 5

USAGE SIMPLE:
    from bridge_f1_f3 import pipeline_complet
    
    # Avec fichiers JSON
    output = pipeline_complet(
        f1_input="diagnostic_ENT-DBD323.json",
        f2_input="contrat_f2_output.json"
    )
    
    # Avec dicts en mémoire
    output = pipeline_complet(f1_input=diag_dict, f2_input=scores_dict)
    
    # Sans F2 (bridge calcule les scores depuis les réponses F1)
    output = pipeline_complet(f1_input="diagnostic_ENT-DBD323.json")
============================================================
"""

import json
from search_kb_no_api import contrat_f3


# ════════════════════════════════════════════════════════════════
# 1. MAPPINGS
# ════════════════════════════════════════════════════════════════

SECTEUR_MAP = {
    # Codes F1 (snake_case)
    "agriculture_sylviculture_peche":  "Agriculture/Sylviculture/Peche",
    "industrie_construction":          "Industrie/Construction",
    "commerce_transport_logistique":   "Commerce/Transport/Logistique",
    "service_tourisme":                "Service/Tourisme",
    "technologie_service_entreprise":  "Technologie/Service-Entreprise",
    # Codes F2 (label court)
    "agriculture":      "Agriculture/Sylviculture/Peche",
    "agri-food":        "Agriculture/Sylviculture/Peche",
    "agri":             "Agriculture/Sylviculture/Peche",
    "agritech":         "Agriculture/Sylviculture/Peche",
    "peche":            "Agriculture/Sylviculture/Peche",
    "sylviculture":     "Agriculture/Sylviculture/Peche",
    "tech_digital":     "Technologie/Service-Entreprise",
    "tech":             "Technologie/Service-Entreprise",
    "digital":          "Technologie/Service-Entreprise",
    "numerique":        "Technologie/Service-Entreprise",
    "fintech":          "Technologie/Service-Entreprise",
    "healthtech":       "Technologie/Service-Entreprise",
    "edtech":           "Technologie/Service-Entreprise",
    "saas":             "Technologie/Service-Entreprise",
    "industrie":        "Industrie/Construction",
    "construction":     "Industrie/Construction",
    "btp":              "Industrie/Construction",
    "manufacturing":    "Industrie/Construction",
    "commerce":         "Commerce/Transport/Logistique",
    "transport":        "Commerce/Transport/Logistique",
    "logistique":       "Commerce/Transport/Logistique",
    "distribution":     "Commerce/Transport/Logistique",
    "artisanat":        "Commerce/Transport/Logistique",
    "services":         "Service/Tourisme",
    "tourisme":         "Service/Tourisme",
    "hotellerie":       "Service/Tourisme",
    "restauration":     "Service/Tourisme",
    "gite":             "Service/Tourisme",
}

SECTEURS_RAG_VALIDES = [
    "Agriculture/Sylviculture/Peche",
    "Industrie/Construction",
    "Commerce/Transport/Logistique",
    "Service/Tourisme",
    "Technologie/Service-Entreprise"
]

REGIONS_INTERIEURES = [
    "siliana","kasserine","kairouan","sidi bouzid","gafsa",
    "tozeur","kebili","tataouine","medenine","jendouba","le kef","zaghouan"
]

# F2 blocker domaine → code gap RAG
BLOCKER_F2_TO_GAP = {
    "organisationnel": "equipe_incomplete",
    "réglementaire":   "certification_manquante",
    "reglementaire":   "certification_manquante",
    "légal":           "absence_structure_juridique",
    "legal":           "absence_structure_juridique",
    "financier":       "absence_business_plan",
    "marché":          "absence_validation_marche",
    "marche":          "absence_validation_marche",
    "technique":       "besoin_prototype",
}

# F2 anomalie ID → codes gap RAG + priorité
ANOMALIE_TO_GAPS = {
    "ANOM_FRAUD_CA_NO_RNE":      ["absence_structure_juridique", "activite_informelle", "urgence_rne"],
    "ANOM_NO_RNE":               ["absence_structure_juridique", "urgence_rne"],
    "ANOM_NO_BP":                ["absence_business_plan"],
    "ANOM_NO_TRACTION":          ["absence_validation_marche"],
    "ANOM_SOLO_FOUNDER":         ["equipe_incomplete"],
    "ANOM_NO_CERTIF":            ["certification_manquante"],
    "ANOM_INNOVATION_LOW":       ["innovation_score_faible"],
    "ANOM_SCALABILITY_LOW":      ["scalabilite_faible"],
}

# F1 gaps texte libre → codes RAG
GAP_KEYWORDS = {
    "rne":                       "absence_structure_juridique",
    "enregistr":                 "absence_structure_juridique",
    "juridique":                 "absence_structure_juridique",
    "business plan":             "absence_business_plan",
    "équipe":                    "equipe_incomplete",
    "fondateur seul":            "equipe_incomplete",
    "solo":                      "equipe_incomplete",
    "certif":                    "certification_manquante",
    "sanitaire":                 "certification_manquante",
    "phytosanitaire":            "certification_manquante",
    "haccp":                     "certification_manquante",
    "chaîne de froid":           "chaine_froid_absente",
    "froid":                     "chaine_froid_absente",
    "client payant":             "absence_validation_marche",
    "traction":                  "absence_validation_marche",
    "proches":                   "absence_validation_marche",
    "entourage":                 "absence_validation_marche",
    "apport":                    "manque_apport_personnel",
    "garantie":                  "manque_garanties",
    "mvp":                       "besoin_prototype",
    "prototype":                 "besoin_prototype",
    "innov":                     "innovation_score_faible",
    "différenciation":           "innovation_score_faible",
    "identique":                 "innovation_score_faible",
    "existant sur le marché":    "innovation_score_faible",
    "propriété intellectuelle":  "innovation_score_faible",
    "jeune":                     "jeune_diplome",
    "diplômé":                   "jeune_diplome",
    "export":                    "export",
    "faible revenu":             "faible_revenu",
    "micro":                     "micro_projet",
}

MONTANT_PAR_STADE = {
    "Ideation":          5000,
    "Market Validation": 30000,
    "Structuration":     150000,
    "Fundraising":       300000,
    "Launch Planning":   500000,
    "Growth":            1000000,
}

# Scores F2 depuis réponses questionnaire F1
SCORES_PAR_VALEUR = {
    "type_cible":                  {"B2C":45,"B2B_SME":55,"B2B_Enterprise":65,"B2B2C":50,"B2G":55},
    "potentiel_financier_marche":  {"niche_ultra_locale":15,"marche_local_limite":30,"marche_national_intermediaire":55,"marche_regional_scalable":75,"marche_global_massif":90},
    "intensite_concurrence":       {"hyper_competition":15,"forte_concurrence":30,"marche_partage":50,"faible_concurrence":65,"ocean_bleu":85},
    "niveau_traction":             {"ideation_pure":5,"premiers_testeurs":25,"traction_initiale":45,"traction_significative":70,"croissance_organique":90},
    "modele_revenu":               {"non_defini":5,"transactionnel_standard":35,"commission_marketplace":50,"abonnement_saas":70,"multi_stream_optimise":85},
    "business_plan_f2":            {"inexistant":5,"en_cours_de_redaction":20,"en_cours_de_validation":40,"valide_interne":60,"valide_externe":80},
    "maturite_produit":            {"idee_brute":5,"maquette_prototype":20,"mvp_valide":55,"produit_stable":75,"produit_mature":90},
    "strategie_prix":              {"aucune":5,"intuitive":20,"alignement_concurrence":45,"valeur_percue":65,"optimisee_dynamique":85},
    "alignement_besoins":          {"non_identifie":5,"suppose_non_valide":20,"important_non_urgent":40,"urgent_important":70,"douleur_critique":90},
    "nouveaute_locale":            {"copie_exacte":5,"amelioration_marginale":20,"adaptation_locale":35,"innovation_incrementale":60,"rupture_totale":90},
    "intensite_tech":              {"aucune_tech":5,"outils_bureautiques":20,"integration_avancee":55,"tech_proprietaire":75,"ia_deeptech":90},
    "barrieres_entree":            {"aucune":5,"marque_reputation":30,"moat_commercial":50,"ip_brevet":75,"reseau_ecosysteme":85},
    "degre_rupture":               {"copie_conforme":5,"amelioration_incrementale":20,"transformation_process":45,"nouveau_segment":65,"creation_marche":90},
    "replicabilite":               {"artisanal_irreplicable":5,"croissance_lineaire_lente":20,"deploiement_operationnel_modere":45,"scalable_structurel":70,"hyperscalable":90},
    "independance_manuelle":       {"100_manuel":5,"forte_dependance":20,"paliers_de_croissance":50,"automatise_partiellement":70,"full_auto":90},
    "couts_deploiement":           {"tres_eleve":10,"modere_eleve":25,"besoin_modere":50,"faible":70,"marginal":90},
    "potentiel_geo":               {"hyper_local":5,"regional":25,"national":50,"continental_mena":75,"global_born_global":90},
    "climat_air":                  {"impact_negatif_lourd":5,"impact_negatif_modere":25,"neutralite_passive":40,"impact_positif_mesurable":70,"impact_regeneratif":90},
    "donnees_eau_fournies":        {"aucune_mesure":5,"estimation_theorique":20,"suivi_manuel_partiel":35,"suivi_digital_temps_reel":70,"optimisation_ia_predictive":90},
    "sols_biodiversite":           {"degradation_active":5,"non_evalue":20,"preservation_passive":35,"impact_positif_certifie":70,"regeneratif_ecosysteme":90},
    "ressources_dechets":          {"economie_lineaire_lourde":5,"gestion_dechets_standard":25,"reduction_a_la_source":50,"revalorisation_upcycling":70,"circularite_totale":90},
}

DIMENSIONS_SCORES = {
    "market":           ["type_cible","potentiel_financier_marche","intensite_concurrence","niveau_traction","modele_revenu"],
    "commercial_offer": ["business_plan_f2","maturite_produit","strategie_prix","alignement_besoins"],
    "innovation":       ["nouveaute_locale","intensite_tech","barrieres_entree","degre_rupture"],
    "scalability":      ["replicabilite","independance_manuelle","couts_deploiement","potentiel_geo"],
    "green":            ["climat_air","donnees_eau_fournies","sols_biodiversite","ressources_dechets"],
}


# ════════════════════════════════════════════════════════════════
# 2. PARSEURS F1 ET F2
# ════════════════════════════════════════════════════════════════

def parser_f1(f1_input) -> dict:
    """Charge et normalise l'output F1 (diagnostic_engine)."""
    if isinstance(f1_input, str):
        with open(f1_input, encoding="utf-8") as f:
            return json.load(f)
    return f1_input


def parser_f2(f2_input) -> dict:
    """Charge et normalise l'output F2 (scoring_engine)."""
    if f2_input is None:
        return None
    if isinstance(f2_input, str):
        with open(f2_input, encoding="utf-8") as f:
            return json.load(f)
    return f2_input


# ════════════════════════════════════════════════════════════════
# 3. EXTRACTEURS DE SCORES
# ════════════════════════════════════════════════════════════════

def extraire_scores_f2(f2: dict) -> dict:
    """
    Extrait les 5 scores depuis l'output F2.
    Format F2: scores.market_score.valeur, scores.commercial_offer_score.valeur ...
    Format F3: {"market": 60, "commercial_offer": 60, ...}
    """
    s = f2.get("scores", {})
    return {
        "market":           s.get("market_score",           {}).get("valeur", 40),
        "commercial_offer": s.get("commercial_offer_score", {}).get("valeur", 40),
        "innovation":       s.get("innovation_score",       {}).get("valeur", 40),
        "scalability":      s.get("scalability_score",      {}).get("valeur", 40),
        "green":            s.get("green_score",            {}).get("valeur", 40),
    }


def calculer_scores_depuis_reponses(reponses: dict) -> dict:
    """Calcule les scores F2 depuis les réponses questionnaire F1 (fallback si pas de F2)."""
    scores = {}
    for dim, questions in DIMENSIONS_SCORES.items():
        vals = []
        for q in questions:
            if q in reponses:
                v = reponses[q].get("valeur", "")
                vals.append(SCORES_PAR_VALEUR.get(q, {}).get(v, 40))
        scores[dim] = round(sum(vals)/len(vals)) if vals else 40
    return scores


# ════════════════════════════════════════════════════════════════
# 4. EXTRACTEURS DE GAPS
# ════════════════════════════════════════════════════════════════

def gaps_depuis_f1(gaps_texte: list, blockers_f1: list, financement_hint: str) -> set:
    """Traduit les gaps F1 texte libre → codes RAG."""
    codes = set()
    for gap in gaps_texte:
        g = gap.lower()
        for kw, code in GAP_KEYWORDS.items():
            if kw in g:
                codes.add(code)
    for b in blockers_f1:
        d = b.get("domaine","").lower()
        for dom, code in BLOCKER_F2_TO_GAP.items():
            if dom in d:
                codes.add(code)
    FINANCEMENT_HINTS = {
        "Love money / Concours":       ["micro_projet","absence_validation_marche"],
        "Microfinance / BTS":          ["faible_revenu","manque_garanties","absence_business_plan"],
        "APII / ANPE":                 ["structuration_incomplete","absence_structure_juridique"],
        "BFPME / Startup Act":         ["besoin_financement_long_terme"],
        "Capital risque / ANAVA":      ["besoin_capital_investissement"],
        "Lignes bancaires / AFD / EU": ["besoin_capital_croissance"],
    }
    for fin, gap_codes in FINANCEMENT_HINTS.items():
        if fin in financement_hint:
            codes.update(gap_codes)
    return codes


def gaps_depuis_f2(blockers_f2: list, anomalies: list, fri: int, is_financeable: bool) -> set:
    """
    Extrait les gaps depuis l'output F2.
    - blockers_actifs.domaine → codes RAG
    - anomalies_detectees.id  → codes RAG prioritaires
    - fri < 30 et is_financeable=False → forcer ressources accompagnement
    """
    codes = set()

    # Blockers F2
    for b in blockers_f2:
        d = b.get("domaine","").lower()
        for dom, code in BLOCKER_F2_TO_GAP.items():
            if dom in d:
                codes.add(code)

    # Anomalies F2 (gaps critiques)
    for a in anomalies:
        aid = a.get("id","")
        for pattern, gap_codes in ANOMALIE_TO_GAPS.items():
            if pattern in aid:
                codes.update(gap_codes)

    # FRI très bas → ajouter gaps prioritaires
    if fri is not None and fri < 30:
        codes.update(["structuration_incomplete","absence_business_plan","besoin_accompagnement"])
    if is_financeable is False:
        codes.update(["non_bancable","besoin_structuration_avant_financement"])

    return codes


def gaps_depuis_profil(profil: dict, localisation: str) -> set:
    """Enrichit les gaps depuis le profil_complet F1."""
    codes = set()
    if profil.get("rne") is False:
        codes.add("absence_structure_juridique")
    if profil.get("business_plan") == "absent":
        codes.add("absence_business_plan")
    if profil.get("certifications_sanitaires") is False:
        codes.add("certification_manquante")
    if profil.get("chaine_froid") is False:
        codes.add("chaine_froid_absente")
    if profil.get("equipe") == "solo":
        codes.add("equipe_incomplete")
    if profil.get("financement") == "aucun":
        codes.add("absence_financement")
    if profil.get("accompagnement") == "jamais":
        codes.add("besoin_accompagnement")
    if profil.get("innovation_niveau") == "tres_faible":
        codes.add("innovation_score_faible")
    if profil.get("saisonnalite") == "Oui, fortement saisonnière":
        codes.add("saisonnalite_forte")
    if localisation and localisation.lower() in REGIONS_INTERIEURES:
        codes.add("regions_interieures")
    return codes


# ════════════════════════════════════════════════════════════════
# 5. TRADUCTEUR SECTEUR
# ════════════════════════════════════════════════════════════════

def traduire_secteur(raw: str) -> str:
    if not raw:
        return "Technologie/Service-Entreprise"
    if raw in SECTEURS_RAG_VALIDES:
        return raw
    cle = raw.lower().replace("-","_").replace(" ","_").replace("/","_")
    if cle in SECTEUR_MAP:
        return SECTEUR_MAP[cle]
    for kw, val in SECTEUR_MAP.items():
        if kw in raw.lower():
            return val
    return "Technologie/Service-Entreprise"


# ════════════════════════════════════════════════════════════════
# 6. GÉNÉRATEUR ROADMAP ENRICHI
# ════════════════════════════════════════════════════════════════

def generer_roadmap_enrichie(stade: str, secteur_rag: str, secteur_label: str,
                              gaps: list, fri: int, anomalies: list,
                              scores: dict, actions_f2: list) -> dict:
    """
    Roadmap personnalisée qui intègre:
    - Actions génériques par stade
    - Action sectorielle spécifique (en tête)
    - Actions correctives des anomalies F2 (urgentes en rouge)
    - Actions des scores F2 les plus faibles
    """

    # Actions génériques par stade
    ACTIONS_STADE = {
        "Ideation": {
            "immediat":    ["Contacter Espaces Entreprendre APII (gratuit)","Déposer dossier ANETI/PAPPE (programme indemnisé)","Formaliser l'idée en 2 pages écrites"],
            "court_terme": ["Réaliser étude de marché (10+ interviews clients)","Tester prototype ou service minimal","Décider forme juridique (SUARL recommandée)"],
            "moyen_terme": ["Rédiger business plan complet","Inscrire au RNE","Postuler BTS micro-crédit si besoin"]
        },
        "Market Validation": {
            "immediat":    ["Construire MVP testable","Documenter preuves de traction (clients payants, LOIs)","Postuler Flat6Labs prochaine cohorte"],
            "court_terme": ["Pitcher 5+ clients potentiels réels","Valider modèle économique chiffré","Déposer candidature Startup Act si innovant"],
            "moyen_terme": ["Contacter Carthage Business Angels","Préparer pitch deck investisseurs","Viser premier chiffre d'affaires réel"]
        },
        "Structuration": {
            "immediat":    ["Créer société au RNE si pas encore fait","Constituer dossier BFPME (business plan modèle GIZ)","Évaluer apport personnel disponible + SOTUGAR"],
            "court_terme": ["Déposer dossier FOPRODI APII pour prime investissement","Vérifier éligibilité garantie SOTUGAR","Finaliser plan cofinancement avec banque partenaire"],
            "moyen_terme": ["Obtenir accord BFPME","Recruter équipe clé","Mettre en place comptabilité formelle"]
        },
        "Fundraising": {
            "immediat":    ["Préparer data room complète (KPIs, états financiers)","Contacter Carthage Business Angels","Vérifier éligibilité label Startup Act"],
            "court_terme": ["Pitcher minimum 3 investisseurs","Déposer dossier Smart Capital / ANAVA","Négocier term sheet avec conseil juridique"],
            "moyen_terme": ["Clôturer tour de table","Déployer fonds selon plan d'affaires","Préparer reporting investisseurs trimestriel"]
        },
        "Launch Planning": {
            "immediat":    ["Finaliser plan de lancement (date, budget marketing)","Constituer dossier BFR si trésorerie tendue","Activer CEPEX si dimension export prévue"],
            "court_terme": ["Lancer activité commerciale","Installer ERP/CRM via Digital Tunisia","Premier bilan mensuel d'activité"],
            "moyen_terme": ["Atteindre seuil de rentabilité","Préparer extension si croissance confirmée","Dossier BFPME extension"]
        },
        "Growth": {
            "immediat":    ["Analyser goulots d'étranglement croissance","Évaluer besoins financement extension","Contacter APII programme mise à niveau PMN"],
            "court_terme": ["Dossier BFPME prêt extension ou BFR","Activer FOPRODEX si export","Étudier levée Series A (AfricInvest, ANAVA)"],
            "moyen_terme": ["Déployer sur nouveau marché géographique","Structurer management intermédiaire","Préparer exit ou prochain tour"]
        }
    }

    # Action sectorielle spécifique
    ACTIONS_SECTEUR = {
        "Agriculture/Sylviculture/Peche":  "Contacter APIA (primes agricoles) + BNA (crédit campagne) + ODESYPANO si Nord-Ouest",
        "Industrie/Construction":          "Déposer dossier FOPRODI APII pour prime 10% équipements industriels",
        "Commerce/Transport/Logistique":   "Contacter CEPEX si export + TRADE-001 pour financement commerce international",
        "Service/Tourisme":                "Vérifier exception BFPME gîtes ruraux + ONTT pour label qualité touristique",
        "Technologie/Service-Entreprise":  "Postuler Startup Act label (exonérations 8 ans) + Smart Capital pour financement innovant",
    }

    base = ACTIONS_STADE.get(stade, ACTIONS_STADE["Structuration"])
    immediat    = base["immediat"].copy()
    court_terme = base["court_terme"].copy()
    moyen_terme = base["moyen_terme"].copy()

    # 1. Action sectorielle en tête (priorité absolue)
    if secteur_rag in ACTIONS_SECTEUR:
        immediat.insert(0, f"[{secteur_label}] {ACTIONS_SECTEUR[secteur_rag]}")

    # 2. Actions correctives anomalies F2 (avant tout financement)
    for a in anomalies:
        action = a.get("action_template","")
        if action and action not in immediat:
            immediat.insert(1, f"🚨 URGENT — {action}")

    # 3. FRI très bas → avertissement
    if fri is not None and fri < 30:
        immediat.append(
            f"⚠️ FRI={fri}/100 — Votre projet n'est pas encore bancable. "
            f"Priorité: structuration et accompagnement avant tout dépôt de dossier financement."
        )

    # 4. Actions F2 sur scores faibles
    for action_f2 in actions_f2:
        if action_f2 and action_f2 not in court_terme:
            court_terme.append(f"[Score F2] {action_f2}")

    return {
        "stade":             stade,
        "secteur":           secteur_label,
        "fri":               fri,
        "immediat_0_30j":    immediat,
        "court_terme_1_3m":  court_terme,
        "moyen_terme_3_12m": moyen_terme,
    }


# ════════════════════════════════════════════════════════════════
# 7. PIPELINE PRINCIPAL F1 + F2 → F3
# ════════════════════════════════════════════════════════════════

def pipeline_complet(f1_input, f2_input=None) -> dict:
    """
    Pipeline complet F1 + F2 → RAG F3.

    Args:
        f1_input  : fichier JSON F1 (str) OU dict diagnostic_engine output
        f2_input  : fichier JSON F2 (str) OU dict scoring_engine output (optionnel)
                    Si None → les scores sont calculés depuis les réponses F1

    Returns:
        dict complet pour dashboard Membre 5:
        {
            entrepreneur_id, nom_entreprise, localisation, secteur_label,
            stade_reel, stade_percu, score_diagnostic, fri, is_financeable,
            divergence_detectee, message_perception_gap, signaux_divergence,
            scores_f2, ressources_recommandees, roadmap, sources_tracees,
            anomalies_f2, blockers_combines,
            diagnostic_f1 (raw), scoring_f2 (raw), bridge_log
        }
    """

    # ── Charger F1 ───────────────────────────────────────────────
    f1  = parser_f1(f1_input)
    f2  = parser_f2(f2_input)

    # ── Extraire champs F1 ───────────────────────────────────────
    entrepreneur_id  = f1.get("entrepreneur_id", "INCONNU")
    stade_reel       = f1.get("stade_reel", "Structuration")
    stade_percu      = f1.get("stade_percu", stade_reel)
    score_diag       = f1.get("score_diagnostic", 0)
    gap_detecte      = f1.get("gap_detecte", False)
    gap_explication  = f1.get("gap_explication", "")
    gaps_texte       = f1.get("gaps", [])
    blockers_f1      = f1.get("blockers", [])
    secteur_f1       = f1.get("secteur", "")
    secteur_label    = f1.get("secteur_label", secteur_f1)
    localisation     = f1.get("localisation", "")
    financement_hint = f1.get("financement_recommande", "")
    signaux          = f1.get("signaux_divergence", [])
    profil           = f1.get("profil_complet", {})
    reponses         = f1.get("reponses", {})
    nom_entreprise   = profil.get("nom_entreprise", "N/A")

    # ── Extraire champs F2 ───────────────────────────────────────
    if f2:
        fri             = f2.get("financing_readiness_index")
        is_financeable  = f2.get("is_financeable", True)
        secteur_f2      = f2.get("secteur_applique", "")
        blockers_f2     = f2.get("blockers_actifs", [])
        anomalies_f2    = f2.get("anomalies_detectees", [])
        resume_f2       = f2.get("resume_executif", "")
        # Actions correctives F2 depuis les scores
        actions_f2 = [
            f2.get("scores",{}).get(k,{}).get("action_template","")
            for k in ["market_score","commercial_offer_score","innovation_score","scalability_score","green_score"]
            if f2.get("scores",{}).get(k,{}).get("valeur",100) < 65
        ]
        scores_f2 = extraire_scores_f2(f2)
    else:
        fri = None
        is_financeable = True
        secteur_f2 = ""
        blockers_f2 = []
        anomalies_f2 = []
        resume_f2 = ""
        actions_f2 = []
        # Fallback: calcul depuis réponses F1
        scores_f2 = calculer_scores_depuis_reponses(reponses) if reponses else {
            "market":40,"commercial_offer":35,"innovation":25,"scalability":40,"green":40
        }

    # ── Traduire secteur (F1 prioritaire, F2 en fallback) ────────
    secteur_raw = secteur_f1 or secteur_f2
    secteur_rag = traduire_secteur(secteur_raw)
    if not secteur_label or secteur_label == secteur_f1:
        secteur_label = f1.get("secteur_label", secteur_raw)

    # ── Agréger tous les gaps (F1 + F2 + profil) ────────────────
    gaps_set = set()
    gaps_set.update(gaps_depuis_f1(gaps_texte, blockers_f1, financement_hint))
    if f2:
        gaps_set.update(gaps_depuis_f2(blockers_f2, anomalies_f2, fri, is_financeable))
    gaps_set.update(gaps_depuis_profil(profil, localisation))
    gaps_final = list(gaps_set)

    # ── Montant estimé ───────────────────────────────────────────
    montant = MONTANT_PAR_STADE.get(stade_reel, 150000)

    # ── Appeler le RAG ───────────────────────────────────────────
    profil_f3 = {
        "stade_diagnostique": stade_reel,
        "stade_declare":      stade_percu,
        "gaps_detectes":      gaps_final,
        "scores":             scores_f2,
        "secteur":            secteur_rag,
        "montant_besoin":     montant,
    }
    output_rag = contrat_f3(profil_f3)

    # ── Roadmap enrichie F1+F2 ───────────────────────────────────
    roadmap = generer_roadmap_enrichie(
        stade=stade_reel,
        secteur_rag=secteur_rag,
        secteur_label=secteur_label,
        gaps=gaps_final,
        fri=fri,
        anomalies=anomalies_f2,
        scores=scores_f2,
        actions_f2=actions_f2
    )

    # ── Message perception gap ───────────────────────────────────
    if gap_detecte and stade_reel != stade_percu:
        msg_gap = (
            f"⚠️  DIVERGENCE DÉTECTÉE — "
            f"Vous pensez être en '{stade_percu}' → stade réel: '{stade_reel}'.\n"
            f"  {gap_explication}"
        )
    else:
        msg_gap = "✅ Votre auto-évaluation correspond au diagnostic."

    # ── Blockers combinés F1+F2 ──────────────────────────────────
    blockers_combines = []
    for b in blockers_f1:
        blockers_combines.append({**b, "source": "F1"})
    for b in blockers_f2:
        # Éviter doublons
        already = any(x.get("domaine","").lower() == b.get("domaine","").lower() for x in blockers_combines)
        if not already:
            blockers_combines.append({**b, "source": "F2"})

    # ── Assembler output final ───────────────────────────────────
    return {
        # Identité
        "entrepreneur_id":   entrepreneur_id,
        "nom_entreprise":    nom_entreprise,
        "localisation":      localisation,
        "secteur_label":     secteur_label,
        "secteur_rag":       secteur_rag,

        # Diagnostic + scoring
        "stade_reel":              stade_reel,
        "stade_percu":             stade_percu,
        "score_diagnostic":        score_diag,
        "fri":                     fri,
        "is_financeable":          is_financeable,
        "fri_interpretation":      f2.get("fri_interpretation","") if f2 else "",
        "resume_executif_f2":      resume_f2,
        "divergence_detectee":     gap_detecte,
        "message_perception_gap":  msg_gap,
        "signaux_divergence":      signaux,
        "anomalies_f2":            anomalies_f2,
        "blockers_combines":       blockers_combines,

        # Scores
        "scores_f2": scores_f2,
        "scores_faibles": [k for k,v in scores_f2.items() if v < 65],

        # RAG Output
        "ressources_recommandees": output_rag.get("ressources_recommandees", []),
        "roadmap":                 roadmap,
        "sources_tracees":         output_rag.get("sources_tracees", []),

        # Raw pour traçabilité
        "diagnostic_f1": f1,
        "scoring_f2":    f2,

        # Log bridge
        "bridge_log": {
            "secteur_f1":      secteur_f1,
            "secteur_f2":      secteur_f2,
            "secteur_rag":     secteur_rag,
            "gaps_total":      len(gaps_final),
            "gaps_codes":      gaps_final,
            "scores_source":   "F2 direct" if f2 else "Calculés depuis réponses F1",
            "montant_estime":  montant,
            "region_interieure": localisation.lower() in REGIONS_INTERIEURES if localisation else False,
        }
    }


# ════════════════════════════════════════════════════════════════
# 8. POINT D'ENTRÉE — TEST AVEC LES VRAIS JSONs
# ════════════════════════════════════════════════════════════════

if __name__ == "__main__":
    import sys, os

    # Détecter les fichiers disponibles
    f1_file = None
    f2_file = None

    if len(sys.argv) >= 3:
        f1_file, f2_file = sys.argv[1], sys.argv[2]
    elif len(sys.argv) == 2:
        f1_file = sys.argv[1]
    else:
        for fname in os.listdir("."):
            if "diagnostic" in fname and fname.endswith(".json"):
                f1_file = fname
            if "contrat_f2" in fname and fname.endswith(".json"):
                f2_file = fname

    if not f1_file:
        print("❌ Fichier diagnostic F1 non trouvé.")
        print("   Usage: python bridge_f1_f3.py diagnostic_ENT-XXX.json [contrat_f2_output.json]")
        exit(1)

    print("=" * 65)
    print("BRIDGE F1+F2 → F3 — PIPELINE COMPLET")
    print("=" * 65)
    print(f"  F1: {f1_file}")
    print(f"  F2: {f2_file or '(non fourni — scores calculés depuis F1)'}")

    output = pipeline_complet(f1_file, f2_file)

    # ── Affichage ────────────────────────────────────────────────
    print(f"\n{'─'*65}")
    print(f"  ENTREPRENEUR")
    print(f"  Nom          : {output['nom_entreprise']} ({output['entrepreneur_id']})")
    print(f"  Localisation : {output['localisation']}")
    print(f"  Secteur      : {output['secteur_label']} → [{output['secteur_rag']}]")

    print(f"\n{'─'*65}")
    print(f"  DIAGNOSTIC F1 + SCORING F2")
    print(f"  Stade perçu  : {output['stade_percu']}")
    print(f"  Stade réel   : {output['stade_reel']}  (score diag: {output['score_diagnostic']}/100)")
    if output['fri'] is not None:
        print(f"  FRI (F2)     : {output['fri']}/100 — {output['fri_interpretation']}")
        print(f"  Bancable     : {'✅ OUI' if output['is_financeable'] else '❌ NON — structuration prioritaire'}")
    print(f"\n  {output['message_perception_gap']}")

    if output['anomalies_f2']:
        print(f"\n  🚨 ANOMALIES F2 ({len(output['anomalies_f2'])}):")
        for a in output['anomalies_f2']:
            print(f"    [{a['id']}] pénalité: -{a.get('penalite',0)} pts")
            print(f"    → {a.get('action_template','')[:80]}")

    print(f"\n{'─'*65}")
    print(f"  SCORES F2")
    for k, v in output['scores_f2'].items():
        bar  = "█"*(int(v)//10) + "░"*(10-int(v)//10)
        flag = " ⚠️" if v < 65 else " ✅"
        print(f"    {k:<20} {int(v):>3}% {bar}{flag}")
    print(f"  Scores faibles: {output['scores_faibles']}")

    print(f"\n{'─'*65}")
    b = output["bridge_log"]
    print(f"  BRIDGE LOG")
    print(f"  Scores source    : {b['scores_source']}")
    print(f"  Gaps total       : {b['gaps_total']} codes RAG")
    print(f"  Région intérieure: {'✅ OUI' if b['region_interieure'] else 'Non'}")
    print(f"  Codes gaps: {b['gaps_codes'][:6]}{'...' if len(b['gaps_codes'])>6 else ''}")

    print(f"\n{'─'*65}")
    print(f"  RESSOURCES RAG ({len(output['ressources_recommandees'])} trouvées)")
    for r in output['ressources_recommandees']:
        print(f"\n    ✅ [{r['id']}] {r['nom']}")
        print(f"       Organisme  : {r['organisme']}")
        print(f"       Pertinence : {r['pertinence']}%")
        print(f"       Taux       : {r['taux']}")
        print(f"       URL        : {r['url_source']}")

    print(f"\n{'─'*65}")
    print(f"  ROADMAP PERSONNALISÉE")
    rm = output['roadmap']
    print(f"  Secteur: {rm['secteur']} | Stade: {rm['stade']}", end="")
    if rm.get('fri') is not None:
        print(f" | FRI: {rm['fri']}/100")
    else:
        print()
    print(f"\n  📍 0-30 jours (URGENT):")
    for a in rm.get("immediat_0_30j", []):
        print(f"    → {a}")
    print(f"\n  📍 1-3 mois:")
    for a in rm.get("court_terme_1_3m", []):
        print(f"    → {a}")
    print(f"\n  📍 3-12 mois:")
    for a in rm.get("moyen_terme_3_12m", []):
        print(f"    → {a}")

    print(f"\n{'─'*65}")
    print(f"  SOURCES TRACÉES:")
    for url in output['sources_tracees']:
        print(f"    🔗 {url}")

    # Sauvegarder
    out_file = f"output_f3_{output['entrepreneur_id']}.json"
    with open(out_file, "w", encoding="utf-8") as f:
        json.dump(output, f, ensure_ascii=False, indent=2)

    print(f"\n{'='*65}")
    print(f"✅ Pipeline F1+F2→F3 opérationnel")
    print(f"✅ Sauvegardé: {out_file}")
    print(f"\n  USAGE MEMBRE 5:")
    print(f"  from bridge_f1_f3 import pipeline_complet")
    print(f"  output = pipeline_complet(f1_dict, f2_dict)")
    print(f"  # output['ressources_recommandees'] → ressources tracées")
    print(f"  # output['roadmap']                 → actions personnalisées")
    print(f"  # output['fri']                     → score bancabilité F2")
    print(f"  # output['message_perception_gap']  → alerte divergence F1")
