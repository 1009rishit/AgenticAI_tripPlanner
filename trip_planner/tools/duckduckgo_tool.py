# tools/duckduckgo_tool.py

from ddgs import DDGS
from crewai.tools import BaseTool
from typing import Type
from pydantic import BaseModel, Field

def search_duckduckgo(query: str, max_results: int = 10):
    """Original search function"""
    results = []
    with DDGS() as ddg:
        for r in ddg.text(query, max_results=max_results):
            results.append(f"- {r.get('title')} ({r.get('href')})\n  {r.get('body')}")
    return "\n".join(results)

# Input schema for the tool
class DuckDuckGoSearchInput(BaseModel):
    """Input schema for DuckDuckGo search."""
    query: str = Field(..., description="The search query string")

# Create the tool using BaseTool
class DuckDuckGoSearchTool(BaseTool):
    name: str = "DuckDuckGo Search"
    description: str = (
        "Search the web for hidden gems, blogs, forums, and travel tips. "
        "Use this tool when looking for local or lesser-known information."
    )
    args_schema: Type[BaseModel] = DuckDuckGoSearchInput

    def _run(self, query: str) -> str:
        return search_duckduckgo(query, max_results=5)

if __name__ == "__main__":
    # Test the tool
    try:
        print("Testing DuckDuckGo Search Tool...")
        tool_instance = DuckDuckGoSearchTool()
        result = tool_instance._run("famous attraction of Jaipur")
        print("Results:")
        print(result)
    except Exception as e:
        print(f"Error: {e}")