"""
Human-Crafted Editorial Design System for VidyaVerse AI
Rooted subtly in warm Madurai limestone, sandstone & terracotta minimalism:
  - Clean warm alabaster paper canvas (#F8F6F2) — zero noisy dots or rainbow gradients
  - Crisp hairline borders (#E5DFD6), restrained 10px–12px radii, Inter + Source Serif 4 typography
  - Minimalist geometric monogram SVG & clean monochrome line icons (zero emoji spam)
"""

import base64
import html
import os
from pathlib import Path
import streamlit as st

from dotenv import load_dotenv
from components.i18n import SUPPORTED_LANGUAGES, get_lang, tr, ui

load_dotenv(Path(__file__).resolve().parent.parent / ".env", override=False)
APP_NAME = os.getenv("APP_PLATFORM_NAME", "VidyaVerse")
ASSETS_DIR = Path(__file__).resolve().parent.parent / "assets"

CURRICULUM_CATALOG = [
    {
        "topic": "Python Programming",
        "code": "01",
        "icon": "PY",
        "tag": "Core Language",
        "desc": "Data model, mutability, comprehensions, GIL, method resolution order, and memory internals.",
    },
    {
        "topic": "Artificial Intelligence & ML",
        "code": "02",
        "icon": "ML",
        "tag": "Machine Learning",
        "desc": "Evaluation metrics, regularization, Transformer self-attention, RAG grounding, and LoRA.",
    },
    {
        "topic": "Data Structures & Algorithms",
        "code": "03",
        "icon": "DS",
        "tag": "Algorithms",
        "desc": "Queues, balanced trees, QuickSort vs MergeSort, Dijkstra, LRU Cache, and Union-Find.",
    },
    {
        "topic": "Web Development & Cloud",
        "code": "04",
        "icon": "CL",
        "tag": "AWS & Cloud Architecture",
        "desc": "Amazon Bedrock, AWS Lambda, S3, IAM Least Privilege, VPC networking, DynamoDB, and Docker.",
    },
    {
        "topic": "Database Systems & SQL",
        "code": "05",
        "icon": "DB",
        "tag": "Data Systems",
        "desc": "Relational joins, 3NF normalization, B+ Tree indexing, MVCC snapshots, and WAL durability.",
    },
    {
        "topic": "Cybersecurity & Networks",
        "code": "06",
        "icon": "SC",
        "tag": "Network Security",
        "desc": "TLS 1.3 forward secrecy, SQLi/CSRF/XSS mitigation, salted KDFs, SSRF, and OAuth 2.0 PKCE.",
    },
]

ARTWORK_META = {
    "madurai_meenakshi_dawn.jpg": (
        "Madurai Sandstone & Water Court",
        "Quiet architectural symmetry inspiring structured, step-by-step mastery.",
    ),
    "madurai_thirumalai_sangam.jpg": (
        "Thirumalai Nayakkar Colonnade",
        "Classical South Indian limestone arches and calm scholarly spaces.",
    ),
    "madurai_vaigai_night_tech.jpg": (
        "Collaborative Engineering Study",
        "Focused peer learning across algorithms, cloud architecture, and systems.",
    ),
}

# Clean minimalist geometric architectural mark (1.6px stroke, human-crafted brand monogram)
BRAND_MARK_SVG = """<svg width="32" height="32" viewBox="0 0 32 32" fill="none" xmlns="http://www.w3.org/2000/svg" style="flex-shrink:0;">
  <rect x="1" y="1" width="30" height="30" rx="8" fill="#9A4A27"/>
  <path d="M9 11L16 22L23 11" stroke="#FAF8F5" stroke-width="2.1" stroke-linecap="round" stroke-linejoin="round"/>
  <path d="M12.5 11L16 16.5L19.5 11" stroke="#E7C6B2" stroke-width="1.5" stroke-linecap="round" stroke-linejoin="round"/>
</svg>"""

POTRAMARAI_CREST_SVG = BRAND_MARK_SVG

CUSTOM_CSS = """
<style>
    @import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700&family=Noto+Sans+Devanagari:wght@400;500;600;700&family=Noto+Sans+Kannada:wght@400;500;600;700&family=Noto+Sans+Malayalam:wght@400;500;600;700&family=Noto+Sans+Tamil:wght@400;500;600;700&family=Noto+Sans+Telugu:wght@400;500;600;700&family=Source+Serif+4:opsz,wght@8..60,600;8..60,700&display=swap');

    html, body, [class*="css"] {
        font-family: 'Inter', 'Noto Sans Tamil', 'Noto Sans Devanagari', 'Noto Sans Telugu', 'Noto Sans Malayalam', 'Noto Sans Kannada', -apple-system, BlinkMacSystemFont, sans-serif;
        color: #1C1917;
        -webkit-font-smoothing: antialiased;
    }

    /* Calm Warm Limestone Paper Canvas — Zero artificial patterns */
    .stApp {
        background-color: #F8F6F2;
    }

    .block-container {
        padding-top: 1.25rem !important;
        padding-bottom: 3rem !important;
        max-width: 1200px !important;
    }

    header[data-testid="stHeader"] {
        background: transparent !important;
    }

    /* Clean Architectural Cards */
    div[data-testid="stVerticalBlockBorderWrapper"] {
        background-color: #FFFFFF !important;
        border: 1px solid #E5DFD5 !important;
        border-radius: 12px !important;
        padding: 1.35rem 1.5rem !important;
        box-shadow: 0 1px 2px rgba(28, 25, 23, 0.03), 0 4px 12px rgba(28, 25, 23, 0.02) !important;
        transition: border-color 0.16s ease, box-shadow 0.16s ease !important;
    }
    div[data-testid="stVerticalBlockBorderWrapper"]:hover {
        border-color: #D2C7B8 !important;
        box-shadow: 0 2px 6px rgba(28, 25, 23, 0.045), 0 8px 20px rgba(28, 25, 23, 0.035) !important;
    }

    /* Top Header Bar */
    .creamy-nav {
        background-color: #FFFFFF;
        border: 1px solid #E5DFD5;
        border-radius: 12px;
        padding: 0.85rem 1.25rem;
        display: flex;
        justify-content: space-between;
        align-items: center;
        flex-wrap: wrap;
        gap: 12px;
    }
    .creamy-title {
        font-family: 'Source Serif 4', 'Noto Sans Tamil', Georgia, serif;
        font-size: 1.38rem;
        font-weight: 700;
        color: #1C1917;
        letter-spacing: -0.02em;
        line-height: 1.15;
    }
    .agent-pill {
        background: #F3EFE9;
        color: #57504A;
        border: 1px solid #E4DDD3;
        padding: 0.24rem 0.65rem;
        border-radius: 6px;
        font-size: 0.75rem;
        font-weight: 600;
        letter-spacing: 0.01em;
    }
    .user-pill {
        background: #FAF8F5;
        border: 1px solid #E4DDD3;
        border-radius: 6px;
        padding: 0.24rem 0.72rem;
        font-weight: 600;
        font-size: 0.78rem;
        color: #292524;
    }

    /* Editorial Hero Surface */
    .hero-card {
        background-color: #FFFFFF;
        border: 1px solid #E5DFD5;
        border-radius: 14px;
        padding: 2rem 2.2rem;
        margin-bottom: 1.5rem;
        box-shadow: 0 1px 3px rgba(28, 25, 23, 0.03);
    }
    .hero-eyebrow {
        display: inline-block;
        color: #9A4A27;
        font-size: 0.74rem;
        font-weight: 700;
        text-transform: uppercase;
        letter-spacing: 0.08em;
        margin-bottom: 0.55rem;
    }
    .hero-headline {
        font-family: 'Source Serif 4', 'Noto Sans Tamil', 'Noto Sans Devanagari', 'Noto Sans Telugu', 'Noto Sans Malayalam', 'Noto Sans Kannada', Georgia, serif;
        font-size: 2.05rem;
        font-weight: 700;
        color: #1C1917;
        letter-spacing: -0.02em;
        line-height: 1.24;
        margin-bottom: 0.7rem;
    }
    .hero-sub {
        font-size: 0.98rem;
        color: #57534E;
        line-height: 1.62;
        margin-bottom: 0.5rem;
    }

    /* Monogram Domain Code Box */
    .domain-code-box {
        width: 36px;
        height: 36px;
        border-radius: 8px;
        background: #F5F1EB;
        border: 1px solid #E5DFD5;
        color: #7C3B1E;
        font-size: 0.76rem;
        font-weight: 700;
        letter-spacing: 0.04em;
        display: inline-flex;
        align-items: center;
        justify-content: center;
    }
    .feature-title {
        font-size: 1.02rem;
        font-weight: 600;
        color: #1C1917;
        letter-spacing: -0.01em;
        margin-bottom: 0.3rem;
    }
    .feature-desc {
        font-size: 0.875rem;
        color: #57534E;
        line-height: 1.55;
    }

    /* General Surface Card */
    .creamy-card {
        background-color: #FFFFFF;
        border: 1px solid #E5DFD5;
        border-radius: 12px;
        padding: 1.25rem 1.4rem;
        margin-bottom: 0.9rem;
    }

    /* Clean KPI Stat Cards */
    .metric-box {
        background: #FFFFFF;
        border: 1px solid #E5DFD5;
        border-radius: 12px;
        padding: 1.05rem 1rem;
        text-align: left;
    }
    .metric-value {
        font-size: 1.65rem;
        font-weight: 700;
        color: #1C1917;
        letter-spacing: -0.02em;
        margin-bottom: 0.15rem;
        line-height: 1.2;
    }
    .metric-label {
        font-size: 0.76rem;
        color: #78716C;
        font-weight: 500;
    }

    /* Recommendation / Decision Callout */
    .decider-banner {
        background: #FCF9F5;
        border: 1px solid #E6DACB;
        border-left: 3.5px solid #9A4A27;
        border-radius: 10px;
        padding: 1.05rem 1.3rem;
        margin: 1rem 0;
    }

    /* Restrained Status Tags */
    .pista-badge {
        background-color: #EDF5F0;
        color: #22543D;
        border: 1px solid #CFE3D6;
        padding: 0.2rem 0.6rem;
        border-radius: 6px;
        font-size: 0.75rem;
        font-weight: 600;
        display: inline-block;
    }
    .terracotta-badge {
        background-color: #FDF2EC;
        color: #9A3412;
        border: 1px solid #F3D3C3;
        padding: 0.2rem 0.6rem;
        border-radius: 6px;
        font-size: 0.75rem;
        font-weight: 600;
        display: inline-block;
    }
    .almond-badge {
        background-color: #F4F1EC;
        color: #44403C;
        border: 1px solid #E5E0D8;
        padding: 0.2rem 0.6rem;
        border-radius: 6px;
        font-size: 0.75rem;
        font-weight: 500;
        display: inline-block;
    }

    /* Clean Documentary Photography Frame (No tacky floating pills) */
    .ai-art-frame {
        border-radius: 10px;
        overflow: hidden;
        border: 1px solid #E5DFD5;
        background: #EFECE6;
    }
    .ai-art-frame img {
        width: 100%;
        display: block;
        object-fit: cover;
        transition: transform 0.35s ease;
    }
    .ai-art-frame:hover img {
        transform: scale(1.02);
    }
    .photo-caption {
        font-size: 0.76rem;
        color: #78716C;
        margin-top: 0.45rem;
        line-height: 1.4;
    }

    /* Buttons: Solid, Crisp Terracotta-Bronze & Clean Secondary */
    .stButton > button[kind="primary"],
    div[data-testid="stFormSubmitButton"] > button {
        background: #9A4A27 !important;
        color: #FFFFFF !important;
        border: 1px solid #8A3F1F !important;
        border-radius: 8px !important;
        padding: 0.5rem 1.1rem !important;
        font-weight: 600 !important;
        font-size: 0.88rem !important;
        letter-spacing: -0.005em !important;
        box-shadow: 0 1px 2px rgba(28, 25, 23, 0.08) !important;
        transition: background-color 0.15s ease !important;
    }
    .stButton > button[kind="primary"]:hover,
    div[data-testid="stFormSubmitButton"] > button:hover {
        background: #7F3B1D !important;
        border-color: #7F3B1D !important;
    }

    .stButton > button[kind="secondary"] {
        background-color: #FFFFFF !important;
        color: #292524 !important;
        border: 1px solid #DCD5CA !important;
        border-radius: 8px !important;
        padding: 0.5rem 1.05rem !important;
        font-weight: 500 !important;
        font-size: 0.88rem !important;
        transition: background-color 0.15s ease, border-color 0.15s ease !important;
    }
    .stButton > button[kind="secondary"]:hover {
        background-color: #F6F3EE !important;
        border-color: #BBAE9E !important;
        color: #1C1917 !important;
    }

    /* Horizontal Top Navigation Bar Links */
    div[data-testid="stPageLink-NavLink"] {
        background-color: transparent !important;
        border: 1px solid transparent !important;
        border-radius: 8px !important;
        padding: 0.38rem 0.6rem !important;
        font-weight: 500 !important;
        font-size: 0.87rem !important;
        color: #44403C !important;
        justify-content: center !important;
        transition: all 0.14s ease !important;
    }
    div[data-testid="stPageLink-NavLink"]:hover {
        background-color: #EFECE6 !important;
        color: #1C1917 !important;
    }
    div[data-testid="stPageLink-NavLink"][aria-current="page"] {
        background-color: #FFFFFF !important;
        border: 1px solid #DFD8CE !important;
        color: #9A4A27 !important;
        font-weight: 600 !important;
        box-shadow: 0 1px 2px rgba(28, 25, 23, 0.04) !important;
    }

    /* =========================================================
       CRUCIAL HIGH-CONTRAST TYPOGRAPHY & CLOUD THEME OVERRIDE
       Ensures text, tabs, inputs, and MCQ radio choices are 100% visible
       under all dark-mode and light-mode system preferences.
       ========================================================= */
    html, body, [class*="css"], .stApp {
        color: #1C1917 !important;
    }

    /* All Markdown & Paragraph Text */
    .stMarkdown, .stMarkdown p, .stMarkdown span, .stMarkdown li, [data-testid="stMarkdownContainer"] p, [data-testid="stMarkdownContainer"] span, [data-testid="stMarkdownContainer"] li {
        color: #1C1917 !important;
    }

    /* All Headings */
    h1, h2, h3, h4, h5, h6,
    [data-testid="stMarkdownContainer"] h1,
    [data-testid="stMarkdownContainer"] h2,
    [data-testid="stMarkdownContainer"] h3,
    [data-testid="stMarkdownContainer"] h4 {
        color: #1C1917 !important;
        font-weight: 700 !important;
    }

    /* Captions */
    [data-testid="stCaptionContainer"] p, .stCaption, small {
        color: #57534E !important;
    }

    /* Streamlit Tabs (Fixes 'Create Account' invisible tab in Auth) */
    div[data-testid="stTabs"] button[data-baseweb="tab"] {
        color: #44403C !important;
        font-weight: 600 !important;
        font-size: 0.95rem !important;
        background-color: transparent !important;
        border-bottom: 2.5px solid transparent !important;
        padding: 0.65rem 1.15rem !important;
        opacity: 1 !important;
    }
    div[data-testid="stTabs"] button[data-baseweb="tab"]:hover {
        color: #9A4A27 !important;
    }
    div[data-testid="stTabs"] button[data-baseweb="tab"][aria-selected="true"] {
        color: #9A4A27 !important;
        font-weight: 700 !important;
        border-bottom-color: #9A4A27 !important;
    }
    div[data-testid="stTabs"] button[data-baseweb="tab"] p,
    div[data-testid="stTabs"] button[data-baseweb="tab"] span,
    div[data-testid="stTabs"] button[data-baseweb="tab"] div {
        color: inherit !important;
        font-weight: inherit !important;
        opacity: 1 !important;
    }

    /* Radio Options (Fixes MCQ option choices disappearing) */
    div[role="radiogroup"] {
        display: flex !important;
        flex-direction: column !important;
        gap: 6px !important;
    }
    div[role="radiogroup"] > label {
        background: #FFFFFF !important;
        border: 1.5px solid #D8CFC4 !important;
        border-radius: 9px !important;
        padding: 0.65rem 1rem !important;
        margin-bottom: 0.35rem !important;
        width: 100% !important;
        cursor: pointer !important;
        transition: all 0.15s ease !important;
    }
    div[role="radiogroup"] > label:hover {
        border-color: #9A4A27 !important;
        background: #FAF7F2 !important;
    }
    div[role="radiogroup"] label div[data-testid="stMarkdownContainer"] p,
    div[role="radiogroup"] label span,
    div[role="radiogroup"] label div {
        color: #1C1917 !important;
        font-weight: 500 !important;
        font-size: 0.95rem !important;
        line-height: 1.5 !important;
        opacity: 1 !important;
    }

    /* Text Inputs, Passwords, Selectboxes & Labels */
    label[data-testid="stWidgetLabel"],
    label[data-testid="stWidgetLabel"] p,
    label[data-testid="stWidgetLabel"] span {
        color: #1C1917 !important;
        font-weight: 600 !important;
        font-size: 0.88rem !important;
        margin-bottom: 0.25rem !important;
    }
    div[data-baseweb="input"], div[data-baseweb="base-input"] {
        background-color: #FFFFFF !important;
        border: 1.5px solid #D8CFC4 !important;
        border-radius: 8px !important;
        color: #1C1917 !important;
    }
    div[data-baseweb="input"]:focus-within {
        border-color: #9A4A27 !important;
        box-shadow: 0 0 0 1px #9A4A27 !important;
    }
    div[data-baseweb="input"] input {
        color: #1C1917 !important;
        background-color: #FFFFFF !important;
        -webkit-text-fill-color: #1C1917 !important;
        font-size: 0.92rem !important;
    }
    div[data-baseweb="input"] input::placeholder {
        color: #8C827A !important;
        -webkit-text-fill-color: #8C827A !important;
    }
    div[data-baseweb="select"] > div {
        background-color: #FFFFFF !important;
        border: 1.5px solid #D8CFC4 !important;
        border-radius: 8px !important;
        color: #1C1917 !important;
    }
    div[data-baseweb="select"] * {
        color: #1C1917 !important;
    }

    /* Chat Messages */
    div[data-testid="stChatMessage"] {
        background-color: #FFFFFF !important;
        border: 1px solid #E5DFD5 !important;
        border-radius: 12px !important;
        padding: 0.95rem 1.2rem !important;
        margin-bottom: 0.65rem !important;
    }

    /* Footer */
    .creamy-footer {
        margin-top: 2.5rem;
        padding-top: 1.1rem;
        border-top: 1px solid #E5DFD5;
        display: flex;
        justify-content: space-between;
        align-items: center;
        flex-wrap: wrap;
        gap: 10px;
        font-size: 0.8rem;
        color: #78716C;
    }
</style>
"""


@st.cache_data(show_spinner=False)
def _read_b64_cached(abs_path: str, mtime_ns: int) -> str:
    p = Path(abs_path)
    raw = p.read_bytes()
    ext = p.suffix.lower().lstrip(".") or "png"
    mime = "jpeg" if ext in ("jpg", "jpeg") else ext
    return f"data:image/{mime};base64,{base64.b64encode(raw).decode('ascii')}"


def _load_asset_b64(filename: str) -> str | None:
    img_path = ASSETS_DIR / filename
    if not img_path.exists():
        return None
    return _read_b64_cached(str(img_path), img_path.stat().st_mtime_ns)


def render_ai_artwork(
    filename: str,
    max_height_px: int = 245,
    fallback_svg: str = "",
    badge: str = "",
    caption: str = "",
):
    """Renders an editorial photograph cleanly inside a crisp hairline frame with optional caption below."""
    data_uri = _load_asset_b64(filename)
    if data_uri:
        meta_title, _ = ARTWORK_META.get(filename, ("", ""))
        sub_cap = caption or meta_title
        cap_html = f'<div class="photo-caption">{html.escape(tr(sub_cap))}</div>' if sub_cap else ""
        st.markdown(
            f'<div class="ai-art-frame">'
            f'<img src="{data_uri}" alt="{APP_NAME}" style="max-height:{max_height_px}px; width:100%; object-fit:cover;">'
            f'</div>{cap_html}',
            unsafe_allow_html=True,
        )
    elif fallback_svg:
        st.markdown(fallback_svg, unsafe_allow_html=True)


def render_header(current_page: str = "Home"):
    """Renders a clean, human-crafted editorial top header and horizontal navigation bar."""
    st.markdown(CUSTOM_CSS, unsafe_allow_html=True)

    if "user" not in st.session_state:
        st.session_state.user = None

    curr_lang = get_lang()
    lang_keys = list(SUPPORTED_LANGUAGES.keys())

    b_col, l_col = st.columns([3.7, 1.3], vertical_alignment="center")
    user = st.session_state.user
    user_display = user["user_id"] if user else ui("guest_learner")

    with b_col:
        st.markdown(
            f'<div class="creamy-nav">'
            f'<div style="display:flex; align-items:center; gap:12px;">'
            f'{BRAND_MARK_SVG}'
            f'<div>'
            f'<div class="creamy-title">{APP_NAME}</div>'
            f'<div style="font-size: 0.8rem; color: #78716C; margin-top: 1px;">{ui("nav_subtitle")}</div>'
            f'</div>'
            f'</div>'
            f'<div style="display: flex; align-items: center; gap: 8px; flex-wrap: wrap;">'
            f'<span class="agent-pill">{ui("agent_active")}</span>'
            f'<span class="user-pill">{html.escape(user_display)}</span>'
            f'</div>'
            f'</div>',
            unsafe_allow_html=True,
        )
    with l_col:
        sel_c, gw_c = st.columns([3.3, 1.1], vertical_alignment="bottom")
        with sel_c:
            picked_lang = st.selectbox(
                "Language",
                lang_keys,
                index=lang_keys.index(curr_lang),
                format_func=lambda k: SUPPORTED_LANGUAGES[k],
                key=f"lang_sel_{current_page}",
                label_visibility="collapsed",
            )
            if picked_lang != curr_lang:
                st.session_state.lang = picked_lang
                st.session_state.language_chosen = True
                st.rerun()
        with gw_c:
            if st.button("Langs", key=f"open_gw_{current_page}", help="Switch language edition", use_container_width=True):
                st.session_state.language_chosen = False
                if current_page == "Home":
                    st.rerun()
                else:
                    st.switch_page("app.py")

    st.markdown("<div style='height: 6px;'></div>", unsafe_allow_html=True)

    cols = st.columns([0.85, 1.15, 1.15, 1.05, 0.95, 1.0, 0.95, 1.05])
    with cols[0]:
        st.page_link("app.py", label=ui("nav_home"), use_container_width=True)
    with cols[1]:
        st.page_link("pages/1_Adaptive_Quiz.py", label=ui("nav_quiz"), use_container_width=True)
    with cols[2]:
        st.page_link("pages/6_Study_Studio.py", label=ui("nav_study"), use_container_width=True)
    with cols[3]:
        st.page_link("pages/7_Coding_Lab.py", label=ui("nav_code"), use_container_width=True)
    with cols[4]:
        st.page_link("pages/5_AI_Tutor_Chat.py", label=ui("nav_tutor"), use_container_width=True)
    with cols[5]:
        st.page_link("pages/2_Student_Dashboard.py", label=ui("nav_dossier"), use_container_width=True)
    with cols[6]:
        st.page_link("pages/4_Learning_History.py", label=ui("nav_history"), use_container_width=True)
    with cols[7]:
        if user:
            if st.button(ui("nav_signout"), key=f"nav_logout_{current_page}", use_container_width=True):
                st.session_state.user = None
                st.session_state.current_quiz = None
                st.session_state.quiz_evaluation = None
                st.switch_page("app.py")
        else:
            st.page_link("pages/3_Authentication.py", label=ui("nav_signin"), use_container_width=True)

    st.markdown(
        "<hr style='border: 0; border-top: 1px solid #E5DFD5; margin: 0.35rem 0 1.35rem 0;'>",
        unsafe_allow_html=True,
    )


def render_footer():
    """Renders a restrained editorial footer across all pages."""
    left_txt = tr("Built with AWS Strands Agents SDK & DecisionModel · Madurai Edition")
    right_txt = tr("Adaptive Assessments · Code Verification · Multilingual Curriculum")
    st.markdown(
        f'<div class="creamy-footer">'
        f'<div><strong>{APP_NAME}</strong> &nbsp;·&nbsp; {left_txt}</div>'
        f'<div>{right_txt}</div>'
        f'</div>',
        unsafe_allow_html=True,
    )
