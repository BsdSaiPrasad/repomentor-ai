from backend.rag.embedder import embed_query
from backend.rag.vector_store import query_chunks

def retrieve(query: str, k: int = 5) -> list[str]:
    """
    Given a user question, find the most relevant syllabus chunks.
    
    Example:
        question = "What topics are covered in Week 3?"
        chunks = retrieve(question, k=3)
        # Returns 3 most relevant pieces of the syllabus
    """
    query_embedding = embed_query(query)
    return query_chunks(query_embedding, k=k)
