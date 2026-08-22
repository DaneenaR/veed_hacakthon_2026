import os

import fal_client
import requests
from dotenv import load_dotenv

from config import FAL_API_KEY, FAL_TEXT_TO_IMAGE_URL, FAL_IMAGE_TO_VIDEO_URL, MOCK_MODE
from utils.polling import poll_job

load_dotenv()


def create_talking_tutor_video(avatar_image_url, audio_voice_url):
    """Feeds the visual asset and voice track into the VEED Fabric 1.0 API via fal.ai"""
    print("🎬 Triggering VEED Fabric 1.0 via fal.ai...")

    try:
        handler = fal_client.submit(
            "fal-ai/veed/fabric-1.0",
            arguments={
                "image_url": avatar_image_url,
                "audio_url": audio_voice_url,
                "resolution": "720p",  # Supports 480p (faster) or 720p (higher quality)
            },
        )

        result = handler.get()
        video_url = result.get("video", {}).get("url")
        return video_url

    except Exception as e:
        print(f"❌ Error communicating with the API: {e}")
        return None


def generate_property_photos(listing, num_images: int = 3) -> list:
    """
    Generates staged property photos from listing facts (no real photos needed).
    Returns a list of image URLs.
    """
    if MOCK_MODE["fal"]:
        return [f"https://placehold.co/1280x720?text=Photo+{i+1}" for i in range(num_images)]

    headers = {"Authorization": f"Key {FAL_API_KEY}", "Content-Type": "application/json"}
    prompt = (
        f"Professional real estate photo, interior of a {listing.beds} bedroom "
        f"{listing.baths} bathroom home, {listing.sqft}, bright natural lighting, "
        f"modern staging, wide angle, photorealistic"
    )

    urls = []
    for _ in range(num_images):
        payload = {"prompt": prompt, "image_size": "landscape_16_9"}
        resp = requests.post(FAL_TEXT_TO_IMAGE_URL, json=payload, headers=headers)
        resp.raise_for_status()
        job = resp.json()
        result = poll_job(job["status_url"], headers)
        urls.append(result["images"][0]["url"])
    return urls


def photo_to_video(photo_url: str) -> str:
    """Animates one still photo into a short video clip. Returns the clip URL."""
    if MOCK_MODE["fal"]:
        return "https://placehold.co/1280x720/mp4?text=Clip"

    headers = {"Authorization": f"Key {FAL_API_KEY}", "Content-Type": "application/json"}
    payload = {"image_url": photo_url, "duration": "4"}

    submit_resp = requests.post(FAL_IMAGE_TO_VIDEO_URL, json=payload, headers=headers)
    submit_resp.raise_for_status()
    job = submit_resp.json()

    result = poll_job(job["status_url"], headers)
    return result["video"]["url"]


def generate_clips(photo_urls: list) -> list:
    """Runs photo_to_video across every photo. Returns a list of clip URLs, same order as input."""
    return [photo_to_video(url) for url in photo_urls]
