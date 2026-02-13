import os
from dotenv import load_dotenv
from typing import List, TypedDict
from pydantic import BaseModel, Field

# LangChain & LangGraph Imports
from langchain_groq import ChatGroq
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.output_parsers import StrOutputParser
from langgraph.graph import StateGraph, END

load_dotenv()
# --- 1. CONFIGURATION ---
# Ensure your GROQ_API_KEY is set in your environment variables
model_name = os.getenv("GROQ_MODEL", "llama-3.3-70b-versatile")
api_key = os.getenv("GROQ_API_KEY")

llm = ChatGroq(
    model=model_name,
    groq_api_key=api_key,
    temperature=0
)

THRESHOLD = 0.8  # The score required to pass the Reviewer
MAX_REVISIONS = 3  # Safety break to prevent infinite loops


# --- 2. STATE DEFINITION ---
class AgentState(TypedDict):
    user_prompt: str
    architecture: dict
    code: str
    review_score: float
    review_feedback: str
    revision_count: int


# --- 3. STRUCTURED OUTPUT SCHEMAS ---
class ArchitectureSchema(BaseModel):
    """Plan for the codebase structure."""
    files: List[str] = Field(description="List of files to be created (e.g. App.tsx, styles.css)")
    technologies: List[str] = Field(description="Stack used (React, TypeScript, Tailwind, etc.)")
    logic_summary: str = Field(description="High-level logic and component hierarchy")


class ReviewSchema(BaseModel):
    """Assessment of the generated code."""
    score: float = Field(description="A score from 0.0 to 1.0 based on code quality")
    feedback: str = Field(description="Critical feedback on what needs to be improved")


# --- 4. AGENT NODES ---

def architect_agent(state: AgentState):
    print("--- NODE: ARCHITECT ---")
    prompt = ChatPromptTemplate.from_messages([
        ("system", "You are a Senior Software Architect. Create a technical JSON blueprint for the user's request."),
        ("user", "{input}")
    ])

    # Using Groq's structured output capability
    structured_llm = llm.with_structured_output(ArchitectureSchema)
    chain = prompt | structured_llm

    result = chain.invoke({"input": state["user_prompt"]})
    return {"architecture": result.model_dump(), "revision_count": 0}


def implementor_agent(state: AgentState):
    print("--- NODE: IMPLEMENTOR ---")
    prompt = ChatPromptTemplate.from_messages([
        ("system",
         "You are a Lead Developer. Write functional, production-ready React/TypeScript code based on the architecture JSON."),
        ("user", "Architecture Blueprint: {arch_json}")
    ])

    chain = prompt | llm | StrOutputParser()
    code_output = chain.invoke({"arch_json": state["architecture"]})
    return {"code": code_output}


def reviewer_agent(state: AgentState):
    print("--- NODE: REVIEWER ---")
    prompt = ChatPromptTemplate.from_messages([
        ("system",
         "You are a QA Engineer. Evaluate the code for bugs, best practices, and typesafety. Return a score (0-1) and feedback in JSON."),
        ("user", "Code to review:\n{code}")
    ])

    structured_llm = llm.with_structured_output(ReviewSchema)
    chain = prompt | structured_llm

    review = chain.invoke({"code": state["code"]})
    print(f"--- Review Score: {review.score} ---")
    return {"review_score": review.score, "review_feedback": review.feedback}


def fixer_agent(state: AgentState):
    print(f"--- NODE: FIXER (Revision #{state['revision_count'] + 1}) ---")
    prompt = ChatPromptTemplate.from_messages([
        ("system",
         "You are a Senior Debugger. Improve the code based on the Reviewer's feedback. Return ONLY the updated code block."),
        ("user", "Current Code:\n{code}\n\nFeedback to address: {feedback}")
    ])

    chain = prompt | llm | StrOutputParser()
    updated_code = chain.invoke({
        "code": state["code"],
        "feedback": state["review_feedback"]
    })

    return {
        "code": updated_code,
        "revision_count": state["revision_count"] + 1
    }


# --- 5. CONDITIONAL LOGIC ---

def route_after_review(state: AgentState):
    """Determines if the code is finished or needs fixing."""
    if state["review_score"] >= THRESHOLD:
        return "accept"
    elif state["revision_count"] >= MAX_REVISIONS:
        print("--- REACHED MAX REVISIONS: Terminating with current version ---")
        return "accept"
    else:
        return "refactor"


# --- 6. GRAPH CONSTRUCTION ---

workflow = StateGraph(AgentState)

# Add all nodes
workflow.add_node("architect", architect_agent)
workflow.add_node("implementor", implementor_agent)
workflow.add_node("reviewer", reviewer_agent)
workflow.add_node("fixer", fixer_agent)

# Set the flow
workflow.set_entry_point("architect")
workflow.add_edge("architect", "implementor")
workflow.add_edge("implementor", "reviewer")

# Add the decision branch
workflow.add_conditional_edges(
    "reviewer",
    route_after_review,
    {
        "accept": END,
        "refactor": "fixer"
    }
)

# Fixer loops back to the Reviewer
workflow.add_edge("fixer", "reviewer")

# Compile the graph
app = workflow.compile()

print(app.get_graph().draw_mermaid())

# --- 7. RUNNING THE AGENT ---
if __name__ == "__main__":
    task = input()

    print(f"Starting work on: {task}\n")

    # Execute the graph
    final_state = app.invoke({"user_prompt": task})

    print("\n" + "=" * 50)
    print("FINAL DELIVERABLE")
    print("=" * 50)
    print(f"Final Score: {final_state['review_score']}")
    print("\nCODE:\n")
    print(final_state["code"])