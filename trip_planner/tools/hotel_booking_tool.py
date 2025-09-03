# tools/hotel_booking_tool.py

from datetime import datetime
from typing import Type
from pydantic import BaseModel, Field
from crewai.tools import BaseTool


# Input schema for the hotel booking tool
class HotelBookingInput(BaseModel):
    """Input schema for booking a hotel."""
    hotel_name: str = Field(..., description="Name of the hotel")
    check_in_date: str = Field(..., description="Check-in date in YYYY-MM-DD format")
    check_out_date: str = Field(..., description="Check-out date in YYYY-MM-DD format")
    num_guests: int = Field(..., description="Number of guests (must be at least 1)")


# Hotel booking tool class
class HotelBookingTool(BaseTool):
    name: str = "Hotel Booking Tool"
    description: str = (
        "Tool to book a hotel given hotel name, check-in date, check-out date, and number of guests."
    )
    args_schema: Type[BaseModel] = HotelBookingInput

    def _run(self, hotel_name: str, check_in_date: str, check_out_date: str, num_guests: int) -> str:
        try:
            # Validate dates
            datetime.strptime(check_in_date, "%Y-%m-%d")
            datetime.strptime(check_out_date, "%Y-%m-%d")

            if num_guests <= 0:
                return "Error: Number of guests must be at least 1."

            # Simulate booking confirmation
            confirmation_number = f"HB-{datetime.now().strftime('%Y%m%d%H%M%S')}-{hash(hotel_name) % 10000}"
            return (
                f"✅ Successfully booked **{hotel_name}** for **{num_guests}** guest(s) "
                f"from **{check_in_date}** to **{check_out_date}**.\n"
                f"📄 Confirmation number: `{confirmation_number}`"
            )

        except ValueError:
            return "❌ Error: Invalid date format. Please use YYYY-MM-DD."
        except Exception as e:
            return f"❌ An unexpected error occurred during booking: {e}"


# # Optional: CLI test
# if __name__ == "__main__":
#     try:
#         print("Testing Hotel Booking Tool...")
#         tool = HotelBookingTool()
#         result = tool._run(
#             hotel_name="Taj Rambagh Palace",
#             check_in_date="2025-09-10",
#             check_out_date="2025-09-15",
#             num_guests=2
#         )
#         print("Result:")
#         print(result)
#     except Exception as e:
#         print(f"Error during test: {e}")
