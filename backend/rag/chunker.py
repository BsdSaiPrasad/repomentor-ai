def chunk_text(text: str, chunk_size: int = 100, overlap: int = 20) -> list[str]:
    """
    Split a long text into smaller overlapping chunks.
    
    >>> chunks = chunk_text("hello world", chunk_size=5, overlap=1)
    >>> len(chunks) > 0
    True
    """
    words = text.split()
    chunks = []
    start = 0

    while start < len(words):
        end = start + chunk_size
        chunk = " ".join(words[start:end])
        chunks.append(chunk)
        start += chunk_size - overlap

    return chunks


def load_and_chunk_file(filepath: str) -> list[str]:
    """Load a text file and return it as chunks."""
    with open(filepath, "r") as f:
        text = f.read()
    return chunk_text(text)
