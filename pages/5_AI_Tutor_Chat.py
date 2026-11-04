"""
VidyaVerse - Academic & Cloud Engineering Tutor
Interactive doubt clearance across 4 pedagogical styles with Strands Decider safety guardrails.
"""

import os
import sys

os.environ["OPENBLAS_NUM_THREADS"] = "1"
os.environ["MKL_NUM_THREADS"] = "1"
os.environ["NUMEXPR_NUM_THREADS"] = "1"
os.environ["OMP_NUM_THREADS"] = "1"

import streamlit as st

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from components.i18n import get_lang, tr
from components.navbar import APP_NAME, render_ai_artwork, render_footer, render_header
from agent import agent_route_tutor_query
from agent_chat import ask_tutor
from database.db_manager import init_db

st.set_page_config(
    page_title=f"Tutor | {APP_NAME}",
    layout="wide",
)

init_db()
render_header("Chat")

active_lang = get_lang()
user = st.session_state.get("user", None)
user_name = user["user_id"] if user else tr("Learner")

default_greeting = (
    f"{tr('Hello')} {user_name}. {tr('I can help you review data structures, debug Python or SQL, analyze Big-O complexity, or examine AWS cloud architectures. What topic would you like to explore?')}"
)

if "chat_messages" not in st.session_state:
    st.session_state.chat_messages = [{"role": "assistant", "content": default_greeting, "is_greeting": True}]
elif len(st.session_state.chat_messages) == 1 and st.session_state.chat_messages[0].get("is_greeting"):
    st.session_state.chat_messages[0]["content"] = default_greeting

hdr_mid, hdr_right = st.columns([3.3, 1.2], vertical_alignment="center")
with hdr_mid:
    st.markdown(
        f"""
        <h2 style="font-family: 'Source Serif 4', Georgia, serif; color: #1C1917; letter-spacing: -0.02em; margin-bottom: 0.2rem;">
            {tr('Academic & Cloud Engineering Tutor')}
        </h2>
        <p style="color: #57534E; font-size: 0.93rem; margin-bottom: 0.4rem;">
            {tr('Select an instruction style below to customize explanations, trade-off analyses, or code diagnostics.')}
        </p>
        """,
        unsafe_allow_html=True,
    )
with hdr_right:
    u_col1, u_col2 = st.columns(2)
    with u_col1:
        transcript_md = "\n\n---\n\n".join(
            f"**{'Student' if m['role'] == 'user' else APP_NAME + ' Tutor'}:**\n\n{m['content']}"
            for m in st.session_state.chat_messages
        )
        st.download_button(
            tr("Export Notes"),
            data=transcript_md.encode("utf-8"),
            file_name="tutor_study_notes.md",
            mime="text/markdown",
            use_container_width=True,
        )
    with u_col2:
        if st.button(tr("Clear Chat"), use_container_width=True):
            st.session_state.chat_messages = [
                {"role": "assistant", "content": default_greeting, "is_greeting": True}
            ]
            st.rerun()

st.markdown("<div style='height: 4px;'></div>", unsafe_allow_html=True)

with st.container(border=True):
    persona_labels = {
        "Standard Mentor": tr("Detailed Mentor"),
        "Socratic Guide": tr("Socratic Discussion"),
        "Mock Interviewer": tr("Technical Interviewer"),
        "Simple Intuition": tr("Conceptual Analogy"),
    }
    persona_keys = list(persona_labels.keys())
    selected_persona = st.radio(
        tr("Pedagogical Mode"),
        persona_keys,
        format_func=lambda k: persona_labels[k],
        horizontal=True,
    )

    st.markdown(
        f"<div style='font-size:0.78rem; font-weight:600; color:#78716C; margin:8px 0 6px 0; text-transform:uppercase; letter-spacing:0.04em;'>{tr('Discussion Starters')}</div>",
        unsafe_allow_html=True,
    )
    q_col1, q_col2, q_col3, q_col4 = st.columns(4)
    selected_prompt = st.session_state.pop("prefill_tutor_prompt", None)

    with q_col1:
        if st.button(tr("QuickSort vs MergeSort"), use_container_width=True):
            selected_prompt = tr("Explain the key differences between QuickSort and MergeSort, including complexity and stability.")
    with q_col2:
        if st.button(tr("Mutable vs Immutable Types"), use_container_width=True):
            selected_prompt = tr("Explain mutable vs immutable objects in Python with examples.")
    with q_col3:
        if st.button(tr("Transformer Attention"), use_container_width=True):
            selected_prompt = tr("Explain how Scaled Dot-Product Self-Attention works in Transformer models.")
    with q_col4:
        if st.button(tr("AWS Bedrock & Lambda"), use_container_width=True):
            selected_prompt = tr("Compare AWS Lambda, Amazon ECS Fargate, and Amazon Bedrock when deploying a production Strands AI Agent.")

chat_container = st.container()
with chat_container:
    for msg in st.session_state.chat_messages:
        role_label = user_name if msg["role"] == "user" else "Tutor"
        with st.chat_message(msg["role"]):
            st.markdown(msg["content"])
            trace_meta = msg.get("decider_trace")
            if trace_meta:
                st.caption(trace_meta)


def _execute_tutor_turn(prompt_text: str):
    """Evaluates query via Strands System-1 DecisionModel Router & Guardrail before generating response."""
    route_info = agent_route_tutor_query(prompt_text, persona=selected_persona)
    if not route_info["guardrail_pass"]:
        blocked_msg = tr(
            "Strands Safety Guardrail: This query touches on exploit scripts or credential interception. "
            "Let us instead focus on secure architectural patterns, AWS IAM Least Privilege, or system defense fundamentals."
        )
        trace_str = f"Decider Trace: Guardrail=BLOCKED · Latency={route_info['latency_ms']}ms"
        return blocked_msg, trace_str

    reply_text = ask_tutor(
        st.session_state.chat_messages[:-1],
        prompt_text,
        persona=selected_persona,
        lang=active_lang,
        routing_strategy=route_info["strategy"],
    )
    trace_str = (
        f"Strands Decider Trace: Domain={route_info['domain']} · "
        f"Strategy={route_info['strategy']} · Confidence={route_info['confidence_pct']}% ({route_info['latency_ms']}ms)"
    )
    return reply_text, trace_str


if selected_prompt:
    st.session_state.chat_messages.append({"role": "user", "content": selected_prompt})
    with st.chat_message("user"):
        st.markdown(selected_prompt)
    with st.chat_message("assistant"):
        with st.spinner(tr("Analyzing query...")):
            reply, trace_caption = _execute_tutor_turn(selected_prompt)
            st.markdown(reply)
            st.caption(trace_caption)
            st.session_state.chat_messages.append(
                {"role": "assistant", "content": reply, "decider_trace": trace_caption}
            )
    st.rerun()

st.markdown("<div style='height: 6px;'></div>", unsafe_allow_html=True)
with st.form("chat_input_form", clear_on_submit=True):
    col_input, col_btn = st.columns([5.2, 1])
    with col_input:
        user_input = st.text_input(
            tr("Ask any question"),
            placeholder=tr("Enter a programming, cloud architecture, or systems design question..."),
            label_visibility="collapsed",
        )
    with col_btn:
        submitted = st.form_submit_button(tr("Submit"), use_container_width=True)

if submitted and user_input.strip():
    clean_query = user_input.strip()
    st.session_state.chat_messages.append({"role": "user", "content": clean_query})
    with st.chat_message("user"):
        st.markdown(clean_query)
    with st.chat_message("assistant"):
        with st.spinner(tr("Thinking...")):
            reply, trace_caption = _execute_tutor_turn(clean_query)
            st.markdown(reply)
            st.caption(trace_caption)
            st.session_state.chat_messages.append(
                {"role": "assistant", "content": reply, "decider_trace": trace_caption}
            )
    st.rerun()

render_footer()
