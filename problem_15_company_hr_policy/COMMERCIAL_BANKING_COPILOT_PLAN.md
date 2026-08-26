# Commercial Banking Relationship Manager Copilot Plan

## Objective
Build a document-grounded assistant that allows Relationship Managers to upload client PDFs, index them in persistent ChromaDB, ask questions, inspect exact evidence, and safely identify missing information.

## Phase 1 — Document RAG MVP
1. Upload one or more client PDF documents.
2. Extract text page by page with `pypdf`.
3. Normalize whitespace and create overlapping chunks.
4. Preserve filename, page, client, and deterministic chunk ID metadata.
5. Generate local embeddings with Sentence Transformers.
6. Persist embeddings in ChromaDB.
7. Prevent duplicate chunks on repeated processing.
8. Filter retrieval by selected client.
9. Apply configurable similarity threshold and top-k limit.
10. Return a strict no-information response when evidence is absent.
11. Display answer, sources, similarity scores, and exact retrieved chunks.

## Phase 2 — Professional Dashboard
- Dashboard metrics for documents and chunks.
- Documents tab with processing status.
- Ask Copilot chat history and follow-up questions.
- Clear/reset database control.

## Phase 3 — Relationship Intelligence
Add evidence-backed early-warning signals only when supported by retrieved documents:
- Revenue decline
- Debt increase
- Liquidity pressure
- Covenant stress
- Delayed payments
- Credit deterioration

Each signal must include reason, source, page, and evidence.

## Phase 4 — Opportunity and Meeting Workflows
- Next-best-action recommendations with priority and confidence.
- Grounded client meeting brief.
- Grounded talking points.
- No unsupported financial or credit conclusions.

## Phase 5 — Outreach and Approval
- Draft client email only; never send automatically.
- Status workflow: `DRAFT`, `PENDING_APPROVAL`, `APPROVED`, `REJECTED`.
- Human review required before any communication can proceed.

## Compliance Controls
- Never mix client documents.
- Never fabricate financial values, risks, or client details.
- Never make unsupported credit decisions.
- Always show evidence for factual claims.
- Keep API keys in `.env`, never source code.
- Display the AI-generated analysis disclaimer.

## Success Criteria
A user can select a client, upload PDFs, process them, ask a supported question, receive document-grounded evidence with page numbers, and receive a clear unavailable response for unsupported questions.
