import os
from dotenv import load_dotenv

load_dotenv()

TAVILY_API_KEY = os.getenv("TAVILY_API_KEY")
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")
FAL_API_KEY = os.getenv("FAL_KEY")
VEED_API_KEY = os.getenv("VEED_API_KEY")

TAVILY_URL = "https://api.tavily.com/search"
FAL_TEXT_TO_IMAGE_URL = "https://queue.fal.run/fal-ai/flux/schnell"
FAL_IMAGE_TO_VIDEO_URL = "https://queue.fal.run/fal-ai/kling-video/v1/standard/image-to-video"
VEED_BASE_URL = "https://api.veed.io"

MOCK_MODE = {
    "tavily": True,
    "openai": True,
    "fal": True,
    "veed": True,
    "h": True,
}