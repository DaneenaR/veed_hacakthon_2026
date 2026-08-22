import os 
import fal_client
from openai import OpenAI
from dotenv import load_dotenv
import requests
from tavily import TavilyClient

load_dotenv()

os.environ["FAL_KEY"] = os.getenv("FAL_KEY")

response = requests.get(
    "https://api.pioneer.ai/base-models",
    params={"supports_inference": "true"},
    headers={"X-API-Key": "YOUR_API_KEY"}
)
print(response.json())

H_API_KEY = os.getenv("H_API_KEY")

tavily_client = TavilyClient(api_key=os.getenv("TAVILY_API_KEY"))

#------HELPER FUNCTIONS------

def upload_photo_to_fal(uploaded_file):
    ...
    
def call_openai(description):
    ...

def call_veed(video_url, script):
    ...

def put_listing_h(video):
    ...