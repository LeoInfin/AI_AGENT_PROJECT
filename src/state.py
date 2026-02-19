from typing import List, TypedDict
from pydantic import BaseModel, Field

class AgentState(TypedDict):
    user_prompt: str
    architecture: dict
    code: str
    review_score: float
    review_feedback: str
    revision_count: int
    final_report: str
    template_name: str
    template_context: dict

class ArchitectureSchema(BaseModel):
    files: List[str] = Field(description="List of files to be created")
    technologies: List[str] = Field(description="Stack used")
    logic_summary: str = Field(description="High-level logic summary")

class ReviewSchema(BaseModel):
    score: float = Field(description="Score from 0.0 to 1.0")
    feedback: str = Field(description="Feedback on improvements")