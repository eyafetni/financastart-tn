"""
============================================================
MEMBRE 3 — RAG PIPELINE COMPLET
AINS Hackathon 2026 – AI for Entrepreneurship
============================================================
Étape 1: Index ChromaDB
Étape 2: Moteur RAG (gaps + scores → ressources tracées)
Étape 3: Contrat F3 (sortie JSON pour Membre 5)
============================================================

INSTALLATION:
    pip install chromadb sentence-transformers anthropic python-dotenv

USAGE:
    python rag_pipeline.py
"""

import json
import os
from typing import Any

# ─── CONFIG ──────────────────────────────────────────────────────────────────
KB_FILE        = "ressources_rag_final.json"     # ta KB finale
CHROMA_DIR     = "./chroma_db"                   # dossier persistance ChromaDB
COLLECTION_NAME = "tunisian_resources"
EMBED_MODEL    = "paraphrase-multilingual-MiniLM-L12-v2"  # multilingue FR+AR
TOP_K          = 40  # ressources retournées par requête


# ─── ÉTAPE 1: INDEXATION CHROMADB ────────────────────────────────────────────
def build_chromadb_index(kb_path: str = KB_FILE) -> Any:
    """
    Charge les fiches JSON et les indexe dans ChromaDB.
    Chaque fiche → 1 document avec embedding sur texte_complet.
    
    Returns: ChromaDB collection
    """
    import chromadb
    from sentence_transformers import SentenceTransformer

    print("▶ Chargement de la base de connaissances...")
    with open(kb_path, encoding="utf-8") as f:
        ressources = json.load(f)
    print(f"  {len(ressources)} fiches chargées")

    print("▶ Initialisation ChromaDB...")
    client = chromadb.PersistentClient(path=CHROMA_DIR)

    # Supprimer et recréer si déjà existante (idempotent)
    try:
        client.delete_collection(COLLECTION_NAME)
        print("  Collection existante supprimée (rebuild)")
    except Exception:
        pass

    collection = client.create_collection(
        name=COLLECTION_NAME,
        metadata={"hnsw:space": "cosine"}  # similarité cosinus
    )

    print(f"▶ Chargement modèle embedding ({EMBED_MODEL})...")
    model = SentenceTransformer(EMBED_MODEL)

    # Préparer les données pour ChromaDB
    ids, documents, metadatas, embeddings = [], [], [], []

    for r in ressources:
        # Texte principal pour l'embedding
        texte = r.get("texte_complet", r.get("nom", ""))

        # Métadonnées filtrables (tout en string pour ChromaDB)
        meta = {
            "id":           r["id"],
            "nom":          r["nom"],
            "organisme":    r["organisme"],
            "type":         r["type"],
            "stades":       "|".join(r.get("stades_eligibles", [])),
            "gaps":         "|".join(r.get("gaps_adresses", [])),
            "montant_min":  str(r.get("montant_min") or 0),
            "montant_max":  str(r.get("montant_max") or 0),
            "devise":       r.get("devise", "TND"),
            "taux":         str(r.get("taux", "")),
            "url_source":   r.get("url_source", ""),
            "categorie":    r.get("categorie", ""),
        }

        ids.append(r["id"])
        documents.append(texte)
        metadatas.append(meta)

    print(f"▶ Génération des embeddings ({len(ids)} fiches)...")
    embs = model.encode(documents, show_progress_bar=True, batch_size=16)
    embeddings = [e.tolist() for e in embs]

    print("▶ Insertion dans ChromaDB...")
    collection.add(
        ids=ids,
        documents=documents,
        metadatas=metadatas,
        embeddings=embeddings
    )

    print(f"✅ Index ChromaDB créé: {collection.count()} documents\n")
    return collection, model


# ─── ÉTAPE 2: MOTEUR RAG ─────────────────────────────────────────────────────
def load_collection():
    """Charge la collection ChromaDB existante (après build)."""
    import chromadb
    from sentence_transformers import SentenceTransformer
    client = chromadb.PersistentClient(path=CHROMA_DIR)
    collection = client.get_collection(COLLECTION_NAME)
    model = SentenceTransformer(EMBED_MODEL)
    return collection, model


def query_rag(
    collection,
    model,
    gaps: list[str],
    stade_actuel: str,
    scores: dict,
    montant_besoin: int = None,
    top_k: int = TOP_K
) -> dict:
    """
    Moteur RAG principal.
    
    Reçoit:
        gaps          → liste de gaps détectés par le diagnostic (ex: ["manque_apport","structuration_incomplete"])
        stade_actuel  → stade réel diagnostiqué (ex: "Structuration")
        scores        → dict scores Feature 2 (ex: {"market":45,"scalability":30,"green":60,...})
        montant_besoin→ montant financement cherché en TND (optionnel)
    
    Retourne:
        dict F3 (contrat Membre 5):
            - ressources_recommandees: list[dict] triées par pertinence
            - roadmap_actions: list ordonnée d'actions
            - explication_rag: texte traçable
    """

    # 1. Construire la requête sémantique à partir des gaps + scores faibles
    scores_faibles = [k for k, v in scores.items() if v < 50]
    
    requete_text = (
        f"Entrepreneur stade {stade_actuel}. "
        f"Gaps identifiés: {', '.join(gaps)}. "
        f"Scores faibles: {', '.join(scores_faibles)}. "
        f"Besoin financement Tunisie PME startup"
    )
    
    # 2. Embedding de la requête
    requete_embedding = model.encode([requete_text])[0].tolist()

    # 3. Filtrage dur par stade (where clause ChromaDB)
    # Inclure stade actuel + stades adjacents (±1)
    stades_order = ["Ideation","Market Validation","Structuration","Fundraising","Launch Planning","Growth"]
    idx = stades_order.index(stade_actuel) if stade_actuel in stades_order else 2
    stades_cibles = set()
    for offset in [-1, 0, 1]:
        i = idx + offset
        if 0 <= i < len(stades_order):
            stades_cibles.add(stades_order[i])

    # 4. Recherche sémantique dans ChromaDB
    results = collection.query(
        query_embeddings=[requete_embedding],
        n_results=min(top_k * 2, collection.count()),  # sursampling puis filtrage
        include=["documents", "metadatas", "distances"]
    )

    # 5. Post-filtrage: stade compatible + montant si fourni
    ressources_filtrees = []
    for meta, doc, dist in zip(
        results["metadatas"][0],
        results["documents"][0],
        results["distances"][0]
    ):
        stades_fiche = set(meta["stades"].split("|"))
        if not stades_cibles.intersection(stades_fiche):
            continue  # stade incompatible

        # Filtre montant optionnel
        if montant_besoin:
            mmin = int(meta["montant_min"] or 0)
            mmax = int(meta["montant_max"] or 0)
            if mmax > 0 and montant_besoin > mmax:
                continue  # trop grand
            if mmin > 0 and montant_besoin < mmin:
                continue  # trop petit

        score_pertinence = round((1 - dist) * 100, 1)  # distance cosinus → %
        
        ressources_filtrees.append({
            "id":               meta["id"],
            "nom":              meta["nom"],
            "organisme":        meta["organisme"],
            "type":             meta["type"],
            "categorie":        meta.get("categorie",""),
            "stades_eligibles": meta["stades"].split("|"),
            "montant_min":      int(meta["montant_min"] or 0),
            "montant_max":      int(meta["montant_max"] or 0),
            "taux":             meta["taux"],
            "devise":           meta["devise"],
            "url_source":       meta["url_source"],
            "score_pertinence": score_pertinence,
            "gaps_adresses_matches": [
                g for g in gaps
                if g in meta["gaps"].split("|")
            ],
            "justification": (
                f"Cette ressource est recommandée car elle correspond au stade {stade_actuel} "
                f"et adresse les gaps: {', '.join([g for g in gaps if g in meta['gaps'].split('|')])}. "
                f"Pertinence RAG: {score_pertinence}%."
            )
        })

    # Trier par score pertinence
    ressources_filtrees.sort(key=lambda x: x["score_pertinence"], reverse=True)
    ressources_finales = ressources_filtrees[:top_k]

    # 6. Générer roadmap ordonnée
    roadmap = _generer_roadmap(gaps, stade_actuel, scores, ressources_finales)

    return {
        "f3_output": {
            "stade_diagnostique": stade_actuel,
            "gaps_detectes": gaps,
            "scores_faibles": scores_faibles,
            "requete_rag": requete_text,
            "ressources_recommandees": ressources_finales,
            "roadmap_actions": roadmap,
            "sources_tracees": [r["url_source"] for r in ressources_finales],
            "note_tracabilite": (
                "Chaque recommandation est tracée à une source officielle vérifiée. "
                "Aucune information inventée. Toutes les URLs sont des sites officiels tunisiens."
            )
        }
    }


def _generer_roadmap(gaps, stade, scores, ressources):
    """Génère une roadmap ordonnée par horizon temporel."""
    
    # Roadmap selon stade
    ACTIONS_PAR_STADE = {
        "Ideation": {
            "immediat":    ["Formaliser l'idée projet sur papier (1-2 pages)", "Contacter Espaces Entreprendre APII (gratuit)", "Vérifier éligibilité programme ANETI/PAPPE"],
            "court_terme": ["Réaliser étude de marché préliminaire", "Constituer équipe fondatrice", "Déposer dossier BTS micro-crédit si besoin financement immédiat"],
            "moyen_terme": ["Structurer le business plan complet", "Décider forme juridique (SUARL conseillée pour 1er projet)", "Envisager label Startup Act si projet innovant"]
        },
        "Market Validation": {
            "immediat":    ["Tester hypothèses avec 10+ clients potentiels", "Construire un MVP minimal", "Documenter les preuves de traction"],
            "court_terme": ["Postuler Flat6Labs Tunis (prochaine cohorte)", "Déposer candidature Startup Act si innovant", "Établir premier modèle économique validé"],
            "moyen_terme": ["Préparer pitch deck pour investisseurs", "Contacter Carthage Business Angels", "Viser premier chiffre d'affaires"]
        },
        "Structuration": {
            "immediat":    ["Créer la société (RNE) si pas encore fait", "Constituer dossier BFPME (business plan modèle GIZ)", "Évaluer apport personnel disponible"],
            "court_terme": ["Déposer dossier FOPRODI APII pour prime investissement", "Vérifier éligibilité SOTUGAR (garantie)", "Finaliser plan de financement avec banque cofinancière"],
            "moyen_terme": ["Obtenir accord BFPME", "Lancer recrutement équipe clé", "Mettre en place comptabilité formelle"]
        },
        "Fundraising": {
            "immediat":    ["Préparer data room complète (états financiers, KPIs)", "Contacter réseau business angels (CBA)", "Vérifier éligibilité label Startup Act"],
            "court_terme": ["Pitcher 3+ investisseurs minimum", "Déposer dossier Smart Capital / ANAVA", "Négocier term sheet avec conseiller juridique"],
            "moyen_terme": ["Clôturer tour de table", "Utiliser fonds levés selon plan", "Préparer reporting investisseurs"]
        },
        "Launch Planning": {
            "immediat":    ["Finaliser plan de lancement (date, budget marketing)", "Constituer dossier BFR si trésorerie tendue", "Activer réseau CEPEX si export prévu"],
            "court_terme": ["Lancer activité commerciale", "Mettre en place outils gestion (ERP/CRM via Digital Tunisia)", "Premier bilan mensuel activité"],
            "moyen_terme": ["Atteindre seuil de rentabilité", "Préparer extension si croissance confirmée", "Dossier BFPME extension si besoin"]
        },
        "Growth": {
            "immediat":    ["Analyser goulots d'étranglement croissance", "Évaluer besoins financement extension", "Contacter APII programme mise à niveau (PMN)"],
            "court_terme": ["Dossier BFPME prêt extension ou BFR", "Activer FOPRODEX si export", "Étudier levée Series A (AfricInvest, ANAVA child funds)"],
            "moyen_terme": ["Déployer nouveau marché géographique", "Structurer management intermédiaire", "Préparer exit ou nouveau tour"]
        }
    }

    actions = ACTIONS_PAR_STADE.get(stade, ACTIONS_PAR_STADE["Structuration"])

    # Enrichir avec ressources trouvées
    if ressources:
        top = ressources[0]
        actions["immediat"].append(
            f"Action prioritaire: Contacter {top['organisme']} → {top['nom']} "
            f"({top['url_source']})"
        )

    return {
        "stade_actuel": stade,
        "immediat_0_30_jours":   actions["immediat"],
        "court_terme_1_3_mois":  actions["court_terme"],
        "moyen_terme_3_12_mois": actions["moyen_terme"],
        "ordre_logique": "Les actions immédiates débloquent les suivantes. Ne pas sauter d'étape."
    }


# ─── ÉTAPE 3: CONTRAT F3 (SORTIE POUR MEMBRE 5) ─────────────────────────────
def generer_contrat_f3(profil_entrepreneur: dict, collection, model) -> dict:
    """
    Interface principale F3 → appelée par Membre 5.
    
    Entrée (profil_entrepreneur):
        {
            "stade_diagnostique": "Structuration",      ← vient du Membre 1 (diagnostic)
            "stade_declare":      "Fundraising",         ← ce que l'entrepreneur croit
            "gaps_detectes":     ["manque_apport","business_model_flou"],
            "scores": {
                "market": 55, "commercial_offer": 40,
                "innovation": 35, "scalability": 30, "green": 70
            },
            "montant_besoin": 500000,                   ← optionnel
            "secteur": "Technologie",                   ← optionnel
            "description_projet": "Plateforme SaaS..."  ← optionnel
        }
    
    Sortie:
        Contrat F3 complet (ressources + roadmap + traçabilité)
    """
    result = query_rag(
        collection=collection,
        model=model,
        gaps=profil_entrepreneur.get("gaps_detectes", []),
        stade_actuel=profil_entrepreneur.get("stade_diagnostique", "Structuration"),
        scores=profil_entrepreneur.get("scores", {}),
        montant_besoin=profil_entrepreneur.get("montant_besoin"),
    )

    # Enrichir avec infos profil
    result["f3_output"]["profil_entrepreneur"] = profil_entrepreneur
    result["f3_output"]["perception_gap"] = {
        "stade_declare": profil_entrepreneur.get("stade_declare", "N/A"),
        "stade_reel": profil_entrepreneur.get("stade_diagnostique", "N/A"),
        "divergence_detectee": profil_entrepreneur.get("stade_declare") != profil_entrepreneur.get("stade_diagnostique"),
        "message": (
            f"⚠️ Vous pensez être en phase '{profil_entrepreneur.get('stade_declare')}' "
            f"mais notre diagnostic situe votre projet en phase '{profil_entrepreneur.get('stade_diagnostique')}'. "
            f"Voici les ressources adaptées à votre stade RÉEL."
        ) if profil_entrepreneur.get("stade_declare") != profil_entrepreneur.get("stade_diagnostique") else
        "✅ Votre auto-évaluation correspond à notre diagnostic."
    }

    return result["f3_output"]


# ─── TESTS AVEC 5 PROFILS FICTIFS ────────────────────────────────────────────
TEST_PROFILES = [
    {
        "nom_test": "Cas A — Jeune diplômé sans apport (pense être en Fundraising)",
        "stade_declare": "Fundraising",
        "stade_diagnostique": "Structuration",
        "gaps_detectes": ["manque_apport_personnel","jeune_diplome","business_model_flou","structuration_incomplete"],
        "scores": {"market": 40, "commercial_offer": 35, "innovation": 60, "scalability": 45, "green": 50},
        "montant_besoin": 200000,
        "secteur": "Technologie"
    },
    {
        "nom_test": "Cas B — Micro-projet artisanat zone rurale",
        "stade_declare": "Ideation",
        "stade_diagnostique": "Ideation",
        "gaps_detectes": ["faible_revenu","exclusion_bancaire","micro_projet","absence_business_plan"],
        "scores": {"market": 30, "commercial_offer": 25, "innovation": 20, "scalability": 15, "green": 45},
        "montant_besoin": 3000,
        "secteur": "Artisanat"
    },
    {
        "nom_test": "Cas C — Startup tech MVP prête pour levée de fonds",
        "stade_declare": "Fundraising",
        "stade_diagnostique": "Fundraising",
        "gaps_detectes": ["besoin_levee_fonds_prive","equity_gap","manque_reseau_investisseurs"],
        "scores": {"market": 70, "commercial_offer": 65, "innovation": 80, "scalability": 75, "green": 55},
        "montant_besoin": 500000,
        "secteur": "FinTech"
    },
    {
        "nom_test": "Cas D — PME industrielle cherche extension",
        "stade_declare": "Growth",
        "stade_diagnostique": "Growth",
        "gaps_detectes": ["besoin_capital_croissance","extension_activite","competitivite_faible"],
        "scores": {"market": 60, "commercial_offer": 70, "innovation": 35, "scalability": 55, "green": 40},
        "montant_besoin": 1500000,
        "secteur": "Industrie"
    },
    {
        "nom_test": "Cas E — Projet agri-tech à fort impact vert",
        "stade_declare": "Structuration",
        "stade_diagnostique": "Market Validation",
        "gaps_detectes": ["absence_validation_marche","secteur_agricole","innovation_score_faible","besoin_prototype"],
        "scores": {"market": 45, "commercial_offer": 40, "innovation": 55, "scalability": 50, "green": 85},
        "montant_besoin": 80000,
        "secteur": "AgriTech"
    }
]


# ─── MAIN ─────────────────────────────────────────────────────────────────────
if __name__ == "__main__":
    import sys

    mode = sys.argv[1] if len(sys.argv) > 1 else "full"

    if mode in ("build", "full"):
        print("=" * 60)
        print("ÉTAPE 1 — BUILD INDEX CHROMADB")
        print("=" * 60)
        collection, model = build_chromadb_index(KB_FILE)
    else:
        print("Chargement collection existante...")
        collection, model = load_collection()

    if mode in ("test", "full"):
        print("=" * 60)
        print("ÉTAPE 2 — TESTS RAG (5 PROFILS)")
        print("=" * 60)

        resultats = []
        for profil in TEST_PROFILES:
            print(f"\n▶ {profil['nom_test']}")
            result = generer_contrat_f3(profil, collection, model)

            # Afficher résumé
            gap_msg = result["perception_gap"]["message"]
            print(f"  Gap perception: {gap_msg[:100]}...")
            print(f"  Ressources trouvées: {len(result['ressources_recommandees'])}")
            for r in result["ressources_recommandees"][:3]:
                print(f"    → [{r['id']}] {r['nom'][:45]} | Score: {r['score_pertinence']}%")
            print(f"  Actions immédiates: {len(result['roadmap_actions']['immediat_0_30_jours'])}")

            resultats.append({
                "profil": profil["nom_test"],
                "output": result
            })

        # Sauvegarder résultats tests
        with open("test_rag_resultats.json", "w", encoding="utf-8") as f:
            json.dump(resultats, f, ensure_ascii=False, indent=2)
        print(f"\n✅ Résultats sauvegardés: test_rag_resultats.json")

    print("\n✅ PIPELINE RAG COMPLET")
