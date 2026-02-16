from langgraph.graph import StateGraph, END
from src.state import AgentState
from src.agents import architect_agent, implementor_agent, reviewer_agent, fixer_agent
import os
import re

# Constants
THRESHOLD = 0.8
MAX_REVISIONS = 3

def route_after_review(state: AgentState):
    if state["review_score"] >= THRESHOLD or state["revision_count"] >= MAX_REVISIONS:
        return "accept"
    return "refactor"


def save_project_to_disk(state: AgentState, base_folder: str = "generated_app"):
    """
    Parses the multi-file string and writes it to a unique local folder.
    If the folder exists, it appends _1, _2, etc.
    """
    # 1. Logic to find a unique folder name
    final_folder = base_folder
    counter = 1

    while os.path.exists(final_folder):
        final_folder = f"{base_folder}_{counter}"
        counter += 1

    # 2. Create the unique directory
    os.makedirs(final_folder)
    print(f"📁 Created unique project folder: {final_folder}")

    raw_code = state.get("code", "")
    if not raw_code:
        print("❌ No code found in state.")
        return

    # 3. Split and Save logic
    file_blocks = re.split(r'^>>>\s*', raw_code, flags=re.MULTILINE)

    for block in file_blocks:
        block = block.strip()
        if not block:
            continue

        lines = block.split('\n')
        filename = lines[0].strip()
        content = "\n".join(lines[1:]).strip()

        # Clean up markdown tags
        content = re.sub(r'```[a-z]*', '', content).replace('```', '').strip()

        file_path = os.path.join(final_folder, filename)
        os.makedirs(os.path.dirname(file_path), exist_ok=True)

        with open(file_path, "w", encoding="utf-8") as f:
            f.write(content)
            print(f"  📄 Written: {filename}")

    print(f"\n✅ Project successfully generated in ./{final_folder}")


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

    print(f"\n🚀 Starting AI Workflow for: {task}")

    # Run the LangGraph
    final_state = app.invoke({"user_prompt": task})

    print("\n" + "=" * 50)
    print("WORKFLOW COMPLETE")
    print("=" * 50)
    print(f"Final Review Score: {final_state.get('review_score')}")

    # Call the OS generation code
    save_project_to_disk(final_state, base_folder="my_ai_project")