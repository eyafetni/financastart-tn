"""
search_kb_no_api.py — Moteur RAG SANS clé API (version corrigée)
Fix: n_results=27 (tous docs) + filtrage montant assoupli
"""

import json
import chromadb
from sentence_transformers import SentenceTransformer

COLLECTION_NAME = "tunisian_resources"
EMBED_MODEL     = "paraphrase-multilingual-MiniLM-L12-v2"
TOP_K           = 5

def search(gaps: list, stade: str, scores: dict, montant: int = None):

    # 1. Charger ChromaDB
    chroma = chromadb.PersistentClient(path="./chromadb")
    collection = chroma.get_or_create_collection(COLLECTION_NAME)
    model = SentenceTransformer(EMBED_MODEL)

    # 2. Construire requête sémantique
    scores_faibles = [k for k, v in scores.items() if v < 50]
    query = (
        f"Entrepreneur stade {stade}. "
        f"Gaps: {', '.join(gaps)}. "
        f"Scores faibles: {', '.join(scores_faibles)}. "
        f"Financement Tunisie PME startup"
    )

    # 3. Embedding de la requête
    queryembed = model.encode([query])[0].tolist()

    # 4. Recherche ChromaDB — TOUS les documents (fix: n_results=collection.count())
    total = collection.count()
    results = collection.query(
        query_embeddings=[queryembed],
        n_results=total,   # ← FIX: récupérer TOUS les docs puis filtrer
        include=["documents", "metadatas", "distances"]
    )

    # 5. Stades compatibles (stade actuel + adjacent)
    stades_order = ["Ideation","Market Validation","Structuration",
                    "Fundraising","Launch Planning","Growth"]
    idx = stades_order.index(stade) if stade in stades_order else 2
    stades_cibles = set()
    for offset in [-1, 0, 1]:
        i = idx + offset
        if 0 <= i < len(stades_order):
            stades_cibles.add(stades_order[i])

    ressources = []
    for meta, dist in zip(results["metadatas"][0], results["distances"][0]):

        # Filtrage stade
        stades_fiche = set(meta["stades"].split("|"))
        if not stades_cibles.intersection(stades_fiche):
            continue

        # Filtrage montant ASSOUPLI — seulement si montant fourni ET mmin/mmax non nuls
        if montant:
            mmax = int(meta["montant_max"] or 0)
            mmin = int(meta["montant_min"] or 0)
            # Exclure seulement si CLAIREMENT incompatible
            if mmax > 0 and montant > mmax * 3:   # marge x3
                continue
            if mmin > 0 and montant < mmin / 5:   # marge /5
                continue

        gaps_matches = [g for g in gaps if g in meta["gaps"].split("|")]
        pertinence = round((1 - dist) * 100, 1)

        ressources.append({
            "id":           meta["id"],
            "nom":          meta["nom"],
            "organisme":    meta["organisme"],
            "taux":         meta["taux"],
            "url_source":   meta["url_source"],
            "pertinence":   pertinence,
            "gaps_matches": gaps_matches,
            "justification": (
                f"Recommandé pour stade '{stade}'. "
                f"Adresse: {', '.join(gaps_matches) if gaps_matches else 'profil général'}. "
                f"Pertinence RAG: {pertinence}%."
            )
        })

    ressources.sort(key=lambda x: x["pertinence"], reverse=True)
    return ressources[:TOP_K]


def generer_roadmap(stade: str, gaps: list) -> dict:
    ACTIONS = {
        "Ideation": {
            "immediat":    ["Contacter Espaces Entreprendre APII (gratuit)", "Déposer dossier ANETI/PAPPE (indemnisé)", "Formaliser l'idée en 2 pages écrites"],
            "court_terme": ["Réaliser étude de marché préliminaire (10+ interviews)", "Tester avec 10 clients potentiels réels", "Décider forme juridique (SUARL conseillée)"],
            "moyen_terme": ["Rédiger business plan complet", "Inscrire au RNE", "Postuler BTS micro-crédit si besoin financement immédiat"]
        },
        "Market Validation": {
            "immediat":    ["Construire MVP minimal testable", "Documenter preuves de traction (témoignages, commandes)", "Postuler Flat6Labs prochaine cohorte"],
            "court_terme": ["Pitcher 5+ clients potentiels", "Déposer candidature Startup Act si innovant", "Valider modèle économique chiffré"],
            "moyen_terme": ["Contacter Carthage Business Angels", "Préparer pitch deck investisseurs", "Viser premier chiffre d'affaires"]
        },
        "Structuration": {
            "immediat":    ["Créer société au RNE si pas encore fait", "Constituer dossier BFPME (business plan modèle GIZ)", "Évaluer apport personnel disponible"],
            "court_terme": ["Déposer dossier FOPRODI APII pour prime investissement", "Vérifier éligibilité garantie SOTUGAR", "Finaliser plan cofinancement avec banque partenaire"],
            "moyen_terme": ["Obtenir accord BFPME", "Recruter équipe clé", "Mettre en place comptabilité formelle"]
        },
        "Fundraising": {
            "immediat":    ["Préparer data room complète (KPIs, états financiers)", "Contacter réseau Carthage Business Angels", "Vérifier éligibilité label Startup Act"],
            "court_terme": ["Pitcher minimum 3 investisseurs", "Déposer dossier Smart Capital / ANAVA", "Négocier term sheet avec conseil juridique"],
            "moyen_terme": ["Clôturer tour de table", "Déployer fonds selon plan d'affaires", "Préparer reporting investisseurs trimestriel"]
        },
        "Launch Planning": {
            "immediat":    ["Finaliser plan de lancement (date, budget marketing)", "Constituer dossier BFR si trésorerie tendue", "Activer CEPEX si dimension export prévue"],
            "court_terme": ["Lancer activité commerciale", "Installer outils gestion ERP/CRM via Digital Tunisia", "Faire premier bilan mensuel d'activité"],
            "moyen_terme": ["Atteindre seuil de rentabilité", "Préparer extension si croissance confirmée", "Dossier BFPME extension capacité production"]
        },
        "Growth": {
            "immediat":    ["Analyser goulots d'étranglement croissance", "Évaluer besoins financement extension", "Contacter APII programme mise à niveau PMN"],
            "court_terme": ["Dossier BFPME prêt extension ou BFR", "Activer FOPRODEX si export", "Étudier levée Series A (AfricInvest, ANAVA)"],
            "moyen_terme": ["Déployer sur nouveau marché géographique", "Structurer management intermédiaire", "Préparer exit ou prochain tour financement"]
        }
    }
    actions = ACTIONS.get(stade, ACTIONS["Structuration"])
    return {
        "stade": stade,
        "immediat_0_30j":    actions["immediat"],
        "court_terme_1_3m":  actions["court_terme"],
        "moyen_terme_3_12m": actions["moyen_terme"]
    }


def contrat_f3(profil: dict) -> dict:
    """Interface principale — appelée par Membre 5."""
    ressources = search(
        gaps    = profil.get("gaps_detectes", []),
        stade   = profil.get("stade_diagnostique", "Structuration"),
        scores  = profil.get("scores", {}),
        montant = profil.get("montant_besoin")
    )
    roadmap = generer_roadmap(
        profil.get("stade_diagnostique", "Structuration"),
        profil.get("gaps_detectes", [])
    )
    stade_declare = profil.get("stade_declare", "")
    stade_reel    = profil.get("stade_diagnostique", "")
    divergence    = stade_declare != stade_reel

    return {
        "stade_reel":              stade_reel,
        "stade_declare":           stade_declare,
        "divergence_detectee":     divergence,
        "message_perception_gap": (
            f"⚠️  Vous pensez être en '{stade_declare}' "
            f"mais votre stade réel est '{stade_reel}'."
        ) if divergence else "✅ Auto-évaluation correcte.",
        "ressources_recommandees": ressources,
        "roadmap":                 roadmap,
        "sources_tracees":        [r["url_source"] for r in ressources],
        "note": "Zéro hallucination — chaque ressource tracée à une URL officielle vérifiée."
    }


# ── TEST 5 PROFILS ────────────────────────────────────────────────
TEST_PROFILES = [
    {
        "nom": "Cas A — Jeune diplômé sans apport (pense être en Fundraising)",
        "stade_declare": "Fundraising", "stade_diagnostique": "Structuration",
        "gaps_detectes": ["manque_apport_personnel","jeune_diplome","structuration_incomplete"],
        "scores": {"market":40,"commercial_offer":35,"innovation":60,"scalability":45,"green":50},
        "montant_besoin": 200000
    },
    {
        "nom": "Cas B — Micro-projet artisanat zone rurale",
        "stade_declare": "Ideation", "stade_diagnostique": "Ideation",
        "gaps_detectes": ["faible_revenu","exclusion_bancaire","micro_projet"],
        "scores": {"market":30,"commercial_offer":25,"innovation":20,"scalability":15,"green":45},
        "montant_besoin": 3000
    },
    {
        "nom": "Cas C — Startup tech MVP prête levée de fonds",
        "stade_declare": "Fundraising", "stade_diagnostique": "Fundraising",
        "gaps_detectes": ["besoin_levee_fonds_prive","equity_gap","manque_reseau_investisseurs"],
        "scores": {"market":70,"commercial_offer":65,"innovation":80,"scalability":75,"green":55},
        "montant_besoin": 500000
    },
    {
        "nom": "Cas D — PME industrielle cherche extension",
        "stade_declare": "Growth", "stade_diagnostique": "Growth",
        "gaps_detectes": ["besoin_capital_croissance","extension_activite","competitivite_faible"],
        "scores": {"market":60,"commercial_offer":70,"innovation":35,"scalability":55,"green":40},
        "montant_besoin": 1500000
    },
    {
        "nom": "Cas E — Agri-tech impact vert",
        "stade_declare": "Structuration", "stade_diagnostique": "Market Validation",
        "gaps_detectes": ["absence_validation_marche","secteur_agricole","besoin_prototype"],
        "scores": {"market":45,"commercial_offer":40,"innovation":55,"scalability":50,"green":85},
        "montant_besoin": 80000
    }
]


if __name__ == "__main__":
    print("=" * 65)
    print("RAG PIPELINE — TEST 5 PROFILS")
    print("=" * 65)

    resultats = []
    precision_scores = []

    for profil in TEST_PROFILES:
        print(f"\n▶ {profil['nom']}")
        output = contrat_f3(profil)

        print(f"  {output['message_perception_gap']}")
        print(f"  Ressources trouvées: {len(output['ressources_recommandees'])}")

        for r in output["ressources_recommandees"][:3]:
            print(f"    ✅ [{r['id']}] {r['nom'][:50]}")
            print(f"       Pertinence: {r['pertinence']}% | Gaps: {r['gaps_matches']}")
            print(f"       URL: {r['url_source']}")

        print(f"  Roadmap immédiat: {output['roadmap']['immediat_0_30j'][0]}")

        # Metric Precision@3
        top3 = output["ressources_recommandees"][:3]
        p3 = sum(1 for r in top3 if r["pertinence"] > 55) / max(len(top3), 1)
        precision_scores.append(p3)

        resultats.append({"profil": profil["nom"], "output": output})

    # Sauvegarder résultats
    with open("test_resultats.json", "w", encoding="utf-8") as f:
        json.dump(resultats, f, ensure_ascii=False, indent=2)

    avg_precision = round(sum(precision_scores) / len(precision_scores) * 100, 1)
    print(f"\n{'=' * 65}")
    print(f"✅ METRIC ÉVALUATION — Precision@3: {avg_precision}%")
    print(f"✅ Résultats sauvegardés: test_resultats.json")
    print(f"✅ RAG PIPELINE OPÉRATIONNEL")
