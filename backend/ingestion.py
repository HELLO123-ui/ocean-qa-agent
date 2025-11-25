"""
Minimal ingestion module.

Parses support documents + checkout.html and builds a Chroma vector DB.

Public functions:
- build_knowledge_base(support_docs, checkout_html) -> str
- get_html_content() -> str
"""

import os
import json
import shutil
from typing import List, Tuple, Dict

import chromadb
from sentence_transformers import SentenceTransformer

# ---------- Paths & globals ----------

BASE_DIR = os.path.dirname(os.path.dirname(__file__))
DB_DIR = os.path.join(BASE_DIR, "chroma_db")
COLLECTION_NAME = "qa_kb"

_embedder = SentenceTransformer("all-MiniLM-L6-v2")

_HTML_CONTENT: str = ""  # will store the latest checkout.html


# ---------- Helpers ----------

def _chunk_text(text: str, chunk_size: int = 800, overlap: int = 150) -> List[str]:
    """Very simple sliding window splitter."""
    text = text.strip()
    if not text:
        return []

    chunks: List[str] = []
    start = 0
    while start < len(text):
        end = min(start + chunk_size, len(text))
        chunks.append(text[start:end])
        if end == len(text):
            break
        start = end - overlap
    return chunks


def _parse_file(file_bytes: bytes, filename: str) -> str:
    """
    Parse support docs into plain text.

    Supports: .txt, .md, .json
    (You can add PDF later if needed.)
    """
    ext = os.path.splitext(filename)[1].lower()

    if ext in {".txt", ".md"}:
        return file_bytes.decode("utf-8", errors="ignore")

    if ext == ".json":
        try:
            data = json.loads(file_bytes.decode("utf-8", errors="ignore"))
            return json.dumps(data, indent=2)
        except json.JSONDecodeError:
            return file_bytes.decode("utf-8", errors="ignore")

    # Fallback: just decode as text
    return file_bytes.decode("utf-8", errors="ignore")


def _reset_db() -> chromadb.Collection:
    """Delete old DB and create a fresh Chroma collection."""
    if os.path.exists(DB_DIR):
        shutil.rmtree(DB_DIR)

    os.makedirs(DB_DIR, exist_ok=True)
    client = chromadb.PersistentClient(path=DB_DIR)
    collection = client.create_collection(COLLECTION_NAME)
    return collection


# ---------- Public API ----------

def build_knowledge_base(
    support_docs: List[Tuple[str, bytes]],
    checkout_html: str,
) -> str:
    """
    Build the vector knowledge base from uploaded documents and checkout.html.

    support_docs: list of (filename, file_bytes)
    checkout_html: string content of checkout.html
    """
    global _HTML_CONTENT
    _HTML_CONTENT = checkout_html

    collection = _reset_db()

    documents: List[str] = []
    metadatas: List[Dict[str, str]] = []
    ids: List[str] = []

    for doc_idx, (filename, file_bytes) in enumerate(support_docs):
        text = _parse_file(file_bytes, filename)
        chunks = _chunk_text(text)

        for chunk_idx, chunk in enumerate(chunks):
            doc_id = f"{filename}-{doc_idx}-{chunk_idx}"
            documents.append(chunk)
            metadatas.append(
                {
                    "source_document": filename,
                    "chunk_index": str(chunk_idx),
                }
            )
            ids.append(doc_id)

    if documents:
        embeddings = _embedder.encode(documents).tolist()
        collection.add(
            documents=documents,
            metadatas=metadatas,
            ids=ids,
            embeddings=embeddings,
        )

    return f"Knowledge base built with {len(documents)} chunks from {len(support_docs)} document(s)."


def get_html_content() -> str:
    """Return the last uploaded checkout.html."""
    return _HTML_CONTENT
