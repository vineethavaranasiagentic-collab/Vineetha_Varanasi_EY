# Data Models Implementation

from dataclasses import dataclass

@dataclass
class PlanStep:
    step: int
    task: str
    query: str
    depends_on: list[int]

@dataclass
class StepResult:
    step: int
    task: str
    query: str
    results: list
    relevant: bool
    sufficient: bool
    retry_count: int
    status: str
    evaluation_reason: str
