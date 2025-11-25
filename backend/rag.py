"""
RAG module.

Provides a simple helper function `query_kb` which:
- loads the Chroma collection built by ingestion.py
- embeds the user query
- returns the most relevant chunks as a single context string
"""

import os
from typing import List

import chromadb
from sentence_transformers import SentenceTransformer

BASE_DIR = os.path.dirname(os.path.dirname(__file__))
DB_DIR = os.path.join(BASE_DIR, "chroma_db")
COLLECTION_NAME = "qa_kb"

_embedder = SentenceTransformer("all-MiniLM-L6-v2")


def _get_collection() -> chromadb.Collection:
    """
    Open the existing Chroma collection.
    Assumes ingestion has already created it.
    """
    client = chromadb.PersistentClient(path=DB_DIR)
    return client.get_collection(COLLECTION_NAME)


def query_kb(query: str, top_k: int = 6) -> str:
    """
    Retrieve relevant chunks for a query and format them as context.

    Parameters
    ----------
    query : str
        Natural language question / description.
    top_k : int
        Number of chunks to retrieve.

    Returns
    -------
    str
        Human-readable context string (document snippets with source metadata).
    """
    collection = _get_collection()

    query_emb = _embedder.encode([query]).tolist()[0]

    results = collection.query(
        query_embeddings=[query_emb],
        n_results=top_k,
    )

    documents: List[str] = results.get("documents", [[]])[0]
    metadatas: List[dict] = results.get("metadatas", [[]])[0]

    context_blocks: List[str] = []
    for doc, meta in zip(documents, metadatas):
        src = meta.get("source_document", "unknown")
        idx = meta.get("chunk_index", "?")
        context_blocks.append(f"[Source: {src}, Chunk: {idx}]\n{doc}")

    return "\n\n".join(context_blocks)
