"""
VidyaVerse - Student Progress & Learning Analytics Ledger
"""

import datetime
import os
import sys

os.environ["OPENBLAS_NUM_THREADS"] = "1"
os.environ["MKL_NUM_THREADS"] = "1"
os.environ["NUMEXPR_NUM_THREADS"] = "1"
os.environ["OMP_NUM_THREADS"] = "1"

import pandas as pd
import streamlit as st

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from components.i18n import get_lang, tr
from components.navbar import APP_NAME, render_ai_artwork, render_footer, render_header
from components.certificate import build_certificate_html
from database.db_manager import (
    get_topic_bank_progress,
    get_user_analytics,
    init_db,
    update_user_avatar,
)
from agent import agent_analyze_student, agent_decide_next_step

st.set_page_config(
    page_title=f"Progress | {APP_NAME}",
    layout="wide",
)

init_db()
render_header("Dashboard")

active_lang = get_lang()
user = st.session_state.get("user", None)

if not user:
    g_left, g_right = st.columns([1.35, 1], vertical_alignment="center")
    with g_left:
        st.markdown(
            f"""
            <div class="hero-card" style="padding: 2.2rem 2rem; margin-bottom: 0;">
                <div class="hero-eyebrow">{tr('Student Progress Ledger')}</div>
                <h2 style="font-family: 'Source Serif 4', Georgia, serif; color: #1C1917; letter-spacing: -0.02em; margin-bottom: 0.6rem;">
                    {tr('Track Your Subject Mastery & Transcripts')}
                </h2>
                <p style="color: #57534E; line-height: 1.6; margin-bottom: 1.2rem; font-size: 0.94rem;">
                    {tr('Sign in to view your subject accuracy matrix, study consistency, completed non-repeating question coverage, and earned mastery certificates.')}
                </p>
            </div>
            """,
            unsafe_allow_html=True,
        )
        st.markdown("<div style='height: 10px;'></div>", unsafe_allow_html=True)
        if st.button(tr("Sign In / Create Account"), type="primary", use_container_width=True):
            st.switch_page("pages/3_Authentication.py")
    with g_right:
        render_ai_artwork("madurai_meenakshi_dawn.jpg", max_height_px=240, caption="Madurai Architectural Heritage")
else:
    analytics = get_user_analytics(user["email"])
    progress_report = agent_analyze_student(analytics)
    recent_quiz = analytics["quiz_history"][0] if analytics["quiz_history"] else None
    decision = agent_decide_next_step(analytics, recent_quiz)

    avg_s = analytics["average_score"]
    if analytics["total_quizzes"] >= 5 and avg_s >= 88:
        tier_label = tr("Distinction")
    elif avg_s >= 82:
        tier_label = tr("Advanced")
    elif avg_s >= 65:
        tier_label = tr("Proficient")
    else:
        tier_label = tr("Developing")

    with st.container(border=True):
        id_col, av_col = st.columns([3.4, 1.2], vertical_alignment="center")
        with id_col:
            joined_date = str(user.get("created_at", ""))[:10] or tr("Active Member")
            st.markdown(
                f"""
                <div style="display:flex; align-items:center; gap:14px; flex-wrap:wrap;">
                    <div style="width:52px; height:52px; border-radius:10px; background:#F5F1EB; border:1px solid #E5DFD5; display:flex; align-items:center; justify-content:center; font-weight:700; color:#7C3B1E; font-size:1.1rem;">
                        {user.get('user_id', 'S')[:2].upper()}
                    </div>
                    <div>
                        <div style="display:flex; align-items:center; gap:8px; flex-wrap:wrap;">
                            <h2 style="font-family:'Source Serif 4', Georgia, serif; color:#1C1917; margin:0; font-size:1.45rem; letter-spacing:-0.01em;">
                                {user['user_id']}
                            </h2>
                            <span class="pista-badge">{tier_label}</span>
                            <span class="almond-badge">{analytics['xp_points']} XP</span>
                        </div>
                        <div style="color:#78716C; font-size:0.84rem; margin-top:3px;">
                            {user['email']} &nbsp;·&nbsp; {tr('Member Since')} {joined_date} &nbsp;·&nbsp; {tr('Status')}: <strong>{tr(progress_report['overall_status'])}</strong>
                        </div>
                    </div>
                </div>
                """,
                unsafe_allow_html=True,
            )
        with av_col:
            st.markdown(
                f"<div style='text-align:right;'><span class='almond-badge'>{tr('Verified Account')}</span></div>",
                unsafe_allow_html=True,
            )

    st.markdown("<div style='height: 8px;'></div>", unsafe_allow_html=True)

    k1, k2, k3, k4, k5 = st.columns(5)
    kpis = [
        (str(analytics["total_quizzes"]), tr("Completed Quizzes")),
        (f"{analytics['average_score']}%", tr("Average Score")),
        (f"{analytics['best_score']}%", tr("Top Score")),
        (f"{analytics['streak_days']} Days", tr("Active Streak")),
        (f"{analytics['distinct_questions_seen']} / {analytics['bank_total']}", tr("Questions Explored")),
    ]
    for col, (val, lbl) in zip([k1, k2, k3, k4, k5], kpis):
        with col:
            st.markdown(
                f"""
                <div class="metric-box">
                    <div class="metric-value">{val}</div>
                    <div class="metric-label">{lbl}</div>
                </div>
                """,
                unsafe_allow_html=True,
            )

    st.markdown(
        f"""
        <div class="decider-banner">
            <div style="display: flex; align-items: center; justify-content: space-between; flex-wrap: wrap; gap: 8px;">
                <div style="font-weight: 600; color: #1C1917; font-size: 0.98rem;">
                    {tr('Next Recommended Milestone')}: {tr(decision['headline'])}
                </div>
                <div style="display:flex; gap:6px; flex-wrap:wrap;">
                    <span class="almond-badge">{tr(decision['recommended_topic'])}</span>
                    <span class="pista-badge">{tr('Target')}: {tr(decision['next_difficulty'])}</span>
                </div>
            </div>
            <div style="color: #57534E; margin-top: 6px; font-size: 0.9rem;">
                {tr(decision['recommendation'])}
            </div>
        </div>
        """,
        unsafe_allow_html=True,
    )

    act1, act2 = st.columns([2, 1])
    with act1:
        if st.button(
            f"{tr('Start Prescribed Round')}: {tr(decision['recommended_topic'])} ({tr(decision['next_difficulty'])})",
            type="primary",
            use_container_width=True,
        ):
            st.session_state.selected_topic = decision["recommended_topic"]
            st.session_state.selected_difficulty = decision["next_difficulty"]
            st.session_state.current_quiz = None
            st.session_state.quiz_evaluation = None
            st.session_state.quiz_step = 2
            st.switch_page("pages/1_Adaptive_Quiz.py")
    with act2:
        if st.button(tr("View Full Transcript"), use_container_width=True):
            st.switch_page("pages/4_Learning_History.py")

    st.markdown("<div style='height: 12px;'></div>", unsafe_allow_html=True)

    col_chart, col_diag = st.columns([1.55, 1])

    with col_chart:
        with st.container(border=True):
            st.markdown(f"#### {tr('Subject Mastery Matrix')}")
            if analytics["topic_mastery"]:
                localized_rows = [
                    {
                        "Subject": tr(r["topic"]),
                        "Mastery (%)": r["mastery_score"],
                    }
                    for r in analytics["topic_mastery"]
                ]
                df_mastery = pd.DataFrame(localized_rows)
                st.bar_chart(df_mastery.set_index("Subject")["Mastery (%)"], color="#9A4A27")

                st.markdown(f"##### {tr('Topic Breakdown')}")
                for row in sorted(analytics["topic_mastery"], key=lambda x: x["mastery_score"], reverse=True):
                    score_val = float(row["mastery_score"])
                    badge_cls = "pista-badge" if score_val >= 70 else "terracotta-badge"
                    st.markdown(
                        f"""
                        <div style="display:flex; justify-content:space-between; align-items:center; font-size:0.88rem; margin-top:6px;">
                            <strong>{tr(row['topic'])}</strong>
                            <span class="{badge_cls}">{score_val}% ({row['quizzes_taken']} {tr('rounds')})</span>
                        </div>
                        """,
                        unsafe_allow_html=True,
                    )
                    st.progress(min(max(score_val / 100.0, 0.0), 1.0))
            else:
                st.info(tr("Complete your first adaptive quiz to populate your Subject Mastery Matrix."))

        with st.container(border=True):
            st.markdown(f"#### {tr('Non-Repeating Question Bank Exploration')}")
            for b_row in get_topic_bank_progress(user["email"]):
                st.markdown(
                    f"""
                    <div style="display:flex; justify-content:space-between; font-size:0.84rem; color:#44403C; margin-top:4px;">
                        <span>{tr(b_row['topic'])}</span>
                        <span><strong>{b_row['seen']} / {b_row['total']}</strong> ({b_row['pct']}%)</span>
                    </div>
                    """,
                    unsafe_allow_html=True,
                )
                st.progress(min(max(b_row["pct"] / 100.0, 0.0), 1.0))

    with col_diag:
        with st.container(border=True):
            st.markdown(f"#### {tr('Diagnostics & Recommendations')}")
            st.caption(tr(progress_report["study_advice"]))

            st.markdown(f"##### {tr('Strong Domains (70% and above)')}")
            if analytics["strong_topics"]:
                pills_html = " ".join(
                    f"<span class='pista-badge' style='margin:3px 4px 3px 0;'>{tr(t)}</span>"
                    for t in analytics["strong_topics"]
                )
                st.markdown(pills_html, unsafe_allow_html=True)
            else:
                st.caption(tr("Score >= 70% in a domain to earn Strong Domain mastery."))

            st.markdown("<div style='height: 10px;'></div>", unsafe_allow_html=True)
            st.markdown(f"##### {tr('Priority Review (under 70%)')}")
            if analytics["weak_topics"]:
                weak_html = " ".join(
                    f"<span class='terracotta-badge' style='margin:3px 4px 3px 0;'>{tr(t)}</span>"
                    for t in analytics["weak_topics"]
                )
                st.markdown(weak_html, unsafe_allow_html=True)
                st.markdown("<div style='height: 8px;'></div>", unsafe_allow_html=True)
                if st.button(tr("Discuss Weak Topics with Tutor"), use_container_width=True):
                    target_weak = analytics["weak_topics"][0]
                    st.session_state.prefill_tutor_prompt = (
                        f"Help me strengthen my fundamentals in {target_weak}. "
                        f"Summarize the 5 most important concepts and common pitfalls."
                    )
                    st.switch_page("pages/5_AI_Tutor_Chat.py")
            else:
                st.caption(tr("Zero flagged weak domains—keep up the strong momentum!"))

        with st.container(border=True):
            st.markdown(f"#### {tr('Mastery Certificates (80% and above)')}")
            certified = analytics.get("certified_topics", [])
            if certified:
                today_str = datetime.date.today().isoformat()
                for idx_c, c_row in enumerate(certified):
                    cert_doc = build_certificate_html(
                        student_name=user["user_id"],
                        topic=c_row["topic"],
                        score=c_row["mastery_score"],
                        date_str=today_str,
                        lang=active_lang,
                    )
                    st.download_button(
                        f"{tr('Certificate')} — {tr(c_row['topic'])} ({c_row['mastery_score']}%)",
                        data=cert_doc.encode("utf-8"),
                        file_name=f"{c_row['topic'].replace(' ', '_')}_Certificate.html",
                        mime="text/html",
                        key=f"dl_cert_{idx_c}",
                        use_container_width=True,
                    )
            else:
                st.caption(tr("Score 80% or above on any subject round to unlock a verifiable certificate."))

        with st.container(border=True):
            st.markdown(f"#### {tr('Practice Labs & Mistakes')}")
            st.markdown(
                f"""
                <div style="display:flex; justify-content:space-between; font-size:0.88rem; margin-bottom:8px;">
                    <span>{tr('Coding Solved')}: <strong>{len(analytics.get('coding_solved', []))} / 6</strong></span>
                    <span>{tr('Mistakes Pending')}: <strong>{analytics.get('mistakes_count', 0)}</strong></span>
                </div>
                """,
                unsafe_allow_html=True,
            )
            lb1, lb2 = st.columns(2)
            with lb1:
                if st.button(tr("Open Coding Lab"), use_container_width=True):
                    st.switch_page("pages/7_Coding_Lab.py")
            with lb2:
                if st.button(tr("Open Study Plan"), use_container_width=True):
                    st.switch_page("pages/6_Study_Studio.py")

render_footer()
