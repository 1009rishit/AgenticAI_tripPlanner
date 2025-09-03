# tasks/budget_task.py
from crewai import Task, Crew
from agents.budget_optimizer_agent import budget_optimizer
import json

def run_budget_optimizer(user_prompt: str, context: dict):
    """
    Runs the Budget Optimizer agent with user input and context.
    
    Args:
        user_prompt (str): The user query or requirement 
            (e.g., "Optimize trip for 7 days under $2000").
        context (dict): Prior task outputs 
            (e.g., transport_estimates, hotel_options, meal_estimate, activities).
    
    Returns:
        dict: {
            "raw": Raw Crew output,
            "structured": JSON-like structured output (if parsing succeeds)
        }
    """
    description = (
        "You are a Budget Optimizer. "
        "Main request: {user_prompt}. "
        "Additional context: {context}. "
        "Use the provided context (transport_estimates, hotel_options, meal_estimate, activities) "
        "along with the user prompt to create a cost-optimized trip plan. "
        "Return strictly paragrapgh format with the following information:\n"
        "- total_estimate\n"
        "- per_day_breakdown (list of daily costs)\n"
        "- per_component_costs (transport, hotel, meals, activities)\n"
        "- suggested_savings (list)\n"
        "- alternatives (list of cheaper options)\n"
    )

    task = Task(
        description=description,
        agent=budget_optimizer,
        expected_output="A valid paragraph format with trip budget optimization details"
    )

    crew = Crew(
        agents=[budget_optimizer],
        tasks=[task],
        verbose=False
    )


    context_str = ", ".join(f"{k}: {v}" for k, v in context.items()) if context else ""
    inputs = {"user_prompt": str(user_prompt), "context": context_str}

    result = crew.kickoff(inputs=inputs)

    return result.raw
