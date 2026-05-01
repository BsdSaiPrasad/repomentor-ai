from sentence_transformers import SentenceTransformer

model = SentenceTransformer("all-MiniLM-L6-v2")

def embed_chunks(chunks: list[str]) -> list[list[float]]:
    """
    Convert a list of text chunks into embedding vectors.
    
    Example:
        chunks = ["Week 1 covers GenAI basics", "Week 2 covers Git"]
        vectors = embed_chunks(chunks)
        # vectors is now a list of 384-number arrays representing meaning
    """
    embeddings = model.encode(chunks, show_progress_bar=True)
    return embeddings.tolist()
