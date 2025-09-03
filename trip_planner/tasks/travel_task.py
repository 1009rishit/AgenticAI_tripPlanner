# tasks/travel_task.py
from crewai import Task, Crew
from agents.travel_researcher import travel_researcher
from typing import Dict, Any

def run_travel_research(user_prompt: str, context: Dict[str, Any]):
    """
    Runs the Travel Researcher agent.
    Args:
        user_prompt: The main query string (e.g., "Plan a 3-day trip to Manali")
        context: Dict with any additional info (e.g., {"destination": "Manali"})
    Returns:
        dict with raw output and placeholder for structured JSON.
    """
    # Format the context dictionary into a readable string for the agent
    formatted_context = "\n".join([f"{k}: {v}" for k, v in context.items() if v is not None])

    description = (
        "Research attractions and local tips for the given trip. "
        "Main request: {query}. "
        "Additional context:\n{formatted_context}. "
        "Output should be a single, continuous natural language paragraph summarizing all findings, "
        "without explicit sections, bullet points, or lists, and without any programmatic wrapping (e.g., no 'raw: CrewOutput(...)')."
    )
    
    task = Task(
        description=description,
        agent=travel_researcher,
        expected_output="A valid paragraph format with listing of attractions, hidden gems, tips and sources."
    )
    
    crew = Crew(
        agents=[travel_researcher],
        tasks=[task],
        verbose=False
    )
    
    inputs = {"query": user_prompt, "formatted_context": formatted_context}
    result = crew.kickoff(inputs=inputs)
    
    return result.raw
