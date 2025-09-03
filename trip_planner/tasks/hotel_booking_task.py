from crewai import Task, Crew
from agents.hotel_booking_agent import hotel_booker

def run_hotel_booking(hotel_name: str, check_in_date: str, check_out_date: str, num_guests: int):
    """
    Runs the Hotel Booking agent to book a hotel.
    """
    description = (
        f"Book the hotel {hotel_name} for {num_guests} guests "
        f"from {check_in_date} to {check_out_date}."
    )

    task = Task(
        description=description,
        agent=hotel_booker,
        expected_output="A confirmation message with a booking confirmation number."
    )

    crew = Crew(
        agents=[hotel_booker],
        tasks=[task],
        verbose=False,
    )

    inputs = {
        "hotel_name": hotel_name,
        "check_in_date": check_in_date,
        "check_out_date": check_out_date,
        "num_guests": num_guests
    }

    result = crew.kickoff(inputs=inputs)

    return result.raw
