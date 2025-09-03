# model.py
import os
from dotenv import load_dotenv
from crewai import LLM

load_dotenv()

# Load your Gemini API key
api_key = os.getenv("GEMINI_API_KEY")

# CrewAI LLM wrapper for Google Gemini
llm = LLM(
    model="gemini/gemini-2.5-flash-lite",
    api_key=api_key,
    temperature=0.7,  
)
