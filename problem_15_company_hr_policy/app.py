"""HR Management Document Copilot."""
from __future__ import annotations

import hashlib
import json
import re
from pathlib import Path
from typing import Any

import numpy as np
import streamlit as st
from pypdf import PdfReader

BASE_DIR = Path(__file__).resolve().parent
UPLOAD_DIR = BASE_DIR / "data" / "uploads"
INDEX_PATH = BASE_DIR / "hr_policy_index.json"
MODEL_NAME = "all-MiniLM-L6-v2"
TOP_K = 5
# Smaller chunks keep individual policy sections together and produce better
# matches for short questions such as "performance policy".
RELEVANCE_THRESHOLD = 0.20
NO_INFORMATION = "The information is not available in the uploaded document."


@st.cache_resource(show_spinner=False)
def get_model() -> Any:
    from sentence_transformers import SentenceTransformer
    return SentenceTransformer(MODEL_NAME)


def extract_chunks(path: Path) -> list[dict[str, Any]]:
    reader = PdfReader(str(path))
    output: list[dict[str, Any]] = []
    for page_number, page in enumerate(reader.pages, 1):
        words = " ".join((page.extract_text() or "").split()).split()
        for index in range(0, len(words), 90):
            text = " ".join(words[index:index + 140])
            if text:
                identity = f"{path.name}|{page_number}|{index}|{text}"
                output.append({"id": hashlib.sha256(identity.encode()).hexdigest(), "text": text, "source": path.name, "page": page_number})
            if index + 140 >= len(words):
                break
    return output


def process_document(uploaded: Any) -> tuple[str, int]:
    UPLOAD_DIR.mkdir(parents=True, exist_ok=True)
    path = UPLOAD_DIR / Path(uploaded.name).name
    path.write_bytes(uploaded.getbuffer())
    chunks = extract_chunks(path)
    if not chunks:
        raise ValueError("No extractable text was found in the PDF.")
    model = get_model()
    embeddings = model.encode([item["text"] for item in chunks], normalize_embeddings=True).tolist()
    INDEX_PATH.write_text(json.dumps({"chunks": chunks, "embeddings": embeddings}), encoding="utf-8")
    return path.name, len(chunks)


def ask_question(question: str) -> dict[str, Any]:
    if not question.strip() or not INDEX_PATH.exists():
        return {"answer": NO_INFORMATION, "chunks": []}
    data = json.loads(INDEX_PATH.read_text(encoding="utf-8"))
    query_vector = get_model().encode([question], normalize_embeddings=True)[0]
    scores = np.asarray(data["embeddings"], dtype=np.float32) @ query_vector
    indices = np.argsort(scores)[::-1][:TOP_K]
    chunks = []
    for index in indices:
        item = data["chunks"][int(index)]
        relevance = float(scores[index])
        if relevance >= RELEVANCE_THRESHOLD:
            chunks.append({**item, "relevance": relevance})
    if not chunks:
        return {"answer": NO_INFORMATION, "chunks": []}
    # Return a concise answer from the matching policy section rather than
    # dumping the complete PDF chunk. The full retrieved evidence remains
    # visible below the answer.
    stop_words = {"what", "when", "where", "which", "who", "how", "can", "could", "would", "tell", "give", "please", "about", "the", "is", "are", "does", "do", "me"}
    query_terms = {term for term in re.findall(r"[a-z0-9]+", question.lower()) if len(term) > 2 and term not in stop_words}
    synonym_groups = ({"leave", "vacation", "holidays"}, {"performance", "review", "reviews", "appraisal"}, {"work", "remote", "home"})
    for group in synonym_groups:
        if query_terms & group:
            query_terms.update(group)
    sentences: list[str] = []
    for item in chunks:
        for sentence in re.split(r"(?<=[.!?])\s+", item["text"]):
            sentence_terms = set(re.findall(r"[a-z0-9]+", sentence.lower()))
            if query_terms & sentence_terms:
                sentences.append(sentence.strip())
    answer_text = " ".join(dict.fromkeys(sentences[:4]))
    if not answer_text:
        answer_text = chunks[0]["text"]
    return {"answer": answer_text, "chunks": chunks}


def main() -> None:
    st.set_page_config(page_title="HR Management System", page_icon="👥")
    st.title("HR Management System")
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
