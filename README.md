# Vineetha_Varanasi_EY

## Capstone Project Planning

The capstone project is a **Commercial Banking Relationship Manager Copilot**. It is an evidence-grounded, human-in-the-loop agentic AI application designed to help relationship managers review client activity, retrieve supporting evidence, identify follow-up questions, and prepare client communication drafts.

### Business requirements

- Maintain client profiles and commercial banking products.
- Review supplied account activity and transaction records.
- Identify supported observations from client data.
- Retrieve and display evidence for every observation.
- Suggest follow-up questions for relationship-manager review.
- Prepare factual client communication drafts.
- Require human approval before any client-facing communication.
- Keep an auditable record of the plan and execution steps.
- Fail safely when a client, document, or required information is unavailable.

### Agentic workflow

1. **Planner agent** validates the relationship-manager request and creates an ordered `CopilotPlan`.
2. **Executor agent** runs the approved steps: load client, load activity, retrieve evidence, analyze, draft, validate, and report.
3. **Validation layer** checks that the output is supported by supplied records.
4. **Human reviewer** approves or edits the draft before it can be used externally.

### Planned technology

- **Python 3.11+** — application language
- **FastAPI** — backend API
- **Streamlit** — relationship-manager interface
- **Pydantic** — typed validation and data models
- **Pandas** — transaction analysis
- **ChromaDB** — planned document and evidence vector storage
- **OpenRouter/LLM adapter** — planned optional natural-language generation layer

### Delivery phases

#### Phase 1 — Local MVP

- Implement planner and executor agents.
- Add typed client, activity, evidence, plan, and report models.
- Use fictional sample customer data.
- Provide FastAPI endpoints for health, clients, planning, and execution.
- Provide a Streamlit dashboard.
- Add unit tests and safe error handling.

#### Phase 2 — Retrieval and LLM integration

- Add ChromaDB-backed evidence indexing.
- Add document upload and semantic retrieval.
- Add an optional OpenRouter integration.
- Validate generated drafts against source facts.

#### Phase 3 — Production readiness

- Add authentication and role-based authorization.
- Add persistent governed storage and immutable audit records.
- Add encryption, PII redaction, monitoring, rate limits, and deployment configuration.
- Complete security, legal, risk, and compliance reviews.

### Safety boundaries

The Copilot is assistive and does not autonomously send messages, approve credit, make lending decisions, recommend trades, or promise investment returns. The current implementation uses fictional data and marks every client-facing draft as requiring human approval.

### Implementation documents

Detailed planning documents are available in [`capstone_project`](./capstone_project/):

- [`ARCHITECTURE.md`](./capstone_project/ARCHITECTURE.md) — system architecture and agent responsibilities
- [`IMPLEMENTATION_PLAN.md`](./capstone_project/IMPLEMENTATION_PLAN.md) — delivery phases and acceptance criteria
- [`DATA_AND_SAFETY.md`](./capstone_project/DATA_AND_SAFETY.md) — data, privacy, safety, and evaluation plan
- [`commercial_banking_relationship_manager_copilot_plan.md`](./capstone_project/commercial_banking_relationship_manager_copilot_plan.md) — original capstone plan

### Run the capstone project

From the repository root:

```powershell
Set-Location .\capstone_project
..\.venv\Scripts\python.exe -m uvicorn main:app --reload
```

Open `http://127.0.0.1:8000/docs` to use the FastAPI documentation. To launch the Streamlit interface, run:

```powershell
Set-Location .\capstone_project
..\.venv\Scripts\python.exe -m streamlit run app.py
```