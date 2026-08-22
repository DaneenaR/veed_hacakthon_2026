import os

import fal_client
from dotenv import load_dotenv

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
