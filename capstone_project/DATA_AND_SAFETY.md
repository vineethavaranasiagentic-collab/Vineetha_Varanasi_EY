# Data, Safety, and Evaluation Plan

## Sample data

The MVP uses fictional data only. No real customer information should be committed to this repository.

Each client record contains an identifier, name, sector, relationship status, and products. Activity records contain dates, transaction types, descriptions, amounts, direction, balance, product, and status.

## Privacy

- Do not store credentials in source files.
- Do not log full account numbers or unnecessary personal data.
- Use synthetic fixtures for tests and demonstrations.
- Add retention and deletion controls before production use.

## Agent safety

The agent is assistive, not autonomous. It may summarize supplied records and identify questions for human review. It must not make credit, pricing, investment, fraud, or eligibility decisions.

## Evaluation

- Plan validity: all steps are allow-listed and ordered.
- Grounding: every observation has a source reference.
- Abstention: missing evidence returns an explicit no-information message.
- Safety: client-facing output is always marked for human approval.
- Reliability: repeated execution with the same input is deterministic.
- Usability: a relationship manager can inspect the plan before execution.
