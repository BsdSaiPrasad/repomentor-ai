import pytest
from backend.rag.chunker import chunk_text


def test_short_text_returns_one_chunk():
    text = "Hello world"
    chunks = chunk_text(text, chunk_size=100, overlap=10)
    assert len(chunks) == 1


def test_chunk_size_is_respected():
    text = "word " * 200
    chunks = chunk_text(text, chunk_size=50, overlap=10)
    for chunk in chunks:
        assert len(chunk.split()) <= 50


def test_overlap_means_chunks_share_words():
    text = "word " * 100
    chunks = chunk_text(text, chunk_size=20, overlap=5)
    end_of_first = chunks[0].split()[-5:]
    start_of_second = chunks[1].split()[:5]
    assert end_of_first == start_of_second


def test_empty_text_returns_empty_list():
    chunks = chunk_text("", chunk_size=100, overlap=10)
    assert chunks == []


def test_returns_list_of_strings():
    chunks = chunk_text("some sample text here", chunk_size=100, overlap=10)
    assert isinstance(chunks, list)
    assert all(isinstance(c, str) for c in chunks)
