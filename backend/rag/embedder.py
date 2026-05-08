import os
from functools import lru_cache


RAG_PROVIDER = os.getenv("RAG_PROVIDER", "local").lower()


@lru_cache(maxsize=1)
def _get_local_model():
    from sentence_transformers import SentenceTransformer

    return SentenceTransformer("all-MiniLM-L6-v2")


@lru_cache(maxsize=1)
def _get_vertex_client():
    from google import genai
    from google.genai.types import HttpOptions

    os.environ.setdefault("GOOGLE_GENAI_USE_VERTEXAI", "True")
    os.environ.setdefault(
        "GOOGLE_CLOUD_LOCATION", os.getenv("GOOGLE_CLOUD_LOCATION", "us-central1")
    )
    project = os.getenv("GOOGLE_CLOUD_PROJECT")
    location = os.getenv("GOOGLE_CLOUD_LOCATION", "us-central1")

    return genai.Client(
        vertexai=True,
        project=project,
        location=location,
        http_options=HttpOptions(api_version="v1"),
    )


def _vertex_embed_texts(
    chunks: list[str], *, task_type: str, title_prefix: str = "RepoMentor Chunk"
) -> list[list[float]]:
    from google.genai.types import EmbedContentConfig

    client = _get_vertex_client()
    embeddings: list[list[float]] = []

    for index, chunk in enumerate(chunks):
        response = client.models.embed_content(
            model="gemini-embedding-001",
            contents=chunk,
            config=EmbedContentConfig(
                task_type=task_type,
                output_dimensionality=768,
                title=f"{title_prefix} {index + 1}",
            ),
        )
        embeddings.append(response.embeddings[0].values)

    return embeddings

def embed_chunks(chunks: list[str]) -> list[list[float]]:
    """
    Convert a list of text chunks into embedding vectors.
    
    Example:
        chunks = ["Week 1 covers GenAI basics", "Week 2 covers Git"]
        vectors = embed_chunks(chunks)
        # vectors is now a list of 384-number arrays representing meaning
    """
    if RAG_PROVIDER == "vertex":
        return _vertex_embed_texts(chunks, task_type="RETRIEVAL_DOCUMENT")

    embeddings = _get_local_model().encode(chunks, show_progress_bar=True)
    return embeddings.tolist()


def embed_query(query: str) -> list[float]:
    if RAG_PROVIDER == "vertex":
        return _vertex_embed_texts(
            [query], task_type="RETRIEVAL_QUERY", title_prefix="RepoMentor Query"
        )[0]

    return _get_local_model().encode(query).tolist()
