"""
Evaluation Tool for EduMateAI
Uses Strands Tool framework to assess student answers and provide constructive feedback.
"""

from strands import tool
import json

@tool
def evaluate_quiz_submission(submission_json: str) -> str:
    """
    Evaluates student quiz responses against answer keys.
    Takes a JSON string with format:
    {
      "topic": "Python Programming",
      "difficulty": "Medium",
      "responses": [
        {"question": "...", "selected": "B", "correct_answer": "B", "explanation": "..."}
      ]
    }
    Returns evaluation report with score, percentage, and constructive pedagogical feedback.
    """
    try:
        data = json.loads(submission_json)
    except Exception as e:
        return json.dumps({"error": f"Invalid submission payload: {str(e)}"})

    topic = data.get("topic", "General")
    difficulty = data.get("difficulty", "Medium")
    responses = data.get("responses", [])

    total = len(responses)
    if total == 0:
        return json.dumps({"score": 0, "total": 0, "percentage": 0, "feedback": "No questions submitted."})

    correct_count = 0
    breakdown = []

    for idx, item in enumerate(responses, 1):
        selected = str(item.get("selected", "")).strip().upper()
        # Normalise: if user picked "B. Tuple", extract "B"
        selected_code = selected[0] if len(selected) > 0 else ""
        correct_code = str(item.get("correct_answer", "")).strip().upper()[:1]

        is_correct = (selected_code == correct_code)
        if is_correct:
            correct_count += 1

        breakdown.append({
            "question_num": idx,
            "question": item.get("question"),
            "selected": selected,
            "correct_answer": item.get("correct_answer"),
            "is_correct": is_correct,
            "explanation": item.get("explanation", "")
        })

    percentage = round((correct_count / total) * 100, 1)

    # Human-centric encouraging feedback
    if percentage >= 90:
        remark = "Outstanding mastery! You demonstrated thorough conceptual understanding."
    elif percentage >= 70:
        remark = "Solid performance! You have a good grasp of the foundational concepts with room for fine-tuning."
    elif percentage >= 50:
        remark = "Fair effort. Reviewing the detailed explanations below will boost your confidence and mastery."
    else:
        remark = "Foundational reinforcement needed. Don't worry—review the key takeaways and try another round!"

    evaluation = {
        "topic": topic,
        "difficulty": difficulty,
        "total_questions": total,
        "correct_count": correct_count,
        "score_percentage": percentage,
        "remark": remark,
        "breakdown": breakdown
    }

    return json.dumps(evaluation, indent=2)

if __name__ == "__main__":
    test_sub = {
        "topic": "Python",
        "difficulty": "Easy",
        "responses": [
            {"question": "Q1", "selected": "B", "correct_answer": "B", "explanation": "Correct!"},
            {"question": "Q2", "selected": "A", "correct_answer": "C", "explanation": "Actual is C"}
        ]
    }
    print(evaluate_quiz_submission(json.dumps(test_sub)))

