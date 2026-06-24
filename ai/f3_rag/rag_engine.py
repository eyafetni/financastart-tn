"""
rag_engine.py — Moteur RAG complet en un seul fichier
======================================================
Fusionne: search_kb_no_api.py + bridge_f1_f3.py

USAGE FRONTEND:
    from rag_engine import run_rag
    output = run_rag("contrat_f2_output.json")
    # ou
    output = run_rag(mon_dict_json)

    output["ressources_recommandees"]  → toutes ressources tracées
    output["roadmap"]                  → actions 0-30j / 1-3m / 3-12m
    output["message_perception_gap"]   → divergence stade
    output["scores_f2"]                → market, innovation, green...
    output["fri"]                      → score bancabilité
"""

import json
import re
import chromadb
from sentence_transformers import SentenceTransformer

import os

# ════════════════════════════════════════════════════════════════
# CONFIGURATION
# ════════════════════════════════════════════════════════════════

SCRIPT_DIR      = os.path.dirname(os.path.abspath(__file__))
COLLECTION_NAME = "tunisian_resources"
EMBED_MODEL     = "paraphrase-multilingual-MiniLM-L12-v2"
CHROMA_PATH     = os.path.join(SCRIPT_DIR, "chromadb")

STADES_ORDER = [
    "Ideation", "Market Validation", "Structuration",
    "Fundraising", "Launch Planning", "Growth"
]

SECTEURS_RAG = [
    "Agriculture/Sylviculture/Peche",
    "Industrie/Construction",
    "Commerce/Transport/Logistique",
    "Service/Tourisme",
    "Technologie/Service-Entreprise",
]

REGIONS_INTERIEURES = [
    "siliana", "kasserine", "kairouan", "sidi bouzid", "gafsa",
    "tozeur", "kebili", "tataouine", "medenine", "jendouba", "le kef", "zaghouan",
]

# ════════════════════════════════════════════════════════════════
# MAPPINGS
# ════════════════════════════════════════════════════════════════

SECTEUR_MAP = {
    "agriculture_sylviculture_peche":  "Agriculture/Sylviculture/Peche",
    "industrie_construction":          "Industrie/Construction",
    "commerce_transport_logistique":   "Commerce/Transport/Logistique",
    "service_tourisme":                "Service/Tourisme",
    "technologie_service_entreprise":  "Technologie/Service-Entreprise",
    "agriculture":  "Agriculture/Sylviculture/Peche",
    "agri-food":    "Agriculture/Sylviculture/Peche",
    "agritech":     "Agriculture/Sylviculture/Peche",
    "peche":        "Agriculture/Sylviculture/Peche",
    "industrie":    "Industrie/Construction",
    "construction": "Industrie/Construction",
    "btp":          "Industrie/Construction",
    "commerce":     "Commerce/Transport/Logistique",
    "transport":    "Commerce/Transport/Logistique",
    "logistique":   "Commerce/Transport/Logistique",
    "services":     "Service/Tourisme",
    "tourisme":     "Service/Tourisme",
    "tech_digital": "Technologie/Service-Entreprise",
    "tech":         "Technologie/Service-Entreprise",
    "digital":      "Technologie/Service-Entreprise",
    "fintech":      "Technologie/Service-Entreprise",
    "saas":         "Technologie/Service-Entreprise",
}

GAP_KEYWORDS = {
    "rne":                    "absence_structure_juridique",
    "enregistr":              "absence_structure_juridique",
    "business plan":          "absence_business_plan",
    "fondateur seul":         "equipe_incomplete",
    "équipe":                 "equipe_incomplete",
    "certif":                 "certification_manquante",
    "sanitaire":              "certification_manquante",
    "phytosanitaire":         "certification_manquante",
    "chaîne de froid":        "chaine_froid_absente",
    "froid":                  "chaine_froid_absente",
    "client payant":          "absence_validation_marche",
    "traction":               "absence_validation_marche",
    "proches":                "absence_validation_marche",
    "apport":                 "manque_apport_personnel",
    "garantie":               "manque_garanties",
    "existant sur le marché": "innovation_score_faible",
    "depuis plus de":         "innovation_score_faible",
    "différenciation":        "innovation_score_faible",
    "concurrent":             "innovation_score_faible",
    "jeune":                  "jeune_diplome",
    "export":                 "export",
    "micro":                  "micro_projet",
}

BLOCKER_TO_GAP = {
    "légal":           "absence_structure_juridique",
    "legal":           "absence_structure_juridique",
    "financier":       "absence_business_plan",
    "marché":          "absence_validation_marche",
    "organisationnel": "equipe_incomplete",
    "réglementaire":   "certification_manquante",
    "reglementaire":   "certification_manquante",
}

ANOMALIE_TO_GAPS = {
    "ANOM_FRAUD_CA_NO_RNE":           ["absence_structure_juridique", "urgence_rne"],
    "ANOM_TEAM_SOLO_FATIGUE":         ["equipe_incomplete", "key_man_risk"],
    "ANOM_ECO_REGIONAL_FUNDS_MISSED": ["regions_interieures", "prime_regionale_manquee"],
    "ANOM_NO_RNE":                    ["absence_structure_juridique"],
    "ANOM_IN_4":                      ["innovation_score_faible"],
}

MONTANT_PAR_STADE = {
    "Ideation":          5000,
    "Market Validation": 30000,
    "Structuration":     150000,
    "Fundraising":       300000,
    "Launch Planning":   500000,
    "Growth":            1000000,
}

ACTIONS_STADE = {
    "Ideation": {
        "immediat":    ["Contacter Espaces Entreprendre APII (gratuit)", "Déposer dossier ANETI/PAPPE (indemnisé)", "Formaliser l'idée en 2 pages"],
        "court_terme": ["Réaliser 10+ interviews clients réels", "Tester service ou prototype minimal", "Décider forme juridique (SUARL recommandée)"],
        "moyen_terme": ["Rédiger business plan complet", "Inscrire au RNE", "Postuler BTS micro-crédit si besoin"],
    },
    "Market Validation": {
        "immediat":    ["Construire MVP testable", "Documenter 3 clients payants ou lettres d'intention", "Postuler Flat6Labs prochaine cohorte"],
        "court_terme": ["Valider modèle économique chiffré", "Pitcher 5+ clients réels", "Déposer candidature Startup Act si innovant"],
        "moyen_terme": ["Contacter Carthage Business Angels", "Préparer pitch deck investisseurs", "Viser premier CA réel"],
    },
    "Structuration": {
        "immediat":    ["Créer société au RNE si pas encore fait", "Constituer dossier BFPME (business plan modèle GIZ)", "Évaluer apport personnel + éligibilité SOTUGAR"],
        "court_terme": ["Déposer dossier FOPRODI APII (prime 10% équipements)", "Vérifier garantie SOTUGAR", "Finaliser cofinancement avec banque partenaire"],
        "moyen_terme": ["Obtenir accord BFPME", "Recruter équipe clé (COO / associé)", "Mettre en place comptabilité formelle"],
    },
    "Fundraising": {
        "immediat":    ["Préparer data room complète (KPIs, états financiers)", "Contacter Carthage Business Angels", "Vérifier éligibilité Startup Act label"],
        "court_terme": ["Pitcher 3+ investisseurs", "Déposer dossier Smart Capital / ANAVA", "Négocier term sheet avec conseil juridique"],
        "moyen_terme": ["Clôturer tour de table", "Déployer fonds selon plan", "Préparer reporting investisseurs trimestriel"],
    },
    "Launch Planning": {
        "immediat":    ["Finaliser plan lancement (date + budget marketing)", "Constituer dossier BFR si trésorerie tendue", "Activer CEPEX si export prévu"],
        "court_terme": ["Lancer activité commerciale", "Installer ERP/CRM via Digital Tunisia", "Premier bilan mensuel"],
        "moyen_terme": ["Atteindre seuil rentabilité", "Préparer extension", "Dossier BFPME extension si croissance"],
    },
    "Growth": {
        "immediat":    ["Analyser goulots de croissance", "Évaluer besoins financement extension", "Contacter APII programme mise à niveau PMN"],
        "court_terme": ["Dossier BFPME extension ou BFR", "Activer FOPRODEX si export", "Étudier Series A (AfricInvest, ANAVA)"],
        "moyen_terme": ["Déployer nouveau marché géographique", "Structurer management intermédiaire", "Préparer exit ou prochain tour"],
    },
}

ACTIONS_SECTEUR = {
    "Agriculture/Sylviculture/Peche": "Contacter APIA (primes agricoles) + BNA (crédit campagne) + ODESYPANO si Nord-Ouest",
    "Industrie/Construction":         "Déposer dossier FOPRODI APII (prime 10% équipements industriels)",
    "Commerce/Transport/Logistique":  "Contacter CEPEX si export + financement commerce international",
    "Service/Tourisme":               "Vérifier exception BFPME gîtes ruraux + ONTT pour label touristique",
    "Technologie/Service-Entreprise": "Postuler Startup Act (exonérations 8 ans) + Smart Capital pour financement innovant",
}


# ════════════════════════════════════════════════════════════════
# FONCTION PRINCIPALE — LA SEULE À APPELER
# ════════════════════════════════════════════════════════════════

def run_rag(input_data) -> dict:
    """
    Fonction principale unique.

    Args:
        input_data : chemin JSON (str) OU dict Python contrat_f2_output

    Returns:
        {
            entrepreneur_id, nom_entreprise, localisation,
            secteur_label, secteur_rag,
            stade_reel, stade_percu,
            divergence_detectee, message_perception_gap, signaux_divergence,
            fri, is_financeable, fri_interpretation,
            scores_f2, scores_faibles,
            anomalies_f2, blockers,
            nombre_ressources, ressources_recommandees,
            roadmap,
            sources_tracees
        }
    """

    # ── Charger le JSON ──────────────────────────────────────────
    if isinstance(input_data, str):
        with open(input_data, encoding="utf-8") as f:
            d = json.load(f)
    else:
        d = input_data

    # ── Extraire les champs du JSON fusionné F1+F2 ───────────────
    entrepreneur_id = d.get("entrepreneur_id", "INCONNU")
    profil          = d.get("profil_complet", {})
    nom_entreprise  = profil.get("nom_entreprise", d.get("nom_entreprise", "N/A"))
    localisation    = d.get("localisation", "")
    secteur_raw     = d.get("secteur", "")
    secteur_label   = d.get("secteur_label", secteur_raw)
    stade_percu     = d.get("stade_percu", "")
    gap_detecte     = d.get("gap_detecte", False)
    gap_explication = d.get("gap_explication", "")
    signaux         = d.get("signaux_divergence", [])
    anomalies       = d.get("anomalies_detectees", [])
    blockers        = d.get("blockers_actifs", [])
    fri             = d.get("financing_readiness_index")
    is_financeable  = d.get("is_financeable", True)
    fri_interp      = d.get("fri_interpretation", "")
    resume_f2       = d.get("resume_executif", "")
    scores_raw      = d.get("scores", {})

    # ── 1. Traduire secteur ──────────────────────────────────────
    secteur_rag = secteur_raw if secteur_raw in SECTEURS_RAG else None
    if not secteur_rag:
        cle = secteur_raw.lower().replace("-","_").replace(" ","_").replace("/","_")
        secteur_rag = SECTEUR_MAP.get(cle)
    if not secteur_rag:
        for kw, val in SECTEUR_MAP.items():
            if kw in secteur_raw.lower():
                secteur_rag = val
                break
    secteur_rag = secteur_rag or "Technologie/Service-Entreprise"

    # ── 2. Extraire stade réel ───────────────────────────────────
    stade_json = d.get("stade_reel", "Structuration")
    stade_reel = stade_json
    if gap_detecte and stade_json == stade_percu:
        for pat in [r"indique ['\"]([^'\"]+)['\"]",
                    r"diagnostic objectif indique ['\"]([^'\"]+)['\"]",
                    r"stade réel est ['\"]([^'\"]+)['\"]"]:
            m = re.search(pat, gap_explication)
            if m and m.group(1).strip() in STADES_ORDER:
                stade_reel = m.group(1).strip()
                break
        else:
            m = re.search(r"surestimé son stade de (\d+)", gap_explication)
            if m:
                n   = int(m.group(1))
                idx = STADES_ORDER.index(stade_percu) if stade_percu in STADES_ORDER else 5
                stade_reel = STADES_ORDER[max(0, idx - n)]

    # ── 3. Extraire scores F2 ────────────────────────────────────
    scores_f2 = {
        "market":           scores_raw.get("market_score",           {}).get("valeur", 40),
        "commercial_offer": scores_raw.get("commercial_offer_score", {}).get("valeur", 40),
        "innovation":       scores_raw.get("innovation_score",       {}).get("valeur", 40),
        "scalability":      scores_raw.get("scalability_score",      {}).get("valeur", 40),
        "green":            scores_raw.get("green_score",            {}).get("valeur", 40),
    }

    # ── 4. Extraire gaps (toutes sources) ────────────────────────
    codes = set()

    # Gaps texte libre F1
    for gap in d.get("gaps", []):
        for kw, code in GAP_KEYWORDS.items():
            if kw in gap.lower():
                codes.add(code)

    # Blockers F2
    for b in blockers:
        dom = b.get("domaine", "").lower()
        for kw, code in BLOCKER_TO_GAP.items():
            if kw in dom:
                codes.add(code)

    # Anomalies F2
    for a in anomalies:
        for pattern, gap_codes in ANOMALIE_TO_GAPS.items():
            if pattern in a.get("id", ""):
                codes.update(gap_codes)

    # Profil complet F1
    mapping_profil = {
        ("rne", False):                       "absence_structure_juridique",
        ("business_plan", "absent"):          "absence_business_plan",
        ("certifications_sanitaires", False): "certification_manquante",
        ("chaine_froid", False):              "chaine_froid_absente",
        ("equipe", "solo"):                   "equipe_incomplete",
        ("financement", "aucun"):             "absence_financement",
        ("accompagnement", "jamais"):         "besoin_accompagnement",
        ("innovation_niveau", "tres_faible"): "innovation_score_faible",
    }
    for (champ, valeur), code in mapping_profil.items():
        if profil.get(champ) == valeur:
            codes.add(code)

    # Scores faibles F2
    if scores_f2["market"] < 30:
        codes.update(["market_score_critique", "absence_validation_marche"])
    if scores_f2["commercial_offer"] < 50:
        codes.update(["proposition_valeur_faible", "business_model_flou"])

    # Localisation → région intérieure
    if localisation and localisation.lower() in REGIONS_INTERIEURES:
        codes.update(["regions_interieures", "prime_regionale_manquee"])

    # FRI bas
    if fri is not None and fri < 50:
        codes.add("besoin_structuration_avant_financement")
    if not is_financeable:
        codes.add("non_bancable")

    gaps_rag = list(codes)
    montant  = MONTANT_PAR_STADE.get(stade_reel, 150000)

    # ── 5. Recherche ChromaDB ────────────────────────────────────
    chroma     = chromadb.PersistentClient(path=CHROMA_PATH)
    collection = chroma.get_or_create_collection(COLLECTION_NAME)
    model      = SentenceTransformer(EMBED_MODEL)

    total_docs = collection.count()
    ressources = []

    if total_docs > 0:
        scores_faibles_list = [k for k, v in scores_f2.items() if v < 65]
        query = (
            f"SECTEUR: {secteur_rag}. "
            f"stade {stade_reel}. "
            f"gaps: {' '.join(gaps_rag[:5])}. "
            f"scores faibles: {' '.join(scores_faibles_list)}. "
            f"financement Tunisie PME entrepreneur"
        )
        queryembed = model.encode([query])[0].tolist()

        results = collection.query(
            query_embeddings=[queryembed],
            n_results=total_docs,
            include=["documents", "metadatas", "distances"]
        )

        # Stades compatibles ±1
        idx = STADES_ORDER.index(stade_reel) if stade_reel in STADES_ORDER else 2
        stades_cibles = {STADES_ORDER[i] for i in range(max(0,idx-1), min(len(STADES_ORDER),idx+2))}

        for meta, dist in zip(results["metadatas"][0], results["distances"][0]):
            # Filtre stade
            if not stades_cibles.intersection(set(meta.get("stades","").split("|"))):
                continue
            # Filtre secteur
            secteurs_fiche = meta.get("secteurs","")
            if secteurs_fiche and secteur_rag not in secteurs_fiche:
                continue
            # Filtre montant assoupli
            if montant:
                mmax = int(meta.get("montant_max") or 0)
                mmin = int(meta.get("montant_min") or 0)
                if mmax > 0 and montant > mmax * 5: continue
                if mmin > 0 and montant < mmin / 10: continue

            pertinence   = round((1 - dist) * 100, 1)
            gaps_matches = [g for g in gaps_rag if g in meta.get("gaps","").split("|")]

            ressources.append({
                "id":           meta["id"],
                "nom":          meta["nom"],
                "organisme":    meta["organisme"],
                "type":         meta.get("type",""),
                "taux":         meta.get("taux",""),
                "url_source":   meta.get("url_source",""),
                "secteurs":     meta.get("secteurs","").split("|"),
                "pertinence":   pertinence,
                "gaps_matches": gaps_matches,
                "justification": (
                    f"Recommandé pour stade '{stade_reel}', secteur '{secteur_rag}'. "
                    + (f"Adresse: {', '.join(gaps_matches)}. " if gaps_matches else "")
                    + f"Pertinence: {pertinence}%."
                )
            })

        ressources.sort(key=lambda x: x["pertinence"], reverse=True)

    # ── 6. Générer roadmap ───────────────────────────────────────
    base        = ACTIONS_STADE.get(stade_reel, ACTIONS_STADE["Structuration"])
    immediat    = base["immediat"].copy()
    court_terme = base["court_terme"].copy()
    moyen_terme = base["moyen_terme"].copy()

    if secteur_rag in ACTIONS_SECTEUR:
        immediat.insert(0, f"[{secteur_label}] {ACTIONS_SECTEUR[secteur_rag]}")
    for a in anomalies[:2]:
        action = a.get("action_template","").strip()
        if action:
            immediat.insert(1, f"🚨 {action}")
    if fri is not None and fri < 50:
        immediat.append(f"⚠️ FRI={fri}/100 — Projet non encore bancable. Structuration prioritaire avant dépôt dossier financement.")
    if scores_f2["market"] < 30:
        court_terme.insert(0, "🎯 [Market Score critique] Obtenir 3 lettres d'intention clients payants avant tout dépôt de dossier")
    if scores_f2["commercial_offer"] < 50:
        court_terme.insert(1, "🎯 [Offre commerciale] Rédiger fiche proposition de valeur (1 page) et tester avec 5 clients réels")

    roadmap = {
        "stade":             stade_reel,
        "secteur":           secteur_label,
        "fri":               fri,
        "immediat_0_30j":    immediat,
        "court_terme_1_3m":  court_terme,
        "moyen_terme_3_12m": moyen_terme,
    }

    # ── 7. Perception gap ────────────────────────────────────────
    divergence = gap_detecte and (stade_reel != stade_percu)
    if divergence:
        msg = (
            f"⚠️ DIVERGENCE DÉTECTÉE — "
            f"Vous pensez être en '{stade_percu}' → stade réel: '{stade_reel}'.\n"
            f"  {gap_explication}"
        )
    else:
        msg = "✅ Auto-évaluation correcte."

    # ── 8. Retourner output final ────────────────────────────────
    return {
        "entrepreneur_id":         entrepreneur_id,
        "nom_entreprise":          nom_entreprise,
        "localisation":            localisation,
        "secteur_label":           secteur_label,
        "secteur_rag":             secteur_rag,
        "stade_reel":              stade_reel,
        "stade_percu":             stade_percu,
        "gap_detecte":             gap_detecte,
        "divergence_detectee":     divergence,
        "message_perception_gap":  msg,
        "signaux_divergence":      signaux,
        "gap_explication":         gap_explication,
        "fri":                     fri,
        "is_financeable":          is_financeable,
        "fri_interpretation":      fri_interp,
        "scores_f2":               scores_f2,
        "scores_faibles":          [k for k,v in scores_f2.items() if v < 65],
        "anomalies_f2":            anomalies,
        "blockers":                blockers,
        "resume_executif":         resume_f2,
        "nombre_ressources":       len(ressources),
        "ressources_recommandees": ressources,
        "roadmap":                 roadmap,
        "sources_tracees":         [r["url_source"] for r in ressources],
    }
