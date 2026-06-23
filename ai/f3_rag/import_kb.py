"""
import_kb.py — Indexation ChromaDB
Inspiré de technovangelist/videoprojects/2024-04-04-build-rag-with-python
Adapté pour Codespaces: sentence-transformers au lieu de Ollama
"""

import json
import chromadb
from sentence_transformers import SentenceTransformer

# ── CONFIG ──────────────────────────────────────────────────────
KB_FILE         = "ressources_rag_final.json"
COLLECTION_NAME = "tunisian_resources"
EMBED_MODEL     = "paraphrase-multilingual-MiniLM-L12-v2"  # multilingue FR+AR
# ────────────────────────────────────────────────────────────────

def build_index():
    # 1. Charger la KB
    print("▶ Chargement KB...")
    with open(KB_FILE, encoding="utf-8") as f:
        ressources = json.load(f)
    print(f"  {len(ressources)} fiches chargées")

    # 2. ChromaDB local persistant (comme technovangelist mais PersistentClient)
    print("▶ Init ChromaDB...")
    chroma = chromadb.PersistentClient(path="./chromadb")
    
    # Supprimer si existe déjà (rebuild propre)
    try:
        chroma.delete_collection(COLLECTION_NAME)
        print("  Collection existante supprimée")
    except Exception:
        pass

    collection = chroma.get_or_create_collection(
        name=COLLECTION_NAME,
        metadata={"hnsw:space": "cosine"}  # même param que technovangelist
    )

    # 3. Modèle d'embedding (remplace ollama.embeddings de technovangelist)
    print(f"▶ Chargement modèle embedding ({EMBED_MODEL})...")
    model = SentenceTransformer(EMBED_MODEL)

    # 4. Préparer documents
    ids, documents, metadatas = [], [], []

    for r in ressources:
        texte = r.get("texte_complet", r.get("nom", ""))
        
        meta = {
            "id":         r["id"],
            "nom":        r["nom"],
            "organisme":  r["organisme"],
            "type":       r["type"],
            "stades":     "|".join(r.get("stades_eligibles", [])),
            "gaps":       "|".join(r.get("gaps_adresses", [])),
            "montant_min": str(r.get("montant_min") or 0),
            "montant_max": str(r.get("montant_max") or 0),
            "url_source":  r.get("url_source", ""),
            "taux":        str(r.get("taux", "")),
        }

        ids.append(r["id"])
        documents.append(texte)
        metadatas.append(meta)

    # 5. Générer embeddings
    print(f"▶ Génération embeddings ({len(ids)} fiches)...")
    embeddings = model.encode(documents, show_progress_bar=True).tolist()

    # 6. Insérer dans ChromaDB
    print("▶ Insertion ChromaDB...")
    collection.add(
        ids=ids,
        documents=documents,
        metadatas=metadatas,
        embeddings=embeddings
    )

    print(f"\n✅ Index créé: {collection.count()} documents dans ChromaDB")
    print(f"✅ Persisté dans ./chromadb/")

if __name__ == "__main__":
    build_index()
