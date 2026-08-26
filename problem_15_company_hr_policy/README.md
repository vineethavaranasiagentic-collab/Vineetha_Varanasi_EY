# Commercial Banking Relationship Manager Copilot

A Python Streamlit application for uploading client PDF documents, indexing them into persistent ChromaDB, retrieving relevant evidence, and answering questions without inventing unsupported facts.

## Architecture

`PDF upload -> page extraction -> overlapping chunks -> embeddings -> ChromaDB -> client-filtered retrieval -> relevance threshold -> answer + exact evidence`

## Setup

From this directory:

```powershell
python -m venv .venv
.\.venv\Scripts\Activate.ps1
pip install -r requirements.txt
Copy-Item .env.example .env
```

The default embedding model is local `all-MiniLM-L6-v2`. The first processing run may download the model.

## Run

```powershell
streamlit run app.py
```

Upload one or more PDFs in the sidebar, choose a client, and click **Process Documents**. Then use **Ask Copilot** to ask questions. The answer displays the retrieved source filename, page, similarity score, and exact chunk text.

## Grounding behavior

The application uses a configurable `RELEVANCE_THRESHOLD` (default `0.70`). If no chunks meet the threshold, it returns:

> The information is not available in the uploaded document.

The selected client is applied as ChromaDB metadata filtering so client documents are not mixed.

## Storage

- Uploaded PDFs: `data/uploads/`
- Persistent vector database: `chroma_db/`
- Collection: `commercial_banking_documents`

Chunk IDs are deterministic hashes, so reprocessing the same content does not create duplicate vectors.

## Troubleshooting

- If a PDF contains scanned images only, it may have no extractable text; use OCR before upload.
- If the embedding model cannot be downloaded, check network access or configure a locally available model.
- If the database is corrupted, stop Streamlit, remove `chroma_db/`, and process the PDFs again.
- Do not commit `.env` or API keys.

## Planned extensions

Relationship Intelligence, meeting briefs, outreach drafts, approval workflow, and next-best-action recommendations are represented as UI sections and should be implemented with the same evidence-only rule before production use.
