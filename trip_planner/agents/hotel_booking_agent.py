from crewai import Agent
from model import llm
from tools.hotel_booking_tool import HotelBookingTool

hotel_booking_tool = HotelBookingTool()

hotel_booker = Agent(
    role="Hotel Booking Agent",
    goal=(
        "Book hotels based on user selection, specified dates, and number of guests. "
        "Confirm booking details and provide a confirmation number. "
        "Always ensure all necessary information (hotel name, check-in, check-out, guests) is available before attempting to book."
    ),
    backstory=(
        "You are an efficient and reliable hotel booking specialist. "
        "You take user's preferences for hotels, dates, and number of guests "
        "and use the Hotel Booking Tool to secure reservations. "
        "You are meticulous about details and always provide booking confirmation."
    ),
    tools=[hotel_booking_tool],
    llm=llm,
    verbose=True,
)
