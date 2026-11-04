"""
VidyaVerse - Study Notes, Interactive Flashcards & 7-Day Study Plan
"""

import html
import os
import sys

os.environ["OPENBLAS_NUM_THREADS"] = "1"
os.environ["MKL_NUM_THREADS"] = "1"

import streamlit as st

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from components.i18n import get_lang, tr
from components.navbar import APP_NAME, render_footer, render_header
from database.db_manager import get_user_analytics, init_db
from agent import agent_create_roadmap, agent_create_study_pack

st.set_page_config(
    page_title=f"Study Notes | {APP_NAME}",
    layout="wide",
)

init_db()
render_header("StudyHub")

user = st.session_state.get("user", None)
analytics = get_user_analytics(user["email"]) if user else {"weak_topics": [], "average_score": 0.0}

SAMPLE_NOTES = """Binary Search: Divides a sorted array in half on every step, achieving O(log n) lookup time.
Hash Table: Stores key-value pairs using a hash function for O(1) average insertion and lookup.
Recursion: A technique where a function calls itself with a smaller input until reaching a base case.
Dynamic Programming: Optimizes overlapping subproblems by caching intermediate results via memoization or tabulation.
BFS Traversal: Explores graph vertices level-by-level using a FIFO Queue data structure."""

st.markdown(
    f"""
    <h2 style="font-family: 'Source Serif 4', Georgia, serif; color: #1C1917; letter-spacing: -0.02em; margin-bottom: 0.25rem;">
        {tr('Study Notes & Structured Roadmaps')}
    </h2>
    <p style="color: #57534E; font-size: 0.94rem; margin-bottom: 1rem;">
        {tr('Convert your lecture notes into interactive study cards and practice quizzes, or follow a 7-day preparation schedule.')}
    </p>
    """,
    unsafe_allow_html=True,
)

tab_notes, tab_roadmap = st.tabs(
    [tr("Flashcards From Notes"), tr("7-Day Study Plan")]
)

# =========================================================
# TAB 1: Notes-to-Flashcards & Custom Quiz
# =========================================================
with tab_notes:
    if "notes_input_val" not in st.session_state:
        st.session_state.notes_input_val = ""
    if "custom_study_pack" not in st.session_state:
        st.session_state.custom_study_pack = None
    if "flipped_flashcards" not in st.session_state:
        st.session_state.flipped_flashcards = set()

    with st.container(border=True):
        top_c1, top_c2 = st.columns([2.6, 1], vertical_alignment="bottom")
        with top_c1:
            pack_title = st.text_input(tr("Deck Title"), value="Core Algorithms & Data Structures")
        with top_c2:
            if st.button(tr("Insert Sample Notes"), use_container_width=True):
                st.session_state.notes_input_val = SAMPLE_NOTES
                st.rerun()

        uploaded_file = st.file_uploader(tr("Upload .txt or .md notes (optional)"), type=["txt", "md"])
        if uploaded_file is not None:
            st.session_state.notes_input_val = uploaded_file.read().decode("utf-8", errors="ignore")

        notes_text = st.text_area(
            tr("Paste Lecture Notes or Definitions (one concept per line: Term: Explanation)"),
            value=st.session_state.notes_input_val,
            height=145,
            placeholder="REST Architecture: Stateless client-server communication over HTTP...",
        )

        if st.button(tr("Generate Study Deck & Quiz"), type="primary", use_container_width=True):
            pack = agent_create_study_pack(notes_text=notes_text, title=pack_title)
            if "error" in pack:
                st.warning(tr(pack["error"]))
            else:
                st.session_state.notes_input_val = notes_text
                st.session_state.custom_study_pack = pack
                st.session_state.flipped_flashcards = set()

    if st.session_state.custom_study_pack:
        pack = st.session_state.custom_study_pack
        st.markdown("<div style='height: 10px;'></div>", unsafe_allow_html=True)

        hdr1, hdr2 = st.columns([2.2, 1.2], vertical_alignment="center")
        with hdr1:
            st.markdown(f"#### {tr('Study Cards')} — *{tr(pack['title'])}*")
            st.caption(tr("Use the Reveal / Hide button on each card to practice active recall."))
        with hdr2:
            if pack.get("quiz"):
                if st.button(tr("Take Quiz From These Notes"), type="primary", use_container_width=True):
                    st.session_state.current_quiz = {
                        "topic": pack["title"],
                        "difficulty": "Custom Notes",
                        "count": len(pack["quiz"]),
                        "questions": pack["quiz"],
                        "guaranteed_distinct": True,
                    }
                    st.session_state.quiz_answers = {}
                    st.session_state.quiz_evaluation = None
                    st.session_state.quiz_step = 2
                    st.session_state.quiz_run_id = st.session_state.get("quiz_run_id", 0) + 1
                    st.switch_page("pages/1_Adaptive_Quiz.py")

        cards = pack.get("flashcards", [])
        for i in range(0, len(cards), 2):
            f_cols = st.columns(2)
            for j, card in enumerate(cards[i : i + 2]):
                card_idx = i + j
                is_flipped = card_idx in st.session_state.flipped_flashcards
                front_safe = html.escape(tr(card["front"]))
                back_safe = html.escape(tr(card["back"]))
                with f_cols[j]:
                    with st.container(border=True):
                        if not is_flipped:
                            st.markdown(
                                f"""
                                <div style="min-height:110px; display:flex; flex-direction:column; justify-content:space-between;">
                                    <div style="font-size:0.74rem; font-weight:600; color:#9A4A27; text-transform:uppercase; letter-spacing:0.06em;">
                                        {tr('Card')} {card_idx + 1} · {tr('Term')}
                                    </div>
                                    <div style="font-size:1.08rem; font-weight:600; color:#1C1917; margin:0.65rem 0;">
                                        {front_safe}
                                    </div>
                                </div>
                                """,
                                unsafe_allow_html=True,
                            )
                            if st.button(tr("Reveal Answer"), key=f"flip_fc_{card_idx}", use_container_width=True):
                                st.session_state.flipped_flashcards.add(card_idx)
                                st.rerun()
                        else:
                            st.markdown(
                                f"""
                                <div style="min-height:110px; display:flex; flex-direction:column; justify-content:space-between; background:#F6FAF7; border-radius:8px; padding:0.75rem 0.9rem; margin-bottom:0.5rem; border:1px solid #D4E6DA;">
                                    <div style="font-size:0.74rem; font-weight:600; color:#22543D; text-transform:uppercase; letter-spacing:0.06em;">
                                        {tr('Card')} {card_idx + 1} · {tr('Definition')}
                                    </div>
                                    <div style="font-size:0.93rem; color:#1C1917; line-height:1.5; margin:0.45rem 0;">
                                        {back_safe}
                                    </div>
                                </div>
                                """,
                                unsafe_allow_html=True,
                            )
                            if st.button(tr("Show Term"), key=f"flip_fc_{card_idx}", use_container_width=True):
                                st.session_state.flipped_flashcards.discard(card_idx)
                                st.rerun()

# =========================================================
# TAB 2: 7-Day Study Plan
# =========================================================
with tab_roadmap:
    with st.container(border=True):
        r_c1, r_c2 = st.columns([2.2, 1], vertical_alignment="bottom")
        goals_list = [
            "Technical Interview & Placement Readiness",
            "AI & Machine Learning Engineering",
            "Full-Stack Cloud & Database Architecture",
        ]
        with r_c1:
            active_lang = get_lang()
            goal_choice = st.selectbox(
                tr("Target Focus Area"),
                goals_list,
                format_func=lambda g, _lg=active_lang: tr(g, _lg),
            )
        with r_c2:
            st.markdown(
                f"<div class='almond-badge' style='padding:0.48rem 0.9rem; width:100%; text-align:center;'>{tr('Current Average')}: {analytics['average_score']}%</div>",
                unsafe_allow_html=True,
            )

    roadmap = agent_create_roadmap(
        weak_topics=analytics.get("weak_topics", []),
        average_score=analytics.get("average_score", 0.0),
        goal=goal_choice,
    )

    if "roadmap_done" not in st.session_state:
        st.session_state.roadmap_done = {}

    done_count = sum(1 for d in roadmap["days"] if st.session_state.roadmap_done.get(d["day"], False))
    st.progress(
        done_count / 7.0,
        text=f"{tr('Weekly Schedule')}: {done_count} / 7 {tr('completed')}",
    )

    for idx, item in enumerate(roadmap["days"]):
        with st.container(border=True):
            d1, d2, d3 = st.columns([0.65, 3.0, 1.15], vertical_alignment="center")
            with d1:
                checked = st.checkbox(
                    tr(item["day"]),
                    value=st.session_state.roadmap_done.get(item["day"], False),
                    key=f"chk_rm_{idx}",
                )
                st.session_state.roadmap_done[item["day"]] = checked
            with d2:
                st.markdown(
                    f"""
                    <div style="font-weight:600; color:#1C1917; font-size:0.97rem;">
                        {tr(item['title'])} <span class="almond-badge" style="margin-left:6px;">{tr(item['difficulty'])}</span>
                    </div>
                    <div style="font-size:0.88rem; color:#57534E; margin-top:3px;">{tr(item['task'])}</div>
                    """,
                    unsafe_allow_html=True,
                )
            with d3:
                if st.button(tr(item["action_label"]), key=f"rm_go_{idx}", use_container_width=True):
                    st.session_state.selected_topic = item["domain"]
                    st.session_state.selected_difficulty = item["difficulty"]
                    st.session_state.current_quiz = None
                    st.session_state.quiz_evaluation = None
                    st.session_state.quiz_step = 1
                    st.switch_page(item["action_page"])

render_footer()
