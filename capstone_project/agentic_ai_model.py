# Agentic AI Model for Commercial Banking Relationship Manager Copilot

from fastapi import FastAPI
from pydantic import BaseModel
from typing import List, Optional

app = FastAPI()

# Data Models
class Client(BaseModel):
    id: int
    name: str
    email: str
    phone: str

class Transaction(BaseModel):
    id: int
    client_id: int
    amount: float
    date: str

class Insight(BaseModel):
    client_id: int
    recommendation: str

# Sample Data
clients = []
transactions = []
insights = []

@app.post("/clients/")
async def create_client(client: Client):
    clients.append(client)
    return client

@app.get("/clients/", response_model=List[Client])
async def get_clients():
    return clients

@app.post("/transactions/")
async def create_transaction(transaction: Transaction):
    transactions.append(transaction)
    return transaction

@app.get("/insights/{client_id}", response_model=List[Insight])
async def get_insights(client_id: int):
    return [insight for insight in insights if insight.client_id == client_id]

@app.post("/insights/")
async def create_insight(insight: Insight):
    insights.append(insight)
    return insight

# Run the application using `uvicorn agentic_ai_model:app --reload`
