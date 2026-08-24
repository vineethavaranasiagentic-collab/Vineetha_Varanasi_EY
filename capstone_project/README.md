# Commercial Banking Relationship Manager Copilot

A focused MVP that analyzes fictional commercial-banking data, detects risks and opportunities, retrieves supporting evidence, recommends next-best-actions, prepares meeting briefs, drafts outreach, and requires RM approval.

## Run

From the repository root:

```text
.venv\Scripts\python.exe capstone_project\main.py
```

The default demo uses `CLIENT-001` and leaves approval pending. To run an approved scenario, use the `run` function with `approved=True`.

All calculations and risk/opportunity rules are deterministic. The OpenRouter integration is optional; the MVP remains runnable without API credentials.
