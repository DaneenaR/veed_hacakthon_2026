import os
import time
import requests
from types import SimpleNamespace
import streamlit as st
from dotenv import load_dotenv

# Import Backend Services
from services.tavily_service import get_market_context
from services.openai_service import generate_script_and_description
from services.veed_service import assemble_video
from services.h_service import post_listing
from services.fal_service import upload_all_photos, generate_clips, NoPhotosUploadedError

load_dotenv()

# --- PAGE CONFIGURATION ---
st.set_page_config(
    page_title="Sheeld RealtorAI | Media Studio",
    layout="wide",
    initial_sidebar_state="collapsed",
)

# --- SVG ICONS ---
SVG_HOUSE = '<svg xmlns="http://www.w3.org/2000/svg" width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="#6D28D9" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><path d="m3 9 9-7 9 7v11a2 2 0 0 1-2 2H5a2 2 0 0 1-2-2z"/><polyline points="9 22 9 12 15 12 15 22"/></svg>'
SVG_SPARKLE = '<svg xmlns="http://www.w3.org/2000/svg" width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="#7C3AED" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><path d="m12 3-1.912 5.813a2 2 0 0 1-1.275 1.275L3 12l5.813 1.912a2 2 0 0 1 1.275 1.275L12 21l1.912-5.813a2 2 0 0 1 1.275-1.275L21 12l-5.813-1.912a2 2 0 0 1-1.275-1.275L12 3Z"/></svg>'

# --- TAILWIND & CUSTOM CSS ---
st.markdown('<script src="https://cdn.tailwindcss.com"></script>', unsafe_allow_html=True)
st.markdown("""
<style>
    @import url('https://fonts.googleapis.com/css2?family=Plus+Jakarta+Sans:wght@400;500;600;700;800&display=swap');

    .stApp {
        background: linear-gradient(135deg, #F3F0FF 0%, #EBE5FF 50%, #F5F3FF 100%);
        color: #0F172A;
        font-family: 'Plus Jakarta Sans', system-ui, -apple-system, sans-serif;
    }

    .brand-header {
        display: flex;
        align-items: center;
        justify-content: space-between;
        margin-bottom: 24px;
        padding-bottom: 12px;
        border-bottom: 1px solid rgba(203, 213, 225, 0.6);
    }
    .brand-title {
        font-size: 1.5rem;
        font-weight: 800;
        letter-spacing: -0.5px;
        color: #4C1D95;
        display: flex;
        align-items: center;
        gap: 10px;
    }
    .studio-badge {
        background: rgba(109, 40, 217, 0.1);
        border: 1px solid rgba(109, 40, 217, 0.25);
        color: #6D28D9;
        font-size: 0.7rem;
        font-weight: 700;
        padding: 3px 8px;
        border-radius: 6px;
        text-transform: uppercase;
        letter-spacing: 0.8px;
    }

    div[data-testid="stVerticalBlockBorderWrapper"] {
        background: rgba(255, 255, 255, 0.72) !important;
        backdrop-filter: blur(16px) saturate(180%) !important;
        -webkit-backdrop-filter: blur(16px) saturate(180%) !important;
        border: 1px solid rgba(203, 213, 225, 0.85) !important;
        border-radius: 18px !important;
        box-shadow: 0 12px 32px -8px rgba(109, 40, 217, 0.06) !important;
    }

    .viewfinder-bar {
        background: #0F172A;
        color: #94A3B8;
        padding: 8px 14px;
        border-top-left-radius: 12px;
        border-top-right-radius: 12px;
        font-size: 0.75rem;
        font-weight: 600;
        display: flex;
        justify-content: space-between;
        align-items: center;
        letter-spacing: 0.5px;
    }
    .rec-dot {
        height: 8px;
        width: 8px;
        background-color: #EF4444;
        border-radius: 50%;
        display: inline-block;
        box-shadow: 0 0 8px #EF4444;
        animation: pulse-red 1.5s infinite;
    }
    @keyframes pulse-red {
        0% { opacity: 1; }
        50% { opacity: 0.3; }
        100% { opacity: 1; }
    }

    .stButton>button {
        background: linear-gradient(135deg, #6D28D9 0%, #5B21B6 100%) !important;
        color: #FFFFFF !important;
        border: none !important;
        border-radius: 10px !important;
        font-weight: 600 !important;
        box-shadow: 0 4px 12px rgba(109, 40, 217, 0.25) !important;
    }

    .stTabs [data-baseweb="tab-list"] {
        gap: 6px;
        background: rgba(237, 233, 254, 0.5);
        padding: 4px;
        border-radius: 12px;
    }
    .stTabs [aria-selected="true"] {
        background-color: #FFFFFF !important;
        color: #5B21B6 !important;
        box-shadow: 0 2px 8px rgba(109, 40, 217, 0.1) !important;
    }

    .app-footer {
        text-align: center;
        padding: 24px 0 8px 0;
        color: #6B21A8;
        font-size: 0.8rem;
        font-weight: 600;
    }
</style>
""", unsafe_allow_html=True)

if "video_generated" not in st.session_state:
    st.session_state["video_generated"] = False

# --- HEADER ---
st.markdown(f"""
<div class="brand-header">
    <div class="brand-title">
        {SVG_HOUSE} <span>sheeld</span> <span style="font-weight:300; color:#6D28D9;">REALTOR STUDIO</span>
    </div>
    <div>
        <span class="studio-badge">Pioneer v2.1 Engine</span>
        <span class="studio-badge" style="margin-left: 6px;">VEED Core Active</span>
    </div>
</div>
""", unsafe_allow_html=True)

# --- SECTION 1: CREATE PROPERTY ---
with st.container(border=True):
    st.markdown(
        f"<div style='display:flex; align-items:center; gap:8px; font-weight:700; font-size:1.1rem; color:#4C1D95; margin-bottom:12px;'>{SVG_SPARKLE} Listing Parameters & Script Specs</div>",
        unsafe_allow_html=True)

    col_left, col_right = st.columns(2)

    with col_left:
        prop_title = st.text_input("Property Title", value="Modern Ocean Villa", placeholder="e.g. Modern Ocean Villa")

        c1, c2 = st.columns(2)
        with c1:
            prop_price = st.text_input("List Price", value="$1,250,000", placeholder="$1,250,000")
        with c2:
            prop_address = st.text_input("Address / Neighborhood", value="Brickell, Miami FL",
                                         placeholder="Brickell, Miami FL")

        c3, c4, c5 = st.columns(3)
        with c3:
            prop_beds = st.text_input("Bedrooms", value="3")
        with c4:
            prop_baths = st.text_input("Bathrooms", value="3")
        with c5:
            prop_sqft = st.text_input("Square Feet", value="2,500 sqft")

        script_desc = st.text_area(
            "Selling Features & Amenities",
            value="Ocean views, private balcony, newly renovated kitchen with marble finishes.",
            height=70
        )

        pioneer_persona = st.selectbox(
            "Pioneer Brand Voice Model",
            ["Luxury Estate Specialist", "High-Energy Modern Agent", "Data-Driven Investment Broker"]
        )

    with col_right:
        uploaded_photos = st.file_uploader(
            "Property Photography Assets (Fal.ai) — required",
            type=["png", "jpg", "jpeg"],
            accept_multiple_files=True
        )

        target_lang = st.selectbox(
            "Narrator Voiceover Language (VEED)",
            ["English", "Spanish", "French", "Mandarin"]
        )

        use_tavily = st.checkbox("Include live Tavily neighborhood market research", value=True)

    st.markdown("<br>", unsafe_allow_html=True)

    # GENERATE BUTTON PIPELINE
    if st.button("Generate Property Tour Video", type="primary", use_container_width=True):
        if not prop_title:
            st.warning("Please enter a property title before generating.")
        elif not uploaded_photos:
            st.error("📸 Please upload at least one property photo before generating a video.")
        else:
            status_text = st.empty()
            progress_bar = st.progress(0)

            # Build Listing object for services expecting dot notation
            listing_obj = SimpleNamespace(
                title=prop_title,
                address=prop_address,
                price=prop_price,
                beds=prop_beds,
                baths=prop_baths,
                sqft=prop_sqft,
                details=script_desc
            )

            try:
                # Step 1: Tavily Service Call
                if use_tavily:
                    status_text.markdown(
                        "**Phase 1/6 [Tavily API]:** Querying submarket comps & historical transactions...")
                    progress_bar.progress(15)
                    market_context = get_market_context(prop_address)
                else:
                    market_context = "No live market data requested."
                    progress_bar.progress(15)

                st.session_state["market_context"] = market_context

                # Step 2: OpenAI + Pioneer Script Generation
                status_text.markdown(
                    f"**Phase 2/6 [OpenAI + Pioneer]:** Synthesizing script in `{pioneer_persona}` voice..."
                )
                progress_bar.progress(30)

                script, social_desc = generate_script_and_description(
                    listing_obj, market_context, persona=pioneer_persona
                )
                st.session_state["generated_script"] = script
                st.session_state["social_description"] = social_desc

                # Step 3: Fal.ai Photo Upload
                status_text.markdown("**Phase 3/6 [Fal.ai Studio]:** Uploading property photos...")
                progress_bar.progress(45)

                photo_urls = upload_all_photos(uploaded_photos)
                st.session_state["photo_urls"] = photo_urls

                # Step 4: Fal.ai Motion Clip Generation
                status_text.markdown("**Phase 4/6 [Fal.ai Studio]:** Generating cinematic property motion clips...")
                progress_bar.progress(60)

                motion_clips = generate_clips(photo_urls)
                st.session_state["motion_clips"] = motion_clips

                # Step 5: VEED — Female AI Voiceover + Audio Merge
                status_text.markdown("**Phase 5/6 [VEED]:** Recording female AI voiceover & merging audio...")
                progress_bar.progress(80)

                # Step 6: VEED — Captioning (both happen inside assemble_video)
                status_text.markdown("**Phase 6/6 [VEED]:** Burning in captions & finalizing render...")
                progress_bar.progress(95)

                video_exports = assemble_video(motion_clips, script)
                st.session_state["video_exports"] = video_exports

                progress_bar.progress(100)
                status_text.empty()
                progress_bar.empty()
                st.toast("Media render completed successfully!")

                st.session_state["video_generated"] = True
                st.session_state["active_title"] = prop_title
                st.rerun()

            except NoPhotosUploadedError as e:
                status_text.empty()
                progress_bar.empty()
                st.error(f"📸 {e}")
            except RuntimeError as e:
                status_text.empty()
                progress_bar.empty()
                st.error(f"⚠️ Video generation failed: {e}")

# --- SECTION 2: RESULTS STUDIO TABS ---
if st.session_state["video_generated"]:
    st.markdown("<br>", unsafe_allow_html=True)

    with st.container(border=True):
        st.markdown(f"### Media Output Monitor: {st.session_state.get('active_title', '')}")

        tab_video, tab_comps, tab_publish = st.tabs([
            "Rendered Tour Video & Script",
            "Market Intelligence & Comps",
            "Multi-Portal Automation"
        ])

        # TAB 1: VIDEO PLAYER & SCRIPT
        with tab_video:
            v_col1, v_col2 = st.columns([1.2, 1])
            with v_col1:
                st.markdown("""
                <div class="viewfinder-bar">
                    <div><span class="rec-dot"></span> LIVE MONITOR</div>
                    <div>4K PRORES • 60 FPS</div>
                    <div>VEED + PIONEER PIPELINE</div>
                </div>
                """, unsafe_allow_html=True)

                exports = st.session_state.get("video_exports", {})
                selected_format = st.radio("Export Aspect Ratio", ["vertical", "horizontal", "square"], horizontal=True)

                video_url = exports.get(selected_format) or "https://commondatastorage.googleapis.com/gtv-videos-bucket/sample/ForBiggerBlazes.mp4"
                st.video(video_url)

                # Display active source images below the player
                photos = st.session_state.get("photo_urls", [])
                if photos:
                    st.markdown("#### Source Property Photos")
                    st.image(photos, use_container_width=True)

            with v_col2:
                st.markdown("#### Pioneer Voiceover Script")
                st.info(st.session_state.get("generated_script", ""))

                st.markdown("#### Generated Social Description")
                st.success(st.session_state.get("social_description", ""))

        # TAB 2: TAVILY MARKET COMPS
        with tab_comps:
            st.markdown("#### Neighborhood Valuation Context (Tavily)")
            st.caption("Live research extracted to back up listing price point.")
            st.info(st.session_state.get("market_context", "No context available."))

        # TAB 3: H-AGENT AUTOMATION
        with tab_publish:
            p_col1, p_col2 = st.columns(2)

            with p_col1:
                st.markdown("#### H-Agent Browser Automation")
                selected_portals = st.multiselect(
                    "Target Syndication Channels",
                    ["Zillow Rental Manager", "Facebook Marketplace", "MLS Matrix Network"],
                    default=["Zillow Rental Manager", "Facebook Marketplace"]
                )

                if st.button("Dispatch H-Agent Browser Automation", type="primary", use_container_width=True):
                    log_box = st.empty()
                    with st.spinner("Executing headless browser instance..."):
                        log_box.markdown("`[H-Agent]` Launching Chromium instance...")
                        time.sleep(0.6)

                        video_url = st.session_state.get("video_exports", {}).get("vertical", "")
                        desc = st.session_state.get("social_description", "")
                        results = post_listing(video_url, desc, selected_portals)

                        for portal, result in results.items():
                            log_box.markdown(f"`[H-Agent]` **{portal}**: {result}")
                            time.sleep(0.5)

                        log_box.success("Syndication finished across all selected target platforms.")

            with p_col2:
                st.markdown("#### Master Video Asset Export")
                st.write("Download MP4 video asset for direct social sharing.")

                final_video_url = st.session_state.get("video_exports", {}).get("vertical", "")

                if final_video_url:
                    try:
                        video_bytes = requests.get(final_video_url, timeout=60).content
                        st.download_button(
                            label="Download MP4 Video Asset",
                            data=video_bytes,
                            file_name=f"{st.session_state.get('active_title', 'property').lower().replace(' ', '_')}_tour.mp4",
                            mime="video/mp4",
                            use_container_width=True
                        )
                    except Exception:
                        st.warning("Couldn't fetch the video for download right now. Try again in a moment.")
                else:
                    st.info("Generate a video first to enable download.")

        st.markdown("<br>", unsafe_allow_html=True)
        if st.button("Create New Property Tour Video", use_container_width=True):
            st.session_state["video_generated"] = False
            st.rerun()

# --- FOOTER ---
st.markdown(
    "<div class='app-footer'>created with love ❤️: Daneena Roy, Fatima Amir, Fatima Waseem</div>",
    unsafe_allow_html=True
)