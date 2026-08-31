# Commercial Banking Relationship Manager Copilot

## Objective

Provide relationship managers with an auditable, human-in-the-loop assistant for reviewing client account activity, retrieving supporting documents, identifying opportunities for follow-up, and drafting evidence-grounded client communications.

## Design principles

- Ground every insight in supplied client data or retrieved evidence.
- Never invent amounts, dates, products, risk events, or recommendations.
- Keep planning deterministic and inspectable.
- Separate orchestration, tools, validation, and presentation.
- Require human approval before external communication or consequential action.
- Record an audit trail for each plan and execution.

## Architecture

```text
Streamlit UI / FastAPI API
          |
          v
  Relationship Manager Agent
          |
     Planner Agent
          |
   Structured CopilotPlan
          |
    Executor Agent
     |       |       |
  Client   Activity  Evidence
  tool     analyzer  retriever
          |
   Deterministic validators
          |
  Evidence-backed response + approval state
          |
      Human RM review
```

## Agent responsibilities

### Planner agent

Converts a user request into ordered, typed steps:

1. Validate the request.
2. Resolve the client.
3. Load client activity.
4. Retrieve relevant evidence.
5. Analyze supported observations.
6. Draft a response or action list.
7. Validate factual support and approval requirements.
8. Present an auditable report.

The planner does not call tools or invent facts.

### Executor agent

Executes only the allowed steps. It uses local sample data by default, returns structured outputs, and fails safely when client data or evidence is missing. It does not send messages, approve credit, or make trades.

## Initial scope

- Client profiles and account activity.
- Transaction summaries and cash-flow observations.
- Evidence snippets from local documents or notes.
- Follow-up suggestions explicitly labeled as review items.
- Draft client review requiring human approval.
- FastAPI endpoints and Streamlit dashboard.

## Out of scope

- Automated lending decisions.
- Investment or trading advice.
- Autonomous client communication.
- Production authentication, core-banking integration, or regulated decisioning.

## Safety controls

- Pydantic input validation.
- Allow-listed planner steps.
- Source-backed observations only.
- No-information response when evidence is absent.
- Drafts marked `human_approval_required=True`.
- Audit events containing plan, steps, status, and evidence references.

## Deployment direction

The first version is local and in-memory for training. A production version should replace repositories with governed databases/vector stores, add identity and role-based access, encrypt sensitive data, redact logs, add monitoring, and obtain compliance approval.
