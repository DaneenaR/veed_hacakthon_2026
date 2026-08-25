from config import MOCK_MODE
# NOTE: app.py must import NoPhotosUploadedError and catch it around the
# upload_all_photos()/generate_clips() calls — see integration note below.

MOCK_PHOTOS = [
    "https://images.unsplash.com/photo-1600596542815-ffad4c1539a9?w=1280&fm=jpg",
    "https://images.unsplash.com/photo-1600585154340-be6161a56a0c?w=1280&fm=jpg",
]
MOCK_VIDEO = "https://commondatastorage.googleapis.com/gtv-videos-bucket/sample/ForBiggerBlazes.mp4"


class NoPhotosUploadedError(Exception):
    """Raised when a user tries to generate a video without uploading any property photos."""
    pass


def upload_all_photos(uploaded_files) -> list[str]:
    """
    Uploads Streamlit file objects to Fal CDN.
    Requires real uploaded files — raises an error if none were provided.
    """
    if not uploaded_files:
        raise NoPhotosUploadedError(
            "Please upload at least one property photo before generating a video."
        )

    if MOCK_MODE.get("fal", False):
        # Still mock the CDN upload step itself (no real network call),
        # but only ever runs when photos were actually provided.
        return MOCK_PHOTOS[: len(uploaded_files)] or MOCK_PHOTOS

    try:
        import fal_client
        photo_urls = []
        for file in uploaded_files:
            cdn_url = fal_client.upload(file.getvalue(), file.type)
            photo_urls.append(cdn_url)
        if not photo_urls:
            raise NoPhotosUploadedError("Photo upload to Fal failed — no URLs were returned.")
        return photo_urls
    except NoPhotosUploadedError:
        raise
    except Exception as e:
        # A real API/network failure — don't silently fake it, let the caller know.
        raise RuntimeError(f"Fal photo upload failed: {e}") from e


def generate_clips(photo_urls: list[str]) -> list[str]:
    """
    Turns each uploaded property photo into a short cinematic video clip,
    designed to showcase the property fully (sweeping/panning motion,
    real estate walkthrough style) rather than generic camera movement.
    """
    if not photo_urls:
        raise NoPhotosUploadedError(
            "No photos available to generate video clips from. Please upload property photos."
        )

    if MOCK_MODE.get("fal", True):
        return [MOCK_VIDEO for _ in photo_urls]

    CINEMATIC_PROMPT = (
        "Smooth, slow cinematic real estate showcase shot. Gentle push-in or "
        "sweeping pan that reveals the full space, professional property tour "
        "style, steady and elegant camera motion, natural lighting, high-end "
        "listing video aesthetic, no distortion, no warping of architecture."
    )

    try:
        import fal_client
        clip_urls = []
        for url in photo_urls:
            result = fal_client.subscribe(
                "fal-ai/kling-video/v1/standard/image-to-video",
                arguments={
                    "prompt": CINEMATIC_PROMPT,
                    "image_url": url,
                    "duration": "5",
                },
            )
            video_url = result.get("video", {}).get("url")
            if video_url:
                clip_urls.append(video_url)
        if not clip_urls:
            raise RuntimeError("Fal video generation returned no clips.")
        return clip_urls
    except Exception as e:
        raise RuntimeError(f"Fal clip generation failed: {e}") from e