import os
from dotenv import load_dotenv
from langchain_groq import ChatGroq

THRESHOLD = 0.8
MAX_REVISIONS = 3

load_dotenv()

llm = ChatGroq(
    model=os.getenv("GROQ_MODEL", "llama-3.3-70b-versatile"),
    api_key=os.getenv("GROQ_API_KEY"),
    temperature=0
)