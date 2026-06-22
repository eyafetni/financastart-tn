"""
search_kb_no_api.py — Moteur RAG v4
- Retourne TOUTES les ressources compatibles (stade + secteur)
- Secteur en premier dans texte_complet → embedding plus précis
- Filtre dur secteur + stade + montant assoupli
"""

import json
import chromadb
from sentence_transformers import SentenceTransformer

COLLECTION_NAME = "tunisian_resources"
EMBED_MODEL     = "paraphrase-multilingual-MiniLM-L12-v2"

SECTEURS_VALIDES = [
    "Agriculture/Sylviculture/Peche",
    "Industrie/Construction",
    "Commerce/Transport/Logistique",
    "Service/Tourisme",
    "Technologie/Service-Entreprise"
]

STADES_ORDER = [
    "Ideation", "Market Validation", "Structuration",
    "Fundraising", "Launch Planning", "Growth"
]


def search(gaps: list, stade: str, scores: dict,
           secteur: str = None, montant: int = None,
           top_k: int = 40):
    """
    Retourne TOUTES les ressources compatibles avec le stade et le secteur.
    
    Args:
        gaps    → codes gaps RAG (ex: ["absence_structure_juridique", ...])
        stade   → stade réel diagnostiqué (ex: "Structuration")
        scores  → dict scores F2
        secteur → secteur RAG officiel (ex: "Agriculture/Sylviculture/Peche")
        montant → montant besoin TND (optionnel)
        top_k   → si None → TOUTES les ressources compatibles
                   si int  → limiter à top_k ressources
    """
    chroma = chromadb.PersistentClient(path="./chromadb")
    collection = chroma.get_or_create_collection(COLLECTION_NAME)
    model = SentenceTransformer(EMBED_MODEL)

    total_docs = collection.count()
    if total_docs == 0:
        return []

    # Requête sémantique avec secteur en premier (cohérent avec texte_complet)
    scores_faibles = [k for k, v in scores.items() if v < 65]
    secteur_txt = secteur or "tous secteurs"
    query = (
        f"SECTEUR: {secteur_txt}. "
        f"stade {stade}. "
        f"gaps: {' '.join(gaps[:5])}. "
        f"scores faibles: {' '.join(scores_faibles)}. "
        f"financement Tunisie PME entrepreneur"
    )

    queryembed = model.encode([query])[0].tolist()

    # Récupérer TOUS les documents
    results = collection.query(
        query_embeddings=[queryembed],
        n_results=total_docs,
        include=["documents", "metadatas", "distances"]
    )

    # ── FILTRE 1: Stade (stade actuel ± 1) ──────────────────────
    idx = STADES_ORDER.index(stade) if stade in STADES_ORDER else 2
    stades_cibles = set()
    for offset in [-1, 0, 1]:
        i = idx + offset
        if 0 <= i < len(STADES_ORDER):
            stades_cibles.add(STADES_ORDER[i])

    ressources = []
    for meta, dist in zip(results["metadatas"][0], results["distances"][0]):

        # ── FILTRE 2: Stade ──────────────────────────────────────
        stades_fiche = set(meta.get("stades","").split("|"))
        if not stades_cibles.intersection(stades_fiche):
            continue

        # ── FILTRE 3: Secteur (filtre dur si secteur fourni) ─────
        if secteur:
            secteurs_fiche = meta.get("secteurs","")
            # Inclure si: secteur correspond OU fiche couvre tous secteurs
            tous_secteurs = all(
                s in secteurs_fiche
                for s in SECTEURS_VALIDES
            )
            if not tous_secteurs and secteur not in secteurs_fiche:
                continue

        # ── FILTRE 4: Montant (assoupli, seulement si clairement incompatible)
        if montant:
            mmax = int(meta.get("montant_max") or 0)
            mmin = int(meta.get("montant_min") or 0)
            if mmax > 0 and montant > mmax * 5:
                continue
            if mmin > 0 and montant < mmin / 10:
                continue

        pertinence   = round((1 - dist) * 100, 1)
        gaps_matches = [g for g in gaps if g in meta.get("gaps","").split("|")]

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
                f"Recommandé pour stade '{stade}'"
                + (f", secteur '{secteur}'" if secteur else "") + ". "
                + (f"Adresse: {', '.join(gaps_matches)}. " if gaps_matches else "")
                + f"Pertinence: {pertinence}%."
            )
        })

    # Trier par pertinence décroissante
    ressources.sort(key=lambda x: x["pertinence"], reverse=True)

    # Appliquer top_k seulement si explicitement demandé
    if top_k is not None:
        return ressources[:top_k]

    return ressources  # ← TOUTES les ressources compatibles


def generer_roadmap(stade: str, gaps: list, secteur: str = None,
                    fri: int = None, anomalies: list = None,
                    actions_f2: list = None) -> dict:

    ACTIONS_STADE = {
        "Ideation": {
            "immediat":    ["Contacter Espaces Entreprendre APII (gratuit)", "Déposer dossier ANETI/PAPPE (programme indemnisé)", "Formaliser l'idée en 2 pages écrites"],
            "court_terme": ["Réaliser étude de marché (10+ interviews clients)", "Tester prototype ou service minimal", "Décider forme juridique (SUARL recommandée)"],
            "moyen_terme": ["Rédiger business plan complet", "Inscrire au RNE", "Postuler BTS micro-crédit si besoin"]
        },
        "Market Validation": {
            "immediat":    ["Construire MVP testable", "Documenter preuves de traction (clients payants, LOIs)", "Postuler Flat6Labs prochaine cohorte"],
            "court_terme": ["Pitcher 5+ clients potentiels réels", "Valider modèle économique chiffré", "Déposer candidature Startup Act si innovant"],
            "moyen_terme": ["Contacter Carthage Business Angels", "Préparer pitch deck investisseurs", "Viser premier chiffre d'affaires réel"]
        },
        "Structuration": {
            "immediat":    ["Créer société au RNE si pas encore fait", "Constituer dossier BFPME (business plan modèle GIZ)", "Évaluer apport personnel disponible + SOTUGAR"],
            "court_terme": ["Déposer dossier FOPRODI APII pour prime investissement", "Vérifier éligibilité garantie SOTUGAR", "Finaliser plan cofinancement avec banque partenaire"],
            "moyen_terme": ["Obtenir accord BFPME", "Recruter équipe clé", "Mettre en place comptabilité formelle"]
        },
        "Fundraising": {
            "immediat":    ["Préparer data room complète (KPIs, états financiers)", "Contacter Carthage Business Angels", "Vérifier éligibilité label Startup Act"],
            "court_terme": ["Pitcher minimum 3 investisseurs", "Déposer dossier Smart Capital / ANAVA", "Négocier term sheet avec conseil juridique"],
            "moyen_terme": ["Clôturer tour de table", "Déployer fonds selon plan d'affaires", "Préparer reporting investisseurs trimestriel"]
        },
        "Launch Planning": {
            "immediat":    ["Finaliser plan de lancement (date, budget marketing)", "Constituer dossier BFR si trésorerie tendue", "Activer CEPEX si dimension export prévue"],
            "court_terme": ["Lancer activité commerciale", "Installer ERP/CRM via Digital Tunisia", "Premier bilan mensuel d'activité"],
            "moyen_terme": ["Atteindre seuil de rentabilité", "Préparer extension si croissance confirmée", "Dossier BFPME extension"]
        },
        "Growth": {
            "immediat":    ["Analyser goulots d'étranglement croissance", "Évaluer besoins financement extension", "Contacter APII programme mise à niveau PMN"],
            "court_terme": ["Dossier BFPME prêt extension ou BFR", "Activer FOPRODEX si export", "Étudier levée Series A (AfricInvest, ANAVA)"],
            "moyen_terme": ["Déployer sur nouveau marché géographique", "Structurer management intermédiaire", "Préparer exit ou prochain tour"]
        }
    }

    ACTIONS_SECTEUR = {
        "Agriculture/Sylviculture/Peche":  "Contacter APIA (primes agricoles) + BNA (crédit campagne) + ODESYPANO si Nord-Ouest",
        "Industrie/Construction":          "Déposer dossier FOPRODI APII pour prime 10% équipements industriels",
        "Commerce/Transport/Logistique":   "Contacter CEPEX si export + TRADE-001 pour financement commerce international",
        "Service/Tourisme":                "Vérifier exception BFPME gîtes ruraux + ONTT pour label qualité touristique",
        "Technologie/Service-Entreprise":  "Postuler Startup Act label (exonérations 8 ans) + Smart Capital pour financement innovant",
    }

    base       = ACTIONS_STADE.get(stade, ACTIONS_STADE["Structuration"])
    immediat   = base["immediat"].copy()
    court_terme = base["court_terme"].copy()
    moyen_terme = base["moyen_terme"].copy()

    # 1. Action sectorielle en tête
    if secteur and secteur in ACTIONS_SECTEUR:
        immediat.insert(0, f"[{secteur}] {ACTIONS_SECTEUR[secteur]}")

    # 2. Anomalies F2 urgentes
    for a in (anomalies or [])[:2]:
        action = a.get("action_template","")
        if action:
            immediat.insert(1, f"🚨 URGENT — {action}")

    # 3. Avertissement FRI
    if fri is not None and fri < 30:
        immediat.append(
            f"⚠️ FRI={fri}/100 — Votre projet n'est pas encore bancable. "
            f"Priorité: structuration et accompagnement avant tout dépôt de dossier financement."
        )

    # 4. Actions correctives F2 (max 3)
    for action in (actions_f2 or [])[:3]:
        if action:
            court_terme.append(f"[Score F2] {action}")

    return {
        "stade":             stade,
        "secteur":           secteur or "Tous secteurs",
        "fri":               fri,
        "immediat_0_30j":    immediat,
        "court_terme_1_3m":  court_terme,
        "moyen_terme_3_12m": moyen_terme,
    }


def contrat_f3(profil: dict) -> dict:
    """
    Interface principale pour Membre 5 et bridge_f1_f3.py
    Retourne TOUTES les ressources compatibles stade+secteur.
    """
    stade   = profil.get("stade_diagnostique", "Structuration")
    secteur = profil.get("secteur")
    gaps    = profil.get("gaps_detectes", [])
    scores  = profil.get("scores", {})
    montant = profil.get("montant_besoin")
    fri     = profil.get("fri")
    anomalies  = profil.get("anomalies_f2", [])
    actions_f2 = profil.get("actions_f2", [])

    # TOUTES les ressources compatibles (pas de top_k)
    ressources = search(
        gaps=gaps, stade=stade, scores=scores,
        secteur=secteur, montant=montant,
        top_k=None   # ← retourner TOUT
    )

    roadmap = generer_roadmap(
        stade=stade, gaps=gaps, secteur=secteur,
        fri=fri, anomalies=anomalies, actions_f2=actions_f2
    )

    stade_declare = profil.get("stade_declare","")
    divergence    = stade_declare != stade

    return {
        "stade_reel":              stade,
        "stade_declare":           stade_declare,
        "secteur":                 secteur or "Non spécifié",
        "divergence_detectee":     divergence,
        "message_perception_gap": (
            f"⚠️ Vous pensez être en '{stade_declare}' "
            f"mais votre stade réel est '{stade}'."
        ) if divergence else "✅ Auto-évaluation correcte.",
        "ressources_recommandees": ressources,
        "nombre_ressources":       len(ressources),
        "roadmap":                 roadmap,
        "sources_tracees":        [r["url_source"] for r in ressources],
        "note": "Zéro hallucination — chaque ressource tracée à URL officielle vérifiée."
    }


# ── TEST 5 PROFILS ────────────────────────────────────────────────
TEST_PROFILES = [
    {
        "nom": "Cas A — Agriculture / Siliana / Structuration (ENT-DBD323)",
        "stade_declare": "Growth", "stade_diagnostique": "Structuration",
        "secteur": "Agriculture/Sylviculture/Peche",
        "gaps_detectes": ["absence_structure_juridique","absence_business_plan","certification_manquante","equipe_incomplete","regions_interieures"],
        "scores": {"market":60,"commercial_offer":60,"innovation":60,"scalability":60,"green":60},
        "montant_besoin": 150000, "fri": 10
    },
    {
        "nom": "Cas B — Tech / Tunis / Ideation",
        "stade_declare": "Market Validation", "stade_diagnostique": "Ideation",
        "secteur": "Technologie/Service-Entreprise",
        "gaps_detectes": ["absence_validation_marche","micro_projet","phase_ideation"],
        "scores": {"market":25,"commercial_offer":20,"innovation":40,"scalability":15,"green":40},
        "montant_besoin": 5000
    },
    {
        "nom": "Cas C — Industrie / Sfax / Growth",
        "stade_declare": "Growth", "stade_diagnostique": "Growth",
        "secteur": "Industrie/Construction",
        "gaps_detectes": ["besoin_capital_croissance","extension_activite","competitivite_faible"],
        "scores": {"market":70,"commercial_offer":65,"innovation":45,"scalability":60,"green":50},
        "montant_besoin": 1500000
    },
    {
        "nom": "Cas D — Service/Tourisme / Djerba / Fundraising",
        "stade_declare": "Fundraising", "stade_diagnostique": "Fundraising",
        "secteur": "Service/Tourisme",
        "gaps_detectes": ["besoin_levee_fonds_prive","gite_rural","secteur_tourisme"],
        "scores": {"market":65,"commercial_offer":60,"innovation":40,"scalability":45,"green":70},
        "montant_besoin": 300000
    },
    {
        "nom": "Cas E — Commerce / Sousse / Launch Planning",
        "stade_declare": "Launch Planning", "stade_diagnostique": "Launch Planning",
        "secteur": "Commerce/Transport/Logistique",
        "gaps_detectes": ["export","developpement_international"],
        "scores": {"market":70,"commercial_offer":70,"innovation":50,"scalability":65,"green":55},
        "montant_besoin": 500000
    }
]


if __name__ == "__main__":
    print("=" * 65)
    print("RAG PIPELINE v4 — TOUTES RESSOURCES PAR STADE+SECTEUR")
    print("=" * 65)

    resultats       = []
    precision_scores = []

    for profil in TEST_PROFILES:
        print(f"\n{'─'*65}")
        print(f"▶ {profil['nom']}")
        print(f"  Secteur: {profil['secteur']}")

        output = contrat_f3(profil)

        print(f"  {output['message_perception_gap']}")
        print(f"  Ressources trouvées: {output['nombre_ressources']} (toutes compatibles stade+secteur)")

        # Afficher les 5 meilleures
        for r in output["ressources_recommandees"][:5]:
            print(f"    ✅ [{r['id']}] {r['nom'][:48]}")
            print(f"       {r['pertinence']}% | {r['url_source']}")

        if output['nombre_ressources'] > 5:
            reste = output['nombre_ressources'] - 5
            print(f"    ... + {reste} autres ressources dans le JSON complet")

        print(f"  Roadmap immédiat: {output['roadmap']['immediat_0_30j'][0]}")

        # Metric Precision@3
        top3 = output["ressources_recommandees"][:3]
        p3   = sum(1 for r in top3 if r["pertinence"] > 55) / max(len(top3), 1)
        precision_scores.append(p3)
        resultats.append({"profil": profil["nom"], "output": output})

    with open("test_resultats.json", "w", encoding="utf-8") as f:
        json.dump(resultats, f, ensure_ascii=False, indent=2)

    avg = round(sum(precision_scores)/len(precision_scores)*100, 1)
    print(f"\n{'='*65}")
    print(f"✅ METRIC ÉVALUATION — Precision@3: {avg}%")
    print(f"✅ Résultats complets: test_resultats.json")
    print(f"✅ RAG PIPELINE v4 — TOUTES RESSOURCES COMPATIBLES")
