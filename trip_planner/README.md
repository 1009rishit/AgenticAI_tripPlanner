# AI Conversational Trip Planner

## Overview
This project presents an intelligent AI-powered conversational trip planner that leverages autonomous agents to provide personalized and comprehensive travel recommendations. Built with CrewAI, Streamlit, and Redis, it offers a seamless and interactive experience for planning your next adventure, from itinerary generation to hotel booking.

## Features
- **Dynamic Agent Orchestration**: Utilizes specialized AI agents (Travel Researcher, Weather Advisor, Hotel Recommender, Budget Optimizer, Transport Advisor, Itinerary Builder) powered by CrewAI to gather, analyze, and synthesize travel information.
- **Intuitive Conversational Interface**: A user-friendly web interface built with Streamlit allows natural language interaction, making trip planning as easy as chatting with a knowledgeable travel agent.
- **Contextual Memory**: The system maintains conversational memory using Redis, ensuring that your preferences and trip details (destination, dates, travelers, budget) are carried over across interactions for a truly personalized experience.
- **Human-in-the-Loop Hotel Booking**: Get personalized hotel recommendations, and with a human confirmation step, securely book your preferred accommodation.
- **Comprehensive Itinerary Generation**: Generates detailed, day-by-day itineraries based on all gathered information and your specific travel parameters.
- **Real-time Weather Information**: Provides accurate weather forecasts and safety advice for your chosen destination and dates.
- **Budget Optimization**: Helps optimize your trip budget by considering various factors and preferences.
- **Transport Advice**: Offers recommendations for travel modes and routes.

## Architecture
The project is structured around the following key components:
- **`app.py`**: The Streamlit application that provides the conversational user interface.
- **`orchestration.py`**: The core orchestration logic, managing agent interactions, parsing user prompts, classifying intents, and maintaining conversational context.
- **`agents/`**: Contains definitions for various specialized AI agents (e.g., `travel_researcher.py`, `hotel_recommendation_agent.py`, `weather_advisor_agent.py`).
- **`tasks/`**: Defines the specific tasks that each agent performs (e.g., `travel_task.py`, `hotel_task.py`, `weather_task.py`).
- **`tools/`**: Houses custom tools used by the agents (e.g., `duckduckgo_tool.py`, `google_serper_tool.py`, `openweather_tool.py`, `hotel_booking_tool.py`).
- **`db/`**: Manages the memory store (e.g., `memory_store.py`) for persistent context.
- **`config/`**: Contains configuration settings (e.g., `setting.py`).

## Setup and Installation

### Prerequisites
- Python 3.9+ (or the version you are using, e.g., 3.13)
- `uv` (recommended for dependency management) or `pip`

### 1. Clone the repository
```bash
git clone https://github.com/your_username/trip_planner.git
cd trip_planner
```
*(Replace `your_username/trip_planner.git` with your actual repository URL)*

### 2. Create and activate a virtual environment
It's highly recommended to use a virtual environment to manage dependencies.

Using `uv` (recommended):
```bash
uv venv
source .venv/bin/activate
```

Using `venv`:
```bash
python -m venv myenv
source myenv/bin/activate
```
*(If you are on Windows, use `myenv\Scripts\activate`)*

### 3. Install dependencies
```bash
uv pip install -r requirements.txt
# Or if using pip:
# pip install -r requirements.txt
```

### 4. Configure API Keys
The project requires several API keys for its tools to function correctly. You will need to set these as environment variables. It's recommended to create a `.env` file in the root directory of the project.

Example `.env` file:
```
OPENWEATHER_API_KEY="your_openweather_api_key_here"
SERPER_API_KEY="your_google_serper_api_key_here"
# Add any other API keys required by your tools (e.g., ORS_API_KEY if using OpenRouteService)
```
- **OpenWeatherMap API Key**: For fetching weather data.
- **Google Serper API Key**: For web search capabilities (used by the Travel Researcher).

You can obtain these API keys from their respective websites.

### 5. Run the Streamlit Application
Once the dependencies are installed and API keys are configured, you can run the Streamlit application:

```bash
streamlit run app.py
```

This will open the application in your web browser, typically at `http://localhost:8501`.

## Usage
Interact with the AI Trip Planner through the Streamlit chat interface. You can start by asking it to:
- "Plan a trip to [destination] from [start date] to [end date] for [number] travelers."
- "Give me some hotel recommendations in [destination]."
- "Reserve a room in [Hotel Name] for me from [check-in date] to [check-out date] for [number] person."
- "What's the weather like in [destination] on [date]?"
- "What are some fun things to do in [destination]?"

The system will intelligently process your requests, utilize the appropriate agents and tools, and provide comprehensive responses.

## Contributing
(Optional section: Add guidelines for contributions, bug reports, feature requests, etc.)

## License
(Optional section: Specify the project's license)

## Contact
(Optional section: Your contact information or how to reach out)
