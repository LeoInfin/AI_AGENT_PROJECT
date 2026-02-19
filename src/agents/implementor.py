from langchain_core.prompts import ChatPromptTemplate
from langchain_core.output_parsers import StrOutputParser
from src.config import llm
from src.state import AgentState

def implementor_agent(state: AgentState):
    print("--- NODE: IMPLEMENTOR ---")

    system_prompt = (
        "You are a Senior Lead Developer. Your task is to implement the provided architecture "
        "into functional, production-ready React and TypeScript code.\n\n"
        
        "CONTEXT:\n"
        "A base 'react_ts_tailwind' template is already in place. Focus on generating the new components "
        "and logic files defined in the architecture. If you need to modify the main App.tsx, "
        "provided those changes as well.\n\n"

        "CRITICAL INSTRUCTIONS:\n"
        "1. Write the code for EVERY file listed in the architecture.\n"
        "2. You MUST separate each file using the delimiter '>>> ' followed by the filename.\n"
        "3. Example format:\n"
        "   >>> src/components/Button.tsx\n"
        "   (code for Button)\n"
        "   >>> src/App.tsx\n"
        "   (code for App)\n\n"

        "4. Do NOT use markdown code blocks (```) for the overall response; just use the delimiters.\n"
        "5. Ensure all imports between files are correct based on the file paths.\n"
        "6. Use modern React patterns (Functional Components, Hooks, and clean TypeScript interfaces)."
    )

    prompt = ChatPromptTemplate.from_messages([
        ("system", system_prompt),
        ("user", "Architecture to implement: {arch_json}")
    ])

    chain = prompt | llm | StrOutputParser()
    code = chain.invoke({"arch_json": state["architecture"]})
    
    return {"code": code}