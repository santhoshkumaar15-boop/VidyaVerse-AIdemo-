"""
VidyaVerse - Python & SQL Verification Sandbox
Interactive in-browser code runner tested against deterministic test cases.
"""

import os
import sys

os.environ["OPENBLAS_NUM_THREADS"] = "1"
os.environ["MKL_NUM_THREADS"] = "1"

import pandas as pd
import streamlit as st

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from components.i18n import tr
from components.navbar import APP_NAME, render_footer, render_header
from database.db_manager import get_solved_challenges, init_db, mark_coding_solved
from tools.coding_tool import CODING_CHALLENGES
from agent import agent_evaluate_code

st.set_page_config(
    page_title=f"Code Lab | {APP_NAME}",
    layout="wide",
)

init_db()
render_header("CodingLab")

user = st.session_state.get("user", None)
solved_ids = set(get_solved_challenges(user["email"])) if user else set(st.session_state.get("guest_solved_labs", []))

st.markdown(
    f"""
    <div style="margin-bottom:0.75rem;">
        <span class="pista-badge" style="margin-bottom:6px;">{len(solved_ids)} / {len(CODING_CHALLENGES)} {tr('Challenges Solved')}</span>
        <h2 style="font-family: 'Source Serif 4', Georgia, serif; color: #1C1917; letter-spacing: -0.02em; margin: 4px 0 6px 0;">
            {tr('Python & SQL Verification Sandbox')}
        </h2>
        <div style="color: #57534E; font-size: 0.93rem;">
            {tr('Write real Python functions and SQL queries verified instantaneously against deterministic test suites.')}
        </div>
    </div>
    """,
    unsafe_allow_html=True,
)

labels = [
    f"{'[Solved] ' if c['id'] in solved_ids else '[Practice] '}[{c['language']} · {tr(c['difficulty'])}] {tr(c['title'])}"
    for c in CODING_CHALLENGES
]
selected_idx = st.selectbox(
    tr("Select Challenge"),
    range(len(CODING_CHALLENGES)),
    format_func=lambda i: labels[i],
)
challenge = CODING_CHALLENGES[selected_idx]

left_spec, right_editor = st.columns([1.15, 1.55], vertical_alignment="top")

with left_spec:
    with st.container(border=True):
        st.markdown(
            f"""
            <div style="display:flex; justify-content:space-between; align-items:center; margin-bottom:0.5rem;">
                <span class="almond-badge">{challenge['language']}</span>
                <span class="pista-badge">{tr(challenge['difficulty'])}</span>
            </div>
            <h4 style="color:#1C1917; margin:0 0 0.6rem 0;">{tr(challenge['title'])}</h4>
            """,
            unsafe_allow_html=True,
        )
        st.markdown(tr(challenge["prompt"]))

        if challenge.get("schema_preview"):
            st.markdown(f"##### {tr('Table Schema & Sample Data')}")
            st.code(challenge["schema_preview"], language="sql")

        with st.expander(tr("View Hint")):
            st.info(tr(challenge["hint"]))

with right_editor:
    with st.container(border=True):
        code_key = f"code_editor_{challenge['id']}"
        student_code = st.text_area(
            f"{tr('Editor')} ({challenge['language']}):",
            value=challenge["starter_code"],
            height=205,
            key=code_key,
        )

        b1, b2 = st.columns([1.6, 1.2])
        with b1:
            run_clicked = st.button(tr("Run & Verify"), type="primary", use_container_width=True)
        with b2:
            review_clicked = st.button(tr("Ask Tutor Review"), use_container_width=True)

        if review_clicked:
            st.session_state.prefill_tutor_prompt = (
                f"Please review my {challenge['language']} attempt for '{challenge['title']}':\n\n"
                f"```{challenge['language'].lower()}\n{student_code}\n```\n\n"
                "Explain how to make it clean and optimal."
            )
            st.switch_page("pages/5_AI_Tutor_Chat.py")

        if run_clicked:
            res = agent_evaluate_code(challenge["id"], student_code)
            if res.get("passed"):
                st.success(f"{tr(res['feedback'])} (+40 XP)")
                if user:
                    mark_coding_solved(user["email"], challenge["id"], challenge["language"])
                else:
                    guest_list = set(st.session_state.get("guest_solved_labs", []))
                    guest_list.add(challenge["id"])
                    st.session_state.guest_solved_labs = list(guest_list)
            else:
                st.error(tr(res["feedback"]))

            if res.get("results"):
                df_tests = pd.DataFrame(res["results"])
                df_tests["Status"] = df_tests["passed"].map(lambda ok: "PASS" if ok else "FAIL")
                st.dataframe(
                    df_tests[["Status", "case", "expected", "actual"]].rename(
                        columns={
                            "Status": tr("Status"),
                            "case": tr("Test Case"),
                            "expected": tr("Expected"),
                            "actual": tr("Output"),
                        }
                    ),
                    use_container_width=True,
                    hide_index=True,
                )
            elif res.get("columns"):
                st.markdown(f"##### {tr('Query Results')}")
                df_sql = pd.DataFrame(res["rows"], columns=res["columns"])
                st.dataframe(df_sql, use_container_width=True, hide_index=True)

render_footer()
