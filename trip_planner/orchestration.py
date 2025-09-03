from datetime import datetime
from typing import Dict, Any, List
import re


from tasks.travel_task import run_travel_research
from tasks.weather_task import run_weather_advice
from tasks.transport_task import run_transport_advice
from tasks.hotel_task import run_hotel_recommendation
from tasks.budget_task import run_budget_optimizer
from tasks.itinerary_task import run_itinerary_builder
from tasks.hotel_booking_task import run_hotel_booking

# Redis memory
from db.memory_store import add_memory, query_memory


class ConversationalOrchestrator:
    """Handles conversational flow with persistent memory and dynamic agent orchestration."""

    def __init__(self, user_id: str = "default_user"):
        self.user_id = user_id
        self.context: Dict[str, Any] = {
            "origin": None,
            "destination": None,
            "start_date": None,
            "end_date": None,
            "travel_mode_preference": None,
            "budget_total": None,
            "travelers": 1,
            "hotel_name": None,
            "check_in_date": None,
            "check_out_date": None,
            "booking_pending_confirmation": False,
            "last_query_intent": "overview" # Tracks the last classified intent
        }
        self.agent_outputs: Dict[str, Any] = {}
        self.conversation_history: List[Dict[str, str]] = []

    # -------------------
    # Context Parsing
    # -------------------
    def parse_user_prompt(self, user_prompt: str) -> Dict[str, Any]:
        ctx = self.context.copy()
        s = user_prompt.lower()

        def normalize_date(d: str):
            d = d.replace("/", "-")
            for fmt in ("%d-%m-%Y", "%d/%m/%Y", "%Y-%m-%d"):
                try:
                    return datetime.strptime(d, fmt).strftime("%Y-%m-%d")
                except:
                    continue
            return None

        # Extract destination (more robust)
        if not ctx["destination"]:
            m_dest = re.search(r"(?:travel to|trip to|plan for|going to|in)\s+([a-z\s\-]+)", s)
            if m_dest:
                ctx["destination"] = m_dest.group(1).strip().title()

        # Extract origin (if provided)
        m_origin = re.search(r"from\s+([a-z\s\-]+)\s+to", s)
        if m_origin:
            ctx["origin"] = m_origin.group(1).strip().title()

        # Extract dates (main trip dates)
        m_dates = re.search(r"(\d{4}-\d{2}-\d{2}|\d{1,2}[/-]\d{1,2}[/-]\d{4})\s*(?:to|-)\s*(\d{4}-\d{2}-\d{2}|\d{1,2}[/-]\d{1,2}[/-]\d{4})", s)
        if m_dates:
            ctx["start_date"] = normalize_date(m_dates.group(1))
            ctx["end_date"] = normalize_date(m_dates.group(2))

        # Extract single date (could be for booking or general inquiry)
        m_single_date = re.search(r"(?:on|for)\s+(\d{4}-\d{2}-\d{2}|\d{1,2}[/-]\d{1,2}[/-]\d{4})", s)
        if m_single_date:
            if not ctx["start_date"]:
                ctx["start_date"] = normalize_date(m_single_date.group(1))
            if not ctx["check_in_date"] and ("book" in s or "reserve" in s):
                ctx["check_in_date"] = normalize_date(m_single_date.group(1))

        # Extract travelers
        m_travelers = re.search(r"(\d+)\s*(?:person|people|traveler)s?", s)
        if m_travelers:
            ctx["travelers"] = int(m_travelers.group(1))

        # Extract budget
        m_budget = re.search(r"budget.*?(\d+)", s)
        if m_budget:
            ctx["budget_total"] = int(m_budget.group(1))

        # Extract travel mode
        if "car" in s: ctx["travel_mode_preference"] = "car"
        elif "flight" in s or "plane" in s: ctx["travel_mode_preference"] = "flight"
        elif "train" in s: ctx["travel_mode_preference"] = "train"

        # Hotel booking specific extraction
        m_hotel_booking = re.search(r"(?:book|reserve)(?: a room in| the)?\s+(.+?)(?=\s*(?:from|for|on|\d{4}-\d{2}-\d{2}|\d{1,2}[/-]\d{1,2}[/-]\d{4}|$))", s)
        if m_hotel_booking:
            hotel_name_extracted = m_hotel_booking.group(1).strip().title()
            if hotel_name_extracted:
                ctx["hotel_name"] = hotel_name_extracted

            # Attempt to extract dates and travelers directly from the booking prompt
            m_booking_details = re.search(r"(?:from|for)\s+(\d{4}-\d{2}-\d{2}|\d{1,2}[/-]\d{1,2}[/-]\d{4})\s*(?:to|-)?\s*(\d{4}-\d{2}-\d{2}|\d{1,2}[/-]\d{1,2}[/-]\d{4})?\s*(?:for\s+(\d+)\s*guest(?:s)?)?", s)
            if m_booking_details:
                ctx["check_in_date"] = normalize_date(m_booking_details.group(1))
                if m_booking_details.group(2):
                    ctx["check_out_date"] = normalize_date(m_booking_details.group(2))
                if m_booking_details.group(3):
                    ctx["travelers"] = int(m_booking_details.group(3))

        # Fallback for booking dates and travelers from main context if not explicitly in booking prompt
        if ("book" in s or "reserve" in s) and not ctx["check_in_date"] and ctx["start_date"]:
            ctx["check_in_date"] = ctx["start_date"]
        if ("book" in s or "reserve" in s) and not ctx["check_out_date"] and ctx["end_date"]:
            ctx["check_out_date"] = ctx["end_date"]
        if ("book" in s or "reserve" in s) and not ctx["travelers"] and self.context.get("travelers"):
            ctx["travelers"] = self.context.get("travelers")

        return ctx

    # -------------------
    # Intent Classification (simplified for dynamic orchestration)
    # -------------------
    def classify_intent(self, user_input: str) -> str:
        user_input_lower = user_input.lower()

        # High priority for booking if booking keywords are present AND a potential hotel name is extracted
        if (re.search(r"book|reserve", user_input_lower) and 
            re.search(r"(.+?)(?:\s+(?:hotel|hostel|kothi))?", user_input_lower) and 
            (self.context.get("hotel_name") or self.context.get("booking_pending_confirmation"))):
            return "hotel_booking"
        
        # If booking is pending confirmation, force hotel_booking intent
        if self.context.get("booking_pending_confirmation") and re.search(r"yes|confirm|book it", user_input_lower):
            return "hotel_booking"

        # Other explicit intents
        if re.search(r"weather|climate|temperature|rain", user_input_lower): return "weather"
        if re.search(r"transport|how to reach|getting there", user_input_lower): return "transport"
        if re.search(r"hotel(?!.*book)|accommodation(?!.*book)|stay(?!.*book)|where to stay(?!.*book)|recommend hotel", user_input_lower): return "hotels"
        if re.search(r"budget|cost|price|expense", user_input_lower): return "budget"
        if re.search(r"itinerary|plan|schedule|day by day", user_input_lower): return "itinerary"
        if re.search(r"plan everything|complete planning|full trip", user_input_lower): return "full_planning"

        return "overview" # Default or general inquiry

    # -------------------
    # Formatting Output
    # -------------------
    @staticmethod
    def format_output(agent_out: Any) -> str:
        # If it's a CrewOutput object or similar that has a 'raw' attribute
        if hasattr(agent_out, 'raw'):
            return agent_out.raw
        return str(agent_out)

    # -------------------
    # Agent Executors (to be implemented more dynamically)
    # -------------------
    def run_travel_research_agent(self, prompt: str, past_context: str):
        out = run_travel_research(prompt, self.context)
        self.agent_outputs["travel_research"] = self.format_output(out)
        return self.agent_outputs["travel_research"]

    def run_weather_agent(self, prompt: str, past_context: str):
        ctx = {
            "destination": self.context.get("destination"),
            "start_date": self.context.get("start_date"),
            "end_date": self.context.get("end_date")
        }
        out = run_weather_advice(prompt, ctx)
        self.agent_outputs["weather_advice"] = self.format_output(out)
        return self.agent_outputs["weather_advice"]

    def run_transport_agent(self, prompt: str, past_context: str):
        ctx = {
            "origin": self.context.get("origin"),
            "destination": self.context.get("destination"),
            "travel_mode_preference": self.context.get("travel_mode_preference")
        }
        out = run_transport_advice(prompt, ctx)
        self.agent_outputs["transport_advice"] = self.format_output(out)
        return self.agent_outputs["transport_advice"]

    def run_hotel_agent(self, prompt: str, past_context: str):
        ctx = {
            "destination": self.context.get("destination"),
            "budget_total": self.context.get("budget_total")
        }
        out = run_hotel_recommendation(prompt, ctx)
        self.agent_outputs["hotel_recommendation"] = self.format_output(out)
        return self.agent_outputs["hotel_recommendation"]

    def run_hotel_booking_agent(self, prompt: str, past_context: str):
        hotel_name = self.context.get("hotel_name")
        check_in_date = self.context.get("check_in_date")
        check_out_date = self.context.get("check_out_date")
        num_guests = self.context.get("travelers")
        booking_pending_confirmation = self.context.get("booking_pending_confirmation", False)

        if not all([hotel_name, check_in_date, check_out_date, num_guests]):
            missing_info = []
            if not hotel_name: missing_info.append("hotel name")
            if not check_in_date: missing_info.append("check-in date (YYYY-MM-DD)")
            if not check_out_date: missing_info.append("check-out date (YYYY-MM-DD)")
            if not num_guests: missing_info.append("number of guests")
            return self.format_output(f"I need the following information to book a hotel: {', '.join(missing_info)}.")

        if booking_pending_confirmation:
            if re.search(r"yes|confirm|book it", prompt.lower()):
                out = run_hotel_booking(hotel_name, check_in_date, check_out_date, num_guests)
                self.agent_outputs["hotel_booking"] = self.format_output(out)
                self.context["booking_pending_confirmation"] = False
                return self.agent_outputs["hotel_booking"]
            else:
                self.context["booking_pending_confirmation"] = False
                return self.format_output("Hotel booking not confirmed. Please provide new details or explicitly confirm to book.")
        else:
            self.context["booking_pending_confirmation"] = True
            return self.format_output(f"I have the following details for your hotel booking: {hotel_name} from {check_in_date} to {check_out_date} for {num_guests} guest(s). Do you want to confirm this booking?")

    def run_budget_agent(self, prompt: str, past_context: str):
        ctx = {
            "budget_total": self.context.get("budget_total")
        }
        out = run_budget_optimizer(prompt, ctx)
        self.agent_outputs["budget_optimizer"] = self.format_output(out)
        return self.agent_outputs["budget_optimizer"]

    def run_itinerary_agent(self, prompt: str, past_context: str):
        required_agents = {
            "travel_research": self.run_travel_research_agent,
            "weather_advice": self.run_weather_agent,
            "transport_advice": self.run_transport_agent,
            "hotel_recommendation": self.run_hotel_agent,
            "budget_optimizer": self.run_budget_agent,
        }

        for agent_key, agent_func in required_agents.items():
            if agent_key not in self.agent_outputs:
                self.agent_outputs[agent_key] = self.format_output(agent_func(prompt, past_context))

        # Now collect context
        ctx = {
            "research": self.agent_outputs.get("travel_research", "No travel research available."),
            "weather": self.agent_outputs.get("weather_advice", "No weather advice available."),
            "transport": self.agent_outputs.get("transport_advice", "No transport advice available."),
            "hotels": self.agent_outputs.get("hotel_recommendation", "No hotel recommendations available."),
            "budget": self.agent_outputs.get("budget_optimizer", "No budget optimization available."),
        }

        try:
            itinerary_output_str = run_itinerary_builder(user_prompt=prompt, context=ctx)
            self.agent_outputs["itinerary"] = itinerary_output_str
        except Exception as e:
            print(f"Error running itinerary builder: {e}")
            self.agent_outputs["itinerary"] = "Sorry, could not generate full itinerary, but here's what I have."

        return self.agent_outputs["itinerary"]

    # -------------------
    # Main Orchestration Logic
    # -------------------
    def process_user_input(self, user_input: str) -> Dict[str, Any]:
        memory_results = query_memory(user_input, top_k=3)
        past_context = ""
        if memory_results and memory_results.get("documents"):
            past_context = "\n".join(memory_results["documents"][0])

        # Update context based on user input
        new_ctx = self.parse_user_prompt(user_input)
        self.context.update({k: v for k, v in new_ctx.items() if v is not None})

        # Dynamic Intent Classification (more flexible)
        intent = self.classify_intent(user_input)
        self.context["last_query_intent"] = intent # Store last intent

        response = None

        # If a booking confirmation is pending, prioritize that
        if self.context.get("booking_pending_confirmation") and intent == "hotel_booking":
            response = self.format_output(self.run_hotel_booking_agent(user_input, past_context))
        
        # Otherwise, run agents based on classified intent
        elif intent == "hotel_booking":
            response = self.format_output(self.run_hotel_booking_agent(user_input, past_context))
        elif intent == "itinerary" or intent == "full_planning":
            response = self.format_output(self.run_itinerary_agent(user_input, past_context))
        elif intent == "hotels":
            response = self.format_output(self.run_hotel_agent(user_input, past_context))
        elif intent == "weather":
            response = self.format_output(self.run_weather_agent(user_input, past_context))
        elif intent == "transport":
            response = self.format_output(self.run_transport_agent(user_input, past_context))
        elif intent == "budget":
            response = self.format_output(self.run_budget_agent(user_input, past_context))
        elif intent == "overview":
            response = self.format_output(self.run_travel_research_agent(user_input, past_context)) # Default to travel research for general queries
        else:
            # Fallback for unhandled explicit intents (shouldn't happen often with good patterns)
            response = self.format_output(self.run_travel_research_agent(user_input, past_context))

        # Store conversation memory in Redis
        memory_metadata = {
            "user_id": self.user_id,
            "intent": intent,
            "timestamp": datetime.now().isoformat()
        }
        doc_id = f"{self.user_id}_{datetime.now().timestamp()}"
        memory_text = f"Q: {user_input}\nA: {response}"
        add_memory(session_id=self.user_id,doc_id=doc_id, text=memory_text, metadata=memory_metadata)

        # Update local conversation history
        self.conversation_history.append({"role": "user", "content": user_input})
        self.conversation_history.append({"role": "assistant", "content": self.format_output(response)})

        return {
            "intent": intent,
            "response": self.format_output(response), # Directly return the response string
            "context": self.context
        }

    # -------------------
    # Context Summary
    # -------------------
    def get_context_summary(self) -> str:
        summary = "📌 **Trip Context:**\n"
        for k, v in self.context.items():
            if v:
                summary += f"- {k}: {v}\n"
        summary += "\n✅ **Completed Agents:** " + ", ".join(self.agent_outputs.keys())
        return summary 