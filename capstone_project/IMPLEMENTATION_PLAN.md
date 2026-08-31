# Implementation Plan

## Phase 1 — Working local MVP

- [x] Define the architecture and safety boundaries.
- [ ] Add typed client, activity, evidence, plan, and execution models.
- [ ] Implement deterministic planner and executor agents.
- [ ] Add local sample banking data.
- [ ] Add FastAPI endpoints for planning and execution.
- [ ] Add a Streamlit interface for relationship managers.
- [ ] Add unit tests for planning, execution, validation, and safe failure.

## Phase 2 — Retrieval and LLM adapter

- Add ChromaDB-backed evidence indexing behind a repository interface.
- Add an optional OpenRouter adapter using environment variables.
- Keep deterministic fallback behavior when no API key is configured.
- Validate generated drafts against source facts before displaying them.

## Phase 3 — Production hardening

- Add authentication, authorization, tenant isolation, and audit persistence.
- Replace in-memory repositories with governed storage.
- Add document ingestion, encryption, PII redaction, monitoring, and rate limits.
- Add approval workflow and immutable audit records.
- Complete legal, risk, compliance, and security reviews.

## Acceptance criteria

1. A request produces a visible structured plan.
2. The executor runs each planned step in order.
3. Results include client, transaction, and evidence references.
4. Unsupported information is not presented as fact.
5. Human approval is required for generated client-facing drafts.
6. Empty, unknown, and malformed requests fail safely.
7. FastAPI tests pass without external services or API keys.
8. The Streamlit UI can submit a request and display the plan and report.
