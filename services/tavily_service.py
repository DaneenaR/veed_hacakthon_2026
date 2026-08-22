import os

from dotenv import load_dotenv
from tavily import TavilyClient

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
