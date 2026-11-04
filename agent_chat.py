"""
AI Academic Tutor & Universal Doubt Clearance Engine for EduMateAI
Powered live by Google GenAI models configured securely via environment variables,
with seamless multi-model routing and encyclopedic/computational resilience.
"""

import ast
import json
import operator
import os
import re
import urllib.parse
import urllib.request
from pathlib import Path

from dotenv import load_dotenv
from components.i18n import LANGUAGE_NAMES, tr

# Load API credentials strictly from .env without hardcoding secrets in source code
ENV_PATH = Path(__file__).resolve().parent / ".env"
load_dotenv(dotenv_path=ENV_PATH, override=False)

# Live model cascade ordered by availability and separate quota pools
MODELS = [
    "gemini-3-flash-preview",
    "gemma-4-26b-a4b-it",
    "gemini-3.5-flash-lite",
    "gemini-3.7-flash",
    "gemini-3.6-flash",
    "gemini-3.5-flash",
    "gemini-3.8-flash",
]

TUTOR_PERSONAS = {
    "Standard Mentor": (
        "You are VidyaVerse AI Tutor, a warm, knowledgeable AI mentor. Answer ANY question clearly "
        "with structured Markdown explanations and examples."
    ),
    "Socratic Guide": (
        "You are VidyaVerse AI in Socratic Guide mode. Instead of giving a dry lecture, walk the student "
        "through intuition, helpful hints, and end with one short thought-provoking check question."
    ),
    "Mock Interviewer": (
        "You are VidyaVerse AI acting as a supportive Senior Technical Interviewer. Answer or evaluate the "
        "topic concisely, highlight key edge cases or complexity trade-offs, and ask one realistic follow-up interview question."
    ),
    "Simple Intuition": (
        "You are VidyaVerse AI in Simple Intuition (ELI12) mode. Explain any concept using everyday, "
        "crystal-clear analogies and simple language before introducing technical terms."
    ),
}

# Built-in instant reference knowledge for offline or high-traffic resilience
FALLBACK_KNOWLEDGE = {
    r"president of india": (
        "The current President of India is **Droupadi Murmu**. "
        "She assumed office on **July 25, 2022**, serving as the 15th President of India. "
        "She is the first person from a tribal community and the second woman (after Pratibha Patil) "
        "to hold India's highest constitutional office."
    ),
    r"prime minister of india": (
        "The Prime Minister of India is **Narendra Modi**, serving in office since May 2014."
    ),
    r"capital of india": "The capital of India is **New Delhi**.",
    r"capital of france": "The capital of France is **Paris**.",
    r"capital of japan": "The capital of Japan is **Tokyo**.",
    r"binary search": (
        "### Binary Search\n"
        "**Binary Search** locates a target value inside a **sorted** array by repeatedly halving the search interval.\n\n"
        "1. Compare `target` with the middle element `arr[mid]`.\n"
        "2. If equal, return `mid`.\n"
        "3. If `target < arr[mid]`, search the left half; otherwise search the right half.\n\n"
        "- **Time Complexity:** `O(log n)`\n"
        "- **Space Complexity:** `O(1)` iterative / `O(log n)` recursive"
    ),
    r"quicksort|mergesort": (
        "### QuickSort vs. MergeSort\n\n"
        "| Feature | QuickSort | MergeSort |\n"
        "|---|---|---|\n"
        "| **Average Time** | `O(n log n)` | `O(n log n)` |\n"
        "| **Worst-Case Time** | `O(n^2)` (mitigated by random/median-of-3 pivot) | `O(n log n)` guaranteed |\n"
        "| **Auxiliary Space** | `O(log n)` stack (in-place partitioning) | `O(n)` auxiliary array |\n"
        "| **Stability** | Unstable | **Stable** |\n\n"
        "- Choose **QuickSort** for cache-friendly in-memory arrays when extra RAM is tight.\n"
        "- Choose **MergeSort** when **stability** or guaranteed worst-case `O(n log n)` matters (or for linked lists)."
    ),
    r"mutable vs immutable|immutable": (
        "### Mutable vs. Immutable Types in Python\n\n"
        "- **Immutable Objects** cannot be altered in place after creation; operations return a brand-new object (`int`, `float`, `bool`, `str`, `tuple`, `frozenset`, `bytes`). Because their hash never changes, immutable objects can serve as `dict` keys and `set` members.\n"
        "- **Mutable Objects** allow in-place modification without changing object identity `id(obj)` (`list`, `dict`, `set`, `bytearray`). Be careful when passing them into functions or avoiding mutable default arguments!"
    ),
    r"transformer|self-attention|attention mechanism": (
        "### Transformer Self-Attention\n"
        "**Self-Attention** allows every token in a sequence to weigh the relevance of every other token dynamically in parallel:\n\n"
        "1. Project each token embedding into **Query (`Q`)**, **Key (`K`)**, and **Value (`V`)** vectors.\n"
        "2. Compute scaled similarity scores: `Attention(Q, K, V) = Softmax((Q @ K^T) / sqrt(d_k)) @ V`.\n"
        "3. Dividing by `sqrt(d_k)` prevents dot products from growing too large and saturating Softmax gradients.\n"
        "4. **Multi-Head Attention** runs several attention heads in parallel so the model captures syntax, coreference, and long-range semantics simultaneously."
    ),
    r"1nf|2nf|3nf|normalization": (
        "### Relational Database Normalization (1NF -> 2NF -> 3NF)\n\n"
        "- **1NF (First Normal Form):** Every column stores **atomic** (indivisible) values—no repeating groups or comma-separated lists in a cell.\n"
        "- **2NF (Second Normal Form):** Meets 1NF + **no partial dependency** (every non-key column depends on the *entire* composite primary key, not just part of it).\n"
        "- **3NF (Third Normal Form):** Meets 2NF + **no transitive dependency** (non-key columns depend *only* on the primary key, never on another non-key column)."
    ),
    r"photosynthesis": (
        "### Photosynthesis\n"
        "**Photosynthesis** is the biochemical process by which green plants, algae, and cyanobacteria convert light energy into chemical energy:\n\n"
        "`6 CO2 + 6 H2O + Light Energy -> C6H12O6 (Glucose) + 6 O2`\n\n"
        "- **Light-Dependent Reactions (Thylakoid membranes):** Chlorophyll absorbs photons, splits water (`H2O`), releases oxygen (`O2`), and produces `ATP` and `NADPH`.\n"
        "- **Calvin Cycle (Stroma):** Uses `ATP` and `NADPH` to fix `CO2` into glucose."
    ),
    r"acid properties|acid in sql": (
        "### ACID Properties in Databases\n"
        "- **Atomicity:** All operations in a transaction succeed together or roll back completely.\n"
        "- **Consistency:** Every committed transaction moves the database from one valid schema/constraint state to another.\n"
        "- **Isolation:** Concurrent transactions execute without exposing uncommitted intermediate state.\n"
        "- **Durability:** Once committed, changes survive crashes via Write-Ahead Logging (`WAL`)."
    ),
    r"aws|bedrock|lambda|fargate": (
        "### Deploying Production Strands AI Agents on AWS (`Lambda` vs `ECS Fargate` + `Amazon Bedrock`)\n\n"
        "| Layer / Service | Ideal Workload | Architectural Role |\n"
        "|---|---|---|\n"
        "| **AWS Lambda** | Event-driven, bursty invocations (`<= 15 min`) | Serverless `@tool` execution & lightweight Strands `DecisionModel` webhook endpoints with scale-to-zero cost |\n"
        "| **Amazon ECS Fargate** | Long-lived streaming UIs, WebSockets, concurrent sessions | Serverless container compute hosting stateful/streaming agent studios (like Streamlit/FastAPI) behind an `ALB` |\n"
        "| **Amazon Bedrock** | Foundation Models + `Knowledge Bases` + `Guardrails` | Managed multi-model inference (`Claude`, `Nova`, `Llama`) with grounded RAG citations and PII/safety filtering |\n\n"
        "- **Best Practice:** Authenticate via **IAM Roles** (zero static secrets), run **Strands `DecisionModel`** as a fast System-1 router/guardrail, and persist session telemetry in **Amazon DynamoDB**."
    ),
}

_SAFE_OPS = {
    ast.Add: operator.add,
    ast.Sub: operator.sub,
    ast.Mult: operator.mul,
    ast.Div: operator.truediv,
    ast.FloorDiv: operator.floordiv,
    ast.Mod: operator.mod,
    ast.Pow: operator.pow,
    ast.USub: operator.neg,
    ast.UAdd: operator.pos,
}


def _eval_ast_math(node):
    if isinstance(node, ast.Constant) and isinstance(node.value, (int, float)):
        return node.value
    if isinstance(node, ast.BinOp) and type(node.op) in _SAFE_OPS:
        left = _eval_ast_math(node.left)
        right = _eval_ast_math(node.right)
        if isinstance(node.op, ast.Pow) and abs(right) > 1000:
            raise ValueError("Exponent too large")
        return _SAFE_OPS[type(node.op)](left, right)
    if isinstance(node, ast.UnaryOp) and type(node.op) in _SAFE_OPS:
        return _SAFE_OPS[type(node.op)](_eval_ast_math(node.operand))
    raise ValueError("Unsupported expression")


def _try_math_calculation(query: str) -> str | None:
    expr_candidate = re.sub(
        r"^(what\s+is|calculate|compute|solve|evaluate)\s+", "", query.strip().lower()
    ).rstrip("?= ")
    expr_candidate = expr_candidate.replace("^", "**")
    if not re.fullmatch(r"[\d\.\s\+\-\*\/\%\(\)]+", expr_candidate) or not re.search(r"[\+\-\*\/\%]", expr_candidate):
        return None
    try:
        tree = ast.parse(expr_candidate, mode="eval")
        val = _eval_ast_math(tree.body)
        formatted = int(val) if isinstance(val, float) and val.is_integer() else round(val, 6)
        return f"### Calculation Result\n\n`{expr_candidate}` = **{formatted}**"
    except Exception:
        return None


def _try_wikipedia_summary(query: str) -> str | None:
    """Queries Wikipedia REST summary when cloud LLM endpoints are unreachable."""
    cleaned = re.sub(
        r"^(who\s+is|who\s+was|what\s+is|what\s+are|tell\s+me\s+about|explain|define|where\s+is)\s+(the\s+|a\s+|an\s+)?",
        "",
        query.strip(),
        flags=re.IGNORECASE,
    ).strip(" ?!.")
    if not cleaned or len(cleaned) < 2:
        return None

    headers = {"User-Agent": "EduMateAI-AcademicTutor/1.0 (Educational Platform)"}
    try:
        search_url = (
            "https://en.wikipedia.org/w/api.php?action=opensearch&limit=1&namespace=0&format=json&search="
            + urllib.parse.quote(cleaned)
        )
        req = urllib.request.Request(search_url, headers=headers)
        with urllib.request.urlopen(req, timeout=4) as resp:
            data = json.loads(resp.read().decode("utf-8"))
        titles = data[1] if isinstance(data, list) and len(data) > 1 else []
        if not titles:
            return None

        best_title = titles[0]
        sum_url = "https://en.wikipedia.org/api/rest_v1/page/summary/" + urllib.parse.quote(
            best_title.replace(" ", "_")
        )
        req_sum = urllib.request.Request(sum_url, headers=headers)
        with urllib.request.urlopen(req_sum, timeout=4) as resp_sum:
            summary_json = json.loads(resp_sum.read().decode("utf-8"))
        extract = summary_json.get("extract", "").strip()
        if extract:
            title_disp = summary_json.get("title", best_title)
            return f"### {title_disp}\n\n{extract}"
    except Exception:
        return None
    return None


def _get_api_key() -> str:
    load_dotenv(dotenv_path=ENV_PATH, override=False)
    return (os.getenv("STRANDS_API_KEY") or os.getenv("GEMINI_API_KEY") or "").strip()


def ask_tutor(
    messages: list[dict],
    user_query: str,
    persona: str = "Standard Mentor",
    lang: str = "en",
    routing_strategy: str = "",
) -> str:
    """
    Answers any student or general-knowledge question cleanly using live Google GenAI models,
    conditioned by the Strands DecisionModel System-1 routing strategy, adapting tone to the
    selected teaching persona and responding in the chosen language (`en`, `ta`, `hi`, `te`, `ml`, `kn`).
    """
    clean_q = user_query.strip()
    if not clean_q:
        return tr("Please enter a question or topic you would like me to explain!", lang)

    persona_instruction = TUTOR_PERSONAS.get(persona, TUTOR_PERSONAS["Standard Mentor"])
    if routing_strategy == "CLOUD_WELL_ARCHITECTED":
        persona_instruction += (
            " Align cloud explanations with the AWS Well-Architected Framework "
            "(Security, Reliability, Performance Efficiency, Cost Optimization, Operational Excellence)."
        )
    elif routing_strategy == "SANDBOX_DIAGNOSTIC":
        persona_instruction += " Provide runnable, bug-free code examples and highlight root-cause diagnostics."
    elif routing_strategy == "SOCRATIC_TRADEOFFS":
        persona_instruction += " Emphasize architectural trade-offs, Big-O bounds, and real-world system scale."

    lang_name = LANGUAGE_NAMES.get(lang, "English")
    if lang != "en":
        persona_instruction += (
            f" CRITICAL LANGUAGE REQUIREMENT: Write your entire explanation in {lang_name}, "
            "keeping programming code or SQL snippets in valid code syntax."
        )

    key = _get_api_key()

    # 1. Live Multi-Model AI Generation
    if key:
        try:
            from google import genai

            client = genai.Client(api_key=key)
            history_lines = [f"System Instruction: {persona_instruction}", ""]
            for msg in messages[-6:]:
                role_label = "Student" if msg.get("role") == "user" else "Tutor"
                content_text = str(msg.get("content", "")).strip()
                if content_text:
                    history_lines.append(f"{role_label}: {content_text}")
            history_lines.append(f"Student: {clean_q}")
            history_lines.append(f"Tutor (respond in {lang_name}):")
            full_prompt = "\n\n".join(history_lines)

            for model_name in MODELS:
                try:
                    response = client.models.generate_content(
                        model=model_name,
                        contents=full_prompt,
                    )
                    if response and getattr(response, "text", None):
                        text = response.text.strip()
                        if text:
                            return text
                except Exception:
                    continue
        except Exception:
            pass

    # 2. Safe Mathematical Evaluator
    math_ans = _try_math_calculation(clean_q)
    if math_ans:
        return tr(math_ans, lang) if lang != "en" else math_ans

    # 3. Built-in Curated Pedagogical Knowledge Base
    lower_q = clean_q.lower()
    for pattern, answer in FALLBACK_KNOWLEDGE.items():
        if re.search(pattern, lower_q):
            out = answer
            if persona == "Socratic Guide":
                out = f"{answer}\n\n**🧭 Socratic Check:** How would this behave on an empty or edge-case input?"
            elif persona == "Mock Interviewer":
                out = f"{answer}\n\n**💼 Interview Follow-Up:** What are the memory vs. latency trade-offs in production?"
            return tr(out, lang) if lang != "en" else out

    # 4. Encyclopedic Summary Lookup
    wiki_ans = _try_wikipedia_summary(clean_q)
    if wiki_ans:
        return tr(wiki_ans, lang) if lang != "en" else wiki_ans

    # 5. Constructive Study Guide Response
    fallback_guide = (
        f"### Study Breakdown: {clean_q}\n\n"
        "Here is a structured framework to approach this topic:\n\n"
        "1. **Core Definition:** Identify the primary concept, inputs, and expected behavior or outcome.\n"
        "2. **Underlying Mechanism:** Break the problem into smaller primitives or step-by-step transitions.\n"
        "3. **Practical Verification:** Test edge cases or concrete examples to solidify intuition."
    )
    return tr(fallback_guide, lang) if lang != "en" else fallback_guide


if __name__ == "__main__":
    print(ask_tutor([], "Who is the President of India?"))
