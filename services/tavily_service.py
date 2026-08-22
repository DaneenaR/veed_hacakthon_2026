import os

import requests
from dotenv import load_dotenv
from tavily import TavilyClient

from config import TAVILY_API_KEY, TAVILY_URL, MOCK_MODE

load_dotenv()


def search_learning_resources(query, max_results=5):
    """Searches the web for learning resources on a topic using Tavily"""
    client = TavilyClient(api_key=os.environ["TAVILY_API_KEY"])

    try:
        response = client.search(query, max_results=max_results)
        return response.get("results", [])
    except Exception as e:
        print(f"❌ Error searching with Tavily: {e}")
        return []


def get_market_context(address: str) -> str:
    """
    Search for recent comps and market trends near the listing.
    Returns a short text block to feed into the OpenAI prompt.
    """
    if MOCK_MODE["tavily"]:
        return "Prices in this area rose 8% over the last year. High demand from young professionals."

    query = f"recent home sales and price trends near {address}"
    payload = {
        "api_key": TAVILY_API_KEY,
        "query": query,
        "search_depth": "basic",
        "max_results": 5,
    }
    resp = requests.post(TAVILY_URL, json=payload, timeout=20)
    resp.raise_for_status()
    results = resp.json().get("results", [])

    snippets = [r.get("content", "")[:300] for r in results[:3]]
    return "\n".join(snippets) if snippets else "No recent market data found."
