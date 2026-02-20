from langchain_core.prompts import ChatPromptTemplate
from src.config import llm
from src.state import AgentState, ReviewSchema

def reviewer_agent(state: AgentState):
    print("--- NODE: REVIEWER ---")
    
    # Concatenate code dictionary into a delimited string for the reviewer
    full_code = "\n".join([f">>> {fname}\n{content}" for fname, content in state["code"].items()])
    
    prompt = ChatPromptTemplate.from_messages([
        ("system", "You are a QA Engineer. Return JSON with 'score' and 'feedback'."),
        ("user", "Code:\n{code}")
    ])
    chain = prompt | llm.with_structured_output(ReviewSchema)
    review = chain.invoke({"code": full_code})
    return {"review_score": review.score, "review_feedback": review.feedback}