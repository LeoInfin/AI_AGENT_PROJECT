import re
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.output_parsers import StrOutputParser
from src.config import llm
from src.state import AgentState

def fixer_agent(state: AgentState):
    print(f"--- NODE: FIXER (Revision #{state['revision_count'] + 1}) ---")
    
    # Concatenate code dictionary for context
    current_code = "\n".join([f">>> {fname}\n{content}" for fname, content in state["code"].items()])
    skeletons_context = "\n".join([f">>> {fname}\n{content}" for fname, content in state.get("rendered_templates", {}).items()])

    system_prompt = (
        "You are a Senior Debugger and Refactoring Specialist.\n\n"
        "YOUR GOAL:\n"
        "Review the provided code and the feedback from the QA Engineer. "
        "Fix the issues while maintaining the overall architecture.\n\n"
        
        "CONTEXT:\n"
        "Below are the pre-rendered skeleton files for reference. "
        "Ensure your fixes are compatible with these files.\n\n"
        
        "SKELETON FILES:\n"
        "{rendered_templates}\n\n"

        "CRITICAL OUTPUT FORMAT:\n"
        "1. You MUST return the COMPLETE codebase, not just the changes.\n"
        "2. Every file must be preceded by the delimiter '>>> ' followed by the filename.\n"
        "3. LOOK FOR MARKERS: If the skeleton for this file contains `{{# AI_STATE #}}`, ensure your fixes are integrated at that location. Replace the marker with your implementation if it hasn't been replaced already.\n"
        "4. Example:\n"
        "   >>> src/App.tsx\n"
        "   (fixed code here)\n"
        "   >>> src/index.css\n"
        "   (code here)\n\n"

        "5. Do NOT use markdown code blocks (```). Just use the '>>> ' delimiters.\n"
        "6. Address every point mentioned in the feedback specifically."
    )

    prompt = ChatPromptTemplate.from_messages([
        ("system", system_prompt),
        ("user", "Current Codebase:\n{code}\n\nReviewer Feedback: {feedback}")
    ])

    chain = prompt | llm | StrOutputParser()

    updated_raw_code = chain.invoke({
        "code": current_code,
        "feedback": state["review_feedback"],
        "rendered_templates": skeletons_context
    })

    # Parse multi-file string back into a dictionary
    file_blocks = re.split(r'^>>>\s*', updated_raw_code, flags=re.MULTILINE)
    updated_code_dict = {}
    for block in file_blocks:
        block = block.strip()
        if not block: continue
        lines = block.split('\n')
        filename = lines[0].strip()
        content = "\n".join(lines[1:]).strip()
        updated_code_dict[filename] = content

    return {
        "code": updated_code_dict,
        "revision_count": state["revision_count"] + 1
    }