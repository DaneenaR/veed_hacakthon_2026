# Sheeld RealtorAI: Listing Video Generator

An AI-powered Streamlit app that turns property photos and listing details into a fully produced real estate tour video, complete with a persuasive script, a female AI voiceover, a lip-synced talking presenter, and burned-in captions.

Built for Tech: Europe using **Tavily**, **OpenAI**, **Pioneer (Fastino Labs)**, **Fal**, and **VEED**.

## What it does

An agent fills in the listing details, picks a brand voice persona, and uploads real property photos, the app then:

1. **Researches** the neighborhood's recent sales and market trends (Tavily)
2. **Writes** a persuasive ~40-second voiceover script and social caption from the raw listing details, in the chosen persona's voice (OpenAI)
3. **Generates cinematic video clips** from the uploaded photos and stitches them into one continuous property tour (Fal)
4. **Produces the final video** (VEED, via Fal):
   - Converts the script into a female AI voiceover
   - Merges that voiceover onto the property tour video
   - Generates a lip-synced talking presenter avatar reading the script, overlaid picture-in-picture in the corner
   - Burns in styled captions
5. **Displays** the finished video in-app, with options to publish it to listing platforms or download the MP4

The result: a ready-to-post listing video an agent can generate in minutes, without a camera crew, editor, or voice actor.

## Agent personas

Choose the voice your listing speaks in:

| Persona | Style |
|---|---|
| **Luxury Estate Specialist** | Polished, aspirational, understated confidence |
| **High-Energy Modern Agent** | Punchy, fast-paced, social-first |
| **Data-Driven Investment Broker** | Analytical, numbers-forward, credibility-focused |

## Pipeline

```
[Listing Facts + Tavily Comps]
             │
             ▼
          OpenAI   ──►  Persuasive script & social caption, in persona voice
             │
             ▼
        Fal (photos) ──►  Photo upload + cinematic image-to-video clips,
             │             stitched into one property tour
             ▼
           VEED   ──►  Female AI voiceover → merged onto video →
             │          talking avatar overlay (lip-synced) → captions
             ▼
        Streamlit  ──►  Final video displayed, ready to publish or download
```

**Why OpenAI and Pioneer are separate steps:** OpenAI handles the *what*,  turning messy listing facts and market data into a clean, structured, persuasive draft. Pioneer is used to apply persona-specific tone and voice styling on top of that draft, so the same facts can be delivered as a luxury pitch, a high-energy hook, or a data-driven case, depending on what the agent selects.

## Tech stack

| Tool | Role |
|---|---|
| [Streamlit](https://streamlit.io) | Web app UI |
| [Tavily](https://tavily.com) | Real-time web search for market data and comps |
| [OpenAI](https://openai.com) | Script/caption generation (GPT) + voiceover audio (TTS, `nova` voice) |
| [Pioneer](https://pioneer.ai) (Fastino Labs) | Persona/brand-voice tuning on top of the drafted script |
| [Fal](https://fal.ai) | Photo upload, image-to-video generation, and hosting for VEED's models |
| [VEED](https://veed.io) (via Fal) | Talking avatar (Fabric 1.0) and auto-captioning (Subtitles) |
| [moviepy](https://zulko.github.io/moviepy/) | Local video editing: clip stitching, audio merge, avatar overlay |

## Setup

### 1. Clone the repo
```bash
git clone https://github.com/DaneenaR/veed_hacakthon_2026.git
cd veed_hacakthon_2026
```

### 2. (Optional) Create a virtual environment
```bash
python -m venv .venv
source .venv/Scripts/activate   # Windows (Git Bash)
# or: source .venv/bin/activate  # Mac/Linux
```

### 3. Install dependencies
```bash
pip install -r requirements.txt
```

### 4. Add your API keys
Create a `.env` file in the project root:
```
OPENAI_API_KEY=your_openai_key_here
PIONEER_API_KEY=your_pioneer_key_here
FAL_KEY=your_fal_key_here
TAVILY_API_KEY=your_tavily_key_here
H_API_KEY=your_h_key_here
```
`.env` is git-ignored — never commit your keys.

### 5. Run the app
```bash
python -m streamlit run app.py
```

## Mock mode

`config.py` has a `MOCK_MODE` switch per service, so the app can be demoed instantly on free placeholder data without burning API credits:

```python
MOCK_MODE = {
    "tavily": True,
    "openai": True,
    "fal": True,
    "veed": True,
    "h": True,
}
```
Set any of these to `False` to run that service live. `h` should stay mocked, see below.

## About the H (publishing) integration

`h_service.py` is intentionally left as a mocked stub. H's public API is a low-level model for interpreting screenshots and returning click coordinates, not a hosted "post this listing" endpoint, actually automating a login and post to a platform like Facebook Marketplace or Zillow requires running H's full agent loop (Surfer-H-CLI) with real account credentials, and risks violating those platforms' bot-posting policies. This is documented here as a roadmap item rather than built live.

## Roadmap

- [ ] Wire up a real H-agent flow for a lower-risk, read-only task (e.g. checking if a listing already exists) as a safer proof of concept
- [ ] Fine-tune a dedicated Pioneer model per persona, trained on real listing copy in that voice
- [ ] True per-format video rendering (vertical/square/horizontal are currently the same render)
- [ ] Swap the hardcoded avatar photo for a per-agent uploaded headshot
- [ ] Analytics feedback loop, track engagement and retrain persona models on what performs best

## Team

Daneena Roy, Fatima Amir Fahim, Fatima Waseem

## License

See [LICENSE](./LICENSE)