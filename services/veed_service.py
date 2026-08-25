import os
import tempfile

import requests
from dotenv import load_dotenv

from config import MOCK_MODE

load_dotenv()

MOCK_VIDEO = "https://commondatastorage.googleapis.com/gtv-videos-bucket/sample/ForBiggerBlazes.mp4"

# OpenAI TTS voice — "nova" and "shimmer" are the female-sounding options.
VOICE = "nova"

# Hardcoded avatar photo used for the talking presenter overlay: a young
# woman in a black blazer, front-facing (clear face/mouth for lip-sync).
# Swap this for a real agent headshot whenever you have one.
AVATAR_IMAGE_URL = "https://v3b.fal.media/files/b/0aa7cc9a/gQBJnQAGSD7G3AS720Qf-.png"

# Size and position (as a fraction of the main video's width) of the
# picture-in-picture avatar box, e.g. bottom-right corner.
AVATAR_WIDTH_FRACTION = 0.22
AVATAR_MARGIN_PX = 24


def _generate_voiceover(script: str) -> str:
    """
    Converts the script into a spoken audio file using a female AI voice.
    Returns a local file path to the generated MP3.
    """
    from openai import OpenAI

    client = OpenAI(api_key=os.environ.get("OPENAI_API_KEY"))

    response = client.audio.speech.create(
        model="tts-1",
        voice=VOICE,
        input=script,
    )

    tmp_path = os.path.join(tempfile.gettempdir(), "voiceover.mp3")
    response.stream_to_file(tmp_path)
    return tmp_path


def _download_to_temp(url: str, suffix: str) -> str:
    """Downloads a remote file (video) to a local temp path so moviepy can read it."""
    resp = requests.get(url, timeout=60)
    resp.raise_for_status()
    tmp_path = os.path.join(tempfile.gettempdir(), f"input{suffix}")
    with open(tmp_path, "wb") as f:
        f.write(resp.content)
    return tmp_path


def _concatenate_clips(clip_urls: list[str]) -> str:
    """
    Downloads every generated property clip and stitches them together,
    one after another, into a single continuous video covering all
    uploaded photos. Returns a local file path to the combined video.
    """
    from moviepy import VideoFileClip, concatenate_videoclips

    local_clips = []
    for i, url in enumerate(clip_urls):
        path = _download_to_temp(url, f"_clip{i}.mp4")
        local_clips.append(VideoFileClip(path))

    combined = concatenate_videoclips(local_clips, method="compose")

    output_path = os.path.join(tempfile.gettempdir(), "combined.mp4")
    combined.write_videofile(
        output_path,
        codec="libx264",
        audio_codec="aac",
        fps=local_clips[0].fps or 24,
        logger=None,
    )

    for clip in local_clips:
        clip.close()
    combined.close()

    return output_path


def _merge_audio_into_video(video_path: str, audio_path: str) -> str:
    """
    Combines the (already concatenated) property video with the generated
    voiceover as its audio track. Returns a public Fal CDN URL to the
    merged video.
    """
    from moviepy import VideoFileClip, AudioFileClip
    import fal_client

    video_clip = VideoFileClip(video_path)
    audio_clip = AudioFileClip(audio_path)

    # Loop or trim the video so its length roughly matches the voiceover.
    if audio_clip.duration > video_clip.duration:
        from moviepy import vfx
        # Loop the video to cover the remaining audio length.
        video_clip = video_clip.with_effects([vfx.Loop(duration=audio_clip.duration)])
    else:
        audio_clip = audio_clip.subclipped(0, video_clip.duration)

    final_clip = video_clip.with_audio(audio_clip)

    output_path = os.path.join(tempfile.gettempdir(), "merged.mp4")
    final_clip.write_videofile(
        output_path,
        codec="libx264",
        audio_codec="aac",
        fps=video_clip.fps or 24,
        logger=None,
    )

    video_clip.close()
    audio_clip.close()
    final_clip.close()

    # Upload the merged video so VEED's captioning API can fetch it by URL.
    with open(output_path, "rb") as f:
        merged_url = fal_client.upload(f.read(), "video/mp4")

    return merged_url


def _generate_avatar_video(script: str, audio_path: str) -> str:
    """
    Generates a lip-synced talking avatar video using VEED Fabric 1.0,
    combining the hardcoded avatar photo with the voiceover audio.
    Returns a local file path to the avatar video.
    """
    import fal_client

    # Fabric 1.0 accepts an audio URL, so upload the local voiceover file first.
    with open(audio_path, "rb") as f:
        audio_url = fal_client.upload(f.read(), "audio/mpeg")

    result = fal_client.subscribe(
        "veed/fabric-1.0",
        arguments={
            "image_url": AVATAR_IMAGE_URL,
            "audio_url": audio_url,
            "resolution": "480p",  # faster/cheaper for a small PiP overlay
        },
    )
    avatar_video_url = result.get("video", {}).get("url")
    if not avatar_video_url:
        raise RuntimeError("VEED Fabric returned no avatar video.")

    return _download_to_temp(avatar_video_url, "_avatar.mp4")


def _overlay_avatar(main_video_path: str, avatar_video_path: str) -> str:
    """
    Composites the talking avatar as a small picture-in-picture box in the
    bottom-right corner of the main property video. The main video's own
    audio track (the voiceover, already merged in) is kept; the avatar
    clip's audio is dropped to avoid doubling it up.
    """
    from moviepy import VideoFileClip, CompositeVideoClip

    main_clip = VideoFileClip(main_video_path)
    avatar_clip = VideoFileClip(avatar_video_path).without_audio()

    # Match avatar clip length to the main video, looping/trimming as needed.
    if avatar_clip.duration < main_clip.duration:
        from moviepy import vfx
        avatar_clip = avatar_clip.with_effects([vfx.Loop(duration=main_clip.duration)])
    else:
        avatar_clip = avatar_clip.subclipped(0, main_clip.duration)

    avatar_width = int(main_clip.w * AVATAR_WIDTH_FRACTION)
    avatar_clip = avatar_clip.resized(width=avatar_width)
    avatar_clip = avatar_clip.with_position(
        (main_clip.w - avatar_width - AVATAR_MARGIN_PX, main_clip.h - avatar_clip.h - AVATAR_MARGIN_PX)
    )

    composite = CompositeVideoClip([main_clip, avatar_clip])

    output_path = os.path.join(tempfile.gettempdir(), "with_avatar.mp4")
    composite.write_videofile(
        output_path,
        codec="libx264",
        audio_codec="aac",
        fps=main_clip.fps or 24,
        logger=None,
    )

    main_clip.close()
    avatar_clip.close()
    composite.close()

    return output_path


def _add_captions(video_url: str) -> str:
    """
    Sends the merged video to VEED's real Subtitles API (hosted on Fal),
    which auto-transcribes the voiceover and burns in styled captions.
    Returns the final captioned video URL.
    """
    import fal_client

    result = fal_client.subscribe(
        "veed/subtitles",
        arguments={
            "video_url": video_url,
            "preset": "glass",   # clean, readable caption style
            "language": None,    # auto-detect
        },
    )
    return result.get("video", {}).get("url") or video_url


def assemble_video(clip_urls: list[str], script: str) -> dict:
    """
    Full pipeline: takes the Fal-generated property video + the OpenAI
    script, adds a female AI voiceover reading the script, merges it onto
    the video, then sends it through VEED to burn in captions.

    Returns a dict of aspect-ratio keys pointing at the same final video
    (true per-format re-rendering is a future enhancement — see note below).
    """
    primary_video = clip_urls[0] if clip_urls else MOCK_VIDEO
    fallback = {"vertical": primary_video, "square": primary_video, "horizontal": primary_video}

    if not script:
        # No script to narrate — return the raw video untouched rather than
        # silently skipping the voiceover step.
        return fallback

    if MOCK_MODE.get("veed", True):
        return fallback

    try:
        audio_path = _generate_voiceover(script)
        combined_video_path = _concatenate_clips(clip_urls) if clip_urls else _download_to_temp(MOCK_VIDEO, ".mp4")

        # Merge voiceover onto the property video, locally, keeping a local path.
        from moviepy import VideoFileClip, AudioFileClip
        video_clip = VideoFileClip(combined_video_path)
        audio_clip = AudioFileClip(audio_path)
        if audio_clip.duration > video_clip.duration:
            from moviepy import vfx
            video_clip = video_clip.with_effects([vfx.Loop(duration=audio_clip.duration)])
        else:
            audio_clip = audio_clip.subclipped(0, video_clip.duration)
        voiced_clip = video_clip.with_audio(audio_clip)
        voiced_path = os.path.join(tempfile.gettempdir(), "voiced.mp4")
        voiced_clip.write_videofile(voiced_path, codec="libx264", audio_codec="aac", fps=video_clip.fps or 24, logger=None)
        video_clip.close()
        audio_clip.close()
        voiced_clip.close()

        # Generate the talking avatar and overlay it as picture-in-picture.
        avatar_video_path = _generate_avatar_video(script, audio_path)
        final_local_path = _overlay_avatar(voiced_path, avatar_video_path)

        # Upload the finished (voiced + avatar) video so VEED captions can fetch it.
        import fal_client
        with open(final_local_path, "rb") as f:
            uploaded_url = fal_client.upload(f.read(), "video/mp4")

        final_video_url = _add_captions(uploaded_url)

        return {
            "vertical": final_video_url,
            "square": final_video_url,
            "horizontal": final_video_url,
        }
    except Exception as e:
        print(f"⚠️ VEED pipeline error (falling back to raw video, no voiceover/avatar/captions): {e}")
        return fallback