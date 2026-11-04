"""
VidyaVerse - Historical Assessment Transcripts & Audit Records
"""

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
from components.navbar import APP_NAME, render_footer, render_header
from database.db_manager import get_user_analytics, init_db

st.set_page_config(
    page_title=f"Transcripts | {APP_NAME}",
    layout="wide",
)

init_db()
render_header("History")

user = st.session_state.get("user", None)

if not user:
    st.markdown(
        f"""
        <div class="hero-card" style="padding: 2.2rem 2rem;">
            <div class="hero-eyebrow">{tr('Assessment Records')}</div>
            <h2 style="font-family: 'Source Serif 4', Georgia, serif; color: #1C1917; letter-spacing: -0.02em; margin-bottom: 0.5rem;">
                {tr('Chronological Audit Log')}
            </h2>
            <p style="color: #57534E; font-size: 0.94rem; max-width: 620px; line-height: 1.6; margin-bottom: 1.2rem;">
                {tr('Sign in to view your complete history of completed assessments, accuracy scores, and export CSV transcripts.')}
            </p>
        </div>
        """,
        unsafe_allow_html=True,
    )
    c1, c2, c3 = st.columns([1.2, 1.2, 1.2])
    with c1:
        if st.button(tr("Sign In to Account"), type="primary", use_container_width=True):
            st.switch_page("pages/3_Authentication.py")
else:
    analytics = get_user_analytics(user["email"])
    quizzes = analytics["quiz_history"]

    st.markdown(
        f"""
        <h2 style="font-family: 'Source Serif 4', Georgia, serif; color: #1C1917; letter-spacing: -0.02em; margin-bottom: 0.25rem;">
            {tr('Assessment History')} — {user['user_id']}
        </h2>
        <p style="color: #57534E; font-size: 0.93rem; margin-bottom: 1.2rem;">
            {tr('Chronological record of every assessment session recorded on your account.')}
        </p>
        """,
        unsafe_allow_html=True,
    )

    if not quizzes:
        with st.container(border=True):
            st.info(tr("No assessment records found. Complete an assessment round to begin your transcript."))
            if st.button(tr("Start Practice Assessment"), type="primary", use_container_width=True):
                st.session_state.quiz_step = 1
                st.switch_page("pages/1_Adaptive_Quiz.py")
    else:
        s1, s2, s3, s4 = st.columns(4)
        stats = [
            (str(analytics["total_quizzes"]), tr("Completed Sessions")),
            (str(analytics["total_questions_answered"]), tr("Questions Answered")),
            (f"{analytics['average_score']}%", tr("Overall Accuracy")),
            (f"{analytics['best_score']}%", tr("Highest Score")),
        ]
        for col, (val, lbl) in zip([s1, s2, s3, s4], stats):
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

        st.markdown("<div style='height: 12px;'></div>", unsafe_allow_html=True)

        with st.container(border=True):
            f_col1, f_col2, f_col3 = st.columns([1.6, 1.2, 1.2], vertical_alignment="bottom")
            distinct_topics = ["All Domains"] + sorted({q["topic"] for q in quizzes})
            distinct_diffs = ["All Tiers", "Easy", "Medium", "Hard"]
            active_lang = get_lang()
            with f_col1:
                sel_topic = st.selectbox(
                    tr("Filter by Subject"),
                    distinct_topics,
                    format_func=lambda x, _lg=active_lang: tr(x, _lg),
                )
            with f_col2:
                sel_diff = st.selectbox(
                    tr("Filter by Difficulty"),
                    distinct_diffs,
                    format_func=lambda x, _lg=active_lang: tr(x, _lg),
                )

            filtered = [
                q for q in quizzes
                if (sel_topic == "All Domains" or q["topic"] == sel_topic)
                and (sel_diff == "All Tiers" or q["difficulty"] == sel_diff)
            ]

            if filtered:
                localized_records = [
                    {
                        tr("Timestamp"): q["created_at"],
                        tr("Domain"): tr(q["topic"]),
                        tr("Difficulty"): tr(q["difficulty"]),
                        tr("Score (%)"): q["score"],
                        tr("Questions"): q["total_questions"],
                        tr("Mentor Remark"): tr(q.get("feedback", "")),
                    }
                    for q in filtered
                ]
                df_display = pd.DataFrame(localized_records)

                with f_col3:
                    csv_bytes = df_display.to_csv(index=False).encode("utf-8-sig")
                    st.download_button(
                        label=tr("Export CSV Transcript"),
                        data=csv_bytes,
                        file_name=f"{user['user_id']}_study_transcript.csv",
                        mime="text/csv",
                        use_container_width=True,
                    )

                st.dataframe(df_display, use_container_width=True, hide_index=True)
            else:
                st.caption(tr("No sessions match the selected filter criteria."))

render_footer()
