import os
from dotenv import load_dotenv
from openai import OpenAI

from config import MOCK_MODE

load_dotenv()

MOCK_SCRIPT = (
    "Welcome home. Tucked into one of the neighborhood's most sought-after pockets, "
    "this property blends comfort, style, and location in a way that's hard to find. "
    "Step inside and picture your next chapter starting here."
)
MOCK_SOCIAL = (
    "✨ Just Listed! A rare find you won't want to miss. "
    "#JustListed #RealEstate #DreamHome"
)


def generate_script_and_description(
    listing,
    market_context: str = "",
    persona: str = "Luxury Estate Specialist",
) -> tuple[str, str]:
    """
    Compiles all listing details entered in the app (title, price, location,
    layout, and the agent's own description of features/amenities) into a
    single, persuasive property tour script and a matching social caption.

    Returns a tuple of (script, social_description).
    """
    if MOCK_MODE.get("openai", False):
        return MOCK_SCRIPT, MOCK_SOCIAL

    client = OpenAI(api_key=os.environ.get("OPENAI_API_KEY"))

    # Pull every field the user filled in — this is the raw material the
    # script gets built from. `details` is the free-text box where the
    # agent describes selling features/amenities in their own words.
    title = getattr(listing, "title", "").strip()
    address = getattr(listing, "address", "").strip()
    price = getattr(listing, "price", "").strip()
    beds = getattr(listing, "beds", "").strip()
    baths = getattr(listing, "baths", "").strip()
    sqft = getattr(listing, "sqft", "").strip()
    details = getattr(listing, "details", "").strip()

    prompt = f"""
    You are an elite real estate copywriter and video scriptwriter, writing in the
    voice of a '{persona}'. Your job is to take the raw listing details below —
    written casually by a busy real estate agent — and turn them into a
    genuinely persuasive, well-structured property tour script that makes a
    buyer want to see this home in person.

    Do not just restate the facts in order. Weave them into a narrative with a
    clear arc: hook the listener in the first line, build desire by
    highlighting what makes this property special, and close with a sense of
    urgency or an emotional pull toward booking a viewing.

    RAW LISTING DETAILS (as entered by the agent):
    - Title: {title}
    - Location: {address}
    - Price: {price}
    - Layout: {beds} bed, {baths} bath, {sqft}
    - Agent's description of features/amenities: "{details}"

    LIVE MARKET CONTEXT (use only if it strengthens the pitch — e.g. rising
    prices, high demand, desirable school district):
    {market_context if market_context else "No additional market context provided."}

    YOUR TASKS:
    1. Write a ~40-second voiceover script (roughly 95-110 words) for a property
       tour video. It should sound natural when spoken aloud, sell the
       lifestyle as much as the specs, and end with a subtle call to action.
    2. Write a short, scroll-stopping social media caption (2-3 sentences)
       with 3-5 relevant real estate hashtags, matching the same persona's
       tone.

    Format your response EXACTLY as:
    [SCRIPT]
    <voiceover script here>
    [DESCRIPTION]
    <social media caption here>
    """

    try:
        response = client.chat.completions.create(
            model="gpt-4o-mini",
            messages=[{"role": "user", "content": prompt}],
            temperature=0.8,
        )
        content = response.choices[0].message.content

        if "[SCRIPT]" in content and "[DESCRIPTION]" in content:
            parts = content.split("[DESCRIPTION]")
            script = parts[0].replace("[SCRIPT]", "").strip()
            social_desc = parts[1].strip()
            return script, social_desc

        # Model didn't follow the format — still return something usable
        # rather than duplicating the same raw text into both fields.
        return content.strip(), MOCK_SOCIAL

    except Exception as e:
        print(f"⚠️ OpenAI call failed, returning fallback: {e}")
        fallback_script = (
            f"Welcome to {title or 'this incredible property'} in {address}. "
            f"Offering {beds} bedrooms and {baths} bathrooms across {sqft}, "
            f"this home stands out for its {details or 'thoughtful design and prime location'}. "
            f"Priced at {price}, this is an opportunity you won't want to miss."
        )
        fallback_social = (
            f"✨ Just Listed! {title or 'A stunning new listing'} in {address} — "
            f"{price}. Don't miss this one. #JustListed #RealEstate #NewListing"
        )
        return fallback_script, fallback_social