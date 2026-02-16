from langchain_core.prompts import ChatPromptTemplate
from langchain_core.output_parsers import StrOutputParser
from src.config import llm
from src.state import AgentState

def implementor_agent(state: AgentState):
    print("--- NODE: IMPLEMENTOR ---")

    # This prompt forces the LLM to use the ">>> filename" format you need for parsing
    system_prompt = (
        "You are a Senior Lead Developer. Your task is to implement the provided architecture "
        "into functional, production-ready React and TypeScript code.\n\n"

        "CRITICAL INSTRUCTIONS:\n"
        "1. Write the code for EVERY file listed in the architecture.\n"
        "2. You MUST separate each file using the delimiter '>>> ' followed by the filename.\n"
        "3. Example format:\n"
        "   >>> src/components/Button.tsx\n"
        "   (code for Button)\n"
        "   >>> src/App.tsx\n"
        "   (code for App)\n\n"

        "4. Do NOT use markdown code blocks (```) for the overall response; just use the delimiters.\n"
        "5. Ensure all imports between files are correct based on the file paths you define.\n"
        "6. Use modern React patterns (Functional Components, Hooks, and clean TypeScript interfaces)."
    )

    prompt = ChatPromptTemplate.from_messages([
        ("system", system_prompt),
        ("user", "Architecture: {arch_json}")
    ])

    chain = prompt | llm | StrOutputParser()
    code = chain.invoke({"arch_json": state["architecture"]})
    return {"code": code}