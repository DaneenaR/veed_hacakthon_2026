import os
from dotenv import load_dotenv
from openai import OpenAI

load_dotenv()


def generate_script_and_description(listing, market_context: str = "", persona: str = "Luxury Estate Specialist") -> tuple[str, str]:
    """
    Generates a real estate tour script and social caption using OpenAI GPT.
    Returns a tuple of (script, social_description).
    """
    client = OpenAI(api_key=os.environ.get("OPENAI_API_KEY"))

    prompt = f"""
    You are a top real estate marketer using the brand voice of a '{persona}'.

    Property Info:
    - Title: {listing.title}
    - Location: {listing.address}
    - Price: {listing.price}
    - Layout: {listing.beds} Bed, {listing.baths} Bath, {listing.sqft}
    - Features: {listing.details}

    Submarket Context:
    {market_context}

    Tasks:
    1. Write a 30-second property tour voiceover script.
    2. Write an engaging social media post caption with hashtags.

    Format your response EXACTLY as:
    [SCRIPT]
    <voiceover text>
    [DESCRIPTION]
    <social media caption>
    """

    try:
        response = client.chat.completions.create(
            model="gpt-4o-mini",
            messages=[{"role": "user", "content": prompt}],
            temperature=0.7,
        )
        content = response.choices[0].message.content

        if "[SCRIPT]" in content and "[DESCRIPTION]" in content:
            parts = content.split("[DESCRIPTION]")
            script = parts[0].replace("[SCRIPT]", "").strip()
            social_desc = parts[1].strip()
            return script, social_desc

        return content.strip(), content.strip()

    except Exception as e:
        print(f"⚠️ OpenAI call failed, returning fallback: {e}")
        fallback_script = f"Welcome to {listing.title} at {listing.address}! Featuring {listing.beds} beds and {listing.baths} baths."
        fallback_social = f"Just Listed! {listing.title} in {listing.address} for {listing.price}."
        return fallback_script, fallback_social