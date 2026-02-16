from langchain_core.prompts import ChatPromptTemplate
from config import llm
from state import AgentState, ArchitectureSchema

def architect_agent(state: AgentState):
    print("--- NODE: ARCHITECT ---")
    prompt = ChatPromptTemplate.from_messages([
        ("system", "You are a Senior Software Architect. Create a JSON blueprint."),
        ("user", "{input}")
    ])
    chain = prompt | llm.with_structured_output(ArchitectureSchema)
    result = chain.invoke({"input": state["user_prompt"]})
    return {"architecture": result.model_dump(), "revision_count": 0}