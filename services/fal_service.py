from config import MOCK_MODE

MOCK_PHOTOS = [
    "https://images.unsplash.com/photo-1600596542815-ffad4c1539a9?w=1280&fm=jpg",
    "https://images.unsplash.com/photo-1600585154340-be6161a56a0c?w=1280&fm=jpg",
]
MOCK_VIDEO = "https://commondatastorage.googleapis.com/gtv-videos-bucket/sample/ForBiggerBlazes.mp4"


def upload_all_photos(uploaded_files) -> list[str]:
    """Uploads Streamlit file objects to Fal CDN or returns mock photo URLs."""
    if MOCK_MODE.get("fal", False):
        return MOCK_PHOTOS[: len(uploaded_files)] if uploaded_files else MOCK_PHOTOS

    try:
        import fal_client
        photo_urls = []
        for file in uploaded_files:
            cdn_url = fal_client.upload(file.getvalue(), file.type)
            photo_urls.append(cdn_url)
        return photo_urls if photo_urls else MOCK_PHOTOS
    except Exception as e:
        print(f"⚠️ Fal upload API error (falling back to mock): {e}")
        return MOCK_PHOTOS[: len(uploaded_files)] if uploaded_files else MOCK_PHOTOS


def generate_property_photos(listing, num_images: int = 3) -> list[str]:
    if MOCK_MODE.get("fal", True):
        return MOCK_PHOTOS[:num_images]

    try:
        import fal_client
        title = getattr(listing, "title", "Modern Property")
        details = getattr(listing, "details", "Luxury real estate interior")
        result = fal_client.subscribe(
            "fal-ai/flux/schnell",
            arguments={
                "prompt": f"Luxury real estate photography of {title}, {details}",
                "num_images": num_images,
                "image_size": "landscape_16_9",
            },
        )
        images = result.get("images", [])
        return [img["url"] for img in images if "url" in img]
    except Exception as e:
        print(f"⚠️ Fal photos API error (falling back to mock): {e}")
        return MOCK_PHOTOS[:num_images]


def generate_clips(photo_urls: list[str]) -> list[str]:
    if MOCK_MODE.get("fal", True):
        return [MOCK_VIDEO for _ in photo_urls]

    try:
        import fal_client
        clip_urls = []
        for url in photo_urls:
            result = fal_client.subscribe(
                "fal-ai/kling-video/v1/standard/image-to-video",
                arguments={
                    "prompt": "Smooth cinematic camera motion",
                    "image_url": url,
                },
            )
            video_url = result.get("video", {}).get("url")
            if video_url:
                clip_urls.append(video_url)
        return clip_urls if clip_urls else [MOCK_VIDEO]
    except Exception as e:
        print(f"⚠️ Fal clip API error (falling back to mock): {e}")
        return [MOCK_VIDEO for _ in photo_urls]