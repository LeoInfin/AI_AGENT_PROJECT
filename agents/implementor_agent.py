from langchain_core.prompts import ChatPromptTemplate
from langchain_core.output_parsers import StrOutputParser
from config import llm
from state import AgentState

def implementor_agent(state: AgentState):
    print("--- NODE: IMPLEMENTOR ---")
    prompt = ChatPromptTemplate.from_messages([
        ("system", "You are a Lead Developer. Write React/TS code."),
        ("user", "Architecture: {arch_json}")
    ])
    chain = prompt | llm | StrOutputParser()
    code = chain.invoke({"arch_json": state["architecture"]})
    return {"code": code}