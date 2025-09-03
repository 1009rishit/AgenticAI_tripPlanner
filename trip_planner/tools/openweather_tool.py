import requests
from datetime import datetime
from collections import defaultdict
from dotenv import load_dotenv
from crewai.tools import BaseTool
from typing import Type
from pydantic import BaseModel, Field
import os

# Load environment variables
load_dotenv()

# Input schema
class OpenWeatherInput(BaseModel):
    city: str = Field(..., description="City name with country code, e.g., 'Paris,FR'")
    days: int = Field(5, description="Number of forecast days (max 5 for free API)")

# Helper function to fetch weather
def fetch_weather_forecast(city: str, days: int = 5):
    api_key = os.getenv("OPEN_WEATHER_API_KEY")
    if not api_key:
        raise ValueError("OPEN_WEATHER_API_KEY not set in .env file")

    url = "https://api.openweathermap.org/data/2.5/forecast"
    params = {
        "q": city,
        "appid": api_key,
        "units": "metric"
    }

    response = requests.get(url, params=params)
    if response.status_code != 200:
        raise Exception(f"OpenWeather API error: {response.status_code} - {response.text}")

    data = response.json()
    daily_data = defaultdict(list)

    # Group forecasts by date
    for entry in data.get("list", []):
        date_str = datetime.fromtimestamp(entry["dt"]).strftime("%Y-%m-%d")
        if len(daily_data) < days:
            daily_data[date_str].append(entry)

    forecast_list = []
    for date, entries in daily_data.items():
        temps = [e["main"]["temp"] for e in entries]
        weather_descriptions = [e["weather"][0]["description"] for e in entries]
        weather_summary = max(set(weather_descriptions), key=weather_descriptions.count)
        forecast_list.append(f"{date}: {weather_summary}, Temp: {min(temps):.1f}°C to {max(temps):.1f}°C")

    return "\n".join(forecast_list)

# Tool class
class OpenWeatherTool(BaseTool):
    name: str = "OpenWeather Forecast"
    description: str = "Provides a multi-day weather forecast for a given city using OpenWeather API."
    args_schema: Type[BaseModel] = OpenWeatherInput

    def _run(self, city: str, days: int = 5) -> str:
        return fetch_weather_forecast(city, days)

# Optional testing block
if __name__ == "__main__":
    try:
        print("Testing OpenWeather Tool...")
        tool_instance = OpenWeatherTool()
        result = tool_instance._run(city="Paris,FR", days=3)
        print("Forecast:")
        print(result)
    except Exception as e:
        print(f"Error: {e}")
