"""Pydantic model used to validate the AI response."""

from pydantic import BaseModel, ConfigDict, Field


class EmailAnalysis(BaseModel):
    """Structured fields displayed to the user after validation."""

    model_config = ConfigDict(extra="ignore")
    summary: str = Field(min_length=1)
    intent: str = Field(min_length=1)
    key_points: list[str]
    action_items: list[str]
    missing_information: list[str]
    draft_reply: str = Field(min_length=1)
