from langgraph.graph import StateGraph, END
from state import AgentState
from agents import architect_agent, implementor_agent, reviewer_agent, fixer_agent

# Constants
THRESHOLD = 0.8
MAX_REVISIONS = 3

def route_after_review(state: AgentState):
    if state["review_score"] >= THRESHOLD or state["revision_count"] >= MAX_REVISIONS:
        return "accept"
    return "refactor"

# Build Graph
workflow = StateGraph(AgentState)

workflow.add_node("architect", architect_agent)
workflow.add_node("implementor", implementor_agent)
workflow.add_node("reviewer", reviewer_agent)
workflow.add_node("fixer", fixer_agent)

workflow.set_entry_point("architect")
workflow.add_edge("architect", "implementor")
workflow.add_edge("implementor", "reviewer")
workflow.add_conditional_edges("reviewer", route_after_review, {"accept": END, "refactor": "fixer"})
workflow.add_edge("fixer", "reviewer")

app = workflow.compile()

if __name__ == "__main__":
    task = input("Enter your coding task: ")
    final_state = app.invoke({"user_prompt": task})
    print(f"\nFinal Score: {final_state['review_score']}")
    print(final_state["code"])