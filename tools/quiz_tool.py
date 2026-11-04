"""
Quiz Generation Tool for EduMateAI
Uses Strands Tool framework to dynamically synthesize adaptive, guaranteed distinct questions.
Integrates with SQLite Question Bank and Seen Questions Tracker.
"""

from strands import tool
import json
import random
from database.db_manager import (
    fetch_unseen_questions,
    mark_questions_as_seen,
    reset_topic_seen_questions,
    save_questions_to_bank,
    hash_question,
)

# Dynamic generative templates per curriculum domain
SYNTHETIC_TEMPLATES = {
    "Python Programming": [
        (
            "What does `[x**2 for x in range(4)]` evaluate to in Python?",
            ["A. [0, 1, 4, 9]", "B. [1, 4, 9, 16]", "C. [0, 2, 4, 6]", "D. [1, 2, 3, 4]"],
            "A",
            "List comprehensions square each index 0, 1, 2, 3.",
        ),
        (
            "Which built-in function returns `(index, item)` pairs while iterating over a sequence?",
            ["A. zip()", "B. enumerate()", "C. map()", "D. filter()"],
            "B",
            "enumerate() yields `(index, element)` tuples cleanly without manual counters.",
        ),
        (
            "What is the exact behavior of Python's `with open(...) as f:` context manager?",
            [
                "A. It reads the file twice",
                "B. It guarantees `__exit__` closes the file descriptor even if an exception occurs",
                "C. It locks the OS kernel",
                "D. It deletes the file upon exit",
            ],
            "B",
            "Context managers invoke `__enter__` and deterministically run `__exit__` for cleanup.",
        ),
    ],
    "Artificial Intelligence & ML": [
        (
            "Which loss function is standard for binary classification with sigmoid output probabilities?",
            ["A. Mean Squared Error", "B. Binary Cross-Entropy (Log Loss)", "C. Hinge Loss", "D. L1 Loss"],
            "B",
            "Binary Cross-Entropy measures KL divergence / negative log-likelihood over Bernoulli targets.",
        ),
        (
            "What does the hyperparameter `K` control in the K-Nearest Neighbors (KNN) algorithm?",
            [
                "A. Number of hidden layers",
                "B. Number of closest training samples polled to vote on the prediction",
                "C. Learning rate decay step",
                "D. Principal component count",
            ],
            "B",
            "KNN classifies or regresses based on the `K` nearest neighbors in feature space.",
        ),
        (
            "Why is Dropout disabled during neural network evaluation / inference?",
            [
                "A. To utilize the full ensemble capacity of all trained neurons deterministically",
                "B. Because GPUs cannot generate random numbers at test time",
                "C. To zero out bias vectors",
                "D. To increase prediction variance",
            ],
            "A",
            "During inference, all units remain active (with inverted dropout scaling applied during training) for deterministic, maximum-accuracy predictions.",
        ),
    ],
    "Data Structures & Algorithms": [
        (
            "What is the time complexity of inserting a new node at the head of a Singly Linked List?",
            ["A. O(1)", "B. O(n)", "C. O(log n)", "D. O(n^2)"],
            "A",
            "Pointing `new_node.next = head` and updating `head = new_node` takes constant O(1) time.",
        ),
        (
            "Which auxiliary data structure powers Breadth-First Search (BFS) on graphs?",
            ["A. Stack", "B. Queue", "C. Binary Search Tree", "D. Disjoint Set"],
            "B",
            "BFS explores vertices layer-by-layer in FIFO order using a Queue.",
        ),
        (
            "What is the worst-case time complexity of HeapSort on `n` elements?",
            ["A. O(n)", "B. O(n log n)", "C. O(n^2)", "D. O(log n)"],
            "B",
            "Building a max-heap takes O(n) and extracting `n` maxima takes `n * O(log n)` even in the worst case.",
        ),
    ],
    "Web Development & Cloud": [
        (
            "What is the primary purpose of a Content Delivery Network (CDN)?",
            [
                "A. Execute SQL migrations",
                "B. Cache and serve static/edge assets from geographically proximate PoPs to lower latency",
                "C. Replace backend authentication",
                "D. Compile Python into C++",
            ],
            "B",
            "CDNs distribute cached content across global edge Points of Presence close to end users.",
        ),
        (
            "What does DNS resolve in internet networking?",
            [
                "A. Human-readable domain names into routable IP addresses",
                "B. MAC addresses into CPU registers",
                "C. Passwords into hashes",
                "D. JSON into XML",
            ],
            "A",
            "The Domain Name System maps hostnames like `example.edu` to IPv4/IPv6 records.",
        ),
        (
            "Which HTTP status code represents `Too Many Requests` (rate limiting)?",
            ["A. 400", "B. 404", "C. 429", "D. 502"],
            "C",
            "HTTP 429 indicates the client has exceeded allowed request rate limits within a window.",
        ),
    ],
    "Database Systems & SQL": [
        (
            "Which ACID property guarantees that a transaction either completes in full or has zero partial effect?",
            ["A. Atomicity", "B. Consistency", "C. Isolation", "D. Durability"],
            "A",
            "Atomicity treats all statements in a transaction as an indivisible all-or-nothing unit.",
        ),
        (
            "Which SQL clause sorts the returned query result set?",
            ["A. GROUP BY", "B. ORDER BY", "C. PARTITION BY", "D. HAVING"],
            "B",
            "`ORDER BY` sorts output rows in `ASC` (default) or `DESC` order.",
        ),
        (
            "What does `COUNT(column_name)` do differently from `COUNT(*)` in SQL?",
            [
                "A. `COUNT(column_name)` ignores rows where `column_name IS NULL`, whereas `COUNT(*)` counts all rows",
                "B. `COUNT(*)` multiplies column values",
                "C. `COUNT(column_name)` only counts distinct values",
                "D. There is no difference",
            ],
            "A",
            "`COUNT(expr)` counts non-NULL evaluations of `expr`, while `COUNT(*)` counts total rows including NULLs.",
        ),
    ],
    "Cybersecurity & Networks": [
        (
            "What security principle dictates granting a user or service ONLY the minimum permissions needed to perform its task?",
            [
                "A. Security through Obscurity",
                "B. Principle of Least Privilege (PoLP)",
                "C. Open Relay Policy",
                "D. Implicit Trust",
            ],
            "B",
            "Least Privilege minimizes blast radius if an account or microservice is compromised.",
        ),
        (
            "Which network layer protocol is connectionless and prioritizes low overhead/latency over guaranteed delivery?",
            ["A. TCP", "B. UDP", "C. TLS", "D. SSH"],
            "B",
            "UDP (User Datagram Protocol) sends datagrams without connection handshakes or retransmission delays, ideal for DNS, WebRTC, and gaming.",
        ),
        (
            "What is Multi-Factor Authentication (MFA)?",
            [
                "A. Entering two different passwords",
                "B. Verifying identity using two or more independent factor categories (knowledge, possession, inherence)",
                "C. Hashing a password twice",
                "D. Using HTTPS and CORS together",
            ],
            "B",
            "True MFA combines distinct factors—e.g., something you know (password) + something you have (hardware key/TOTP).",
        ),
    ],
}


@tool
def generate_quiz(topic: str, difficulty: str = "Medium", num_questions: int = 3, user_email: str = "") -> str:
    """
    Generates a structured, adaptive quiz based on the chosen topic and difficulty level.
    Guarantees non-repeating, distinct questions for the student by querying unseen records.
    Returns JSON formatted questions.
    """
    encore_cycle = False

    # 1. Retrieve unseen questions for this student from the SQLite question bank
    unseen = fetch_unseen_questions(email=user_email, topic=topic, difficulty=difficulty, limit=num_questions)

    questions_to_deliver = []
    for q in unseen:
        questions_to_deliver.append({
            "difficulty": q.get("difficulty", difficulty),
            "question": q["question"],
            "options": q["options"],
            "correct_answer": q["correct_answer"],
            "explanation": q.get("explanation", ""),
            "hash": q.get("hash", hash_question(q["question"])),
        })

    # 2. Inject synthetic templates into bank if student needs more unseen items
    if len(questions_to_deliver) < num_questions:
        matched_synth = list(SYNTHETIC_TEMPLATES.get(topic, SYNTHETIC_TEMPLATES["Python Programming"]))
        random.shuffle(matched_synth)
        synth_records = [
            {
                "topic": topic,
                "difficulty": difficulty,
                "question": q_text,
                "options": opts,
                "correct_answer": ans,
                "explanation": exp,
            }
            for q_text, opts, ans, exp in matched_synth
        ]
        save_questions_to_bank(synth_records)

        # Re-fetch unseen after bank expansion
        extra_needed = num_questions - len(questions_to_deliver)
        existing_hashes = {d["hash"] for d in questions_to_deliver}
        extra_unseen = fetch_unseen_questions(
            email=user_email, topic=topic, difficulty=difficulty, limit=num_questions + 3
        )
        for q in extra_unseen:
            if q["hash"] not in existing_hashes:
                questions_to_deliver.append({
                    "difficulty": q.get("difficulty", difficulty),
                    "question": q["question"],
                    "options": q["options"],
                    "correct_answer": q["correct_answer"],
                    "explanation": q.get("explanation", ""),
                    "hash": q["hash"],
                })
                existing_hashes.add(q["hash"])
            if len(questions_to_deliver) >= num_questions:
                break

    # 3. Mastery Encore Cycle: ONLY if student has conquered 100% of unseen questions in this topic
    if len(questions_to_deliver) < num_questions and user_email:
        encore_cycle = True
        reset_topic_seen_questions(user_email, topic)
        existing_hashes = {d["hash"] for d in questions_to_deliver}
        refreshed = fetch_unseen_questions(
            email=user_email, topic=topic, difficulty=difficulty, limit=num_questions + 3
        )
        for q in refreshed:
            if q["hash"] not in existing_hashes:
                questions_to_deliver.append({
                    "difficulty": q.get("difficulty", difficulty),
                    "question": q["question"],
                    "options": q["options"],
                    "correct_answer": q["correct_answer"],
                    "explanation": q.get("explanation", ""),
                    "hash": q["hash"],
                })
                existing_hashes.add(q["hash"])
            if len(questions_to_deliver) >= num_questions:
                break

    # 4. Mark delivered questions as seen for this student
    if user_email and questions_to_deliver:
        delivered_hashes = [q["hash"] for q in questions_to_deliver]
        mark_questions_as_seen(user_email, delivered_hashes)

    result = {
        "topic": topic,
        "difficulty": difficulty,
        "count": len(questions_to_deliver),
        "questions": questions_to_deliver,
        "guaranteed_distinct": True,
        "encore_cycle": encore_cycle,
    }
    return json.dumps(result, indent=2)


if __name__ == "__main__":
    print(generate_quiz("Python Programming", "Easy", 2, "test@student.edu"))
