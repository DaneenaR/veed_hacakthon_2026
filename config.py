import os
from dotenv import load_dotenv

load_dotenv()

# Standard SDK key declarations
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")
FAL_KEY = os.getenv("FAL_KEY")
TAVILY_API_KEY = os.getenv("TAVILY_API_KEY")
H_API_KEY = os.getenv("H_API_KEY")
PIONEER_API_KEY = os.getenv("PIONEER_API_KEY")

# Endpoint Definitions
TAVILY_URL = "https://api.tavily.com/search"
FAL_TEXT_TO_IMAGE_URL = "https://queue.fal.run/fal-ai/flux/schnell"
FAL_IMAGE_TO_VIDEO_URL = "https://queue.fal.run/fal-ai/kling-video/v1/standard/image-to-video"

# Set mock mode flags to False to run live API requests
MOCK_MODE = {
    "tavily": True,
    "openai": True,
    "fal": True,
    "veed": True,
    "h": True,
}