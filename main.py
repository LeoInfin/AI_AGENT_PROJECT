from langgraph.graph import StateGraph, END
from src.state import AgentState
from src.agents import architect_agent, implementor_agent, reviewer_agent, fixer_agent
import os
import re
from src.utils.graph_loader import create_graph
from src.utils.renderer import save_project_to_disk


app = create_graph()

if __name__ == "__main__":
    task = input("Enter your coding task: ")

    print(f"\n🚀 Starting AI Workflow for: {task}")

    # Run the LangGraph
    final_state = app.invoke({"user_prompt": task})

    print("\n" + "=" * 50)
    print("WORKFLOW COMPLETE")
    print("=" * 50)
    print(f"Final Review Score: {final_state.get('review_score')}")

    # Call the OS generation code
    save_project_to_disk(final_state, base_folder="my_ai_project")