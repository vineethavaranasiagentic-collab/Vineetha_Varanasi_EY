import os
import json
import logging
from pydantic import BaseModel

# Configuration
JIRA_MODE = os.getenv('JIRA_MODE', 'mock')

# Set up logging
logging.basicConfig(level=logging.INFO)

# Pydantic models
class Ticket(BaseModel):
    ticket_id: str
    customer_id: str
    issue_category: str
    issue_description: str
    resolution: str
    created_at: str
    status: str

class Customer(BaseModel):
    customer_id: str
    customer_name: str
    status: str
    churned: bool
    churn_date: str = None

class Plan(BaseModel):
    question: str
    steps: list

class PlanStep(BaseModel):
    step_id: int
    description: str
    tool: str
    depends_on: list[int]

class ExecutionTrace:
    def __init__(self):
        self.traces = []

    def add_trace(self, step_id, description, result):
        self.traces.append({
            'step_id': step_id,
            'description': description,
            'result': result
        })

    def display_trace(self):
        for trace in self.traces:
            logging.info(f"Step {trace['step_id']}: {trace['description']} - Result: {trace['result']}")

# Main function
if __name__ == '__main__':
    logging.info("Starting Ticket Intelligence System...")
    # Example usage
    trace = ExecutionTrace()
    trace.add_trace(1, "Retrieve ticket 4021", "Ticket found")
    trace.display_trace()