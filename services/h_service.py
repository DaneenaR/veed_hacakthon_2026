from config import MOCK_MODE

def post_listing(video_url: str, description: str, target_portals: list = None) -> dict:
    """
    Stretch goal: logs into listing sites and posts the video + description.
    Returns a dict of {platform: status}.
    """
    if target_portals is None:
        target_portals = ["Zillow Rental Manager", "Facebook Marketplace"]

    if MOCK_MODE.get("h", True):
        return {portal: "mock: would post here" for portal in target_portals}

    # Real implementation goes here once you've confirmed H's interface
    raise NotImplementedError("H integration not yet wired up")