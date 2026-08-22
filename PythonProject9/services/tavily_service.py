import requests
from config import TAVILY_API_KEY, TAVILY_URL, MOCK_MODE

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