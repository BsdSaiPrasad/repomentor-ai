import os
import json
import math

RAG_PROVIDER = os.getenv("RAG_PROVIDER", "local").lower()

CHROMA_PATH = os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))), "chroma_db")
VERTEX_INDEX_PATH = os.path.join(
    os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))),
    "vertex_index.json",
)

if RAG_PROVIDER != "vertex":
    import chromadb

    client = chromadb.PersistentClient(path=CHROMA_PATH)

def get_collection():
    """Get or create the syllabus collection in ChromaDB."""
    return client.get_or_create_collection(name="syllabus")


def _write_vertex_index(chunks: list[str], embeddings: list[list[float]]):
    payload = {"documents": chunks, "embeddings": embeddings}
    with open(VERTEX_INDEX_PATH, "w", encoding="utf-8") as handle:
        json.dump(payload, handle)


def _read_vertex_index() -> dict:
    with open(VERTEX_INDEX_PATH, "r", encoding="utf-8") as handle:
        return json.load(handle)


def _cosine_similarity(left: list[float], right: list[float]) -> float:
    numerator = sum(a * b for a, b in zip(left, right))
    left_norm = math.sqrt(sum(a * a for a in left))
    right_norm = math.sqrt(sum(b * b for b in right))
    if left_norm == 0 or right_norm == 0:
        return 0.0
    return numerator / (left_norm * right_norm)

def store_chunks(chunks: list[str], embeddings: list[list[float]]):
    """
    Save chunks and their embeddings into ChromaDB.
    
    Example:
        chunks = ["Week 1 covers GenAI basics"]
        embeddings = [[0.1, 0.4, 0.2, ...]]  # 384 numbers
        store_chunks(chunks, embeddings)
        # Now saved in ChromaDB, ready to search
    """
    if RAG_PROVIDER == "vertex":
        _write_vertex_index(chunks, embeddings)
        return

    collection = get_collection()
    ids = [f"chunk_{i}" for i in range(len(chunks))]
    collection.upsert(documents=chunks, embeddings=embeddings, ids=ids)

def query_chunks(query_embedding: list[float], k: int = 5) -> list[str]:
    """
    Find the k most relevant chunks for a given query embedding.
    
    Example:
        # Ask about Week 3
        results = query_chunks(query_embedding, k=3)
        # Returns top 3 most relevant syllabus chunks
    """
    if RAG_PROVIDER == "vertex":
        payload = _read_vertex_index()
        documents = payload.get("documents", [])
        embeddings = payload.get("embeddings", [])

        ranked = sorted(
            zip(documents, embeddings, strict=False),
            key=lambda item: _cosine_similarity(query_embedding, item[1]),
            reverse=True,
        )
        return [doc for doc, _embedding in ranked[:k]]

    collection = get_collection()
    results = collection.query(query_embeddings=[query_embedding], n_results=k)
    return results["documents"][0]
