from langchain_core.prompts import ChatPromptTemplate
from langchain_core.output_parsers import StrOutputParser
from src.config import llm
from src.state import AgentState

def fixer_agent(state: AgentState):
    print(f"--- NODE: FIXER (Revision #{state['revision_count'] + 1}) ---")

    system_prompt = (
        "You are a Senior Debugger and Refactoring Specialist.\n\n"
        "YOUR GOAL:\n"
        "Review the provided code and the feedback from the QA Engineer. "
        "Fix the issues while maintaining the overall architecture.\n\n"

        "CRITICAL OUTPUT FORMAT:\n"
        "1. You MUST return the COMPLETE codebase, not just the changes.\n"
        "2. Every file must be preceded by the delimiter '>>> ' followed by the filename.\n"
        "3. Example:\n"
        "   >>> src/App.tsx\n"
        "   (fixed code here)\n"
        "   >>> src/index.css\n"
        "   (code here)\n\n"

        "4. Do NOT use markdown code blocks (```). Just use the '>>> ' delimiters.\n"
        "5. Address every point mentioned in the feedback specifically."
    )

    prompt = ChatPromptTemplate.from_messages([
        ("system", system_prompt),
        ("user", "Current Codebase:\n{code}\n\nReviewer Feedback: {feedback}")
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