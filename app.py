"""
VidyaVerse - Curriculum Overview & Assessment Launcher
"""

import os
import sys

os.environ["OPENBLAS_NUM_THREADS"] = "1"
os.environ["MKL_NUM_THREADS"] = "1"
os.environ["NUMEXPR_NUM_THREADS"] = "1"
os.environ["OMP_NUM_THREADS"] = "1"

import streamlit as st

sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from components.i18n import get_lang, tr
from components.language_gateway import LANGUAGE_GATEWAY_CARDS, render_language_gateway
from components.navbar import APP_NAME, CURRICULUM_CATALOG, render_ai_artwork, render_footer, render_header
from database.db_manager import get_user_analytics, init_db
from agent import agent_decide_next_step

st.set_page_config(
    page_title=f"{APP_NAME} | Technical Learning Studio",
    layout="wide",
)

init_db()

if st.query_params.get("view") == "home":
    st.session_state.language_chosen = True
if st.query_params.get("lang") in ("en", "ta", "hi", "te", "ml", "kn"):
    st.session_state.lang = st.query_params["lang"]

# Language Selection Gateway displayed on initial arrival
if not st.session_state.get("language_chosen", False):
    render_language_gateway()
    st.stop()

render_header("Home")

user = st.session_state.get("user", None)

# ---------------------------------------------------------
# Editorial Hero Section
# ---------------------------------------------------------
st.markdown('<div class="hero-card">', unsafe_allow_html=True)
hero_left, hero_right = st.columns([1.35, 1], vertical_alignment="center")
with hero_left:
    eyebrow = tr("Engineering & Cloud Practice")
    headline = tr("Master Computer Science & Cloud Architecture")
    sub_desc = tr(
        f"{APP_NAME} combines non-repeating adaptive assessments, live Python and SQL sandboxes, "
        "active-recall study decks, and structured doubt clearance across 6 core technical domains."
    )
    st.markdown(
        f"""
        <div class="hero-eyebrow">{eyebrow}</div>
        <div class="hero-headline">{headline}</div>
        <div class="hero-sub">{sub_desc}</div>
        """,
        unsafe_allow_html=True,
    )
    st.markdown("<div style='height: 10px;'></div>", unsafe_allow_html=True)
    cta1, cta2, cta3, cta4 = st.columns(4)
    with cta1:
        if st.button(tr("Start Assessment"), type="primary", use_container_width=True):
            st.session_state.quiz_step = 1
            st.switch_page("pages/1_Adaptive_Quiz.py")
    with cta2:
        if st.button(tr("Code Lab"), use_container_width=True):
            st.switch_page("pages/7_Coding_Lab.py")
    with cta3:
        if st.button(tr("Study Notes"), use_container_width=True):
            st.switch_page("pages/6_Study_Studio.py")
    with cta4:
        if user is None:
            if st.button(tr("Sign In"), use_container_width=True):
                st.switch_page("pages/3_Authentication.py")
        else:
            if st.button(tr("My Progress"), use_container_width=True):
                st.switch_page("pages/2_Student_Dashboard.py")

with hero_right:
    active_lang = get_lang()
    active_card = next((c for c in LANGUAGE_GATEWAY_CARDS if c["code"] == active_lang), LANGUAGE_GATEWAY_CARDS[0])
    hero_img = "madurai_meenakshi_dawn.jpg" if active_lang in ("ta", "en") else active_card["image"]
    render_ai_artwork(hero_img, max_height_px=240, caption="Madurai Architectural Heritage")

st.markdown("</div>", unsafe_allow_html=True)

# ---------------------------------------------------------
# Personalized Resume Banner (When Signed In)
# ---------------------------------------------------------
if user:
    analytics = get_user_analytics(user["email"])
    recent_q = analytics["quiz_history"][0] if analytics["quiz_history"] else None
    decision = agent_decide_next_step(analytics, recent_q)

    with st.container(border=True):
        b_col1, b_col2 = st.columns([3, 1.1], vertical_alignment="center")
        with b_col1:
            welcome_txt = tr(f"Welcome back, {user['user_id']}!")
            avg_txt = tr("Average Mastery")
            streak_txt = tr("Day Streak")
            solved_txt = tr("Questions Solved")
            rec_topic_disp = tr(decision["recommended_topic"])
            rec_diff_disp = tr(decision["next_difficulty"])
            rec_body = tr(decision["recommendation"])
            st.markdown(
                f"""
                <div style="display:flex; align-items:center; gap:8px; flex-wrap:wrap; margin-bottom:4px;">
                    <span style="font-weight:600; font-size:1.02rem; color:#1C1917;">{welcome_txt}</span>
                    <span class="pista-badge">{avg_txt}: {analytics['average_score']}%</span>
                    <span class="almond-badge">{analytics['streak_days']} {streak_txt}</span>
                    <span class="almond-badge">{analytics['distinct_questions_seen']} {solved_txt}</span>
                </div>
                <div style="font-size:0.9rem; color:#57534E; margin-top:2px;">
                    <strong>{tr('Recommended Target')} ({rec_topic_disp} · {rec_diff_disp}):</strong> {rec_body}
                </div>
                """,
                unsafe_allow_html=True,
            )
        with b_col2:
            if st.button(tr("Resume Practice"), type="primary", use_container_width=True):
                st.session_state.selected_topic = decision["recommended_topic"]
                st.session_state.selected_difficulty = decision["next_difficulty"]
                st.session_state.current_quiz = None
                st.session_state.quiz_evaluation = None
                st.session_state.quiz_step = 2
                st.switch_page("pages/1_Adaptive_Quiz.py")

# ---------------------------------------------------------
# Feature Pillars
# ---------------------------------------------------------
st.markdown("<div style='height: 4px;'></div>", unsafe_allow_html=True)
vis1, vis2, vis3 = st.columns(3)
visual_cards = [
    (
        "madurai_vaigai_night_tech.jpg",
        "Guided Doubt Clearance",
        "Ask questions across algorithms, system trade-offs, and cloud architecture in 4 teaching styles.",
        "Open Tutor",
        "pages/5_AI_Tutor_Chat.py",
    ),
    (
        "madurai_thirumalai_sangam.jpg",
        "Notes & 7-Day Roadmaps",
        "Generate active-recall study cards from your own notes and follow calibrated weekly study schedules.",
        "Open Notes",
        "pages/6_Study_Studio.py",
    ),
    (
        "coding_lab_sandbox.jpg",
        "Live Code Verification",
        "Write real Python functions and SQL queries evaluated instantaneously against unit test suites.",
        "Open Lab",
        "pages/7_Coding_Lab.py",
    ),
]
for col, (img_name, v_title, v_desc, v_btn, v_page) in zip([vis1, vis2, vis3], visual_cards):
    with col:
        with st.container(border=True):
            render_ai_artwork(img_name, max_height_px=150)
            st.markdown(
                f"""
                <div class="feature-title" style="margin-top:0.75rem;">{tr(v_title)}</div>
                <div class="feature-desc" style="min-height:48px; margin-bottom:0.75rem;">{tr(v_desc)}</div>
                """,
                unsafe_allow_html=True,
            )
            if st.button(tr(v_btn), key=f"vis_{img_name}", use_container_width=True):
                st.switch_page(v_page)

st.markdown("<div style='height: 14px;'></div>", unsafe_allow_html=True)

# ---------------------------------------------------------
# Curriculum Tracks
# ---------------------------------------------------------
st.markdown(
    f"""
    <div style="display:flex; justify-content:space-between; align-items:flex-end; flex-wrap:wrap; margin-bottom: 0.85rem;">
        <div>
            <h3 style="font-family: 'Source Serif 4', Georgia, serif; color: #1C1917; letter-spacing: -0.01em; margin: 0;">
                {tr('Curriculum Tracks')}
            </h3>
            <div style="color: #78716C; font-size: 0.9rem; margin-top: 2px;">
                {tr('Select any subject below to launch a targeted assessment round.')}
            </div>
        </div>
        <span class="almond-badge">{tr('6 Core Domains')}</span>
    </div>
    """,
    unsafe_allow_html=True,
)

for row_start in range(0, len(CURRICULUM_CATALOG), 3):
    row_cols = st.columns(3)
    for idx, item in enumerate(CURRICULUM_CATALOG[row_start : row_start + 3]):
        with row_cols[idx]:
            with st.container(border=True):
                st.markdown(
                    f"""
                    <div style="display:flex; justify-content:space-between; align-items:center; margin-bottom:0.6rem;">
                        <span class="domain-code-box">{item.get('code', str(row_start + idx + 1).zfill(2))}</span>
                        <span class="almond-badge">{tr(item['tag'])}</span>
                    </div>
                    <div class="feature-title">{tr(item['topic'])}</div>
                    <div class="feature-desc" style="min-height: 44px; margin-bottom: 0.85rem;">{tr(item['desc'])}</div>
                    """,
                    unsafe_allow_html=True,
                )
                if st.button(
                    f"{tr('Practice Domain')} →",
                    key=f"home_topic_{row_start + idx}",
                    use_container_width=True,
                ):
                    st.session_state.selected_topic = item["topic"]
                    st.session_state.current_quiz = None
                    st.session_state.quiz_evaluation = None
                    st.session_state.quiz_step = 1
                    st.switch_page("pages/1_Adaptive_Quiz.py")

render_footer()
