import os

from dotenv import load_dotenv
from openai import OpenAI

load_dotenv()


def generate_educational_script(textbook_topic):
    """Uses OpenAI to convert complex topics into a fun student script"""
    print(f"🤖 Simplifying topic: '{textbook_topic}'...")

    client = OpenAI(api_key=os.environ.get("OPENAI_API_KEY"))

    try:
        response = client.chat.completions.create(
            model="gpt-4o-mini",
            messages=[
                {
                    "role": "user",
                    "content": f"Explain this like I am 5 years old, in a fun and engaging way for a short video script: {textbook_topic}",
                }
            ],
        )
        return response.choices[0].message.content
    except Exception as e:
        print(f"⚠️ OpenAI call failed, falling back to placeholder: {e}")
        return f"Hey there! Let's break down {textbook_topic} simply. It is basically like a network of nodes..."
