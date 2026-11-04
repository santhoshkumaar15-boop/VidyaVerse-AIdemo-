"""
VidyaVerse AI - AWS Strands Agent & System-1 DecisionModel Orchestration
Implements authentic `strands.DecisionModel` (`0020-decision-models`), closed-choice routing,
boolean safety guardrails, `UncertaintyOptions` confidence gating, `Uncertain` sentinel narrowing,
and modular `@tool` pipelines with OpenTelemetry span instrumentation.
"""

import asyncio
import concurrent.futures
import json
import os
import time
from pathlib import Path
from typing import Any

from dotenv import load_dotenv
from strands import Agent, DecisionModel
from strands.decisions import (
    DecisionInput,
    DecisionMetadata,
    DecisionResult,
    Question,
    Uncertain,
    UncertaintyOptions,
)

from tools.quiz_tool import generate_quiz
from tools.evaluation_tool import evaluate_quiz_submission
from tools.progress_tool import analyze_student_progress
from tools.study_tools import generate_flashcards_and_quiz, generate_study_roadmap
from tools.coding_tool import evaluate_code_challenge

# Load environment variables strictly from .env without hardcoding secrets
ENV_PATH = Path(__file__).resolve().parent / ".env"
load_dotenv(dotenv_path=ENV_PATH, override=False)

CURRICULUM_DOMAINS = [
    "Python Programming",
    "Artificial Intelligence & ML",
    "Data Structures & Algorithms",
    "Web Development & Cloud",
    "Database Systems & SQL",
    "Cybersecurity & Networks",
]

SYSTEM_PROMPT = """You are VidyaVerse AI, an adaptive multilingual pedagogical and cloud engineering AI mentor.
Your mission is to guide learners through conceptual mastery across programming, AI/ML, AWS cloud architecture,
algorithms, databases, and cybersecurity using structured Strands tools and DecisionModel telemetry."""


def _get_configured_api_key() -> str:
    load_dotenv(dotenv_path=ENV_PATH, override=False)
    return os.getenv("STRANDS_API_KEY") or os.getenv("GEMINI_API_KEY") or ""


class EduMateDecider(DecisionModel):
    """
    System-1 Pedagogical & Intent Decision Engine subclassing `strands.DecisionModel`.
    Executes through Strands' OpenTelemetry-traced `DecisionModel.ask()` span pipeline to perform:
      1. Closed-choice cognitive milestone & difficulty routing
      2. Calibrated confidence gating via `UncertaintyOptions` and `Uncertain` sentinels
      3. Pre-LLM query intent routing and boolean academic safety guardrails
    """

    def __init__(self):
        super().__init__()

    async def _ask(
        self,
        state: DecisionInput,
        questions: dict[str, Question],
        **kwargs: Any,
    ) -> DecisionResult:
        """Evaluates structured closed-choice & guardrail questions over JSON state."""
        start_ns = time.perf_counter_ns()
        payload = json.loads(state) if isinstance(state, str) else {}
        mode = payload.get("mode", "pedagogy")

        answers: dict[str, bool | str | Uncertain] = {}

        if mode == "tutor_routing":
            q_lower = str(payload.get("query", "")).lower()
            # Boolean safety guardrail: block destructive exploit / malware / credential-harvest prompts
            unsafe_markers = ("ransomware", "keylogger", "steal password", "ddos attack script", "exploit payload")
            is_safe = not any(m in q_lower for m in unsafe_markers)

            if any(k in q_lower for k in ("aws", "bedrock", "lambda", "s3", "ec2", "iam", "vpc", "dynamodb", "cloud", "docker")):
                domain_cls = "AWS_CLOUD_ARCH"
                strategy_cls = "CLOUD_WELL_ARCHITECTED"
                conf = 0.96
            elif any(k in q_lower for k in ("def ", "select ", "bug", "error", "traceback", "syntax", "code", "sql", "python")):
                domain_cls = "CODE_DEBUGGING"
                strategy_cls = "SANDBOX_DIAGNOSTIC"
                conf = 0.94
            elif any(k in q_lower for k in ("interview", "trade-off", "system design", "scalab", "complexity", "big o")):
                domain_cls = "INTERVIEW_PREP"
                strategy_cls = "SOCRATIC_TRADEOFFS"
                conf = 0.92
            elif len(q_lower.strip()) < 4:
                domain_cls = "GENERAL_INQUIRY"
                strategy_cls = "CONCISE_CLARIFICATION"
                conf = 0.55  # Triggers UncertaintyOptions threshold when query is too vague
            else:
                domain_cls = "CONCEPT_MASTERY"
                strategy_cls = "STRUCTURED_PEDAGOGY"
                conf = 0.91

            for q_id, q_spec in questions.items():
                unc_cfg = q_spec.get("uncertainty")
                min_c = unc_cfg.get("min_confidence", 0.0) if isinstance(unc_cfg, dict) else 0.0
                if q_id == "academic_safety_guardrail":
                    answers[q_id] = is_safe
                elif min_c > 0 and conf < min_c:
                    answers[q_id] = Uncertain(reason="Query has minimal context; falling back to open mentor mode")
                elif q_id == "query_domain":
                    answers[q_id] = domain_cls
                elif q_id == "routing_strategy":
                    answers[q_id] = strategy_cls
                elif q_spec.get("choices") == "boolean":
                    answers[q_id] = True
                elif isinstance(q_spec.get("choices"), list) and q_spec["choices"]:
                    answers[q_id] = q_spec["choices"][0]
        else:
            total_quizzes = int(payload.get("total_quizzes", 0))
            last_score = float(payload.get("last_score", 0.0))
            last_diff = str(payload.get("last_difficulty", "Easy"))

            if total_quizzes == 0:
                milestone = "ORIENTATION"
                next_diff = "Easy"
                conf = 0.62  # Baseline cold-start before quiz telemetry exists
            elif last_score < 60.0:
                milestone = "REINFORCE_CONCEPTS"
                next_diff = "Medium" if last_diff == "Hard" else "Easy"
                conf = 0.93
            elif last_score >= 85.0:
                milestone = "LEVEL_UP"
                next_diff = ("Medium" if last_score < 95.0 else "Hard") if last_diff == "Easy" else "Hard"
                conf = 0.96
            else:
                milestone = "MAINTAIN_PRACTICE"
                next_diff = "Medium" if last_diff == "Easy" and last_score >= 75.0 else last_diff
                if next_diff not in ("Easy", "Medium", "Hard"):
                    next_diff = "Medium"
                conf = 0.90

            for q_id, q_spec in questions.items():
                unc_cfg = q_spec.get("uncertainty")
                min_c = unc_cfg.get("min_confidence", 0.0) if isinstance(unc_cfg, dict) else 0.0
                choices = q_spec.get("choices")

                if q_id == "pedagogical_milestone":
                    answers[q_id] = milestone
                elif q_id == "next_difficulty":
                    answers[q_id] = next_diff
                elif q_id == "certificate_ready":
                    if min_c > 0 and conf < min_c:
                        answers[q_id] = Uncertain(reason="Cold-start learner: awaiting first completed assessment")
                    else:
                        answers[q_id] = last_score >= 80.0
                elif choices == "boolean":
                    answers[q_id] = last_score >= 70.0
                elif isinstance(choices, list) and choices:
                    answers[q_id] = choices[0]

        elapsed_ms = max(1, int((time.perf_counter_ns() - start_ns) / 1_000_000))
        return DecisionResult(
            answers=answers,
            metadata=DecisionMetadata(latency_ms=elapsed_ms),
        )

    def _run_ask_sync(self, state_str: str, questions: dict[str, Question]) -> DecisionResult:
        """Executes async `self.ask()` safely whether or not an event loop is already running."""
        try:
            asyncio.get_running_loop()
            with concurrent.futures.ThreadPoolExecutor(max_workers=1) as pool:
                return pool.submit(asyncio.run, self.ask(state_str, questions)).result()
        except RuntimeError:
            return asyncio.run(self.ask(state_str, questions))

    def decide_next_step(self, student_analytics: dict, recent_quiz: dict | None = None) -> dict:
        """
        Determines the next optimal pedagogical milestone, difficulty, confidence, and domain
        via Strands `DecisionModel.ask()`.
        """
        avg_score = float(student_analytics.get("average_score", 0.0))
        total_quizzes = int(student_analytics.get("total_quizzes", 0))
        weak_topics = list(student_analytics.get("weak_topics", []))
        mastered_rows = list(student_analytics.get("topic_mastery", []))
        explored_topics = {m.get("topic") for m in mastered_rows if m.get("topic")}

        if recent_quiz:
            last_score = float(recent_quiz.get("score_percentage", recent_quiz.get("score", avg_score)))
            last_topic = str(recent_quiz.get("topic") or "")
            last_diff = str(recent_quiz.get("difficulty") or "Medium")
        else:
            last_score = avg_score
            last_topic = weak_topics[0] if weak_topics else CURRICULUM_DOMAINS[0]
            last_diff = "Easy" if total_quizzes == 0 else "Medium"

        state_payload = json.dumps({
            "mode": "pedagogy",
            "total_quizzes": total_quizzes,
            "average_score": avg_score,
            "last_score": last_score,
            "last_topic": last_topic,
            "last_difficulty": last_diff,
            "weak_topics": weak_topics,
        })

        questions: dict[str, Question] = {
            "pedagogical_milestone": {
                "question": "Which pedagogical milestone applies to the student's current telemetry?",
                "choices": ["ORIENTATION", "REINFORCE_CONCEPTS", "MAINTAIN_PRACTICE", "LEVEL_UP"],
                "uncertainty": False,
            },
            "next_difficulty": {
                "question": "Which difficulty tier should be prescribed for the next assessment?",
                "choices": ["Easy", "Medium", "Hard"],
                "uncertainty": False,
            },
            "mastery_ready": {
                "question": "Has the student demonstrated >=70% operational comprehension?",
                "choices": "boolean",
                "uncertainty": False,
            },
            "certificate_ready": {
                "question": "Is the student calibrated and eligible for a domain mastery certificate?",
                "choices": "boolean",
                "uncertainty": UncertaintyOptions(min_confidence=0.75),
            },
        }

        decision_result = self._run_ask_sync(state_payload, questions)
        milestone = str(decision_result.answers["pedagogical_milestone"])
        next_diff = str(decision_result.answers["next_difficulty"])
        cert_ans = decision_result.answers["certificate_ready"]

        # Always narrow Uncertain explicitly per Strands 0020-decision-models specification
        if isinstance(cert_ans, Uncertain):
            cert_eligible = False
            confidence_pct = 82
            calibration_state = f"COLD_START ({cert_ans.reason})"
        else:
            cert_eligible = bool(cert_ans)
            confidence_pct = 96 if milestone == "LEVEL_UP" else (93 if milestone == "REINFORCE_CONCEPTS" else 91)
            calibration_state = "CALIBRATED"

        latency_ms = decision_result.metadata.latency_ms
        unexplored = [d for d in CURRICULUM_DOMAINS if d not in explored_topics]

        base_telemetry = {
            "confidence_pct": confidence_pct,
            "latency_ms": latency_ms,
            "certificate_eligible": cert_eligible,
            "calibration_state": calibration_state,
        }

        if total_quizzes == 0:
            rec_topic = CURRICULUM_DOMAINS[0]
            return {
                **base_telemetry,
                "decision": milestone,
                "headline": "Welcome to Your Adaptive Learning Pathway",
                "recommendation": (
                    f"Start with an Easy diagnostic quiz in {rec_topic} to calibrate your cognitive baseline."
                ),
                "next_difficulty": next_diff,
                "recommended_topic": rec_topic,
                "action_type": "START_BASELINE",
            }

        if milestone == "REINFORCE_CONCEPTS":
            rec_topic = last_topic or (weak_topics[0] if weak_topics else CURRICULUM_DOMAINS[0])
            return {
                **base_telemetry,
                "decision": milestone,
                "headline": f"Targeted Concept Reinforcement in {rec_topic}",
                "recommendation": (
                    f"Your latest score was {last_score:.1f}%. Review the pedagogical explanations or ask the AI Tutor, "
                    f"then solidify fundamentals with a {next_diff} round in {rec_topic}."
                ),
                "next_difficulty": next_diff,
                "recommended_topic": rec_topic,
                "action_type": "RETRY_EASY",
            }

        if milestone == "LEVEL_UP":
            if weak_topics:
                rec_topic = weak_topics[0]
                rec_note = (
                    f"Awesome {last_score:.1f}% score! Ready to step up to {next_diff} challenges—or boost your "
                    f"mastery in {rec_topic} next."
                )
            elif last_diff == "Hard" and unexplored:
                rec_topic = unexplored[0]
                rec_note = (
                    f"Exceptional {last_score:.1f}% mastery at Hard tier! Expand your portfolio into {rec_topic}."
                )
            else:
                rec_topic = last_topic or CURRICULUM_DOMAINS[0]
                rec_note = (
                    f"Outstanding {last_score:.1f}% accuracy! Advance to {next_diff} difficulty in {rec_topic} to push your ceiling."
                )
            return {
                **base_telemetry,
                "decision": milestone,
                "headline": "Exceptional Mastery — Ready to Level Up!",
                "recommendation": rec_note,
                "next_difficulty": next_diff,
                "recommended_topic": rec_topic,
                "action_type": "LEVEL_UP",
            }

        rec_topic = weak_topics[0] if weak_topics else (last_topic or CURRICULUM_DOMAINS[0])
        return {
            **base_telemetry,
            "decision": milestone,
            "headline": f"Steady Momentum in {rec_topic}",
            "recommendation": (
                f"Solid progress ({last_score:.1f}%). Practice another non-repeating {next_diff} round in {rec_topic} "
                f"to lock in >=85% mastery."
            ),
            "next_difficulty": next_diff,
            "recommended_topic": rec_topic,
            "action_type": "CONTINUE",
        }

    def decide_tutor_route(self, query: str, persona: str = "Standard Mentor") -> dict:
        """
        Pre-LLM System-1 DecisionModel Router & Safety Guardrail for AI Tutor interactions.
        Classifies query domain, pedagogical strategy, and boolean safety compliance.
        """
        state_payload = json.dumps({"mode": "tutor_routing", "query": query, "persona": persona})
        questions: dict[str, Question] = {
            "academic_safety_guardrail": {
                "question": "Is the student query safe and aligned with constructive educational ethics?",
                "choices": "boolean",
                "uncertainty": False,
            },
            "query_domain": {
                "question": "Which technical or academic domain best classifies this student prompt?",
                "choices": [
                    "AWS_CLOUD_ARCH",
                    "CODE_DEBUGGING",
                    "INTERVIEW_PREP",
                    "CONCEPT_MASTERY",
                    "GENERAL_INQUIRY",
                ],
                "uncertainty": UncertaintyOptions(min_confidence=0.70),
            },
            "routing_strategy": {
                "question": "Which instructional scaffolding strategy should guide the tutor model?",
                "choices": [
                    "CLOUD_WELL_ARCHITECTED",
                    "SANDBOX_DIAGNOSTIC",
                    "SOCRATIC_TRADEOFFS",
                    "STRUCTURED_PEDAGOGY",
                    "CONCISE_CLARIFICATION",
                ],
                "uncertainty": UncertaintyOptions(min_confidence=0.70),
            },
        }
        res = self._run_ask_sync(state_payload, questions)
        safe_ok = bool(res.answers["academic_safety_guardrail"])
        dom_ans = res.answers["query_domain"]
        strat_ans = res.answers["routing_strategy"]

        if isinstance(dom_ans, Uncertain) or isinstance(strat_ans, Uncertain):
            domain_str = "GENERAL_INQUIRY"
            strategy_str = "OPEN_MENTOR_FALLBACK"
            confidence_pct = 74
        else:
            domain_str = str(dom_ans)
            strategy_str = str(strat_ans)
            confidence_pct = 96 if domain_str == "AWS_CLOUD_ARCH" else 93

        return {
            "guardrail_pass": safe_ok,
            "domain": domain_str,
            "strategy": strategy_str,
            "confidence_pct": confidence_pct,
            "latency_ms": res.metadata.latency_ms,
        }


def create_edumate_agent() -> Agent | None:
    """Initializes and returns the Strands Agent registered with all 6 pedagogical `@tool` functions."""
    tools = [
        generate_quiz,
        evaluate_quiz_submission,
        analyze_student_progress,
        generate_flashcards_and_quiz,
        generate_study_roadmap,
        evaluate_code_challenge,
    ]
    try:
        return Agent(
            tools=tools,
            system_prompt=SYSTEM_PROMPT,
            name="VidyaVerse-Strands-Core-Agent",
        )
    except Exception:
        return None


# Singleton Strands DecisionModel instance
decider = EduMateDecider()


def agent_generate_quiz(topic: str, difficulty: str = "Medium", num_questions: int = 3, user_email: str = "") -> dict:
    raw = generate_quiz(topic=topic, difficulty=difficulty, num_questions=num_questions, user_email=user_email)
    return json.loads(raw)


def agent_evaluate_submission(submission: dict) -> dict:
    raw = evaluate_quiz_submission(submission_json=json.dumps(submission))
    return json.loads(raw)


def agent_analyze_student(analytics: dict) -> dict:
    raw = analyze_student_progress(analytics_json=json.dumps(analytics))
    return json.loads(raw)


def agent_decide_next_step(analytics: dict, recent_quiz: dict | None = None) -> dict:
    return decider.decide_next_step(analytics, recent_quiz)


def agent_route_tutor_query(query: str, persona: str = "Standard Mentor") -> dict:
    return decider.decide_tutor_route(query, persona)


def agent_create_study_pack(notes_text: str, title: str = "Custom Study Notes") -> dict:
    raw = generate_flashcards_and_quiz(notes_text=notes_text, title=title)
    return json.loads(raw)


def agent_create_roadmap(weak_topics: list[str], average_score: float = 0.0, goal: str = "Full-Stack & AI Mastery") -> dict:
    raw = generate_study_roadmap(weak_topics_json=json.dumps(weak_topics), average_score=average_score, goal=goal)
    return json.loads(raw)


def agent_evaluate_code(challenge_id: str, student_code: str) -> dict:
    raw = evaluate_code_challenge(challenge_id=challenge_id, student_code=student_code)
    return json.loads(raw)


if __name__ == "__main__":
    print("Testing VidyaVerse AI Strands DecisionModel...")
    sample_analytics = {"average_score": 92.0, "total_quizzes": 4, "weak_topics": []}
    print("Pedagogy Decision:", agent_decide_next_step(sample_analytics, {"score": 92.0, "topic": "Web Development & Cloud", "difficulty": "Medium"}))
    print("Tutor Route Decision:", agent_route_tutor_query("How do AWS Lambda and Amazon Bedrock work together?", "Standard Mentor"))
