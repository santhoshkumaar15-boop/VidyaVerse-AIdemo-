"""
VidyaVerse - Student Authentication Portal (Sign In & Registration)
"""

import os
import sys

os.environ["OPENBLAS_NUM_THREADS"] = "1"
os.environ["MKL_NUM_THREADS"] = "1"

import streamlit as st

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from components.i18n import get_lang, tr
from components.navbar import APP_NAME, render_ai_artwork, render_footer, render_header
from database.db_manager import authenticate_user, init_db, register_user

st.set_page_config(
    page_title=f"Sign In | {APP_NAME}",
    layout="wide",
)

init_db()
render_header("Auth")

active_lang = get_lang()
user = st.session_state.get("user", None)

if user:
    with st.container(border=True):
        st.success(f"{tr('Signed in as')} **{user['user_id']}** ({user['email']}).")
        c1, c2, c3 = st.columns(3)
        with c1:
            if st.button(tr("Open Progress"), type="primary", use_container_width=True):
                st.switch_page("pages/2_Student_Dashboard.py")
        with c2:
            if st.button(tr("Start Assessment"), use_container_width=True):
                st.session_state.quiz_step = 1
                st.switch_page("pages/1_Adaptive_Quiz.py")
        with c3:
            if st.button(tr("Sign Out"), use_container_width=True):
                st.session_state.user = None
                st.session_state.current_quiz = None
                st.session_state.quiz_evaluation = None
                st.rerun()
else:
    left_info, right_forms = st.columns([1.15, 1.35], vertical_alignment="top")

    with left_info:
        render_ai_artwork("madurai_thirumalai_sangam.jpg", max_height_px=220)
        st.markdown("<div style='height: 8px;'></div>", unsafe_allow_html=True)
        st.markdown(
            f"""
            <div class="creamy-card" style="margin-bottom: 0;">
                <div class="hero-eyebrow">{tr('Student Profile')}</div>
                <h3 style="font-family: 'Source Serif 4', Georgia, serif; color: #1C1917; letter-spacing: -0.01em; margin-top: 0; margin-bottom: 0.5rem;">
                    {tr('Synchronized Mastery Progress')}
                </h3>
                <p style="color: #57534E; font-size: 0.92rem; line-height: 1.55; margin-bottom: 0.85rem;">
                    {tr(f'Create an account on {APP_NAME} to record assessment history, maintain question bank coverage, and earn verifiable certificates.')}
                </p>
                <div style="font-size:0.86rem; color:#44403C; line-height:1.7;">
                    • <strong>{tr('Non-Repeating Question Bank')}</strong><br>
                    • <strong>{tr('Calibrated Difficulty Progression')}</strong><br>
                    • <strong>{tr('Verifiable Mastery Certificates')}</strong>
                </div>
            </div>
            """,
            unsafe_allow_html=True,
        )

    with right_forms:
        tab_login, tab_register = st.tabs([tr("Sign In"), tr("Create Account")])

        with tab_login:
            with st.container(border=True):
                st.markdown(f"<h4 style='color: #1C1917 !important; font-weight: 700; margin-top: 0; margin-bottom: 0.25rem;'>{tr('Sign In to Account')}</h4>", unsafe_allow_html=True)
                st.markdown(f"<p style='color: #57534E !important; font-size: 0.88rem; margin-bottom: 0.85rem;'>{tr('Enter your registered email address and password.')}</p>", unsafe_allow_html=True)
                with st.form("login_form"):
                    login_email = st.text_input(tr("Email Address"), placeholder="student@example.edu")
                    login_password = st.text_input(tr("Password"), type="password", placeholder="••••••••")
                    submitted_login = st.form_submit_button(tr("Sign In"), use_container_width=True)

                    if submitted_login:
                        success, user_data, message = authenticate_user(login_email, login_password)
                        if success:
                            st.session_state.user = user_data
                            st.success(tr("Signed in successfully."))
                            st.switch_page("pages/2_Student_Dashboard.py")
                        else:
                            st.error(tr(message))

        with tab_register:
            with st.container(border=True):
                st.markdown(f"<h4 style='color: #1C1917 !important; font-weight: 700; margin-top: 0; margin-bottom: 0.25rem;'>{tr('Create Student Account')}</h4>", unsafe_allow_html=True)
                st.markdown(f"<p style='color: #57534E !important; font-size: 0.88rem; margin-bottom: 0.85rem;'>{tr('Register once to synchronize your assessment records.')}</p>", unsafe_allow_html=True)
                with st.form("register_form"):
                    reg_email = st.text_input(tr("Email Address"), placeholder="student@example.edu")
                    reg_userid = st.text_input(tr("Display Name"), placeholder="e.g. AlexMorgan")
                    reg_pass = st.text_input(tr("Password"), type="password", placeholder="••••")
                    reg_confirm = st.text_input(tr("Confirm Password"), type="password", placeholder="••••")

                    submitted_reg = st.form_submit_button(tr("Create Account"), use_container_width=True)
                    if submitted_reg:
                        success, message = register_user(reg_email, reg_userid, reg_pass, reg_confirm)
                        if success:
                            ok_auto, u_auto, _ = authenticate_user(reg_email, reg_pass)
                            if ok_auto and u_auto:
                                st.session_state.user = u_auto
                                st.success(tr("Account created successfully."))
                                st.switch_page("pages/2_Student_Dashboard.py")
                            else:
                                st.success(tr(message))
                        else:
                            if message == "already the email id exists":
                                if active_lang == "en":
                                    st.error("already the email id exists")
                                else:
                                    st.error(f"{tr('This email address is already registered')} (already the email id exists)")
                            else:
                                st.error(tr(message))

render_footer()
