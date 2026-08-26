# Problem 16 — Semantic Ticket Search

This program performs semantic vector search over customer-support `.txt` files using Sentence Transformers and persistent ChromaDB.

## Setup

Place ticket files in the `tickets/` folder. The program discovers all `.txt` files automatically. Then install dependencies:

```powershell
c:\Users\user\Documents\AgenticAITraining\Vineetha_Varanasi_EY\.venv\Scripts\python.exe -m pip install -r requirements.txt
```

## Run

```powershell
c:\Users\user\Documents\AgenticAITraining\Vineetha_Varanasi_EY\.venv\Scripts\python.exe semantic_search.py
```

The first run may download `all-MiniLM-L6-v2`. Ticket chunks and embeddings are persisted in `chroma_db/`. Deterministic chunk IDs make repeated indexing safe.

The program runs a paraphrase test for `Session expires randomly every few minutes.` versus `App keeps logging me out.`, then opens an interactive prompt. Type `exit` to quit.

## Planner and executor

Run the inspectable planner-executor workflow with:

```powershell
python planner_executor.py
```

The planner creates steps for validation, model loading, indexing, semantic search, and reporting. The executor runs those steps and prints the plan, indexed counts, matches, similarity scores, and ticket evidence.

Similarity is calculated from ChromaDB cosine distance as `1 - distance`, so higher scores indicate better semantic matches.
