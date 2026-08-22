from dataclasses import dataclass, field
from typing import List

@dataclass
class Listing:
    address: str
    price: str
    beds: int
    baths: int
    sqft: str
    photo_paths: List[str] = field(default_factory=list)
    market_context: str = ""
    script: str = ""
    description: str = ""
    video_clip_urls: List[str] = field(default_factory=list)
    final_video_urls: dict = field(default_factory=dict)  # {"square": url, "vertical": url, "horizontal": url}