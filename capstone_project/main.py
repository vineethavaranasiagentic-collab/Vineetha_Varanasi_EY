"""FastAPI entry point for the Commercial Banking RM Copilot."""

from fastapi import FastAPI, HTTPException
from pydantic import BaseModel, Field

from agents import CLIENTS, CopilotPlan, create_plan, execute_plan

app = FastAPI(title="Commercial Banking Relationship Manager Copilot", version="1.0.0")


class CopilotRequest(BaseModel):
    request: str = Field(min_length=1)
    client_id: str = "client_001"


@app.get("/health")
def health() -> dict[str, str]:
    return {"status": "ok"}


@app.get("/clients")
def list_clients():
    return list(CLIENTS.values())


@app.post("/plan", response_model=CopilotPlan)
def plan_request(payload: CopilotRequest):
    try:
        return create_plan(payload.request, payload.client_id)
    except ValueError as exc:
        raise HTTPException(status_code=400, detail=str(exc)) from exc


@app.post("/execute")
def execute_request(payload: CopilotRequest):
    try:
        return {"plan": create_plan(payload.request, payload.client_id), "report": execute_plan(create_plan(payload.request, payload.client_id))}
    except ValueError as exc:
        raise HTTPException(status_code=400, detail=str(exc)) from exc


if __name__ == "__main__":
    import uvicorn
    uvicorn.run("main:app", host="127.0.0.1", port=8000, reload=False)
