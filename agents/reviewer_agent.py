from langchain_core.prompts import ChatPromptTemplate
from config import llm
from state import AgentState, ReviewSchema

def reviewer_agent(state: AgentState):
    print("--- NODE: REVIEWER ---")
    prompt = ChatPromptTemplate.from_messages([
        ("system", "You are a QA Engineer. Return JSON with 'score' and 'feedback'."),
        ("user", "Code:\n{code}")
    ])
    chain = prompt | llm.with_structured_output(ReviewSchema)
    review = chain.invoke({"code": state["code"]})
    return {"review_score": review.score, "review_feedback": review.feedback}