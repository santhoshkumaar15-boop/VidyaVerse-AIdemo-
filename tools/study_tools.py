"""
Simple Strands Study Tools for EduMateAI
1. Notes-to-Flashcards & Custom Quiz Generator
2. 7-Day Personalized AI Study Roadmap Builder
"""

import json
import re
from strands import tool


def _extract_pairs_from_notes(notes_text: str) -> list[tuple[str, str]]:
    """Extracts simple (term, explanation) pairs from bullet points, colons, or sentences."""
    lines = [
        re.sub(r"^[\-\*\d\.\)\s]+", "", ln).strip()
        for ln in notes_text.splitlines()
        if len(ln.strip()) > 10
    ]
    if not lines:
        lines = [s.strip() for s in re.split(r"(?<=[.!?])\s+", notes_text.strip()) if len(s.strip()) > 12]

    pairs = []
    for ln in lines:
        if ":" in ln:
            head, tail = ln.split(":", 1)
            if 2 <= len(head.strip()) <= 60 and len(tail.strip()) >= 8:
                pairs.append((head.strip(), tail.strip()))
                continue
        if " - " in ln:
            head, tail = ln.split(" - ", 1)
            if 2 <= len(head.strip()) <= 60 and len(tail.strip()) >= 8:
                pairs.append((head.strip(), tail.strip()))
                continue
        match_is = re.match(r"^([A-Za-z0-9_/\s\(\)]{3,45}?)\s+(?:is|are|means|refers to)\s+(.+)$", ln)
        if match_is:
            pairs.append((match_is.group(1).strip(), match_is.group(2).strip()))
        else:
            words = ln.split()
            short_title = " ".join(words[:4]).rstrip(",.;:") + "..."
            pairs.append((short_title, ln))

    return pairs[:6]


@tool
def generate_flashcards_and_quiz(notes_text: str, title: str = "Custom Study Notes") -> str:
    """
    Converts pasted lecture notes or study material into interactive flashcards and a quick quiz.
    Uses clean, deterministic extraction so it works instantaneously on any text.
    """
    clean_text = (notes_text or "").strip()
    if len(clean_text) < 20:
        return json.dumps({"error": "Please provide at least a couple of sentences or bullet points of notes."})

    pairs = _extract_pairs_from_notes(clean_text)
    if not pairs:
        pairs = [(title, clean_text[:220])]

    flashcards = [
        {"front": term, "back": desc}
        for term, desc in pairs
    ]

    # Build up to 4 clean multiple-choice review questions from the extracted pairs
    distractor_pool = [
        "An unrelated hardware clock interrupt signal.",
        "A deprecated legacy compiler flag with no runtime effect.",
        "A static CSS layout property for browser margins.",
        "None of the listed descriptions apply.",
    ]

    quiz_items = []
    all_backs = [p[1] for p in pairs]
    letters = ["A", "B", "C", "D"]

    for idx, (term, correct_desc) in enumerate(pairs[:4]):
        wrong_choices = [b for j, b in enumerate(all_backs) if j != idx][:3]
        for fallback_d in distractor_pool:
            if len(wrong_choices) >= 3:
                break
            if fallback_d not in wrong_choices:
                wrong_choices.append(fallback_d)

        # Place correct option deterministically at rotated position (idx % 4)
        pos = idx % 4
        raw_opts = wrong_choices[:pos] + [correct_desc] + wrong_choices[pos:3]
        formatted_opts = [f"{letters[i]}. {opt}" for i, opt in enumerate(raw_opts)]

        quiz_items.append({
            "question": f"According to your notes on '{title}', what best describes {term}?",
            "options": formatted_opts,
            "correct_answer": letters[pos],
            "explanation": f"From your study notes: {term} — {correct_desc}",
        })

    return json.dumps(
        {
            "title": title,
            "flashcards": flashcards,
            "quiz": quiz_items,
        },
        indent=2,
    )


@tool
def generate_study_roadmap(weak_topics_json: str = "[]", average_score: float = 0.0, goal: str = "Full-Stack & AI Mastery") -> str:
    """
    Generates a clear 7-Day Personalized Study Roadmap tailored to the student's weak domains and goal.
    """
    try:
        weak_list = json.loads(weak_topics_json) if weak_topics_json else []
    except Exception:
        weak_list = []

    primary_focus = weak_list[0] if len(weak_list) >= 1 else "Python Programming"
    secondary_focus = weak_list[1] if len(weak_list) >= 2 else "Data Structures & Algorithms"
    target_diff = "Easy" if average_score < 60 else ("Medium" if average_score < 85 else "Hard")

    days = [
        {
            "day": "Day 1",
            "title": f"Diagnostic & Core Primitives: {primary_focus}",
            "domain": primary_focus,
            "difficulty": target_diff,
            "task": f"Complete a 3-question adaptive round in {primary_focus} and review every rubric explanation.",
            "action_page": "pages/1_Adaptive_Quiz.py",
            "action_label": "Start Day 1 Quiz",
        },
        {
            "day": "Day 2",
            "title": "Hands-On Python Algorithm Lab",
            "domain": "Python Programming",
            "difficulty": target_diff,
            "task": "Write and pass a live unit-tested Python function inside the Interactive Coding Lab.",
            "action_page": "pages/7_Coding_Lab.py",
            "action_label": "Open Coding Lab",
        },
        {
            "day": "Day 3",
            "title": f"Problem-Solving Deep Dive: {secondary_focus}",
            "domain": secondary_focus,
            "difficulty": target_diff,
            "task": f"Solve unseen {secondary_focus} problems and clarify tricky trade-offs in Socratic Tutor mode.",
            "action_page": "pages/1_Adaptive_Quiz.py",
            "action_label": "Start Day 3 Quiz",
        },
        {
            "day": "Day 4",
            "title": "Relational Schemas & Live SQL Sandbox",
            "domain": "Database Systems & SQL",
            "difficulty": "Medium",
            "task": "Practice SQL joins/aggregations in the Coding Lab, then take a Database Systems quiz.",
            "action_page": "pages/7_Coding_Lab.py",
            "action_label": "Practice SQL Lab",
        },
        {
            "day": "Day 5",
            "title": "AI, Transformers & Modern Cloud Systems",
            "domain": "Artificial Intelligence & ML",
            "difficulty": target_diff,
            "task": "Master AI/ML concepts and convert your own revision summary into interactive Flip Flashcards.",
            "action_page": "pages/1_Adaptive_Quiz.py",
            "action_label": "Start AI/ML Quiz",
        },
        {
            "day": "Day 6",
            "title": "Spaced-Repetition Mistake Redemption",
            "domain": "Cybersecurity & Networks",
            "difficulty": target_diff,
            "task": "Clear any items in your Mistake Notebook via Redemption Mode and complete a Security check.",
            "action_page": "pages/1_Adaptive_Quiz.py",
            "action_label": "Launch Redemption",
        },
        {
            "day": "Day 7",
            "title": f"Timed Mock Exam & Certificate Milestone ({goal})",
            "domain": primary_focus,
            "difficulty": "Hard" if average_score >= 75 else "Medium",
            "task": "Complete a Timed Exam Simulation scoring >= 80% to unlock your Printable Mastery Certificate!",
            "action_page": "pages/1_Adaptive_Quiz.py",
            "action_label": "Take Final Exam",
        },
    ]

    return json.dumps({"goal": goal, "recommended_tier": target_diff, "days": days}, indent=2)
