"""
ingest.py — Document Ingestion & Chunking
Pipeline stage 1: Load documents from /documents, clean text, split into chunks.

Output: list of dicts {text, source, chunk_index}
"""

import os
import re
from pathlib import Path


DOCUMENTS_DIR = Path(__file__).parent.parent / "documents"
CHUNK_SIZE = 450      # characters (~400-500 per planning.md)
CHUNK_OVERLAP = 60    # characters (~50-75 per planning.md)


def clean_text(text: str) -> str:
    """Strip Markdown syntax, HTML artifacts, and normalise whitespace."""
    # Remove HTML tags
    text = re.sub(r"<[^>]+>", " ", text)
    # Remove Markdown headings markers (keep the heading text)
    text = re.sub(r"^#{1,6}\s+", "", text, flags=re.MULTILINE)
    # Remove Markdown bold/italic markers
    text = re.sub(r"[*_]{1,3}(.+?)[*_]{1,3}", r"\1", text)
    # Remove Markdown links, keep display text
    text = re.sub(r"\[([^\]]+)\]\([^)]+\)", r"\1", text)
    # Remove Markdown image syntax
    text = re.sub(r"!\[[^\]]*\]\([^)]+\)", "", text)
    # Remove horizontal rules
    text = re.sub(r"^[-*_]{3,}\s*$", "", text, flags=re.MULTILINE)
    # Collapse multiple blank lines into one
    text = re.sub(r"\n{3,}", "\n\n", text)
    # Normalise whitespace (tabs, trailing spaces)
    text = re.sub(r"[ \t]+", " ", text)
    text = text.strip()
    return text


def chunk_text(text: str, chunk_size: int = CHUNK_SIZE, overlap: int = CHUNK_OVERLAP) -> list[str]:
    """
    Split text into overlapping character-level chunks.
    Tries to break on sentence boundaries ('. ') when possible to avoid
    cutting a thought mid-sentence.
    """
    chunks = []
    start = 0
    text_len = len(text)

    while start < text_len:
        end = min(start + chunk_size, text_len)

        # If we're not at the very end, try to snap to a sentence boundary
        if end < text_len:
            # Look for '. ' or '\n' within the last 80 characters of the window
            snap_window = text[max(start, end - 80): end]
            # Find the last sentence-ending punctuation in that window
            match = None
            for pattern in (r"\.\s", r"\n"):
                for m in re.finditer(pattern, snap_window):
                    match = m
                if match:
                    break
            if match:
                end = max(start, end - 80) + match.end()

        chunk = text[start:end].strip()
        if chunk:
            chunks.append(chunk)

        # Advance start, stepping back by overlap
        start = end - overlap
        if start >= end or end == text_len:
            break

    return chunks


def load_documents(documents_dir: Path = DOCUMENTS_DIR) -> list[dict]:
    """
    Load all .txt and .md files from the documents directory.
    Returns a flat list of chunk dicts: {text, source, chunk_index}.
    """
    supported_extensions = {".txt", ".md"}
    all_chunks: list[dict] = []

    doc_files = sorted(
        f for f in documents_dir.iterdir()
        if f.is_file() and f.suffix.lower() in supported_extensions and f.name != ".gitkeep"
    )

    if not doc_files:
        print(f"[ingest] No documents found in {documents_dir}")
        return all_chunks

    for doc_path in doc_files:
        raw_text = doc_path.read_text(encoding="utf-8", errors="replace")
        cleaned = clean_text(raw_text)
        chunks = chunk_text(cleaned)

        for idx, chunk in enumerate(chunks):
            all_chunks.append({
                "text": chunk,
                "source": doc_path.name,
                "chunk_index": idx,
            })

        print(f"[ingest] {doc_path.name}: {len(chunks)} chunks")

    print(f"[ingest] Total chunks: {len(all_chunks)}")
    return all_chunks


if __name__ == "__main__":
    chunks = load_documents()
    # Quick sanity preview
    for c in chunks[:3]:
        print(f"\n--- {c['source']} chunk {c['chunk_index']} ---")
        print(c["text"][:200])
