import os
import requests
from dotenv import load_dotenv
from tavily import TavilyClient

from config import TAVILY_API_KEY, TAVILY_URL, MOCK_MODE

load_dotenv()


def get_market_context(address: str) -> str:
    """
    Searches for recent comps and neighborhood trends near the given address.
    Returns a short text block formatted for OpenAI prompt injection.
    """
    if MOCK_MODE.get("tavily", False):
        return "Prices in this area rose 8% over the last year. High demand from young professionals."

    query = f"recent home sales and price trends near {address}"

    try:
        # Preferred: Use SDK if key is available
        api_key = TAVILY_API_KEY or os.getenv("TAVILY_API_KEY")
        if api_key:
            client = TavilyClient(api_key=api_key)
            response = client.search(query=query, search_depth="basic", max_results=5)
            results = response.get("results", [])
        else:
            # Fallback REST Endpoint execution
            payload = {
                "api_key": TAVILY_API_KEY,
                "query": query,
                "search_depth": "basic",
                "max_results": 5,
            }
            resp = requests.post(TAVILY_URL, json=payload, timeout=20)
            resp.raise_for_status()
            results = resp.json().get("results", [])

        snippets = [r.get("content", "")[:300] for r in results[:3] if r.get("content")]
        return "\n".join(snippets) if snippets else "No recent market data found."

    except Exception as e:
        print(f"❌ Error fetching Tavily market context: {e}")
        return "Market data temporarily unavailable."