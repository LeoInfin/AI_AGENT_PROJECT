from langchain_core.prompts import ChatPromptTemplate
from src.config import llm
from src.state import AgentState, ArchitectureSchema

def architect_agent(state: AgentState):
    print("--- NODE: ARCHITECT ---")
    
    # I set default template info here so the renderer knows what to use later
    template_name = state.get("template_name", "react_ts_tailwind")
    template_context = state.get("template_context", {
        "project_name": "My AI Project",
        "primary_color": "#3b82f6",
        "secondary_color": "#10b981",
        "main_content": None,
        "imports": None
    })

    prompt = ChatPromptTemplate.from_messages([
        ("system", (
            "You are a Senior Software Architect. Create a JSON blueprint of the files needed for the project.\n"
            "The project will start from a base 'react_ts_tailwind' template which includes:\n"
            "- Vite configuration\n"
            "- TypeScript setup\n"
            "- Tailwind CSS setup\n"
            "- Basic src/App.tsx and src/main.tsx\n\n"
            "Your task is to identify and list only the additional custom components and logic files required to fulfill the user's request."
        )),
        ("user", "User Request: {input}")
    ])
    
    chain = prompt | llm.with_structured_output(ArchitectureSchema)
    result = chain.invoke({"input": state["user_prompt"]})
    
    return {
        "architecture": result.model_dump(),
        "template_name": template_name,
        "template_context": template_context,
        "revision_count": 0
    }