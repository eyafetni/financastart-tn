"""
search_kb.py — Moteur de recherche RAG
Inspiré de technovangelist/videoprojects/2024-04-04-build-rag-with-python/search.py
Adapté: sentence-transformers + anthropic au lieu de ollama
"""

import sys
import json
import chromadb
import anthropic
from sentence_transformers import SentenceTransformer

COLLECTION_NAME = "tunisian_resources"
EMBED_MODEL     = "paraphrase-multilingual-MiniLM-L12-v2"
TOP_K           = 5

def search(gaps: list, stade: str, scores: dict, montant: int = None):
    # 1. Charger ChromaDB (même logique que technovangelist)
    chroma = chromadb.PersistentClient(path="./chromadb")
    collection = chroma.get_or_create_collection(COLLECTION_NAME)
    model = SentenceTransformer(EMBED_MODEL)

    # 2. Construire la requête (remplace sys.argv de technovangelist)
    scores_faibles = [k for k, v in scores.items() if v < 50]
    query = (
        f"Entrepreneur stade {stade}. "
        f"Gaps: {', '.join(gaps)}. "
        f"Scores faibles: {', '.join(scores_faibles)}. "
        f"Financement Tunisie PME startup"
    )

    # 3. Embedding requête (remplace ollama.embeddings)
    queryembed = model.encode([query])[0].tolist()

    # 4. Recherche ChromaDB (identique à technovangelist)
    results = collection.query(
        query_embeddings=[queryembed],
        n_results=TOP_K * 2,
        include=["documents", "metadatas", "distances"]
    )

    # 5. Filtrage stade + montant
    stades_order = ["Ideation","Market Validation","Structuration",
                    "Fundraising","Launch Planning","Growth"]
    idx = stades_order.index(stade) if stade in stades_order else 2
    stades_cibles = set()
    for offset in [-1, 0, 1]:
        i = idx + offset
        if 0 <= i < len(stades_order):
            stades_cibles.add(stades_order[i])

    ressources = []
    for meta, doc, dist in zip(
        results["metadatas"][0],
        results["documents"][0],
        results["distances"][0]
    ):
        stades_fiche = set(meta["stades"].split("|"))
        if not stades_cibles.intersection(stades_fiche):
            continue
        if montant:
            mmax = int(meta["montant_max"] or 0)
            mmin = int(meta["montant_min"] or 0)
            if mmax > 0 and montant > mmax: continue
            if mmin > 0 and montant < mmin: continue

        pertinence = round((1 - dist) * 100, 1)
        ressources.append({
            "id": meta["id"],
            "nom": meta["nom"],
            "organisme": meta["organisme"],
            "url": meta["url_source"],
            "taux": meta["taux"],
            "pertinence": pertinence,
            "justification": f"Adresse les gaps: {', '.join([g for g in gaps if g in meta['gaps'].split('|')])}. Score RAG: {pertinence}%"
        })

    ressources.sort(key=lambda x: x["pertinence"], reverse=True)
    ressources = ressources[:TOP_K]

    # 6. Génération réponse (remplace ollama.generate de technovangelist)
    client = anthropic.Anthropic()
    
    docs_context = "\n\n".join([
        f"[{r['id']}] {r['nom']} ({r['organisme']})\nURL: {r['url']}\nPertinence: {r['pertinence']}%"
        for r in ressources
    ])

    # Même logique que technovangelist: query + docs → réponse
    modelquery = (
        f"Entrepreneur en phase '{stade}', gaps: {', '.join(gaps)}. "
        f"Réponds UNIQUEMENT en te basant sur ces ressources tunisiennes vérifiées:\n\n{docs_context}"
    )

    response = client.messages.create(
        model="claude-sonnet-4-6",
        max_tokens=600,
        system=(
            "Tu es conseiller entrepreneuriat Tunisie. "
            "Réponds uniquement avec les ressources fournies. "
            "Cite toujours l'ID et l'URL. Jamais d'invention."
        ),
        messages=[{"role": "user", "content": modelquery}]
    )

    return {
        "ressources": ressources,
        "reponse_llm": response.content[0].text,
        "sources": [r["url"] for r in ressources]
    }


if __name__ == "__main__":
    # Test rapide depuis terminal: python search_kb.py
    resultat = search(
        gaps=["manque_apport_personnel", "structuration_incomplete"],
        stade="Structuration",
        scores={"market": 40, "innovation": 55, "scalability": 30, "green": 60},
        montant=200000
    )
    print("\n=== RESSOURCES RECOMMANDÉES ===")
    for r in resultat["ressources"]:
        print(f"  [{r['id']}] {r['nom']} — {r['pertinence']}%")
        print(f"       {r['url']}")
    print("\n=== RÉPONSE ASSISTANT ===")
    print(resultat["reponse_llm"])
