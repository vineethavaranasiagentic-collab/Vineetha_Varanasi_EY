"""Commercial Banking Relationship Manager Copilot."""
from __future__ import annotations

import hashlib
from pathlib import Path
from typing import Any

import chromadb
import streamlit as st
from pypdf import PdfReader

BASE_DIR = Path(__file__).resolve().parent
UPLOAD_DIR = BASE_DIR / "data" / "uploads"
CHROMA_DIR = BASE_DIR / "chroma_db"
COLLECTION_NAME = "commercial_banking_documents"
MODEL_NAME = "all-MiniLM-L6-v2"
DEFAULT_CLIENT = "Default Client"
TOP_K = 5
RELEVANCE_THRESHOLD = 0.70
NO_INFORMATION = "The information is not available in the uploaded document."


def get_collection() -> Any:
    client = chromadb.PersistentClient(path=str(CHROMA_DIR))
    return client.get_or_create_collection(name=COLLECTION_NAME, metadata={"hnsw:space": "cosine"})


@st.cache_resource(show_spinner=False)
def get_model() -> Any:
    from sentence_transformers import SentenceTransformer
    return SentenceTransformer(MODEL_NAME)


def extract_chunks(path: Path) -> list[dict[str, Any]]:
    reader = PdfReader(str(path))
    output: list[dict[str, Any]] = []
    for page_number, page in enumerate(reader.pages, 1):
        words = " ".join((page.extract_text() or "").split()).split()
        for index in range(0, len(words), 650):
            text = " ".join(words[index:index + 800])
            if text:
                identity = f"{DEFAULT_CLIENT}|{path.name}|{page_number}|{index}|{text}"
                output.append({"id": hashlib.sha256(identity.encode()).hexdigest(), "text": text, "source": path.name, "page": page_number, "client": DEFAULT_CLIENT})
            if index + 800 >= len(words):
                break
    return output


def process_document(uploaded: Any) -> tuple[str, int]:
    UPLOAD_DIR.mkdir(parents=True, exist_ok=True)
    path = UPLOAD_DIR / Path(uploaded.name).name
    path.write_bytes(uploaded.getbuffer())
    chunks = extract_chunks(path)
    if not chunks:
        raise ValueError("No extractable text was found in the PDF.")
    store = get_collection()
    ids = [item["id"] for item in chunks]
    existing = set(store.get(ids=ids).get("ids", []))
    new_items = [item for item in chunks if item["id"] not in existing]
    if new_items:
        model = get_model()
        store.upsert(ids=[item["id"] for item in new_items], documents=[item["text"] for item in new_items], metadatas=[{"source": item["source"], "page": item["page"], "client": item["client"]} for item in new_items], embeddings=model.encode([item["text"] for item in new_items], normalize_embeddings=True).tolist())
    return path.name, len(new_items)


def ask_question(question: str) -> dict[str, Any]:
    store = get_collection()
    if not question.strip() or not store.get(where={"client": DEFAULT_CLIENT}, limit=1).get("ids"):
        return {"answer": NO_INFORMATION, "chunks": []}
    result = store.query(query_embeddings=get_model().encode([question], normalize_embeddings=True).tolist(), n_results=TOP_K, where={"client": DEFAULT_CLIENT}, include=["documents", "metadatas", "distances"])
    chunks = []
    for text, metadata, distance in zip(result["documents"][0], result["metadatas"][0], result["distances"][0]):
        relevance = 1.0 - float(distance)
        if relevance >= RELEVANCE_THRESHOLD:
            chunks.append({"text": text, **metadata, "relevance": relevance})
    if not chunks:
        return {"answer": NO_INFORMATION, "chunks": []}
    evidence = "\n\n".join(f"{item['source']} — page {item['page']}: {item['text']}" for item in chunks)
    return {"answer": f"Based only on the uploaded document evidence:\n\n{evidence}", "chunks": chunks}


def main() -> None:
    st.set_page_config(page_title="Commercial Banking Copilot", page_icon="🏦")
    st.title("Commercial Banking Relationship Manager Copilot")
    st.caption("Answers are based only on the uploaded document. Verify information before taking action.")
    st.subheader("Upload a document")
    uploaded = st.file_uploader("Choose one client PDF document", type=["pdf"])
    if st.button("Upload and process document", type="primary"):
        if uploaded is None:
            st.warning("Please choose a PDF document first.")
        else:
            try:
                with st.spinner("Extracting text and indexing document in ChromaDB..."):
                    filename, count = process_document(uploaded)
                st.success(f"{filename} processed. Added {count} new chunk(s) to ChromaDB.")
            except Exception as exc:
                st.error(f"Could not process the document: {exc}")
    st.divider()
    st.subheader("Ask Copilot")
    question = st.text_input("Ask a question about the uploaded document")
    if st.button("Ask Copilot"):
        try:
            result = ask_question(question)
            st.markdown("### Answer")
            st.write(result["answer"])
            st.markdown("### Retrieved Context")
            if not result["chunks"]:
                st.info("No sufficiently relevant document chunks were found.")
            for index, item in enumerate(result["chunks"], 1):
                with st.expander(f"Source {index}: {item['source']} — Page {item['page']} — Similarity {item['relevance']:.2f}"):
                    st.code(item["text"])
        except Exception as exc:
            st.error(f"Unable to answer safely: {exc}")


if __name__ == "__main__":
    main()
