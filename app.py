import os
import time
import streamlit as st
from dotenv import load_dotenv

load_dotenv()

# --- PAGE CONFIGURATION ---
st.set_page_config(
    page_title="Sheeld RealtorAI | Studio",
    page_icon="🔮",
    layout="wide",
    initial_sidebar_state="collapsed",
)

# --- CUSTOM CSS ---
st.markdown("""
<style>
    .stApp {
        background-color: #F4F6FC;
        color: #1E293B;
        font-family: 'Inter', system-ui, -apple-system, sans-serif;
    }
    .brand-logo {
        font-size: 1.6rem;
        font-weight: 800;
        color: #4F46E5;
        margin-bottom: 20px;
    }
    .stButton>button {
        border-radius: 12px;
        font-weight: 600;
    }
    .app-footer {
        text-align: center;
        padding: 30px 0 10px 0;
        color: #64748B;
        font-size: 0.85rem;
        font-weight: 500;
        letter-spacing: 0.3px;
    }
    .comp-card {
        background: #F8FAFC;
        border: 1px solid #E2E8F0;
        border-radius: 12px;
        padding: 14px;
        margin-bottom: 10px;
    }
    .stTabs [data-baseweb="tab-list"] {
        gap: 8px;
    }
    .stTabs [data-baseweb="tab"] {
        border-radius: 10px;
        padding: 8px 16px;
    }
</style>
""", unsafe_allow_html=True)

if "video_generated" not in st.session_state:
    st.session_state["video_generated"] = False

# --- HEADER ---
st.markdown(
    "<div class='brand-logo'>🔮 <b>sheeld</b> <span style='color:#94A3B8; font-weight:400;'>| RealtorAI Studio</span></div>",
    unsafe_allow_html=True)

# --- SECTION 1: CREATE PROPERTY (INPUT SECTION) ---
with st.container(border=True):
    st.markdown("### 🏡 Create Property Video")

    col_left, col_right = st.columns(2)

    with col_left:
        prop_title = st.text_input("Property Title", value="Modern Ocean Villa", placeholder="e.g. Modern Ocean Villa")

        c1, c2 = st.columns(2)
        with c1:
            prop_price = st.text_input("Price", value="$1,250,000", placeholder="$1,250,000")
        with c2:
            prop_address = st.text_input("Address / Neighborhood", value="Brickell, Miami FL",
                                         placeholder="Brickell, Miami FL")

        script_desc = st.text_area(
            "Property Details & Selling Features (Script Input)",
            value="3 Bed, 3 Bath, ocean views, private balcony, newly renovated kitchen with marble finishes.",
            height=100
        )

        use_tavily = st.checkbox("🔍 Fetch live Tavily market comps to enrich OpenAI script", value=True)

    with col_right:
        uploaded_photos = st.file_uploader(
            "Upload Property Pictures (Fal.ai)",
            type=["png", "jpg", "jpeg"],
            accept_multiple_files=True
        )

        target_lang = st.selectbox(
            "Voiceover Language (VEED)",
            ["English", "Spanish", "French", "Mandarin"]
        )

    st.markdown("<br>", unsafe_allow_html=True)

    # GENERATE BUTTON & PROGRESS PIPELINE
    if st.button("⚡ Generate Video", type="primary", use_container_width=True):
        if not prop_title:
            st.warning("Please enter a property title before generating.")
        else:
            status_text = st.empty()
            progress_bar = st.progress(0)

            # Step 1: Tavily Search Comps
            if use_tavily:
                status_text.markdown("🔍 **Step 1/4 (Tavily):** Searching neighborhood comps & market trends...")
                progress_bar.progress(25)
                time.sleep(1.0)

                st.session_state["tavily_comps"] = [
                    {"address": "101 Brickell Ave #1402", "price": "$1,180,000", "sqft": "$810/sqft",
                     "status": "Sold 2 wks ago"},
                    {"address": "150 SE 25th Rd #801", "price": "$1,310,000", "sqft": "$845/sqft",
                     "status": "Sold 1 mo ago"},
                    {"address": "Brickell Submarket Trend", "price": "+12.4% YoY Growth",
                     "sqft": "Avg 32 Days on Market", "status": "Active Market Trend"}
                ]
            else:
                st.session_state["tavily_comps"] = []

            # Step 2: OpenAI Scripting
            status_text.markdown("✍️ **Step 2/4 (OpenAI):** Merging listing details + Tavily comps into tour script...")
            progress_bar.progress(50)
            time.sleep(1.0)

            st.session_state["generated_script"] = (
                f"Welcome to {prop_title} in {prop_address}, offered at {prop_price}. "
                f"Featuring {script_desc} With Brickell submarket prices growing over 12% YoY, "
                f"this home represents top value compared to recent neighborhood sales averaging over $800/sqft. "
                f"Schedule your tour today!"
            )

            # Step 3: Fal.ai Motion
            status_text.markdown("🖼️ **Step 3/4 (Fal.ai):** Generating motion clips from property photos...")
            progress_bar.progress(75)
            time.sleep(1.0)

            # Step 4: VEED Rendering
            status_text.markdown("🎬 **Step 4/4 (VEED):** Synthesizing avatar voiceover & compiling captions...")
            progress_bar.progress(100)
            time.sleep(1.0)

            status_text.empty()
            progress_bar.empty()
            st.toast("Tour video generated successfully!")

            st.session_state["video_generated"] = True
            st.session_state["video_url"] = "https://www.w3schools.com/html/mov_bbb.mp4"
            st.session_state["active_title"] = prop_title
            st.rerun()

# --- SECTION 2: OUTPUT & MARKET COMPARISON (LOADS BELOW GENERATE BUTTON) ---
if st.session_state["video_generated"]:
    st.markdown("<br>", unsafe_allow_html=True)

    with st.container(border=True):
        st.markdown(f"### 🎬 Results Studio: {st.session_state.get('active_title', '')}")

        # TABBED OUTPUT LAYOUT
        tab_video, tab_comps, tab_publish = st.tabs([
            "📽️ Rendered Video & Script (VEED + OpenAI)",
            "📊 Market Comps Comparison (Tavily)",
            "🚀 Publish & Export (H-Agent)"
        ])

        # TAB 1: VIDEO PLAYER & SCRIPT
        with tab_video:
            v_col1, v_col2 = st.columns([1.2, 1])
            with v_col1:
                st.markdown("#### Rendered Tour Video")
                st.video(st.session_state["video_url"])
            with v_col2:
                st.markdown("#### OpenAI Narration Script")
                st.info(st.session_state.get("generated_script", ""))

        # TAB 2: TAVILY MARKET COMPS COMPARISON
        with tab_comps:
            st.markdown("#### Neighborhood Comps & Market Intelligence")
            st.caption("Live search results fetched via Tavily API to ground script pricing context.")

            comps = st.session_state.get("tavily_comps", [])
            if comps:
                comp_cols = st.columns(len(comps))
                for idx, comp in enumerate(comps):
                    with comp_cols[idx]:
                        st.markdown(f"""
                        <div class='comp-card'>
                            <b>📍 {comp['address']}</b><br/>
                            <span style='color: #4F46E5; font-weight:700; font-size:1.1rem;'>{comp['price']}</span><br/>
                            <small>{comp['sqft']} • <i>{comp['status']}</i></small>
                        </div>
                        """, unsafe_allow_html=True)
            else:
                st.info("No Tavily market comps were requested for this render.")

        # TAB 3: H-AGENT AUTOMATION & EXPORT
        with tab_publish:
            p_col1, p_col2 = st.columns(2)

            with p_col1:
                st.markdown("#### 🤖 Auto-Post via H-Agent")
                selected_portals = st.multiselect(
                    "Select Target Portals",
                    ["Zillow Manager", "Facebook Marketplace", "MLS Matrix"],
                    default=["Zillow Manager", "Facebook Marketplace"]
                )

                if st.button("Launch H-Agent Automation", type="primary", use_container_width=True):
                    with st.spinner("H-Agent opening headless browser to post listing..."):
                        time.sleep(2)
                        st.success("H-Agent successfully submitted listings to selected portals!")

            with p_col2:
                st.markdown("#### 💾 Local Export")
                st.write("Download the MP4 video file to your computer.")

                st.download_button(
                    label="📥 Download Video (.mp4)",
                    data=b"sample_video_bytes_content",
                    file_name=f"{st.session_state.get('active_title', 'property').lower().replace(' ', '_')}_tour.mp4",
                    mime="video/mp4",
                    use_container_width=True
                )

        st.markdown("<br>", unsafe_allow_html=True)
        if st.button("➕ Create Another Property Video", use_container_width=True):
            st.session_state["video_generated"] = False
            st.rerun()

# --- FOOTER WATERMARK ---
st.markdown(
    "<div class='app-footer'>created with love ❤️: Daneena Roy, Fatima Amir, Fatima Waseem</div>",
    unsafe_allow_html=True
)