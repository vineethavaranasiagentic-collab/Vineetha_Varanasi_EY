"""Stable Flask UI for the HR Management System."""
from __future__ import annotations

import html
import uuid
from pathlib import Path
from flask import Flask, request, render_template_string, session
from werkzeug.utils import secure_filename

from app import ask_question, process_document

BASE_DIR = Path(__file__).resolve().parent
UPLOAD_DIR = BASE_DIR / "data" / "uploads"
ALLOWED_EXTENSIONS = {"pdf"}
app = Flask(__name__)
app.secret_key = "local-hr-management-session-key"
app.config["MAX_CONTENT_LENGTH"] = 200 * 1024 * 1024

TEMPLATE = """<!doctype html><html><head><meta charset='utf-8'><title>HR Management System</title>
<style>body{{font-family:Arial;max-width:850px;margin:40px auto;padding:0 20px;color:#172033}}h1{{color:#173b73}}section{{border:1px solid #d9e0eb;border-radius:10px;padding:20px;margin:20px 0}}.answer{{background:#f3f7fb;padding:16px;border-radius:8px;margin-top:20px}}button{{background:#1769aa;color:white;border:0;border-radius:6px;padding:11px 18px;cursor:pointer}}input{{padding:10px;margin:10px 0;width:95%}}pre{{white-space:pre-wrap;background:#fff;padding:12px;border-radius:6px}}</style></head>
<body><h1>HR Management System</h1><p>Answers use only the uploaded HR policy document.</p>
<section><h2>Upload one PDF document</h2><form method='post' action='/upload' enctype='multipart/form-data'><input name='document' type='file' accept='.pdf' required><br><button>Upload and index document</button></form>{upload_message}</section>
<section><h2>Ask Copilot</h2><form method='post' action='/ask'><input name='question' placeholder='Ask, type a topic, or enter a request about the policy' required><br><button>Ask Copilot</button></form>{answer}</section></body></html>"""


def page(upload_message: str = "", answer: str = "", chunks: list[dict] | None = None) -> str:
    evidence = ""
    for index, chunk in enumerate(chunks or [], 1):
        evidence += f"<h3>Source {index}: {html.escape(str(chunk.get('source')))} — Page {chunk.get('page')}</h3><pre>{html.escape(str(chunk.get('text')))}</pre>"
    answer_html = f"<div class='answer'><h2>Answer</h2><p>{html.escape(answer).replace(chr(10), '<br>')}</p>{evidence}</div>" if answer else ""
    document_name = session.get("document_name")
    status = f"<p><strong>Active document:</strong> {html.escape(document_name)}</p>" if document_name else "<p><strong>No document uploaded for this session.</strong></p>"
    return TEMPLATE.format(upload_message=status + (f"<p>{html.escape(upload_message)}</p>" if upload_message else ""), answer=answer_html)


@app.get("/")
def home() -> str:
    return page()


@app.post("/upload")
def upload() -> str:
    document = request.files.get("document")
    if not document or not document.filename:
        return page("Please select a PDF document.")
    filename = secure_filename(document.filename)
    if Path(filename).suffix.lower().lstrip(".") not in ALLOWED_EXTENSIONS:
        return page("Only PDF files are supported.")
    UPLOAD_DIR.mkdir(parents=True, exist_ok=True)
    destination = UPLOAD_DIR / filename
    document.save(destination)
    class Uploaded:
        name = filename
        def getbuffer(self):
            return destination.read_bytes()
    try:
        # Rebuild the index after every upload so the active document is always searchable.
        saved_name, count = process_document(Uploaded())
        session["document_name"] = saved_name
        return page(f"Indexed {saved_name}: {count} chunk(s) saved.")
    except Exception as exc:
        return page(f"Could not index the document: {exc}")


@app.post("/ask")
def ask() -> str:
    question = request.form.get("question", "").strip()
    if not question:
        return page("", "Please enter a question.")
    try:
        if "document_name" not in session:
            return page("Please upload a document before asking a question.")
        result = ask_question(question)
        return page("", result["answer"], result.get("chunks", []))
    except Exception as exc:
        return page("", f"Unable to answer safely: {exc}")


if __name__ == "__main__":
    app.run(host="127.0.0.1", port=5000, debug=False)
