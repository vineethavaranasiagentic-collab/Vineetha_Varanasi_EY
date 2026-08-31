# Commercial Banking Relationship Manager Copilot

This folder contains a local, evidence-grounded agentic AI MVP.

## Components

- `agents.py` — typed models, deterministic planner agent, executor agent, sample data, and safety controls.
- `main.py` — FastAPI service.
- `app.py` — Streamlit interface.
- `ARCHITECTURE.md` — system architecture and boundaries.
- `IMPLEMENTATION_PLAN.md` — delivery phases and acceptance criteria.
- `DATA_AND_SAFETY.md` — data, privacy, safety, and evaluation plan.
- `test_agents.py` — focused tests.

## Run the API

From the repository root:

```powershell
Set-Location .\capstone_project
..\.venv\Scripts\python.exe -m uvicorn main:app --reload
```

Open `http://127.0.0.1:8000/docs` for the interactive API documentation.

## Run the Streamlit UI

```powershell
Set-Location .\capstone_project
..\.venv\Scripts\python.exe -m streamlit run app.py
```

## Run focused tests

```powershell
..\.venv\Scripts\python.exe -m pytest capstone_project/test_agents.py -q
```

The application uses fictional data, does not call an external LLM, and never sends a client message. Every draft is marked as requiring human approval.
