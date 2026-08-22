from openai import OpenAI
from config import OPENAI_API_KEY, MOCK_MODE

_client = None

def _get_client():
    global _client
    if _client is None:
        _client = OpenAI(api_key=OPENAI_API_KEY)
    return _client


def generate_script_and_description(listing, market_context: str) -> tuple[str, str]:
    if MOCK_MODE["openai"]:
        return (
            "Welcome to this stunning home, perfectly located and full of natural light.",
            "A beautifully staged property in a fast-growing neighborhood. Don't miss it."
        )

    client = _get_client()
    prompt = f"""
You are writing marketing copy for a real estate video ad.

Listing facts:
- Address: {listing.address}
- Price: {listing.price}
- Beds: {listing.beds}, Baths: {listing.baths}, Size: {listing.sqft}

Local market context:
{market_context}

Write two things, clearly separated by "---":
1. A 20-30 second video voiceover script (natural, energetic, no fluff)
2. A short listing description for social media (2-3 sentences, includes one specific
   market stat from the context above if relevant)
"""
    resp = client.chat.completions.create(
        model="gpt-4o-mini",
        messages=[{"role": "user", "content": prompt}],
        max_tokens=400,
    )
    text = resp.choices[0].message.content
    parts = text.split("---")
    script = parts[0].strip()
    description = parts[1].strip() if len(parts) > 1 else ""
    return script, description