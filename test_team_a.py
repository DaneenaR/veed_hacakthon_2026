import sys
from services import tavily_service, openai_service, fal_service, veed_service, h_service
from listing_models.listing import Listing


def make_test_listing():
    return Listing(address="221 Baker Street, London", price="£450,000",
                    beds=2, baths=1, sqft="750 sqft")


def test_tavily():
    result = tavily_service.get_market_context("221 Baker Street, London")
    print("MARKET CONTEXT:\n", result)


def test_openai():
    listing = make_test_listing()
    script, desc = openai_service.generate_script_and_description(
        listing, "Prices in this area rose 8% last year."
    )
    print("SCRIPT:\n", script)
    print("\nDESCRIPTION:\n", desc)


def test_fal_photos():
    urls = fal_service.generate_property_photos(make_test_listing(), num_images=2)
    print("PHOTO URLS:", urls)


def test_fal_video():
    urls = fal_service.generate_property_photos(make_test_listing(), num_images=1)
    clip_url = fal_service.photo_to_video(urls[0])
    print("CLIP URL:", clip_url)


def test_veed():
    result = veed_service.assemble_video(
        ["https://placehold.co/1280x720/mp4"],
        "Welcome to this stunning two bedroom flat."
    )
    print("FINAL VIDEOS:", result)


def test_h():
    result = h_service.post_listing(
        {"square": "https://placehold.co/600x600/mp4"},
        "A beautifully staged two bedroom flat."
    )
    print("H POST RESULT:", result)


def test_full_pipeline():
    """Runs everything in sequence, exactly like app.py will call it."""
    listing = make_test_listing()
    print("1/5 Tavily...")
    listing.market_context = tavily_service.get_market_context(listing.address)

    print("2/5 OpenAI...")
    listing.script, listing.description = openai_service.generate_script_and_description(
        listing, listing.market_context
    )

    print("3/5 Fal photos...")
    listing.photo_urls = fal_service.generate_property_photos(listing)

    print("4/5 Fal clips...")
    listing.video_clip_urls = fal_service.generate_clips(listing.photo_urls)

    print("5/5 VEED...")
    listing.final_video_urls = veed_service.assemble_video(listing.video_clip_urls, listing.script)

    print("\n--- PIPELINE COMPLETE ---")
    print("Description:", listing.description)
    print("Final videos:", listing.final_video_urls)


TESTS = {
    "tavily": test_tavily,
    "openai": test_openai,
    "fal_photos": test_fal_photos,
    "fal_video": test_fal_video,
    "veed": test_veed,
    "h": test_h,
    "full": test_full_pipeline,
}

if __name__ == "__main__":
    if len(sys.argv) < 2 or sys.argv[1] not in TESTS:
        print(f"Usage: python test_team_a.py [{'|'.join(TESTS)}]")
        sys.exit(1)
    TESTS[sys.argv[1]]()