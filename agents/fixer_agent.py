from langchain_core.prompts import ChatPromptTemplate
from langchain_core.output_parsers import StrOutputParser
from config import llm
from state import AgentState
def fixer_agent(state: AgentState):
    print(f"--- NODE: FIXER ---")
    prompt = ChatPromptTemplate.from_messages([
        ("system", "You are a Senior Debugger. Fix code based on feedback."),
        ("user", "Code:\n{code}\n\nFeedback: {feedback}")
    ])
    chain = prompt | llm | StrOutputParser()
    updated_code = chain.invoke({"code": state["code"], "feedback": state["review_feedback"]})
    return {"code": updated_code, "revision_count": state["revision_count"] + 1}