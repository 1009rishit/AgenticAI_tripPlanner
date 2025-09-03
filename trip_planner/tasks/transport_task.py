# tasks/transport_task.py
from crewai import Task, Crew
from agents.transport_advisor_agent import transport_advisor

def run_transport_advice(user_prompt: str, context: dict):
    """
    Runs the Transport Advisor agent.
    Context should include: origin, destination, travel_mode_preference (e.g. 'car'), travelers count.
    Returns raw result.
    """
    description = (
        "Recommend transport options for origin -> destination and key local legs. "
        "Consider user's travel_mode_preference and any constraints in context. "
        "Main request: {user_prompt}. "
        "Additional context: {context}. "
        "Output should include: recommended_mode(s), estimated_times, costs_estimates, in paragrapgh format  "
        "route_notes, safety_advice, apps/tips, sources."
    )

    task = Task(
        description=description,
        agent=transport_advisor,
        expected_output="A valid paragraph format with transport advice"
    )

    crew = Crew(
        agents=[transport_advisor],
        tasks=[task],
        verbose=False
    )

    # stringify context for safe interpolation
    context_str = ", ".join(f"{k}: {v}" for k, v in context.items())
    inputs = {"user_prompt": user_prompt, "context": context_str}

    result = crew.kickoff(inputs=inputs)

    return result.raw
