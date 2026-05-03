import chromadb
import os

CHROMA_PATH = os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))), "chroma_db")

client = chromadb.PersistentClient(path=CHROMA_PATH)

def get_collection():
    """Get or create the syllabus collection in ChromaDB."""
    return client.get_or_create_collection(name="syllabus")

def store_chunks(chunks: list[str], embeddings: list[list[float]]):
    """
    Save chunks and their embeddings into ChromaDB.
    
    Example:
        chunks = ["Week 1 covers GenAI basics"]
        embeddings = [[0.1, 0.4, 0.2, ...]]  # 384 numbers
        store_chunks(chunks, embeddings)
        # Now saved in ChromaDB, ready to search
    """
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
    collection = get_collection()
    results = collection.query(query_embeddings=[query_embedding], n_results=k)
    return results["documents"][0]
