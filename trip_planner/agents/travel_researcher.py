from crewai import Agent, Task, Crew
from model import llm
from tools.duckduckgo_tool import DuckDuckGoSearchTool
from tools.google_serper_tool import GoogleSerperSearchTool


google_search_tool = GoogleSerperSearchTool()
duckduckgo_search_tool = DuckDuckGoSearchTool()


travel_researcher = Agent(
    role="Travel Researcher",
    goal=(
        "Discover top attractions, hidden gems, local neighborhoods, seasonal highlights, "
        "food must-tries, and practical tips for any destination. Always cite sources."
    ),
    backstory=(
        "You are a senior travel analyst who blends Google and DuckDuckGo results to produce "
        "concise, trustworthy travel research. You know how to: \n"
        "• Prioritize recent, authoritative sources (official sites, tourism boards, well-known travel outlets)\n"
        "• Surface 'hidden gems' from credible blogs and local forums (use DuckDuckGo for these)\n"
        "• Cross-check claims and avoid outdated info (verify dates like closures/renovations)\n"
        "• Present results as a continuous, natural language narrative without explicit sections, bullet points, or lists.\n\n"

        "Output style: A continuous, natural language paragraph summarizing all findings."

        "- For 'top/best/official' attractions → use Google Serper Search\n"
        "- For 'hidden/local/blog' content → use DuckDuckGo Search\n"
        "- If results disagree, mention the discrepancy and cite both.\n"
        "- Include links for every recommendation cluster."
    ),
    tools=[google_search_tool, duckduckgo_search_tool],  
    llm=llm,
    verbose=True,
)
