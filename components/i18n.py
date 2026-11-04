"""
Multilingual Localization Engine (i18n) for EduMateAI
Supports 6 Languages:
  - English (en)
  - Tamil / தமிழ் (ta)
  - Hindi / हिन्दी (hi)
  - Telugu / తెలుగు (te)
  - Malayalam / മലയാളം (ml)
  - Kannada / ಕನ್ನಡ (kn)

Combines an instant curated UI dictionary with a fast SQLite-cached translator
that preserves inline code (`...`) and MCQ option prefixes (`A. `, `B. `, `C. `, `D. `).
"""

import json
import re
import sqlite3
import urllib.parse
import urllib.request
from pathlib import Path
import streamlit as st

SUPPORTED_LANGUAGES = {
    "en": "English",
    "ta": "தமிழ் · Tamil",
    "hi": "हिन्दी · Hindi",
    "te": "తెలుగు · Telugu",
    "ml": "മലയാളം · Malayalam",
    "kn": "ಕನ್ನಡ · Kannada",
}

LANGUAGE_NAMES = {
    "en": "English",
    "ta": "Tamil (தமிழ்)",
    "hi": "Hindi (हिन्दी)",
    "te": "Telugu (తెలుగు)",
    "ml": "Malayalam (മലയാളം)",
    "kn": "Kannada (ಕನ್ನಡ)",
}

# Instant zero-latency core UI dictionary for navigation and high-frequency labels
UI_TRANSLATIONS = {
    "nav_subtitle": {
        "en": "Computer Science, AWS Cloud & Engineering Practice",
        "ta": "கணினி அறிவியல், கிளவுட் மற்றும் பொறியியல் பயிற்சித் தளம்",
        "hi": "कंप्यूटर विज्ञान, क्लाउड और इंजीनियरिंग अभ्यास मंच",
        "te": "కంప్యూటర్ సైన్స్, క్లౌడ్ & ఇంజనీరింగ్ ప్రాక్టీస్ వేదిక",
        "ml": "കമ്പ്യൂട്ടർ സയൻസ്, ക്ലൗഡ് & എഞ്ചിനീയറിംഗ് പരിശീലന വേദി",
        "kn": "ಕಂಪ್ಯೂಟರ್ ಸೈನ್ಸ್, ಕ್ಲೌಡ್ ಮತ್ತು ಎಂಜಿನಿಯರಿಂಗ್ ಅಭ್ಯಾಸ ವೇದಿಕೆ",
    },
    "agent_active": {
        "en": "Strands Engine",
        "ta": "Strands தளம்",
        "hi": "Strands इंजन",
        "te": "Strands ఇంజిన్",
        "ml": "Strands എഞ്ചിൻ",
        "kn": "Strands ಎಂಜಿನ್",
    },
    "guest_learner": {
        "en": "Guest",
        "ta": "விருந்தினர்",
        "hi": "अतिथि",
        "te": "అతిథి",
        "ml": "അതിഥി",
        "kn": "ಅತಿಥಿ",
    },
    "nav_home": {
        "en": "Home",
        "ta": "முகப்பு",
        "hi": "होम",
        "te": "హోమ్",
        "ml": "ഹോം",
        "kn": "ಮುಖಪುಟ",
    },
    "nav_quiz": {
        "en": "Assessments",
        "ta": "தேர்வுகள்",
        "hi": "अभ्यास परीक्षा",
        "te": "పరీక్షలు",
        "ml": "പരീക്ഷകൾ",
        "kn": "ಪರೀಕ್ಷೆಗಳು",
    },
    "nav_study": {
        "en": "Study Notes",
        "ta": "பாடக் குறிப்புகள்",
        "hi": "अध्ययन नोट्स",
        "te": "స్టడీ నోట్స్",
        "ml": "പഠന കുറിപ്പുകൾ",
        "kn": "ಅಧ್ಯಯನ ಟಿಪ್ಪಣಿಗಳು",
    },
    "nav_code": {
        "en": "Code Lab",
        "ta": "குறியீட்டு ஆய்வகம்",
        "hi": "कोड लैब",
        "te": "కోడ్ ల్యాబ్",
        "ml": "കോഡ് ലാബ്",
        "kn": "ಕೋಡ್ ಲ್ಯಾಬ್",
    },
    "nav_tutor": {
        "en": "Tutor",
        "ta": "ஆசிரியர்",
        "hi": "ट्यूटर",
        "te": "ట్యూటర్",
        "ml": "ട്യൂട്ടർ",
        "kn": "ಶಿಕ್ಷಕ",
    },
    "nav_dossier": {
        "en": "Progress",
        "ta": "முன்னேற்றம்",
        "hi": "प्रगति",
        "te": "పురోగతి",
        "ml": "പുരോഗതി",
        "kn": "ಪ್ರಗತಿ",
    },
    "nav_history": {
        "en": "Records",
        "ta": "பதிவுகள்",
        "hi": "रिकॉर्ड",
        "te": "రికార్డులు",
        "ml": "രേഖകൾ",
        "kn": "ದಾಖಲೆಗಳು",
    },
    "nav_signin": {
        "en": "Sign In",
        "ta": "உள்நுழைக",
        "hi": "साइन इन",
        "te": "సైన్ ఇన్",
        "ml": "സൈൻ ഇൻ",
        "kn": "ಸೈನ್ ಇನ್",
    },
    "nav_signout": {
        "en": "Sign Out",
        "ta": "வெளியேறு",
        "hi": "साइन आउट",
        "te": "సైన్ అవుట్",
        "ml": "സൈൻ ഔട്ട്",
        "kn": "ಸೈನ್ ಔಟ್",
    },
}

_MEM_CACHE: dict[tuple[str, str], str] = {}
_DB_PATH = Path(__file__).resolve().parent.parent / "database" / "student.db"


def _ensure_cache_table():
    with sqlite3.connect(_DB_PATH, timeout=15) as conn:
        conn.execute("PRAGMA journal_mode=WAL;")
        conn.execute(
            """
            CREATE TABLE IF NOT EXISTS translation_cache (
                lang TEXT NOT NULL,
                src_text TEXT NOT NULL,
                dst_text TEXT NOT NULL,
                PRIMARY KEY (lang, src_text)
            )
            """
        )
        for lg, src_t, dst_t in conn.execute("SELECT lang, src_text, dst_text FROM translation_cache"):
            _MEM_CACHE[(lg, src_t)] = dst_t
        conn.commit()


_ensure_cache_table()


def get_lang() -> str:
    """Returns currently selected ISO language code (`en`, `ta`, `hi`, `te`, `ml`, `kn`)."""
    if "lang" not in st.session_state or st.session_state.lang not in SUPPORTED_LANGUAGES:
        st.session_state.lang = "en"
    return st.session_state.lang


def ui(key: str) -> str:
    """Fast lookup for predefined UI dictionary keys."""
    lang = get_lang()
    entry = UI_TRANSLATIONS.get(key, {})
    return entry.get(lang) or entry.get("en", key)


def _mask_code_spans(text: str) -> tuple[str, list[str]]:
    """Masks inline `code` spans so programming syntax is never mangled during translation."""
    spans: list[str] = []

    def repl(match):
        idx = len(spans)
        spans.append(match.group(0))
        return f"__CD{idx}__"

    masked = re.sub(r"`[^`]+`", repl, text)
    return masked, spans


def _unmask_code_spans(text: str, spans: list[str]) -> str:
    result = text
    for idx, original in enumerate(spans):
        # Handle slight spacing variations introduced by translators around tokens
        result = re.sub(rf"__\s*CD\s*{idx}\s*__", lambda _: original, result, flags=re.IGNORECASE)
    return result


def _fetch_google_translate(text: str, target_lang: str) -> str:
    url = (
        "https://translate.googleapis.com/translate_a/single?client=gtx&sl=en&tl="
        + urllib.parse.quote(target_lang)
        + "&dt=t&q="
        + urllib.parse.quote(text)
    )
    req = urllib.request.Request(url, headers={"User-Agent": "Mozilla/5.0"})
    with urllib.request.urlopen(req, timeout=4) as resp:
        payload = json.loads(resp.read().decode("utf-8"))
    return "".join(seg[0] for seg in payload[0] if seg and seg[0])


def tr(text: str, lang: str | None = None) -> str:
    """
    Translates any English string into the active language (`ta`, `hi`, `te`, `ml`, `kn`)
    with two-tier caching (RAM + SQLite) and automatic preservation of inline `code` and MCQ prefixes.
    """
    target = lang or get_lang()
    if target == "en" or not text or not text.strip():
        return text

    cache_key = (target, text)
    if cache_key in _MEM_CACHE:
        return _MEM_CACHE[cache_key]

    try:
        with sqlite3.connect(_DB_PATH, timeout=15) as conn:
            row = conn.execute(
                "SELECT dst_text FROM translation_cache WHERE lang = ? AND src_text = ?",
                (target, text),
            ).fetchone()
            if row:
                _MEM_CACHE[cache_key] = row[0]
                return row[0]
    except Exception:
        pass

    # Preserve leading MCQ option prefix like "A. ", "B. ", "C. ", "D. " so answer grading never breaks
    opt_match = re.match(r"^([A-D]\.\s+)(.+)$", text, flags=re.DOTALL)
    prefix = ""
    core_text = text
    if opt_match:
        prefix = opt_match.group(1)
        core_text = opt_match.group(2)

    masked, code_spans = _mask_code_spans(core_text)
    try:
        translated_core = _fetch_google_translate(masked, target)
        restored = _unmask_code_spans(translated_core, code_spans)
        final_text = f"{prefix}{restored}"
    except Exception:
        return text

    _MEM_CACHE[cache_key] = final_text
    try:
        with sqlite3.connect(_DB_PATH, timeout=15) as conn:
            conn.execute(
                "INSERT OR REPLACE INTO translation_cache (lang, src_text, dst_text) VALUES (?, ?, ?)",
                (target, text, final_text),
            )
            conn.commit()
    except Exception:
        pass

    return final_text


def _translate_pure_http(text: str, target: str) -> str | None:
    """Translates text over HTTP while preserving MCQ prefixes (`A. `) and inline `code` spans."""
    opt_match = re.match(r"^([A-D]\.\s+)(.+)$", text, flags=re.DOTALL)
    prefix = ""
    core_text = text
    if opt_match:
        prefix = opt_match.group(1)
        core_text = opt_match.group(2)

    masked, code_spans = _mask_code_spans(core_text)
    try:
        translated_core = _fetch_google_translate(masked, target)
        restored = _unmask_code_spans(translated_core, code_spans)
        return f"{prefix}{restored}"
    except Exception:
        return None


def warm_translations(texts: list[str], langs: list[str] | None = None) -> None:
    """Translates uncached strings concurrently via HTTP and persists via a single SQLite executemany."""
    target_langs = [lg for lg in (langs or [get_lang()]) if lg != "en"]
    if not target_langs or not texts:
        return
    unique_pairs = list(
        {(lg, t) for lg in target_langs for t in texts if t and t.strip() and (lg, t) not in _MEM_CACHE}
    )
    if not unique_pairs:
        return
    from concurrent.futures import ThreadPoolExecutor

    def _worker(pair: tuple[str, str]):
        lg, src_t = pair
        out = _translate_pure_http(src_t, lg)
        return (lg, src_t, out) if out else None

    with ThreadPoolExecutor(max_workers=20) as pool:
        results = [r for r in pool.map(_worker, unique_pairs) if r is not None]

    if not results:
        return
    for lg, src_t, dst_t in results:
        _MEM_CACHE[(lg, src_t)] = dst_t
    try:
        with sqlite3.connect(_DB_PATH, timeout=15) as conn:
            conn.executemany(
                "INSERT OR REPLACE INTO translation_cache (lang, src_text, dst_text) VALUES (?, ?, ?)",
                results,
            )
            conn.commit()
    except Exception:
        pass


def tr_quiz_dict(quiz: dict, lang: str | None = None) -> dict:
    """Returns a localized view of a quiz dictionary while keeping original answer keys intact."""
    target = lang or get_lang()
    if target == "en" or not quiz:
        return quiz

    localized_questions = []
    for q in quiz.get("questions", []):
        localized_questions.append({
            **q,
            "question_display": tr(q["question"], target),
            "options_display": [tr(opt, target) for opt in q.get("options", [])],
            "explanation_display": tr(q.get("explanation", ""), target),
        })
    return {
        **quiz,
        "topic_display": tr(quiz.get("topic", ""), target),
        "difficulty_display": tr(quiz.get("difficulty", ""), target),
        "questions_localized": localized_questions,
    }
