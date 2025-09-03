# tasks/itinerary_task.py
from crewai import Task, Crew
from agents.itinerary_builder import itinerary_planner

def run_itinerary_builder(user_prompt: str, context: dict):
    """
    Runs the Itinerary Builder agent.
    Context should include aggregated outputs from: travel_research, weather, transport, hotels, budget.
    The itinerary builder will create a day-by-day plan and return it in paragraph format (not JSON).
    """
    description = """
    You are creating a day-by-day travel itinerary.

    User Request:
    {user_prompt}

    Supporting Context:
    - Travel Research: {research_output}
    - Weather: {weather_output}
    - Transport: {transport_output}
    - Hotels: {hotels_output}
    - Budget: {budget_output}

    Instructions:
    Write the complete itinerary in a natural, narrative style.
    Each day should be written in paragraph format, like a travel blog or guidebook.
    Do NOT use JSON, bullet points, or lists.
    Just write flowing text with transitions.
    """

    task = Task(
        description=description,
        agent=itinerary_planner,
        expected_output="A detailed day-by-day itinerary written as natural language paragraphs only",
    )

    crew = Crew(
        agents=[itinerary_planner],
        tasks=[task],
        verbose=False
    )

    inputs = {
        "user_prompt": user_prompt,
        "research_output": context.get("research", "No travel research available."),
        "weather_output": context.get("weather", "No weather advice available."),
        "transport_output": context.get("transport", "No transport advice available."),
        "hotels_output": context.get("hotels", "No hotel recommendations available."),
        "budget_output": context.get("budget", "No budget optimization available."),
    }
    result = crew.kickoff(inputs=inputs)

    return result.raw

