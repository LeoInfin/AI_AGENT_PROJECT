from langgraph.graph import StateGraph, END
from src.state import AgentState
from src.agents import architect_agent, implementor_agent, reviewer_agent, fixer_agent
from src.config import THRESHOLD, MAX_REVISIONS

def route_after_review(state: AgentState):
    if state["review_score"] >= THRESHOLD or state["revision_count"] >= MAX_REVISIONS:
        return "accept"
    return "refactor"


def create_graph():
    workflow = StateGraph(AgentState)

    workflow.add_node("architect", architect_agent)
    workflow.add_node("implementor", implementor_agent)
    workflow.add_node("reviewer", reviewer_agent)
    workflow.add_node("fixer", fixer_agent)

    workflow.set_entry_point("architect")
    workflow.add_edge("architect", "implementor")
    workflow.add_edge("implementor", "reviewer")
    workflow.add_conditional_edges(
        "reviewer", 
        route_after_review, 
        {"accept": END, "refactor": "fixer"}
    )
    workflow.add_edge("fixer", "reviewer")

    return workflow.compile()