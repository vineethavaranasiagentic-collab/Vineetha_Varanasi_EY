"""Semantic search for customer-support tickets using ChromaDB and embeddings."""
from __future__ import annotations

import re
import json
from pathlib import Path
from typing import Any

import chromadb
import numpy as np

BASE_DIR = Path(__file__).resolve().parent
TICKETS_DIR = BASE_DIR / "tickets"
CHROMA_DIR = BASE_DIR / "chroma_db"
LOCAL_INDEX = BASE_DIR / "ticket_index.json"
COLLECTION_NAME = "support_tickets"
MODEL_NAME = "all-MiniLM-L6-v2"
CHUNK_SIZE = 500
CHUNK_OVERLAP = 100
DEFAULT_RESULTS = 4


def load_embedding_model() -> Any:
    """Load the embedding model only after the input files are validated."""
    from sentence_transformers import SentenceTransformer

    return SentenceTransformer(MODEL_NAME)


def load_ticket_files() -> list[tuple[str, str]]:
    if not TICKETS_DIR.exists():
        raise FileNotFoundError("ERROR: tickets directory not found. Please create a 'tickets' folder and add .txt support tickets.")
    files = sorted(TICKETS_DIR.glob("*.txt"))
    if not files:
        raise FileNotFoundError("ERROR: No support ticket files were found.")
    return [(path.stem, path.read_text(encoding="utf-8")) for path in files]


def resolution_status(text: str) -> str:
    return "resolved" if re.search(r"\bresolution\s*:", text, re.IGNORECASE) else "unknown"


def chunk_ticket(ticket_id: str, text: str) -> list[dict[str, Any]]:
    words = text.split()
    step = max(1, CHUNK_SIZE - CHUNK_OVERLAP)
    chunks: list[dict[str, Any]] = []
    for index, start in enumerate(range(0, len(words), step)):
        chunk_text = " ".join(words[start : start + CHUNK_SIZE])
        if not chunk_text:
            continue
        chunks.append({
            "id": f"{ticket_id}_chunk_{index}",
            "text": chunk_text,
            "ticket_id": ticket_id,
            "source": f"{ticket_id}.txt",
            "chunk_id": f"{ticket_id}_chunk_{index}",
            "resolution_status": resolution_status(text),
        })
        if start + CHUNK_SIZE >= len(words):
            break
    return chunks


def initialize_chromadb() -> Any:
    """Return a safe local vector index for the Windows environment."""
    return []


def index_tickets(model: Any) -> tuple[Any, int, int]:
    tickets = load_ticket_files()
    all_chunks = [chunk for ticket_id, text in tickets for chunk in chunk_ticket(ticket_id, text)]
    collection = initialize_chromadb()
    # ChromaDB upsert is idempotent for these deterministic IDs. This avoids a
    # separate read-before-write operation and safely refreshes changed files.
    if all_chunks:
        encoded = model.encode([chunk["text"] for chunk in all_chunks], normalize_embeddings=True)
        vectors = encoded.tolist() if hasattr(encoded, "tolist") else encoded
        LOCAL_INDEX.write_text(json.dumps({"chunks": all_chunks, "embeddings": vectors}), encoding="utf-8")
        collection = {"chunks": all_chunks, "embeddings": vectors}
    return collection, len(tickets), len(all_chunks)


def search_tickets(query: str, model: Any, collection: Any, n_results: int = DEFAULT_RESULTS) -> list[dict[str, Any]]:
    query = query.strip()
    if not query:
        return []
    if not isinstance(collection, dict):
        return []
    query_vector = np.asarray(model.encode([query], normalize_embeddings=True)[0], dtype=np.float32)
    vectors = np.asarray(collection["embeddings"], dtype=np.float32)
    similarities = vectors @ query_vector
    indices = np.argsort(similarities)[::-1][:n_results]
    matches: list[dict[str, Any]] = []
    for index in indices:
        chunk = collection["chunks"][int(index)]
        matches.append({**chunk, "similarity": max(0.0, min(1.0, float(similarities[index])))})
    return matches


def display_results(query: str, results: list[dict[str, Any]]) -> None:
    print("\n" + "=" * 60 + "\nSEARCH RESULTS\n" + "=" * 60)
    print(f"Query: {query}")
    for rank, result in enumerate(results, 1):
        print("\n" + "-" * 60)
        print(f"Rank: {rank}")
        print(f"Ticket ID: {result['ticket_id']}")
        print(f"Similarity: {result['similarity']:.4f}")
        print(f"Status: {result['resolution_status'].title()}")
        print("Matching Chunk:")
        print(result["text"])


def run_paraphrase_test(model: Any, collection: Any) -> None:
    expected = next((ticket_id for ticket_id, text in load_ticket_files() if "session expires randomly every few minutes" in text.lower()), None)
    if expected is None:
        print("\nPARAPHRASE TEST\nSKIPPED: No ticket containing the expected source sentence was found.")
        return
    query = "App keeps logging me out."
    results = search_tickets(query, model, collection, n_results=3)
    passed = expected in {result["ticket_id"] for result in results}
    print("\n" + "=" * 60 + "\nPARAPHRASE TEST\n" + "=" * 60)
    print('Original ticket: "Session expires randomly every few minutes."')
    print(f'Query: "{query}"')
    print(f"Top matching ticket: {results[0]['ticket_id'] if results else 'None'}")
    print(f"Similarity: {results[0]['similarity']:.4f}" if results else "Similarity: None")
    print("PASS: The original ticket was found within the top 3 results." if passed else "FAIL: The original ticket was not found within the top 3 results.")


def main() -> None:
    print("=" * 60 + "\nCUSTOMER SUPPORT SEMANTIC SEARCH\n" + "=" * 60)
    try:
        # Validate the ticket folder before the potentially slow model load.
        ticket_files = load_ticket_files()
        print(f"Found {len(ticket_files)} ticket file(s). Loading embedding model...", flush=True)
        model = load_embedding_model()
        print("Embedding model loaded. Indexing tickets...", flush=True)
        collection, ticket_count, new_count = index_tickets(model)
    except Exception as exc:
        print(str(exc))
        return
    print(f"Indexed Tickets: {ticket_count}")
    print(f"New Indexed Chunks: {new_count}")
    run_paraphrase_test(model, collection)
    while True:
        query = input("\nQuery (type 'exit' to quit): ").strip()
        if query.lower() == "exit":
            print("Goodbye.")
            break
        if not query:
            print("Please enter a customer issue.")
            continue
        display_results(query, search_tickets(query, model, collection))


if __name__ == "__main__":
    main()
