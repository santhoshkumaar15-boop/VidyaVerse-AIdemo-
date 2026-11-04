"""
VidyaVerse - Adaptive Practice Assessments
Interactive 3-stage assessment workflow with clickable step navigation,
non-repeating domain questions, mistake review, and printable certificates.
"""

import datetime
import os
import sys
import time

os.environ["OPENBLAS_NUM_THREADS"] = "1"
os.environ["MKL_NUM_THREADS"] = "1"

import streamlit as st

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from components.i18n import get_lang, tr, warm_translations
from components.navbar import APP_NAME, CURRICULUM_CATALOG, render_footer, render_header
from components.certificate import build_certificate_html
from database.db_manager import (
    get_mistakes,
    get_topic_bank_progress,
    get_user_analytics,
    init_db,
    resolve_mistake,
    save_mistake,
    save_quiz_result,
)
from agent import agent_decide_next_step, agent_evaluate_submission, agent_generate_quiz

st.set_page_config(
    page_title=f"Assessments | {APP_NAME}",
    layout="wide",
)

init_db()
render_header("Quiz")

active_lang = get_lang()
user = st.session_state.get("user", None)
user_email = user["email"] if user else "guest@edumate.ai"
student_display_name = user["user_id"] if user else tr("Guest Scholar")

for key, default_val in [
    ("current_quiz", None),
    ("quiz_answers", {}),
    ("quiz_evaluation", None),
    ("last_quiz_evaluation", None),
    ("quiz_step", 1),
    ("quiz_run_id", 0),
    ("timed_mode_active", False),
    ("quiz_start_ts", None),
    ("quiz_elapsed_sec", None),
    ("guest_mistakes", {}),
]:
    if key not in st.session_state:
        st.session_state[key] = default_val

ALL_TOPICS = [c["topic"] for c in CURRICULUM_CATALOG]
DIFF_OPTIONS = ["Easy", "Medium", "Hard"]

active_mistakes = (
    get_mistakes(user["email"]) if user else list(st.session_state.guest_mistakes.values())
)

default_diff = st.session_state.get("selected_difficulty", "Medium")
default_topic = st.session_state.get("selected_topic", ALL_TOPICS[0])

if user and "selected_difficulty" not in st.session_state:
    analytics_pre = get_user_analytics(user_email)
    recent_pre = analytics_pre["quiz_history"][0] if analytics_pre["quiz_history"] else None
    dec_pre = agent_decide_next_step(analytics_pre, recent_pre)
    default_diff = dec_pre["next_difficulty"]
    if "selected_topic" not in st.session_state:
        default_topic = dec_pre.get("recommended_topic", ALL_TOPICS[0])

# Keep quiz_step synchronized if external pages launched a quiz directly
if st.session_state.current_quiz is not None and st.session_state.quiz_evaluation is None and st.session_state.quiz_step == 1:
    # Only auto-advance if quiz_step wasn't explicitly set to 1 by user
    if not st.session_state.get("_manual_step_1", False):
        st.session_state.quiz_step = 2

st.markdown(
    f"""
    <h2 style="font-family: 'Source Serif 4', Georgia, serif; color: #1C1917; letter-spacing: -0.02em; margin-bottom: 0.25rem;">
        {tr('Practice Assessments')}
    </h2>
    <p style="color: #57534E; font-size: 0.94rem; margin-bottom: 1rem;">
        {tr('Work through unseen questions in your chosen topic, review detailed solutions, and earn mastery certificates.')}
    </p>
    """,
    unsafe_allow_html=True,
)

# =========================================================
# Interactive Clickable 3-Step Workflow Bar
# =========================================================
active_step = st.session_state.quiz_step
st_col1, st_col2, st_col3 = st.columns(3)

with st_col1:
    if st.button(
        f"1. {tr('Configure Assessment')}",
        key="quiz_step_btn_1",
        type="primary" if active_step == 1 else "secondary",
        use_container_width=True,
    ):
        st.session_state.quiz_step = 1
        st.session_state._manual_step_1 = True
        st.rerun()

with st_col2:
    if st.button(
        f"2. {tr('Solve Questions')}",
        key="quiz_step_btn_2",
        type="primary" if active_step == 2 else "secondary",
        use_container_width=True,
    ):
        st.session_state._manual_step_1 = False
        if st.session_state.current_quiz is None or st.session_state.quiz_evaluation is not None:
            quiz_data = agent_generate_quiz(
                topic=default_topic,
                difficulty=default_diff,
                num_questions=3,
                user_email=user_email,
            )
            st.session_state.selected_topic = default_topic
            st.session_state.selected_difficulty = default_diff
            st.session_state.current_quiz = quiz_data
            st.session_state.quiz_answers = {}
            st.session_state.quiz_evaluation = None
            st.session_state.quiz_start_ts = time.time()
            st.session_state.quiz_run_id += 1
        st.session_state.quiz_step = 2
        st.rerun()

with st_col3:
    if st.button(
        f"3. {tr('Results & Certificate')}",
        key="quiz_step_btn_3",
        type="primary" if active_step == 3 else "secondary",
        use_container_width=True,
    ):
        st.session_state._manual_step_1 = False
        st.session_state.quiz_step = 3
        st.rerun()

st.markdown("<div style='height: 8px;'></div>", unsafe_allow_html=True)

# =========================================================
# STEP 1: Quiz Configuration + Mistake Review
# =========================================================
if active_step == 1:
    if st.session_state.current_quiz is not None and st.session_state.quiz_evaluation is None:
        with st.container(border=True):
            res_c1, res_c2 = st.columns([3, 1.1], vertical_alignment="center")
            with res_c1:
                st.markdown(
                    f"**{tr('Assessment in progress')}:** {tr(st.session_state.current_quiz['topic'])} "
                    f"({tr(st.session_state.current_quiz['difficulty'])} · {len(st.session_state.current_quiz['questions'])} {tr('Questions')})"
                )
            with res_c2:
                if st.button(f"{tr('Resume Questions')} →", use_container_width=True):
                    st.session_state._manual_step_1 = False
                    st.session_state.quiz_step = 2
                    st.rerun()

    cfg_col, red_col = st.columns([1.85, 1], vertical_alignment="top")

    with cfg_col:
        with st.container(border=True):
            st.markdown(
                f"<h4 style='color:#1C1917; font-weight:600; margin-top:0;'>{tr('Session Parameters')}</h4>",
                unsafe_allow_html=True,
            )
            c1, c2, c3 = st.columns([1.6, 1, 1])
            with c1:
                t_idx = ALL_TOPICS.index(default_topic) if default_topic in ALL_TOPICS else 0
                topic_choice = st.selectbox(
                    tr("Subject"),
                    ALL_TOPICS,
                    index=t_idx,
                    format_func=lambda t, _lg=active_lang: tr(t, _lg),
                )
            with c2:
                d_idx = DIFF_OPTIONS.index(default_diff) if default_diff in DIFF_OPTIONS else 1
                difficulty_choice = st.selectbox(
                    tr("Difficulty"),
                    DIFF_OPTIONS,
                    index=d_idx,
                    format_func=lambda d, _lg=active_lang: tr(d, _lg),
                )
            with c3:
                num_q = st.slider(tr("Question Count"), min_value=2, max_value=5, value=3)

            timed_toggle = st.checkbox(tr("Enable timed exam mode (45s per question)"), value=False)

            bank_stats = {row["topic"]: row for row in get_topic_bank_progress(user_email)}
            t_stat = bank_stats.get(topic_choice, {"seen": 0, "total": 10, "pct": 0.0})
            st.caption(
                f"{tr('Question coverage')} ({tr(topic_choice)}): {t_stat['seen']} / {t_stat['total']} {tr('completed')}"
            )

            if st.button(tr("Start Assessment"), type="primary", use_container_width=True):
                with st.spinner(tr("Preparing questions...")):
                    quiz_data = agent_generate_quiz(
                        topic=topic_choice,
                        difficulty=difficulty_choice,
                        num_questions=num_q,
                        user_email=user_email,
                    )
                    st.session_state.selected_topic = topic_choice
                    st.session_state.selected_difficulty = difficulty_choice
                    st.session_state.current_quiz = quiz_data
                    st.session_state.quiz_answers = {}
                    st.session_state.quiz_evaluation = None
                    st.session_state.timed_mode_active = timed_toggle
                    st.session_state.quiz_start_ts = time.time()
                    st.session_state.quiz_run_id += 1
                    st.session_state._manual_step_1 = False
                    st.session_state.quiz_step = 2
                    st.rerun()

    with red_col:
        with st.container(border=True):
            st.markdown(
                f"<h4 style='color:#1C1917; font-weight:600; margin-top:0;'>{tr('Mistake Review')}</h4>",
                unsafe_allow_html=True,
            )
            st.markdown(
                f"""
                <p style="font-size:0.88rem; color:#57534E; line-height:1.55;">
                    {tr('Questions missed in earlier sessions are saved here automatically. Answer them correctly in a review round to clear them.')}
                </p>
                <div style="margin-bottom:0.85rem;">
                    <span class="{'terracotta-badge' if active_mistakes else 'pista-badge'}">
                        {len(active_mistakes)} {tr('Pending Review')}
                    </span>
                </div>
                """,
                unsafe_allow_html=True,
            )
            if active_mistakes:
                if st.button(tr("Practice Missed Questions"), use_container_width=True):
                    batch = active_mistakes[:5]
                    st.session_state.current_quiz = {
                        "topic": batch[0].get("topic", "Mixed Review"),
                        "difficulty": "Redemption",
                        "count": len(batch),
                        "questions": batch,
                        "is_redemption": True,
                    }
                    st.session_state.quiz_answers = {}
                    st.session_state.quiz_evaluation = None
                    st.session_state.timed_mode_active = False
                    st.session_state.quiz_start_ts = time.time()
                    st.session_state.quiz_run_id += 1
                    st.session_state._manual_step_1 = False
                    st.session_state.quiz_step = 2
                    st.rerun()
            else:
                st.caption(tr("No missed questions pending review."))
                if st.button(tr("Build Quiz From Notes"), use_container_width=True):
                    st.switch_page("pages/6_Study_Studio.py")

# =========================================================
# STEP 2: Solve Questions
# =========================================================
elif active_step == 2:
    if st.session_state.current_quiz is None:
        st.session_state.current_quiz = agent_generate_quiz(
            topic=default_topic,
            difficulty=default_diff,
            num_questions=3,
            user_email=user_email,
        )
        st.session_state.quiz_start_ts = time.time()

    quiz = st.session_state.current_quiz
    run_id = st.session_state.quiz_run_id
    questions = quiz["questions"]
    allotted_sec = len(questions) * 45

    timer_badge = (
        f'<span class="terracotta-badge" style="margin-right:6px;">{tr("Timed")}: {allotted_sec}s</span>'
        if st.session_state.timed_mode_active
        else ""
    )
    mode_badge = (
        f'<span class="terracotta-badge" style="margin-right:6px;">{tr("Mistake Review")}</span>'
        if quiz.get("is_redemption")
        else f'<span class="pista-badge" style="margin-right:6px;">{tr("Unseen Questions")}</span>'
    )

    st.markdown(
        f"""
        <div class="creamy-card" style="border-left: 3.5px solid #9A4A27;">
            <div style="display: flex; justify-content: space-between; align-items: center; flex-wrap: wrap; gap: 8px;">
                <div>
                    <div style="font-size: 0.74rem; color: #78716C; font-weight: 600; text-transform: uppercase; letter-spacing: 0.05em;">{tr('Active Assessment')}</div>
                    <h3 style="margin: 2px 0 0 0; color: #1C1917; font-size: 1.2rem;">{tr(quiz['topic'])}</h3>
                </div>
                <div>
                    {timer_badge}
                    {mode_badge}
                    <span class="almond-badge">{tr(quiz['difficulty'])} · {len(questions)} {tr('Questions')}</span>
                </div>
            </div>
        </div>
        """,
        unsafe_allow_html=True,
    )

    if active_lang != "en":
        batch_texts = [quiz.get("topic", ""), quiz.get("difficulty", "")]
        for q in questions:
            batch_texts.append(q["question"])
            batch_texts.extend(q.get("options", []))
            batch_texts.append(q.get("explanation", ""))
        warm_translations(batch_texts, [active_lang])

    for idx, q in enumerate(questions, 1):
        with st.container(border=True):
            q_diff = tr(q.get("difficulty", quiz["difficulty"]))
            q_text_disp = tr(q["question"])
            localized_opts = [tr(opt) for opt in q["options"]]
            st.markdown(
                f"""
                <div style="display:flex; justify-content:space-between; align-items:flex-start; gap:12px; margin-bottom:0.55rem;">
                    <div style="font-size: 1rem; font-weight: 600; color: #1C1917; line-height: 1.48;">
                        {idx}. {q_text_disp}
                    </div>
                    <span class="almond-badge">{q_diff}</span>
                </div>
                """,
                unsafe_allow_html=True,
            )
            selected_opt = st.radio(
                f"q_label_{idx}",
                localized_opts,
                key=f"q_{run_id}_{active_lang}_{idx}",
                index=None,
                label_visibility="collapsed",
            )
            st.session_state.quiz_answers[idx] = selected_opt

    answered_count = sum(1 for i in range(1, len(questions) + 1) if st.session_state.quiz_answers.get(i))
    st.progress(
        answered_count / max(len(questions), 1),
        text=f"{tr('Answered')}: {answered_count} / {len(questions)}",
    )

    act_col1, act_col2 = st.columns([2.4, 1])
    with act_col1:
        if st.button(tr("Submit Answers"), type="primary", use_container_width=True):
            unanswered = [i for i in range(1, len(questions) + 1) if not st.session_state.quiz_answers.get(i)]
            if unanswered:
                st.warning(f"{tr('Please select an answer for question')} {', '.join(map(str, unanswered))}.")
            else:
                start_t = st.session_state.quiz_start_ts or time.time()
                st.session_state.quiz_elapsed_sec = max(1, int(time.time() - start_t))

                submission_payload = {
                    "topic": quiz["topic"],
                    "difficulty": quiz["difficulty"],
                    "responses": [
                        {
                            "question": q["question"],
                            "selected": st.session_state.quiz_answers[idx],
                            "correct_answer": q["correct_answer"],
                            "explanation": q["explanation"],
                        }
                        for idx, q in enumerate(questions, 1)
                    ],
                }
                evaluation_res = agent_evaluate_submission(submission_payload)
                st.session_state.quiz_evaluation = evaluation_res
                st.session_state.last_quiz_evaluation = evaluation_res
                st.session_state.quiz_step = 3

                for q_orig, b_res in zip(questions, evaluation_res["breakdown"]):
                    if b_res["is_correct"]:
                        if user:
                            resolve_mistake(user["email"], q_orig["question"])
                        else:
                            st.session_state.guest_mistakes.pop(q_orig["question"], None)
                    else:
                        if user:
                            save_mistake(user["email"], quiz["topic"], quiz["difficulty"], q_orig)
                        else:
                            st.session_state.guest_mistakes[q_orig["question"]] = {
                                **q_orig,
                                "topic": quiz["topic"],
                                "difficulty": quiz["difficulty"],
                            }

                if user and quiz["difficulty"] in DIFF_OPTIONS:
                    save_quiz_result(
                        email=user["email"],
                        topic=quiz["topic"],
                        difficulty=quiz["difficulty"],
                        score=evaluation_res["score_percentage"],
                        total_questions=evaluation_res["total_questions"],
                        feedback=evaluation_res["remark"],
                    )
                st.rerun()
    with act_col2:
        if st.button(tr("Change Topic"), use_container_width=True):
            st.session_state.current_quiz = None
            st.session_state.quiz_answers = {}
            st.session_state.quiz_evaluation = None
            st.session_state.quiz_step = 1
            st.rerun()

# =========================================================
# STEP 3: Scorecard, Detailed Solutions & Certificate
# =========================================================
else:
    ev = st.session_state.quiz_evaluation or st.session_state.last_quiz_evaluation

    if ev is None:
        # Clean interactive empty state when user clicks Step 3 before taking a quiz
        with st.container(border=True):
            st.markdown(
                f"""
                <h4 style="color:#1C1917; margin-top:0;">{tr('Assessment Results & Mastery Certificates')}</h4>
                <p style="color:#57534E; font-size:0.93rem; line-height:1.6;">
                    {tr('Complete a short assessment round to view your question-by-question explanations, Strands DecisionModel recommendation, and downloadable certificate (unlocked at 80% or above).')}
                </p>
                """,
                unsafe_allow_html=True,
            )
            if user:
                user_analytics = get_user_analytics(user["email"])
                earned_certs = user_analytics.get("certified_topics", [])
                if earned_certs:
                    st.markdown(f"**{tr('Previously Earned Certificates')}**")
                    today_str = datetime.date.today().isoformat()
                    for idx_c, c_row in enumerate(earned_certs):
                        cert_doc = build_certificate_html(
                            student_name=user["user_id"],
                            topic=c_row["topic"],
                            score=c_row["mastery_score"],
                            date_str=today_str,
                            lang=active_lang,
                        )
                        st.download_button(
                            f"{tr('Download Certificate')} — {tr(c_row['topic'])} ({c_row['mastery_score']}%)",
                            data=cert_doc.encode("utf-8"),
                            file_name=f"{c_row['topic'].replace(' ', '_')}_Certificate.html",
                            mime="text/html",
                            key=f"step3_cert_{idx_c}",
                        )
            e_c1, e_c2 = st.columns([1.4, 2.2])
            with e_c1:
                if st.button(f"{tr('Start 3-Question Assessment')} →", type="primary", use_container_width=True):
                    st.session_state.current_quiz = agent_generate_quiz(
                        topic=default_topic,
                        difficulty=default_diff,
                        num_questions=3,
                        user_email=user_email,
                    )
                    st.session_state.quiz_answers = {}
                    st.session_state.quiz_evaluation = None
                    st.session_state.quiz_start_ts = time.time()
                    st.session_state.quiz_run_id += 1
                    st.session_state.quiz_step = 2
                    st.rerun()
    else:
        elapsed_s = st.session_state.quiz_elapsed_sec or 0

        if user:
            post_analytics = get_user_analytics(user["email"])
        else:
            post_analytics = {
                "total_quizzes": 1,
                "average_score": ev["score_percentage"],
                "weak_topics": [ev["topic"]] if ev["score_percentage"] < 70 else [],
                "topic_mastery": [{"topic": ev["topic"], "mastery_score": ev["score_percentage"]}],
            }
        next_decision = agent_decide_next_step(post_analytics, ev)

        sc1, sc2, sc3 = st.columns([1, 1, 2])
        with sc1:
            st.markdown(
                f"""
                <div class="metric-box">
                    <div class="metric-value">{ev['score_percentage']}%</div>
                    <div class="metric-label">{tr('Accuracy Score')}</div>
                </div>
                """,
                unsafe_allow_html=True,
            )
        with sc2:
            time_note = f" · {elapsed_s}s" if st.session_state.timed_mode_active else ""
            st.markdown(
                f"""
                <div class="metric-box">
                    <div class="metric-value">{ev['correct_count']} / {ev['total_questions']}</div>
                    <div class="metric-label">{tr(ev['difficulty'])}{time_note}</div>
                </div>
                """,
                unsafe_allow_html=True,
            )
        with sc3:
            st.markdown(
                f"""
                <div class="creamy-card" style="margin-bottom:0; height:100%; display:flex; flex-direction:column; justify-content:center;">
                    <div style="font-weight:600; color:#1C1917; font-size:0.96rem; margin-bottom:4px;">
                        {tr('Evaluation Summary')} — {tr(ev['topic'])}
                    </div>
                    <div style="color:#57534E; font-size:0.9rem;">{tr(ev['remark'])}</div>
                </div>
                """,
                unsafe_allow_html=True,
            )

        if ev["score_percentage"] >= 80.0:
            today_str = datetime.date.today().isoformat()
            cert_html = build_certificate_html(
                student_name=student_display_name,
                topic=ev["topic"],
                score=ev["score_percentage"],
                date_str=today_str,
                lang=active_lang,
            )
            with st.container(border=True):
                cert_c1, cert_c2 = st.columns([2.6, 1.1], vertical_alignment="center")
                with cert_c1:
                    st.markdown(
                        f"**{tr('Certificate of Mastery Unlocked')}** — {student_display_name} · **{ev['score_percentage']}%** in **{tr(ev['topic'])}**"
                    )
                with cert_c2:
                    st.download_button(
                        tr("Download Certificate (.html)"),
                        data=cert_html.encode("utf-8"),
                        file_name=f"{ev['topic'].replace(' ', '_')}_Certificate.html",
                        mime="text/html",
                        use_container_width=True,
                    )

        st.markdown(
            f"""
            <div class="decider-banner">
                <div style="display:flex; justify-content:space-between; align-items:center; flex-wrap:wrap; gap:8px;">
                    <div style="font-weight:600; color:#1C1917; font-size:0.98rem;">
                        {tr('Recommended Next Step')}: {tr(next_decision['headline'])}
                    </div>
                    <div style="display:flex; gap:6px; flex-wrap:wrap;">
                        <span class="almond-badge">Strands Decider · {next_decision.get('confidence_pct', 94)}% ({next_decision.get('latency_ms', 1)}ms)</span>
                        <span class="pista-badge">{tr(next_decision['recommended_topic'])} · {tr(next_decision['next_difficulty'])}</span>
                    </div>
                </div>
                <div style="color:#57534E; margin-top:6px; font-size:0.9rem;">
                    {tr(next_decision['recommendation'])}
                </div>
            </div>
            """,
            unsafe_allow_html=True,
        )

        missed_items = [b for b in ev["breakdown"] if not b["is_correct"]]
        btn_c1, btn_c2, btn_c3, btn_c4 = st.columns(4)
        with btn_c1:
            if st.button(f"{tr('Next Round')}: {tr(next_decision['next_difficulty'])}", type="primary", use_container_width=True):
                next_q = agent_generate_quiz(
                    topic=next_decision["recommended_topic"],
                    difficulty=next_decision["next_difficulty"],
                    num_questions=min(max(len(ev["breakdown"]), 2), 5),
                    user_email=user_email,
                )
                st.session_state.selected_topic = next_decision["recommended_topic"]
                st.session_state.selected_difficulty = next_decision["next_difficulty"]
                st.session_state.current_quiz = next_q
                st.session_state.quiz_answers = {}
                st.session_state.quiz_evaluation = None
                st.session_state.quiz_start_ts = time.time()
                st.session_state.quiz_run_id += 1
                st.session_state.quiz_step = 2
                st.rerun()
        with btn_c2:
            if st.button(tr("Configure New Quiz"), use_container_width=True):
                st.session_state.current_quiz = None
                st.session_state.quiz_answers = {}
                st.session_state.quiz_evaluation = None
                st.session_state.quiz_step = 1
                st.rerun()
        with btn_c3:
            if missed_items:
                if st.button(tr("Discuss Missed Question"), use_container_width=True):
                    st.session_state.prefill_tutor_prompt = (
                        f"In my {ev['topic']} assessment, I missed: \"{missed_items[0]['question']}\". "
                        f"Explain this concept step by step with a clear example."
                    )
                    st.switch_page("pages/5_AI_Tutor_Chat.py")
            else:
                if st.button(tr("Open Coding Lab"), use_container_width=True):
                    st.switch_page("pages/7_Coding_Lab.py")
        with btn_c4:
            if user:
                if st.button(tr("View Progress"), use_container_width=True):
                    st.switch_page("pages/2_Student_Dashboard.py")
            else:
                if st.button(tr("Sign In to Save"), use_container_width=True):
                    st.switch_page("pages/3_Authentication.py")

        st.markdown("<div style='height: 10px;'></div>", unsafe_allow_html=True)
        st.markdown(f"#### {tr('Question-by-Question Review')}")

        for b in ev["breakdown"]:
            badge = tr("Correct") if b["is_correct"] else tr("Saved for Review")
            badge_bg = "#EDF5F0" if b["is_correct"] else "#FDF2EC"
            accent_color = "#22543D" if b["is_correct"] else "#9A3412"

            st.markdown(
                f"""
                <div class="creamy-card" style="border-left: 3.5px solid {accent_color};">
                    <div style="display: flex; justify-content: space-between; align-items: flex-start; gap: 12px; margin-bottom: 0.5rem;">
                        <strong style="color:#1C1917; font-size:0.96rem;">{b['question_num']}. {tr(b['question'])}</strong>
                        <span style="background: {badge_bg}; color: {accent_color}; padding: 0.2rem 0.6rem; border-radius: 6px; font-weight: 600; font-size: 0.76rem; white-space: nowrap;">
                            {badge}
                        </span>
                    </div>
                    <div style="font-size: 0.88rem; color: #44403C; display:flex; gap:24px; flex-wrap:wrap;">
                        <div><strong>{tr('Selected')}:</strong> {tr(b['selected'])}</div>
                        <div><strong>{tr('Correct Option')}:</strong> {b['correct_answer']}</div>
                    </div>
                    <div style="margin-top: 0.6rem; font-size: 0.88rem; background: #FAF8F5; border: 1px solid #EAE4DC; padding: 0.7rem 0.9rem; border-radius: 8px; color: #44403C;">
                        <strong>{tr('Explanation')}:</strong> {tr(b['explanation'])}
                    </div>
                </div>
                """,
                unsafe_allow_html=True,
            )

render_footer()
