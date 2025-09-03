# tools/google_serper_tool.py

import os
import requests
from crewai.tools import BaseTool
from typing import Type
from pydantic import BaseModel, Field

class GoogleSerperSearch:
    """
    Tool for performing Google Search using Serper API
    Docs: https://serper.dev
    """

    def __init__(self, api_key=None):
        self.api_key = api_key or os.getenv("GOOGLE_SURPER_API")
        if not self.api_key:
            raise ValueError("❌ GOOGLE_SURPER_API not set. Please set it in your environment variables.")

        self.endpoint = "https://google.serper.dev/search"

    def search(self, query: str, num_results: int = 10):
        """
        Perform a Google search via Serper API
        """
        headers = {
            "X-API-KEY": self.api_key,
            "Content-Type": "application/json"
        }

        payload = {
            "q": query,
            "num": num_results
        }

        try:
            response = requests.post(self.endpoint, headers=headers, json=payload, timeout=30)
            
            if response.status_code != 200:
                return f"Serper API error: {response.status_code}, {response.text}"

            data = response.json()
            results = []

            # Format results for better readability
            for item in data.get("organic", [])[:num_results]:
                result_text = f"- {item.get('title', 'No title')} ({item.get('link', 'No link')})\n  {item.get('snippet', 'No snippet available')}"
                results.append(result_text)

            return "\n\n".join(results) if results else "No results found."
            
        except requests.exceptions.RequestException as e:
            return f"Request failed: {str(e)}"
        except Exception as e:
            return f"Error occurred: {str(e)}"

_serper_search = GoogleSerperSearch()

# Input schema for the tool
class GoogleSerperSearchInput(BaseModel):
    """Input schema for Google Serper search."""
    query: str = Field(..., description="The search query string")

# Create the tool using BaseTool
class GoogleSerperSearchTool(BaseTool):
    name: str = "Google Serper Search"
    description: str = (
        "Search Google for official websites, tourism boards, and authoritative sources. "
        "Use this tool when looking for official information, popular attractions, or well-established sources."
    )
    args_schema: Type[BaseModel] = GoogleSerperSearchInput

    def _run(self, query: str) -> str:
        query = str(query)
        return _serper_search.search(query, num_results=5)

if __name__ == "__main__":
    # Test the tool
    try:
        print("Testing Google Serper Search Tool...")
        tool_instance = GoogleSerperSearchTool()
        result = tool_instance._run("Best tourist attractions in India")
        print("Results:")
        print(result)
    except Exception as e:
        print(f"Error: {e}")
        print("Make sure to set GOOGLE_SERPER_API in your environment variables.")