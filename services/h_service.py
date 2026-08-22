from config import MOCK_MODE

def post_listing(video_urls: dict, description: str) -> dict:
    """
    Stretch goal: logs into listing sites and posts the video + description.
    Returns a dict of {platform: status}. Currently mocked — replace the body
    once H's API/agent access is confirmed at the venue.
    """
    if MOCK_MODE.get("h", True):
        return {
            "zillow": "mock: would post here",
            "facebook_marketplace": "mock: would post here",
        }

    # Real implementation goes here once you've confirmed H's interface
    raise NotImplementedError("H integration not yet wired up")