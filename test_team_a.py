import sys
from types import SimpleNamespace
from services import tavily_service, openai_service, fal_service, veed_service, h_service


def make_test_listing():
    """Generates a standard listing object matching app.py SimpleNamespace structure."""
    return SimpleNamespace(
        title="Luxury Modern Apartment",
        address="221 Baker Street, London",
        price="£450,000",
        beds="2",
        baths="1",
        sqft="750 sqft",
        details="Newly renovated kitchen, high ceilings, close to public transport."
    )


def test_tavily():
    result = tavily_service.get_market_context("221 Baker Street, London")
    print("MARKET CONTEXT:\n", result)


def test_openai():
    listing = make_test_listing()
    script, desc = openai_service.generate_script_and_description(
        listing, "Prices in this area rose 8% last year.", persona="Luxury Estate Specialist"
    )
    print("SCRIPT:\n", script)
    print("\nDESCRIPTION:\n", desc)


def test_fal_photos():
    urls = fal_service.generate_property_photos(make_test_listing(), num_images=2)
    print("PHOTO URLS:", urls)


def test_fal_video():
    urls = fal_service.generate_property_photos(make_test_listing(), num_images=1)
    clips = fal_service.generate_clips(urls)
    print("CLIP URLS:", clips)


def test_veed():
    result = veed_service.assemble_video(
        ["https://placehold.co/1280x720.png"],
        "Welcome to this stunning two bedroom flat."
    )
    print("FINAL VIDEOS:", result)


def test_h():
    result = h_service.post_listing(
        "https://placehold.co/400x700/mp4",
        "A beautifully staged two bedroom flat.",
        ["Zillow Rental Manager", "Facebook Marketplace"]
    )
    print("H POST RESULT:", result)


def test_full_pipeline():
    """Runs the complete end-to-end execution flow matching app.py."""
    listing = make_test_listing()

    print("1/5 Tavily...")
    market_context = tavily_service.get_market_context(listing.address)

    print("2/5 OpenAI...")
    script, description = openai_service.generate_script_and_description(
        listing, market_context, persona="Luxury Estate Specialist"
    )

    print("3/5 Fal photos...")
    photo_urls = fal_service.generate_property_photos(listing)

    print("4/5 Fal clips...")
    motion_clips = fal_service.generate_clips(photo_urls)

    print("5/5 VEED...")
    final_video_urls = veed_service.assemble_video(motion_clips, script)

    print("\n--- PIPELINE COMPLETE ---")
    print("Description:\n", description)
    print("Final videos:\n", final_video_urls)


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
        print(f"Usage: python test_team_a.py [{'|'.join(TESTS.keys())}]")
        sys.exit(1)
    TESTS[sys.argv[1]]()