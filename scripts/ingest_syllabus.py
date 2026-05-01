import sys
import os

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from backend.rag.chunker import load_and_chunk_file
from backend.rag.embedder import embed_chunks
from backend.rag.vector_store import store_chunks

def ingest():
    files = ["docs/syllabus.txt", "docs/schedule.txt"]
    all_chunks = []

    for filepath in files:
        print(f"Loading {filepath}...")
        chunks = load_and_chunk_file(filepath)
        all_chunks.extend(chunks)
        print(f"  Got {len(chunks)} chunks")

    print(f"Total chunks: {len(all_chunks)}")
    print("Generating embeddings...")
    embeddings = embed_chunks(all_chunks)
    print("Storing in ChromaDB...")
    store_chunks(all_chunks, embeddings)
    print("Done! Syllabus and schedule are now searchable.")

if __name__ == "__main__":
    ingest()
