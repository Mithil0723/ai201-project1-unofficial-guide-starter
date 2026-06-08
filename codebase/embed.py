"""
embed.py — Embedding & Vector Store
Pipeline stage 2: Embed chunks with all-MiniLM-L6-v2 and persist to ChromaDB.

Public API:
    build_index()          -> embed all documents and store in ChromaDB
    retrieve(query, k=5)   -> return top-k chunks as list of dicts
"""

import hashlib
from pathlib import Path

import chromadb
from chromadb.config import Settings
from sentence_transformers import SentenceTransformer

from ingest import load_documents

# --- Config ---------------------------------------------------------------

CHROMA_DIR = Path(__file__).parent / "chroma_store"
COLLECTION_NAME = "indian_food_health"
EMBEDDING_MODEL = "all-MiniLM-L6-v2"

# --------------------------------------------------------------------------

_model: SentenceTransformer | None = None
_collection: chromadb.Collection | None = None


def _get_model() -> SentenceTransformer:
    global _model
    if _model is None:
        print(f"[embed] Loading embedding model: {EMBEDDING_MODEL}")
        _model = SentenceTransformer(EMBEDDING_MODEL)
    return _model


def _get_collection(persist: bool = True) -> chromadb.Collection:
    global _collection
    if _collection is None:
        if persist:
            client = chromadb.PersistentClient(path=str(CHROMA_DIR))
        else:
            client = chromadb.EphemeralClient()
        _collection = client.get_or_create_collection(
            name=COLLECTION_NAME,
            metadata={"hnsw:space": "cosine"},
        )
    return _collection


def _chunk_id(source: str, chunk_index: int, text: str) -> str:
    """Stable, deterministic ID for a chunk so re-indexing is idempotent."""
    digest = hashlib.md5(text.encode()).hexdigest()[:8]
    return f"{source}__{chunk_index}__{digest}"


def build_index(force_rebuild: bool = False) -> None:
    """
    Load all documents, embed each chunk, and upsert into ChromaDB.
    Set force_rebuild=True to clear the collection before inserting.
    """
    collection = _get_collection()

    if force_rebuild:
        print("[embed] Clearing existing collection...")
        # Delete all existing documents
        existing = collection.get()
        if existing["ids"]:
            collection.delete(ids=existing["ids"])

    chunks = load_documents()
    if not chunks:
        print("[embed] No chunks to embed — aborting.")
        return

    model = _get_model()

    texts = [c["text"] for c in chunks]
    ids = [_chunk_id(c["source"], c["chunk_index"], c["text"]) for c in chunks]
    metadatas = [{"source": c["source"], "chunk_index": c["chunk_index"]} for c in chunks]

    # Embed in batches to avoid memory spikes
    batch_size = 64
    all_embeddings: list[list[float]] = []

    for i in range(0, len(texts), batch_size):
        batch = texts[i: i + batch_size]
        vecs = model.encode(batch, show_progress_bar=False).tolist()
        all_embeddings.extend(vecs)
        print(f"[embed] Embedded {min(i + batch_size, len(texts))}/{len(texts)} chunks")

    collection.upsert(
        ids=ids,
        documents=texts,
        embeddings=all_embeddings,
        metadatas=metadatas,
    )
    print(f"[embed] Index built: {len(texts)} chunks stored in ChromaDB at {CHROMA_DIR}")


def retrieve(query: str, k: int = 5) -> list[dict]:
    """
    Semantic search: return the top-k most relevant chunks for the query.

    Returns a list of dicts:
        {text, source, chunk_index, distance}
    """
    collection = _get_collection()
    if collection.count() == 0:
        return []

    model = _get_model()

    query_vec = model.encode([query]).tolist()

    results = collection.query(
        query_embeddings=query_vec,
        n_results=k,
        include=["documents", "metadatas", "distances"],
    )

    hits = []
    for doc, meta, dist in zip(
        results["documents"][0],
        results["metadatas"][0],
        results["distances"][0],
    ):
        hits.append({
            "text": doc,
            "source": meta["source"],
            "chunk_index": meta["chunk_index"],
            "distance": round(dist, 4),
        })

    return hits


if __name__ == "__main__":
    build_index()

    # Quick retrieval smoke-test
    test_query = "Why is turmeric anti-inflammatory?"
    print(f"\n[embed] Test query: '{test_query}'")
    hits = retrieve(test_query, k=3)
    for h in hits:
        print(f"\n  [{h['source']} chunk {h['chunk_index']} | dist={h['distance']}]")
        print(f"  {h['text'][:200]}")
