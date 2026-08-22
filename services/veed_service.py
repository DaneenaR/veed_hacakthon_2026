import requests
from config import VEED_API_KEY, VEED_BASE_URL, MOCK_MODE
from utils.polling import poll_job

def assemble_video(clip_urls: list[str], script: str) -> dict:
    """
    Assembles clips + script into a captioned, voiced-over video, exported in
    three formats. Returns {"square": url, "vertical": url, "horizontal": url}.
    Confirm exact endpoint path/payload shape against VEED's current docs.
    """
    if MOCK_MODE["veed"]:
        return {
            "square": "https://placehold.co/600x600/mp4",
            "vertical": "https://placehold.co/400x700/mp4",
            "horizontal": "https://placehold.co/800x450/mp4",
        }

    headers = {"Authorization": f"Bearer {VEED_API_KEY}", "Content-Type": "application/json"}
    payload = {
        "clips": clip_urls,
        "voiceover_script": script,
        "auto_captions": True,
        "export_formats": ["square", "vertical", "horizontal"],
    }
    resp = requests.post(f"{VEED_BASE_URL}/v1/projects", json=payload, headers=headers)
    resp.raise_for_status()
    job = resp.json()

    result = poll_job(job["status_url"], headers)
    return result["exports"]