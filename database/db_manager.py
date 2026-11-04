"""
Database and Authentication Manager for EduMateAI
Simple, clean SQLite persistence for users, quiz history, topic mastery,
non-repeating question hashes, mistake notebook, and coding lab progress.
"""

import sqlite3
import hashlib
import os
import datetime
import json
from pathlib import Path

DB_PATH = Path(__file__).parent / "student.db"


def get_connection():
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    return conn


def hash_question(question_text: str) -> str:
    """Generates a deterministic SHA-256 hash for a question to prevent duplicates."""
    clean = question_text.strip().lower()
    return hashlib.sha256(clean.encode("utf-8")).hexdigest()


def save_questions_to_bank(questions: list[dict]):
    """Bulk inserts questions into the database bank, ignoring duplicates."""
    with get_connection() as conn:
        cursor = conn.cursor()
        for q in questions:
            q_hash = hash_question(q["question"])
            cursor.execute(
                """
                INSERT OR IGNORE INTO questions_bank 
                (topic, difficulty, question, options_json, correct_answer, explanation, question_hash)
                VALUES (?, ?, ?, ?, ?, ?, ?)
                """,
                (
                    q.get("topic", "General"),
                    q.get("difficulty", "Medium"),
                    q["question"],
                    json.dumps(q["options"]),
                    q["correct_answer"],
                    q.get("explanation", ""),
                    q_hash,
                ),
            )
        conn.commit()


def init_db():
    """Initialize all SQLite tables and auto-seed the curriculum bank if needed."""
    with get_connection() as conn:
        cursor = conn.cursor()
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS users (
                email TEXT PRIMARY KEY COLLATE NOCASE,
                user_id TEXT NOT NULL,
                password_hash TEXT NOT NULL,
                salt TEXT NOT NULL,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                avatar TEXT DEFAULT '🎓'
            )
        """)
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS quiz_history (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                email TEXT NOT NULL,
                topic TEXT NOT NULL,
                difficulty TEXT NOT NULL,
                score REAL NOT NULL,
                total_questions INTEGER NOT NULL,
                feedback TEXT,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (email) REFERENCES users (email)
            )
        """)
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS topic_mastery (
                email TEXT NOT NULL,
                topic TEXT NOT NULL,
                mastery_score REAL NOT NULL DEFAULT 0.0,
                quizzes_taken INTEGER NOT NULL DEFAULT 0,
                last_updated TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                PRIMARY KEY (email, topic),
                FOREIGN KEY (email) REFERENCES users (email)
            )
        """)
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS questions_bank (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                topic TEXT NOT NULL,
                difficulty TEXT NOT NULL,
                question TEXT NOT NULL,
                options_json TEXT NOT NULL,
                correct_answer TEXT NOT NULL,
                explanation TEXT NOT NULL,
                question_hash TEXT UNIQUE NOT NULL
            )
        """)
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS student_seen_questions (
                email TEXT NOT NULL,
                question_hash TEXT NOT NULL,
                seen_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                PRIMARY KEY (email, question_hash),
                FOREIGN KEY (email) REFERENCES users (email)
            )
        """)
        # Mistake Notebook for Spaced-Repetition Redemption Mode
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS mistake_notebook (
                email TEXT NOT NULL,
                question_hash TEXT NOT NULL,
                topic TEXT NOT NULL,
                difficulty TEXT NOT NULL,
                question TEXT NOT NULL,
                options_json TEXT NOT NULL,
                correct_answer TEXT NOT NULL,
                explanation TEXT NOT NULL,
                missed_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                PRIMARY KEY (email, question_hash)
            )
        """)
        # Coding Lab Solved Challenges Tracker
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS coding_submissions (
                email TEXT NOT NULL,
                challenge_id TEXT NOT NULL,
                language TEXT NOT NULL,
                solved_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                PRIMARY KEY (email, challenge_id)
            )
        """)

        cursor.execute("SELECT COUNT(*) as cnt FROM questions_bank")
        bank_count = cursor.fetchone()["cnt"]
        conn.commit()

    if bank_count < 60:
        try:
            from database.seed_questions import CURRICULUM_DATASET
            save_questions_to_bank(CURRICULUM_DATASET)
        except Exception:
            pass


def _hash_password(password: str, salt: str = None) -> tuple[str, str]:
    if not salt:
        salt = os.urandom(16).hex()
    pwd_bytes = (password + salt).encode("utf-8")
    pwd_hash = hashlib.sha256(pwd_bytes).hexdigest()
    return pwd_hash, salt


def register_user(email: str, user_id: str, password: str, confirm_password: str) -> tuple[bool, str]:
    """Registers a new student. Returns exact string 'already the email id exists' on duplicate."""
    email_clean = email.strip().lower()
    user_id_clean = user_id.strip()

    if not email_clean or not user_id_clean or not password:
        return False, "All fields are required."
    if "@" not in email_clean or "." not in email_clean.split("@")[-1]:
        return False, "Please enter a valid email address."
    if password != confirm_password:
        return False, "Passwords do not match."
    if len(password) < 4:
        return False, "Password must be at least 4 characters long."

    with get_connection() as conn:
        cursor = conn.cursor()
        cursor.execute("SELECT email FROM users WHERE email = ?", (email_clean,))
        if cursor.fetchone():
            return False, "already the email id exists"

        pwd_hash, salt = _hash_password(password)
        cursor.execute(
            "INSERT INTO users (email, user_id, password_hash, salt) VALUES (?, ?, ?, ?)",
            (email_clean, user_id_clean, pwd_hash, salt),
        )
        conn.commit()
        return True, "Registration successful! You can now log in."


def authenticate_user(email: str, password: str) -> tuple[bool, dict | None, str]:
    """Authenticates a user via Email ID and password."""
    email_clean = email.strip().lower()
    if not email_clean or not password:
        return False, None, "Email and password are required."

    with get_connection() as conn:
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM users WHERE email = ?", (email_clean,))
        row = cursor.fetchone()
        if not row:
            return False, None, "Invalid email or password."

        computed_hash, _ = _hash_password(password, row["salt"])
        if computed_hash == row["password_hash"]:
            return True, {
                "email": row["email"],
                "user_id": row["user_id"],
                "created_at": row["created_at"],
                "avatar": row["avatar"],
            }, "Login successful."
        return False, None, "Invalid email or password."


def update_user_avatar(email: str, avatar: str) -> bool:
    if not email or not avatar:
        return False
    with get_connection() as conn:
        cursor = conn.cursor()
        cursor.execute("UPDATE users SET avatar = ? WHERE email = ?", (avatar, email.strip().lower()))
        conn.commit()
        return cursor.rowcount > 0


# -------------------------------------------------------------
# Mistake Notebook (Simple Spaced-Repetition Vault)
# -------------------------------------------------------------
def save_mistake(email: str, topic: str, difficulty: str, question_obj: dict):
    """Logs a missed question into the student's Mistake Notebook."""
    if not email or not question_obj.get("question"):
        return
    email_clean = email.strip().lower()
    q_hash = hash_question(question_obj["question"])
    with get_connection() as conn:
        conn.execute(
            """
            INSERT OR REPLACE INTO mistake_notebook
            (email, question_hash, topic, difficulty, question, options_json, correct_answer, explanation, missed_at)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, CURRENT_TIMESTAMP)
            """,
            (
                email_clean,
                q_hash,
                topic,
                difficulty,
                question_obj["question"],
                json.dumps(question_obj.get("options", [])),
                question_obj.get("correct_answer", ""),
                question_obj.get("explanation", ""),
            ),
        )
        conn.commit()


def resolve_mistake(email: str, question_text: str):
    """Removes a question from the Mistake Notebook once answered correctly in Redemption Mode."""
    if not email or not question_text:
        return
    q_hash = hash_question(question_text)
    with get_connection() as conn:
        conn.execute(
            "DELETE FROM mistake_notebook WHERE email = ? AND question_hash = ?",
            (email.strip().lower(), q_hash),
        )
        conn.commit()


def get_mistakes(email: str) -> list[dict]:
    """Returns all active missed questions in the student's Mistake Notebook."""
    if not email:
        return []
    with get_connection() as conn:
        rows = conn.execute(
            "SELECT * FROM mistake_notebook WHERE email = ? ORDER BY missed_at DESC",
            (email.strip().lower(),),
        ).fetchall()
        return [
            {
                "topic": r["topic"],
                "difficulty": r["difficulty"],
                "question": r["question"],
                "options": json.loads(r["options_json"]),
                "correct_answer": r["correct_answer"],
                "explanation": r["explanation"],
                "hash": r["question_hash"],
            }
            for r in rows
        ]


# -------------------------------------------------------------
# Coding Lab Progress Helpers
# -------------------------------------------------------------
def mark_coding_solved(email: str, challenge_id: str, language: str):
    if not email or not challenge_id:
        return
    with get_connection() as conn:
        conn.execute(
            """
            INSERT OR REPLACE INTO coding_submissions (email, challenge_id, language, solved_at)
            VALUES (?, ?, ?, CURRENT_TIMESTAMP)
            """,
            (email.strip().lower(), challenge_id, language),
        )
        conn.commit()


def get_solved_challenges(email: str) -> list[str]:
    if not email:
        return []
    with get_connection() as conn:
        rows = conn.execute(
            "SELECT challenge_id FROM coding_submissions WHERE email = ?",
            (email.strip().lower(),),
        ).fetchall()
        return [r["challenge_id"] for r in rows]


# -------------------------------------------------------------
# Analytics & Mastery Tracking
# -------------------------------------------------------------
def _compute_streak_days(quizzes: list[dict]) -> int:
    if not quizzes:
        return 0
    unique_dates = sorted({str(q["created_at"])[:10] for q in quizzes if q.get("created_at")}, reverse=True)
    if not unique_dates:
        return 1
    streak = 1
    try:
        prev_day = datetime.date.fromisoformat(unique_dates[0])
        for d_str in unique_dates[1:]:
            curr_day = datetime.date.fromisoformat(d_str)
            if (prev_day - curr_day).days == 1:
                streak += 1
                prev_day = curr_day
            else:
                break
    except Exception:
        return 1
    return streak


def _compute_badges(
    total_quizzes: int,
    avg_score: float,
    seen_count: int,
    strong_topics: list[str],
    quizzes: list[dict],
    coding_solved_count: int,
) -> list[dict]:
    badges = []
    if total_quizzes >= 1:
        badges.append({"icon": "🌱", "title": "First Milestone", "desc": "Completed your baseline adaptive assessment"})
    if any(q.get("score", 0) >= 100.0 for q in quizzes):
        badges.append({"icon": "💎", "title": "Flawless Precision", "desc": "Scored 100% on an assessment session"})
    if seen_count >= 10:
        badges.append({"icon": "🎲", "title": "Curiosity Explorer", "desc": "Solved 10+ distinct non-repeating questions"})
    if coding_solved_count >= 1:
        badges.append({"icon": "💻", "title": "Code Craftsman", "desc": f"Solved {coding_solved_count} hands-on Coding Lab challenge(s)"})
    if len(strong_topics) >= 2:
        badges.append({"icon": "🏛️", "title": "Multi-Domain Scholar", "desc": "Achieved >=70% mastery across multiple subjects"})
    if total_quizzes >= 5 and avg_score >= 85.0:
        badges.append({"icon": "👑", "title": "Strands Grandmaster", "desc": "Sustained >=85% mastery across 5+ quizzes"})
    return badges


def get_user_analytics(email: str) -> dict:
    """Computes profile metrics, badges, mistakes, coding lab count, and mastery analytics."""
    email_clean = email.strip().lower()
    with get_connection() as conn:
        cursor = conn.cursor()
        quizzes = [
            dict(r)
            for r in cursor.execute(
                "SELECT * FROM quiz_history WHERE email = ? ORDER BY created_at DESC, id DESC",
                (email_clean,),
            ).fetchall()
        ]
        mastery = [
            dict(r)
            for r in cursor.execute(
                "SELECT topic, mastery_score, quizzes_taken FROM topic_mastery WHERE email = ? ORDER BY mastery_score ASC",
                (email_clean,),
            ).fetchall()
        ]
        seen_count = cursor.execute(
            "SELECT COUNT(*) as count FROM student_seen_questions WHERE email = ?", (email_clean,)
        ).fetchone()["count"]
        bank_total = cursor.execute("SELECT COUNT(*) as count FROM questions_bank").fetchone()["count"]
        mistakes_count = cursor.execute(
            "SELECT COUNT(*) as count FROM mistake_notebook WHERE email = ?", (email_clean,)
        ).fetchone()["count"]
        coding_solved = [
            r["challenge_id"]
            for r in cursor.execute(
                "SELECT challenge_id FROM coding_submissions WHERE email = ?", (email_clean,)
            ).fetchall()
        ]

        total_quizzes = len(quizzes)
        avg_score = round(sum(q["score"] for q in quizzes) / total_quizzes, 1) if total_quizzes > 0 else 0.0
        best_score = round(max((q["score"] for q in quizzes), default=0.0), 1)
        total_q_answered = sum(int(q.get("total_questions", 0)) for q in quizzes)

        weak_topics = [m["topic"] for m in mastery if m["mastery_score"] < 70.0]
        strong_topics = [m["topic"] for m in mastery if m["mastery_score"] >= 70.0]
        certified_topics = [m for m in mastery if m["mastery_score"] >= 80.0]
        streak_days = _compute_streak_days(quizzes)
        xp_points = int(total_q_answered * 15 + len(coding_solved) * 40 + round(avg_score * total_quizzes * 0.5))

        return {
            "total_quizzes": total_quizzes,
            "average_score": avg_score,
            "best_score": best_score,
            "total_questions_answered": total_q_answered,
            "xp_points": xp_points,
            "quiz_history": quizzes,
            "topic_mastery": mastery,
            "weak_topics": weak_topics,
            "strong_topics": strong_topics,
            "certified_topics": certified_topics,
            "mistakes_count": mistakes_count,
            "coding_solved": coding_solved,
            "distinct_questions_seen": seen_count,
            "bank_total": bank_total,
            "streak_days": streak_days,
            "badges": _compute_badges(total_quizzes, avg_score, seen_count, strong_topics, quizzes, len(coding_solved)),
        }


def get_topic_bank_progress(email: str) -> list[dict]:
    email_clean = email.strip().lower() if email else ""
    with get_connection() as conn:
        rows = conn.execute(
            """
            SELECT qb.topic,
                   COUNT(qb.id) AS total_count,
                   SUM(CASE WHEN ssq.question_hash IS NOT NULL THEN 1 ELSE 0 END) AS seen_count
            FROM questions_bank qb
            LEFT JOIN student_seen_questions ssq
              ON qb.question_hash = ssq.question_hash AND ssq.email = ?
            GROUP BY qb.topic
            ORDER BY qb.topic ASC
            """,
            (email_clean,),
        ).fetchall()
        return [
            {
                "topic": r["topic"],
                "seen": r["seen_count"] or 0,
                "total": r["total_count"] or 1,
                "pct": round(((r["seen_count"] or 0) / (r["total_count"] or 1)) * 100, 1),
            }
            for r in rows
        ]


def save_quiz_result(email: str, topic: str, difficulty: str, score: float, total_questions: int, feedback: str = ""):
    email_clean = email.strip().lower()
    with get_connection() as conn:
        cursor = conn.cursor()
        cursor.execute(
            """
            INSERT INTO quiz_history (email, topic, difficulty, score, total_questions, feedback)
            VALUES (?, ?, ?, ?, ?, ?)
            """,
            (email_clean, topic, difficulty, score, total_questions, feedback),
        )
        row = cursor.execute(
            "SELECT mastery_score, quizzes_taken FROM topic_mastery WHERE email = ? AND topic = ?",
            (email_clean, topic),
        ).fetchone()
        if row:
            new_score = round(((row["mastery_score"] * row["quizzes_taken"]) + score) / (row["quizzes_taken"] + 1), 1)
            cursor.execute(
                """
                UPDATE topic_mastery 
                SET mastery_score = ?, quizzes_taken = ?, last_updated = CURRENT_TIMESTAMP
                WHERE email = ? AND topic = ?
                """,
                (new_score, row["quizzes_taken"] + 1, email_clean, topic),
            )
        else:
            cursor.execute(
                "INSERT INTO topic_mastery (email, topic, mastery_score, quizzes_taken) VALUES (?, ?, ?, 1)",
                (email_clean, topic, score),
            )
        conn.commit()


def mark_questions_as_seen(email: str, question_hashes: list[str]):
    if not email or not question_hashes:
        return
    email_clean = email.strip().lower()
    with get_connection() as conn:
        for h in question_hashes:
            conn.execute(
                "INSERT OR IGNORE INTO student_seen_questions (email, question_hash) VALUES (?, ?)",
                (email_clean, h),
            )
        conn.commit()


def reset_topic_seen_questions(email: str, topic: str):
    if not email or not topic:
        return
    with get_connection() as conn:
        conn.execute(
            """
            DELETE FROM student_seen_questions
            WHERE email = ? AND question_hash IN (
                SELECT question_hash FROM questions_bank WHERE topic LIKE ?
            )
            """,
            (email.strip().lower(), f"%{topic}%"),
        )
        conn.commit()


def fetch_unseen_questions(email: str, topic: str, difficulty: str, limit: int = 3) -> list[dict]:
    email_clean = email.strip().lower() if email else ""
    with get_connection() as conn:
        cursor = conn.cursor()
        rows = cursor.execute(
            """
            SELECT * FROM questions_bank
            WHERE topic LIKE ? AND difficulty = ?
            AND question_hash NOT IN (
                SELECT question_hash FROM student_seen_questions WHERE email = ?
            )
            ORDER BY RANDOM()
            LIMIT ?
            """,
            (f"%{topic}%", difficulty, email_clean, limit),
        ).fetchall()

        if len(rows) < limit:
            needed = limit - len(rows)
            existing_ids = [r["id"] for r in rows]
            id_placeholder = f"AND id NOT IN ({','.join(['?'] * len(existing_ids))})" if existing_ids else ""
            params = [f"%{topic}%"] + existing_ids + [email_clean, needed]
            rows.extend(
                cursor.execute(
                    f"""
                    SELECT * FROM questions_bank
                    WHERE topic LIKE ?
                    {id_placeholder}
                    AND question_hash NOT IN (
                        SELECT question_hash FROM student_seen_questions WHERE email = ?
                    )
                    ORDER BY RANDOM()
                    LIMIT ?
                    """,
                    params,
                ).fetchall()
            )

        return [
            {
                "question": r["question"],
                "options": json.loads(r["options_json"]),
                "correct_answer": r["correct_answer"],
                "explanation": r["explanation"],
                "difficulty": r["difficulty"],
                "topic": r["topic"],
                "hash": r["question_hash"],
            }
            for r in rows
        ]


init_db()
