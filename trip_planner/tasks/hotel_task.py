# tasks/hotel_task.py
from crewai import Task, Crew
from agents.hotel_recommendation_agent import hotel_recommender

def run_hotel_recommendation(user_prompt: str, context: dict):
    """
    Runs the Hotel Recommender agent.
    Context expected keys: destination, budget_per_night or total_budget, 
    travelers, neighborhoods_of_interest
    Returns raw + structured (if parsed later).
    """
    description = (
        "Recommend hotels/alternatives in destination within given budget and near attractions/neighborhoods. "
        "Main request: {user_prompt}. "
        "Additional context: {context}. "
        "Output should be paragrapgh structure and include grouped suggestions "
        "by budget (budget/mid/luxury), with name, brief notes, approximate price, "
        "and booking tips."
    )

    task = Task(
        description=description,
        agent=hotel_recommender,
        expected_output="A valid paragraph format with Hotel recommendations grouped by budget"
    )

    crew = Crew(
        agents=[hotel_recommender],
        tasks=[task],
        verbose=False,
    )

    # stringify context for safe interpolation
    context_str = ", ".join(f"{k}: {v}" for k, v in context.items())
    inputs = {"user_prompt": user_prompt, "context": context_str}

    result = crew.kickoff(inputs=inputs)

    return result.raw
