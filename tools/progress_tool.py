"""
Progress Tool for EduMateAI
Uses Strands Tool framework to compute mastery indicators, analyze weak topics, and suggest next steps.
"""

from strands import tool
import json

@tool
def analyze_student_progress(analytics_json: str) -> str:
    """
    Analyzes historical quiz performance and topic mastery.
    Takes JSON string containing student quiz records and topic mastery.
    Returns targeted recommendations, adaptive difficulty adjustments, and strength/weakness analysis.
    """
    try:
        data = json.loads(analytics_json)
    except Exception as e:
        return json.dumps({"error": f"Invalid analytics payload: {str(e)}"})

    total_quizzes = data.get("total_quizzes", 0)
    avg_score = data.get("average_score", 0.0)
    topic_mastery = data.get("topic_mastery", [])
    weak_topics = data.get("weak_topics", [])
    strong_topics = data.get("strong_topics", [])

    # Pedagogical adaptive recommendation
    if avg_score >= 80:
        recommended_level = "Hard"
        study_advice = "Ready for advanced problem-solving and architectural edge cases."
    elif avg_score >= 60:
        recommended_level = "Medium"
        study_advice = "Focus on intermediate design patterns and algorithmic optimization."
    else:
        recommended_level = "Easy"
        study_advice = "Solidify core syntax, data types, and primary primitives before advancing."

    insights = {
        "overall_status": "Mastery Advancing" if avg_score >= 70 else "Active Practice Recommended",
        "recommended_difficulty": recommended_level,
        "study_advice": study_advice,
        "weak_topics_count": len(weak_topics),
        "strong_topics_count": len(strong_topics),
        "focus_areas": weak_topics if weak_topics else ["Keep practicing diverse domains!"]
    }

    return json.dumps(insights, indent=2)

if __name__ == "__main__":
    sample = {
        "total_quizzes": 3,
        "average_score": 75.0,
        "topic_mastery": [{"topic": "Python", "mastery_score": 85.0}],
        "weak_topics": [],
        "strong_topics": ["Python"]
    }
    print(analyze_student_progress(json.dumps(sample)))

