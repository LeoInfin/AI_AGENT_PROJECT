from typing import List, TypedDict, Dict
from pydantic import BaseModel, Field

class AgentState(TypedDict):
    user_prompt: str
    architecture: dict
    code: Dict[str, str]
    review_score: float
    review_feedback: str
    revision_count: int
    final_report: str
    template_name: str
    template_context: dict
    rendered_templates: Dict[str, str]

class ArchitectureSchema(BaseModel):
    files: List[str] = Field(description="List of files to be created")
    technologies: List[str] = Field(description="Stack used")
    template_context: dict = Field(description="Key-value pairs for the Jinja2 template (e.g., project_name, primary_color, secondary_color, custom_components)")
    logic_summary: str = Field(description="High-level logic summary")

class ReviewSchema(BaseModel):
    score: float = Field(description="Score from 0.0 to 1.0")
    feedback: str = Field(description="Feedback on improvements")