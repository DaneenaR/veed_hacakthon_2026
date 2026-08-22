from config import MOCK_MODE

MOCK_VIDEO = "https://commondatastorage.googleapis.com/gtv-videos-bucket/sample/ForBiggerBlazes.mp4"


def assemble_video(clip_urls: list[str], script: str) -> dict:
    """
    Assembles motion clips into video outputs.
    Prioritizes generated Fal motion clips if available, falling back to sample MP4.
    """
    # Use the first generated Fal video clip if present, otherwise default to working sample MP4
    primary_video = clip_urls[0] if (clip_urls and len(clip_urls) > 0) else MOCK_VIDEO

    fallback = {
        "vertical": primary_video,
        "square": primary_video,
        "horizontal": primary_video,
    }

    if MOCK_MODE.get("veed", True):
        return fallback

    try:
        import fal_client

        source_image = clip_urls[
            0] if clip_urls else "https://images.unsplash.com/photo-1600596542815-ffad4c1539a9?w=1280"

        result = fal_client.subscribe(
            "veed/fabric-1.0",
            arguments={
                "image_url": source_image,
                "text": script,
                "resolution": "720p",
            },
        )
        video_url = result.get("video", {}).get("url") or primary_video
        return {"vertical": video_url, "square": video_url, "horizontal": video_url}
    except Exception as e:
        print(f"⚠️ VEED API error (falling back to generated/sample video): {e}")
        return fallback