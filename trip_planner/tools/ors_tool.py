import os
import requests
from dotenv import load_dotenv
from typing import Type
from pydantic import BaseModel, Field
from crewai.tools import BaseTool

# Load environment variables
load_dotenv()

# -----------------------------
# Original ORS API call logic
# -----------------------------
def get_route_summary(start_lat, start_lon, end_lat, end_lon, mode="driving-car"):
    api_key = os.getenv("ORS_API_KEY")
    if not api_key:
        raise ValueError("ORS_API_KEY not set in .env file")

    url = f"https://api.openrouteservice.org/v2/directions/{mode}"
    headers = {
        "Authorization": api_key,
        "Content-Type": "application/json"
    }
    body = {
        "coordinates": [
            [start_lon, start_lat],
            [end_lon, end_lat]
        ]
    }

    try:
        response = requests.post(url, json=body, headers=headers, timeout=10)
        response.raise_for_status()
        data = response.json()
    except requests.exceptions.RequestException as e:
        raise Exception(f"Request failed: {e}")
    except ValueError:
        raise Exception("Invalid JSON response received from ORS API")

    if "routes" not in data or not data["routes"]:
        raise Exception(f"No route data found: {data}")

    summary = data["routes"][0]["summary"]
    return {
        "distance_km": round(summary["distance"] / 1000, 2),  # meters → km
        "duration_min": round(summary["duration"] / 60, 2),   # seconds → minutes
        "mode": mode
    }

# -----------------------------
# Simplified Input schema for location-based searches
# -----------------------------
class ORSLocationInput(BaseModel):
    start_location: str = Field(..., description="Starting location (city, address, or landmark)")
    end_location: str = Field(..., description="Destination location (city, address, or landmark)")
    mode: str = Field("driving-car", description="Transport mode: driving-car, cycling-regular, foot-walking, etc.")

# -----------------------------
# Helper function to get coordinates from location names
# -----------------------------
def get_coordinates(location: str):
    """
    Get coordinates for a location using a geocoding service.
    This is a simplified version - you might want to use a proper geocoding API.
    """
    # Using OpenRouteService geocoding API
    api_key = os.getenv("ORS_API_KEY")
    if not api_key:
        raise ValueError("ORS_API_KEY not set in .env file")
    
    geocode_url = "https://api.openrouteservice.org/geocode/search"
    params = {
        "api_key": api_key,
        "text": location,
        "size": 1
    }
    
    try:
        response = requests.get(geocode_url, params=params, timeout=10)
        response.raise_for_status()
        data = response.json()
        
        if not data.get("features"):
            raise Exception(f"Location '{location}' not found")
        
        coordinates = data["features"][0]["geometry"]["coordinates"]
        return coordinates[1], coordinates[0]  # lat, lon
    except Exception as e:
        raise Exception(f"Failed to geocode '{location}': {e}")

# -----------------------------
# ORS Tool as CrewAI BaseTool (Location-based)
# -----------------------------
class ORSLocationTool(BaseTool):
    name: str = "OpenRouteService Location Route Finder"
    description: str = (
        "Get travel distance, duration, and route summary between two locations by name. "
        "Supports driving, cycling, walking, and other modes. Just provide location names."
    )
    args_schema: Type[BaseModel] = ORSLocationInput

    def _run(self, start_location: str, end_location: str, mode: str = "driving-car") -> str:
        """
        CrewAI tool interface to call ORS API with location names.
        """
        try:
            # Get coordinates for both locations
            start_lat, start_lon = get_coordinates(start_location)
            end_lat, end_lon = get_coordinates(end_location)
            
            # Get route summary
            summary = get_route_summary(start_lat, start_lon, end_lat, end_lon, mode)
            
            return (
                f"Route from {start_location} to {end_location}\n"
                f"Mode: {summary['mode']}\n"
                f"Distance: {summary['distance_km']} km\n"
                f"Duration: {summary['duration_min']} minutes"
            )
        except Exception as e:
            return f"Error getting route information: {str(e)}"

# -----------------------------
# Original coordinate-based tool (kept for backward compatibility)
# -----------------------------
class ORSSearchInput(BaseModel):
    start_lat: float = Field(..., description="Start latitude")
    start_lon: float = Field(..., description="Start longitude")
    end_lat: float = Field(..., description="End latitude")
    end_lon: float = Field(..., description="End longitude")
    mode: str = Field("driving-car", description="Transport mode: driving-car, cycling-regular, foot-walking, etc.")

class ORSTool(BaseTool):
    name: str = "OpenRouteService Route Finder"
    description: str = (
        "Get travel distance, duration, and route summary between two coordinates. "
        "Supports driving, cycling, walking, and other modes."
    )
    args_schema: Type[BaseModel] = ORSSearchInput

    def _run(self, start_lat: float, start_lon: float, end_lat: float, end_lon: float, mode: str = "driving-car") -> str:
        """
        CrewAI tool interface to call ORS API.
        """
        try:
            summary = get_route_summary(start_lat, start_lon, end_lat, end_lon, mode)
            return f"Mode: {summary['mode']}\nDistance: {summary['distance_km']} km\nDuration: {summary['duration_min']} minutes"
        except Exception as e:
            return f"Error getting route information: {str(e)}"

# -----------------------------
# Test run
# -----------------------------
if __name__ == "__main__":
    try:
        print("Testing ORS Location Tool...")
        tool = ORSLocationTool()
        result = tool._run(
            start_location="Delhi, India",
            end_location="Leh, Ladakh, India",
            mode="driving-car"
        )
        print("Result:")
        print(result)
    except Exception as e:
        print(f"Error: {e}")