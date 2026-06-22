"""
============================================================
bridge_f1_f3.py — Bridge FINAL
Input  : contrat_f2_output.json (JSON fusionné F1+F2)
Output : ressources RAG + roadmap pour Dashboard Membre 5
============================================================

USAGE:
    from bridge_f1_f3 import pipeline_complet
    output = pipeline_complet("contrat_f2_output.json")

    # Ou dict en mémoire
    output = pipeline_complet(json_dict)

    # Output contient:
    output["ressources_recommandees"]  → TOUTES ressources Agriculture tracées
    output["roadmap"]                  → actions 0-30j, 1-3m, 3-12m
    output["scores_f2"]                → market:16.3, commercial:40, ...
    output["fri"]                      → 40
    output["message_perception_gap"]   → alerte divergence
============================================================
"""

import json
import re
from search_kb_no_api import contrat_f3

# ════════════════════════════════════════════════════════════════
# 1. MAPPINGS
# ════════════════════════════════════════════════════════════════

SECTEUR_MAP = {
    "agriculture_sylviculture_peche":  "Agriculture/Sylviculture/Peche",
    "industrie_construction":          "Industrie/Construction",
    "commerce_transport_logistique":   "Commerce/Transport/Logistique",
    "service_tourisme":                "Service/Tourisme",
    "technologie_service_entreprise":  "Technologie/Service-Entreprise",
    "agriculture":   "Agriculture/Sylviculture/Peche",
    "agri-food":     "Agriculture/Sylviculture/Peche",
    "agri":          "Agriculture/Sylviculture/Peche",
    "agritech":      "Agriculture/Sylviculture/Peche",
    "peche":         "Agriculture/Sylviculture/Peche",
    "industrie":     "Industrie/Construction",
    "construction":  "Industrie/Construction",
    "btp":           "Industrie/Construction",
    "commerce":      "Commerce/Transport/Logistique",
    "transport":     "Commerce/Transport/Logistique",
    "logistique":    "Commerce/Transport/Logistique",
    "services":      "Service/Tourisme",
    "tourisme":      "Service/Tourisme",
    "tech_digital":  "Technologie/Service-Entreprise",
    "tech":          "Technologie/Service-Entreprise",
    "digital":       "Technologie/Service-Entreprise",
    "fintech":       "Technologie/Service-Entreprise",
    "saas":          "Technologie/Service-Entreprise",
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

GAP_KEYWORDS = {
    "rne":                       "absence_structure_juridique",
    "enregistr":                 "absence_structure_juridique",
    "juridique":                 "absence_structure_juridique",
    "business plan":             "absence_business_plan",
    "plan d'affaires":           "absence_business_plan",
    "équipe":                    "equipe_incomplete",
    "fondateur seul":            "equipe_incomplete",
    "solo":                      "equipe_incomplete",
    "certif":                    "certification_manquante",
    "sanitaire":                 "certification_manquante",
    "phytosanitaire":            "certification_manquante",
    "chaîne de froid":           "chaine_froid_absente",
    "froid":                     "chaine_froid_absente",
    "logistique non":            "chaine_froid_absente",
    "client payant":             "absence_validation_marche",
    "traction":                  "absence_validation_marche",
    "proches":                   "absence_validation_marche",
    "apport":                    "manque_apport_personnel",
    "garantie":                  "manque_garanties",
    "mvp":                       "besoin_prototype",
    "innov":                     "innovation_score_faible",
    "identique":                 "innovation_score_faible",
    "existant sur le marché":    "innovation_score_faible",
    "depuis plus de":            "innovation_score_faible",
    "différenciation":           "innovation_score_faible",
    "propriété intellectuelle":  "innovation_score_faible",
    "concurrent":                "innovation_score_faible",
    "jeune":                     "jeune_diplome",
    "export":                    "export",
    "micro":                     "micro_projet",
    "faible revenu":             "faible_revenu",
}

BLOCKER_TO_GAP = {
    "légal":           "absence_structure_juridique",
    "legal":           "absence_structure_juridique",
    "financier":       "absence_business_plan",
    "marché":          "absence_validation_marche",
    "marche":          "absence_validation_marche",
    "organisationnel": "equipe_incomplete",
    "réglementaire":   "certification_manquante",
    "reglementaire":   "certification_manquante",
    "technique":       "besoin_prototype",
}

MONTANT_PAR_STADE = {
    "Ideation":          5000,
    "Market Validation": 30000,
    "Structuration":     150000,
    "Fundraising":       300000,
    "Launch Planning":   500000,
    "Growth":            1000000,
}


# ════════════════════════════════════════════════════════════════
# 2. EXTRACTEUR STADE RÉEL
# ════════════════════════════════════════════════════════════════

def extraire_stade_reel(d: dict) -> str:
    """
    Le JSON fusionné peut avoir stade_reel=stade_percu (bug F1).
    On extrait le vrai stade depuis gap_explication si gap_detecte=True.
    Ex: "indique 'Structuration'" → "Structuration"
    """
    stade_json  = d.get("stade_reel", "Structuration")
    stade_percu = d.get("stade_percu", stade_json)
    gap_detecte = d.get("gap_detecte", False)

    if not gap_detecte:
        return stade_json

    # Chercher stade réel dans gap_explication
    explication = d.get("gap_explication","")
    patterns = [
        r"indique ['\"](\w[\w\s]+)['\"]",
        r"diagnostic objectif indique ['\"]([^'\"]+)['\"]",
        r"stade réel est ['\"]([^'\"]+)['\"]",
        r"objectif.*?['\"]([^'\"]+)['\"]",
    ]
    for pat in patterns:
        m = re.search(pat, explication)
        if m:
            stade_trouve = m.group(1).strip()
            stades_valides = ["Ideation","Market Validation","Structuration",
                              "Fundraising","Launch Planning","Growth"]
            if stade_trouve in stades_valides:
                return stade_trouve

    # Fallback: si stade_reel == stade_percu et gap détecté → régresser d'un niveau
    if stade_json == stade_percu and gap_detecte:
        stades = ["Ideation","Market Validation","Structuration",
                  "Fundraising","Launch Planning","Growth"]
        # Chercher "surestimé son stade de N niveau(x)"
        m = re.search(r"surestimé son stade de (\d+)", explication)
        if m:
            n = int(m.group(1))
            idx = stades.index(stade_percu) if stade_percu in stades else 5
            idx_reel = max(0, idx - n)
            return stades[idx_reel]

    return stade_json


# ════════════════════════════════════════════════════════════════
# 3. TRADUCTEUR SECTEUR
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
# 4. EXTRACTEUR GAPS
# ════════════════════════════════════════════════════════════════

def extraire_gaps(d: dict, stade_reel: str) -> list:
    """
    Extrait et traduit les gaps depuis TOUTES les sources du JSON fusionné:
    - gaps[] texte libre (F1)
    - blockers_actifs[].domaine (F2)
    - anomalies_detectees[].id (F2)
    - profil_complet (F1)
    - scores faibles (F2)
    - localisation (F1)
    """
    codes = set()
    profil      = d.get("profil_complet", {})
    localisation = d.get("localisation","")
    scores      = d.get("scores", {})
    anomalies   = d.get("anomalies_detectees", [])
    blockers    = d.get("blockers_actifs", [])

    # SOURCE 1: gaps texte libre F1
    for gap in d.get("gaps", []):
        g = gap.lower()
        for kw, code in GAP_KEYWORDS.items():
            if kw in g:
                codes.add(code)

    # SOURCE 2: blockers F2
    for b in blockers:
        dom = b.get("domaine","").lower()
        for d_kw, code in BLOCKER_TO_GAP.items():
            if d_kw in dom:
                codes.add(code)

    # SOURCE 3: anomalies F2
    ANOMALIE_GAPS = {
        "ANOM_FRAUD_CA_NO_RNE":         ["absence_structure_juridique","activite_informelle","urgence_rne"],
        "ANOM_NO_RNE":                  ["absence_structure_juridique","urgence_rne"],
        "ANOM_TEAM_SOLO_FATIGUE":       ["equipe_incomplete","key_man_risk"],
        "ANOM_ECO_REGIONAL_FUNDS_MISSED":["regions_interieures","prime_regionale_manquee"],
        "ANOM_IN_4":                    ["innovation_score_faible"],
    }
    for a in anomalies:
        aid = a.get("id","")
        for pattern, gap_codes in ANOMALIE_GAPS.items():
            if pattern in aid:
                codes.update(gap_codes)

    # SOURCE 4: profil_complet F1
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
    if profil.get("acces_foncier") == "Oui, location court terme":
        codes.add("foncier_precaire")

    # SOURCE 5: scores faibles F2 → gaps supplémentaires
    if scores.get("market_score",{}).get("valeur",100) < 30:
        codes.add("market_score_critique")
        codes.add("absence_validation_marche")
    if scores.get("commercial_offer_score",{}).get("valeur",100) < 50:
        codes.add("proposition_valeur_faible")
        codes.add("business_model_flou")

    # SOURCE 6: localisation → région intérieure
    if localisation and localisation.lower() in REGIONS_INTERIEURES:
        codes.add("regions_interieures")
        codes.add("prime_regionale_manquee")

    # SOURCE 7: FRI bas
    fri = d.get("financing_readiness_index")
    if fri is not None and fri < 50:
        codes.add("besoin_structuration_avant_financement")
    if d.get("is_financeable") is False:
        codes.add("non_bancable")

    return list(codes)


# ════════════════════════════════════════════════════════════════
# 5. EXTRACTEUR SCORES F2
# ════════════════════════════════════════════════════════════════

def extraire_scores_f2(d: dict) -> dict:
    """
    Extrait les 5 scores depuis le JSON fusionné.
    Clés F2: market_score, commercial_offer_score, innovation_score, ...
    Clés RAG: market, commercial_offer, innovation, scalability, green
    """
    s = d.get("scores", {})
    return {
        "market":           s.get("market_score",           {}).get("valeur", 40),
        "commercial_offer": s.get("commercial_offer_score", {}).get("valeur", 40),
        "innovation":       s.get("innovation_score",       {}).get("valeur", 40),
        "scalability":      s.get("scalability_score",      {}).get("valeur", 40),
        "green":            s.get("green_score",            {}).get("valeur", 40),
    }


# ════════════════════════════════════════════════════════════════
# 6. ROADMAP ENRICHIE F1+F2
# ════════════════════════════════════════════════════════════════

def generer_roadmap(stade: str, secteur_rag: str, secteur_label: str,
                    gaps: list, fri: int, anomalies: list,
                    scores: dict) -> dict:

    ACTIONS_STADE = {
        "Ideation": {
            "immediat":    ["Contacter Espaces Entreprendre APII (gratuit)", "Déposer dossier ANETI/PAPPE (indemnisé)", "Formaliser l'idée en 2 pages"],
            "court_terme": ["Réaliser 10+ interviews clients réels", "Tester service ou prototype minimal", "Décider forme juridique (SUARL recommandée)"],
            "moyen_terme": ["Rédiger business plan complet", "Inscrire au RNE", "Postuler BTS micro-crédit si besoin"]
        },
        "Market Validation": {
            "immediat":    ["Construire MVP testable", "Documenter 3 clients payants ou LOIs", "Postuler Flat6Labs prochaine cohorte"],
            "court_terme": ["Valider modèle économique chiffré", "Déposer candidature Startup Act si innovant", "Pitcher 5+ clients réels"],
            "moyen_terme": ["Contacter Carthage Business Angels", "Préparer pitch deck investisseurs", "Viser premier CA réel"]
        },
        "Structuration": {
            "immediat":    ["Créer société au RNE si pas encore fait", "Constituer dossier BFPME (business plan modèle GIZ)", "Évaluer apport personnel + éligibilité SOTUGAR"],
            "court_terme": ["Déposer dossier FOPRODI APII (prime 10% équipements)", "Vérifier garantie SOTUGAR", "Finaliser cofinancement avec banque partenaire"],
            "moyen_terme": ["Obtenir accord BFPME", "Recruter équipe clé (COO / associé)", "Mettre en place comptabilité formelle"]
        },
        "Fundraising": {
            "immediat":    ["Préparer data room complète (KPIs, états financiers)", "Contacter Carthage Business Angels", "Vérifier éligibilité Startup Act label"],
            "court_terme": ["Pitcher 3+ investisseurs", "Déposer dossier Smart Capital / ANAVA", "Négocier term sheet avec conseil juridique"],
            "moyen_terme": ["Clôturer tour de table", "Déployer fonds selon plan", "Préparer reporting investisseurs trimestriel"]
        },
        "Launch Planning": {
            "immediat":    ["Finaliser plan lancement (date + budget marketing)", "Constituer dossier BFR si trésorerie tendue", "Activer CEPEX si export prévu"],
            "court_terme": ["Lancer activité commerciale", "Installer ERP/CRM via Digital Tunisia", "Premier bilan mensuel"],
            "moyen_terme": ["Atteindre seuil rentabilité", "Préparer extension", "Dossier BFPME extension si croissance"]
        },
        "Growth": {
            "immediat":    ["Analyser goulots croissance", "Évaluer besoins extension", "Contacter APII programme mise à niveau PMN"],
            "court_terme": ["Dossier BFPME extension ou BFR", "Activer FOPRODEX si export", "Étudier Series A (AfricInvest, ANAVA)"],
            "moyen_terme": ["Déployer nouveau marché", "Structurer management intermédiaire", "Préparer exit ou prochain tour"]
        }
    }

    ACTIONS_SECTEUR = {
        "Agriculture/Sylviculture/Peche":  "Contacter APIA Siliana (primes agricoles) + BNA (crédit campagne) + ODESYPANO (développement régional Nord-Ouest)",
        "Industrie/Construction":          "Déposer dossier FOPRODI APII (prime 10% équipements industriels)",
        "Commerce/Transport/Logistique":   "Contacter CEPEX si export + TRADE-001 pour financement commerce international",
        "Service/Tourisme":                "Vérifier exception BFPME gîtes ruraux + ONTT pour label touristique",
        "Technologie/Service-Entreprise":  "Postuler Startup Act (exonérations 8 ans) + Smart Capital pour financement innovant",
    }

    base        = ACTIONS_STADE.get(stade, ACTIONS_STADE["Structuration"])
    immediat    = base["immediat"].copy()
    court_terme = base["court_terme"].copy()
    moyen_terme = base["moyen_terme"].copy()

    # 1. Action sectorielle en tête
    if secteur_rag in ACTIONS_SECTEUR:
        immediat.insert(0, f"[{secteur_label}] {ACTIONS_SECTEUR[secteur_rag]}")

    # 2. Anomalies F2 urgentes (max 2)
    for a in anomalies[:2]:
        action = a.get("action_template","").strip()
        if action:
            immediat.insert(1, f"🚨 {action}")

    # 3. FRI avertissement
    if fri is not None and fri < 50:
        immediat.append(
            f"⚠️ FRI={fri}/100 — Projet non encore bancable. "
            f"Structuration et accompagnement prioritaires avant dépôt dossier financement."
        )

    # 4. Actions correctives scores faibles F2 (max 3, seulement si score < 50)
    scores_critiques = {k:v for k,v in scores.items() if v < 50}
    if "market" in scores_critiques:
        court_terme.insert(0, "🎯 [Market Score critique] Obtenir 3 lettres d'intention clients payants avant tout dépôt de dossier")
    if "commercial_offer" in scores_critiques:
        court_terme.insert(1, "🎯 [Offre commerciale] Rédiger fiche proposition de valeur (1 page) et tester avec 5 clients réels")

    return {
        "stade":             stade,
        "secteur":           secteur_label,
        "fri":               fri,
        "immediat_0_30j":    immediat,
        "court_terme_1_3m":  court_terme,
        "moyen_terme_3_12m": moyen_terme,
    }


# ════════════════════════════════════════════════════════════════
# 7. PIPELINE PRINCIPAL
# ════════════════════════════════════════════════════════════════

def pipeline_complet(input_data) -> dict:
    """
    Input  : contrat_f2_output.json (JSON fusionné F1+F2)
             → fichier JSON (str) OU dict en mémoire
    Output : dict complet pour Dashboard Membre 5
    """

    # Charger
    if isinstance(input_data, str):
        with open(input_data, encoding="utf-8") as f:
            d = json.load(f)
    else:
        d = input_data

    # ── Extraire tous les champs ─────────────────────────────────
    entrepreneur_id = d.get("entrepreneur_id", "INCONNU")
    profil          = d.get("profil_complet", {})
    nom_entreprise  = profil.get("nom_entreprise", d.get("nom_entreprise","N/A"))
    localisation    = d.get("localisation","")
    secteur_raw     = d.get("secteur","")
    secteur_label   = d.get("secteur_label", secteur_raw)
    stade_percu     = d.get("stade_percu","")
    gap_detecte     = d.get("gap_detecte", False)
    gap_explication = d.get("gap_explication","")
    signaux         = d.get("signaux_divergence", [])
    anomalies       = d.get("anomalies_detectees", [])
    blockers        = d.get("blockers_actifs", [])
    fri             = d.get("financing_readiness_index")
    is_financeable  = d.get("is_financeable", True)
    fri_interp      = d.get("fri_interpretation","")
    resume_f2       = d.get("resume_executif","")

    # ── Extraire le vrai stade réel ──────────────────────────────
    stade_reel = extraire_stade_reel(d)

    # ── Traduire secteur ─────────────────────────────────────────
    secteur_rag = traduire_secteur(secteur_raw)

    # ── Extraire scores F2 ───────────────────────────────────────
    scores_f2 = extraire_scores_f2(d)

    # ── Extraire gaps (toutes sources) ───────────────────────────
    gaps_rag = extraire_gaps(d, stade_reel)

    # ── Montant estimé ───────────────────────────────────────────
    montant = MONTANT_PAR_STADE.get(stade_reel, 150000)

    # ── Actions correctives F2 ───────────────────────────────────
    actions_f2 = []
    for k in ["market_score","commercial_offer_score","innovation_score","scalability_score","green_score"]:
        score_data = d.get("scores",{}).get(k,{})
        if score_data.get("valeur",100) < 65:
            action = score_data.get("action_template","").strip()
            if action:
                actions_f2.append(action)

    # ── Appeler le RAG ───────────────────────────────────────────
    profil_f3 = {
        "stade_diagnostique": stade_reel,
        "stade_declare":      stade_percu,
        "gaps_detectes":      gaps_rag,
        "scores":             scores_f2,
        "secteur":            secteur_rag,
        "montant_besoin":     montant,
        "fri":                fri,
        "anomalies_f2":       anomalies,
        "actions_f2":         actions_f2,
    }
    output_rag = contrat_f3(profil_f3)

    # ── Roadmap enrichie ─────────────────────────────────────────
    roadmap = generer_roadmap(
        stade=stade_reel,
        secteur_rag=secteur_rag,
        secteur_label=secteur_label,
        gaps=gaps_rag,
        fri=fri,
        anomalies=anomalies,
        scores=scores_f2,
    )

    # ── Message perception gap ───────────────────────────────────
    if gap_detecte and stade_reel != stade_percu:
        msg_gap = (
            f"⚠️ DIVERGENCE DÉTECTÉE — "
            f"Vous pensez être en '{stade_percu}' → stade réel: '{stade_reel}'.\n"
            f"  {gap_explication}"
        )
    else:
        msg_gap = "✅ Auto-évaluation correcte."

    # ── Output final ─────────────────────────────────────────────
    return {
        # Identité
        "entrepreneur_id":   entrepreneur_id,
        "nom_entreprise":    nom_entreprise,
        "localisation":      localisation,
        "secteur_label":     secteur_label,
        "secteur_rag":       secteur_rag,

        # Diagnostic
        "stade_reel":              stade_reel,
        "stade_percu":             stade_percu,
        "gap_detecte":             gap_detecte,
        "divergence_detectee":     gap_detecte and stade_reel != stade_percu,
        "message_perception_gap":  msg_gap,
        "signaux_divergence":      signaux,
        "gap_explication":         gap_explication,

        # Scoring F2
        "fri":                fri,
        "is_financeable":     is_financeable,
        "fri_interpretation": fri_interp,
        "scores_f2":          scores_f2,
        "scores_faibles":     [k for k,v in scores_f2.items() if v < 65],
        "anomalies_f2":       anomalies,
        "blockers":           blockers,
        "resume_executif":    resume_f2,

        # RAG F3
        "nombre_ressources":       output_rag.get("nombre_ressources", len(output_rag.get("ressources_recommandees",[]))),
        "ressources_recommandees": output_rag.get("ressources_recommandees", []),
        "roadmap":                 roadmap,
        "sources_tracees":         output_rag.get("sources_tracees", []),

        # Bridge log
        "bridge_log": {
            "secteur_raw":         secteur_raw,
            "secteur_rag":         secteur_rag,
            "stade_extrait_de":    "gap_explication" if stade_reel != d.get("stade_reel") else "stade_reel",
            "gaps_codes":          gaps_rag,
            "gaps_total":          len(gaps_rag),
            "scores_source":       "F2 direct",
            "montant_estime":      montant,
            "region_interieure":   localisation.lower() in REGIONS_INTERIEURES if localisation else False,
        }
    }


# ════════════════════════════════════════════════════════════════
# 8. MAIN — TEST AVEC LE VRAI JSON
# ════════════════════════════════════════════════════════════════

if __name__ == "__main__":
    import sys, os

    # Détecter fichier input
    if len(sys.argv) > 1:
        fichier = sys.argv[1]
    elif os.path.exists("contrat_f2_output.json"):
        fichier = "contrat_f2_output.json"
    else:
        for f in os.listdir("."):
            if "contrat_f2" in f and f.endswith(".json"):
                fichier = f
                break
        else:
            print("❌ Aucun fichier contrat_f2_output.json trouvé.")
            print("   Usage: python bridge_f1_f3.py contrat_f2_output.json")
            exit(1)

    print("=" * 65)
    print(f"BRIDGE F1+F2 → RAG F3")
    print(f"Input: {fichier}")
    print("=" * 65)

    output = pipeline_complet(fichier)

    # ── Identité
    print(f"\n  Entrepreneur : {output['nom_entreprise']} ({output['entrepreneur_id']})")
    print(f"  Localisation : {output['localisation']}")
    print(f"  Secteur      : {output['secteur_label']} → [{output['secteur_rag']}]")

    # ── Diagnostic
    print(f"\n{'─'*65}")
    print(f"  DIAGNOSTIC")
    print(f"  Stade perçu  : {output['stade_percu']}")
    print(f"  Stade réel   : {output['stade_reel']}")
    print(f"  {output['message_perception_gap'][:100]}")

    # ── Scoring
    print(f"\n{'─'*65}")
    print(f"  SCORES F2")
    for k, v in output["scores_f2"].items():
        bar  = "█"*(int(v)//10) + "░"*(10-int(v)//10)
        flag = " ⚠️ FAIBLE" if v < 65 else " ✅"
        print(f"    {k:<20} {int(v):>3}% {bar}{flag}")
    print(f"\n  FRI : {output['fri']}/100 — {output['fri_interpretation'][:60]}")
    print(f"  Bancable : {'✅' if output['is_financeable'] else '❌ NON'}")

    # ── Anomalies
    if output["anomalies_f2"]:
        print(f"\n{'─'*65}")
        print(f"  ANOMALIES F2 ({len(output['anomalies_f2'])})")
        for a in output["anomalies_f2"]:
            if a.get("action_template"):
                print(f"  🚨 [{a['id']}] {a['action_template'][:70]}")

    # ── Gaps
    print(f"\n{'─'*65}")
    b = output["bridge_log"]
    print(f"  GAPS RAG ({b['gaps_total']} codes extraits)")
    for g in b["gaps_codes"]:
        print(f"    • {g}")
    print(f"  Région intérieure : {'✅ Siliana détectée' if b['region_interieure'] else 'Non'}")

    # ── Ressources
    print(f"\n{'─'*65}")
    print(f"  RESSOURCES RAG — {output['nombre_ressources']} ressources compatibles")
    print(f"  ({output['secteur_rag']} + {output['stade_reel']})\n")
    for r in output["ressources_recommandees"]:
        print(f"  ✅ [{r['id']}] {r['nom']}")
        print(f"     Organisme  : {r['organisme']}")
        print(f"     Pertinence : {r['pertinence']}%")
        print(f"     Taux       : {r['taux'] or 'Voir site'}")
        print(f"     URL        : {r['url_source']}")
        if r.get("gaps_matches"):
            print(f"     Gaps couverts: {r['gaps_matches']}")
        print()

    # ── Roadmap
    print(f"{'─'*65}")
    rm = output["roadmap"]
    print(f"  ROADMAP — {rm['secteur']} | {rm['stade']} | FRI: {rm['fri']}/100\n")
    print(f"  📍 0-30 jours (URGENT):")
    for a in rm["immediat_0_30j"]:
        print(f"    → {a}")
    print(f"\n  📍 1-3 mois:")
    for a in rm["court_terme_1_3m"]:
        print(f"    → {a}")
    print(f"\n  📍 3-12 mois:")
    for a in rm["moyen_terme_3_12m"]:
        print(f"    → {a}")

    # ── Sources
    print(f"\n{'─'*65}")
    print(f"  SOURCES TRACÉES:")
    for url in output['sources_tracees']:
        print(f"    🔗 {url}")

    # Sauvegarder
    out_file = f"output_f3_{output['entrepreneur_id']}.json"
    with open(out_file, "w", encoding="utf-8") as f:
        json.dump(output, f, ensure_ascii=False, indent=2)

    print(f"\n{'='*65}")
    print(f"✅ Pipeline complet — {output['nombre_ressources']} ressources Agriculture trouvées")
    print(f"✅ Sauvegardé: {out_file}")
    print(f"\n  USAGE MEMBRE 5:")
    print(f"  from bridge_f1_f3 import pipeline_complet")
    print(f"  output = pipeline_complet('contrat_f2_output.json')")
    print(f"  output = pipeline_complet(json_dict)  # ou dict en mémoire")
    

