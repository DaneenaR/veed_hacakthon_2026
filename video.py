from services.fal_service import create_talking_tutor_video
from services.open_ai import generate_educational_script

if __name__ == "__main__":
    # Example student problem to solve
    student_prompt = "How does recursion work in Python programming?"
    script = generate_educational_script(student_prompt)
    print(f"Script Generated: {script}\n")

    # Placeholder asset URLs for testing. Tomorrow, these will be your generated assets.
    test_avatar = "https://unsplash.com"   # Static portrait
    test_audio = "https://soundhelix.com"  # Audio track

    # Tomorrow, you will pass your live URLs into this wrapper
    # video_result = create_talking_tutor_video(test_avatar, test_audio)
    # print(f"🚀 Success! View your educational avatar video here: {video_result}")
    print("⚙️ Pipeline test complete! Run this tomorrow morning once you receive your live API keys.")
