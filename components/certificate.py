"""
Printable Mastery Certificate Generator for EduMateAI
Supports all 6 languages (English, Tamil, Hindi, Telugu, Malayalam, Kannada) with Indic Google Fonts.
"""

import hashlib
from components.i18n import get_lang, tr
from components.navbar import APP_NAME


def build_certificate_html(student_name: str, topic: str, score: float, date_str: str, lang: str | None = None) -> str:
    """Returns a standalone, print-ready HTML certificate localized in the active language."""
    active_lang = lang or get_lang()
    cert_code = hashlib.sha256(f"{student_name}:{topic}:{score}".encode("utf-8")).hexdigest()[:10].upper()

    seal_txt = tr("Verified Cognitive Mastery", active_lang)
    title_txt = tr("Certificate of Mastery", active_lang)
    certifies_txt = tr("This certifies that", active_lang)
    proficiency_txt = tr("has demonstrated exceptional conceptual and analytical proficiency in", active_lang)
    topic_disp = tr(topic, active_lang)
    score_lbl = tr("Verified Mastery Score", active_lang)
    date_lbl = tr("Issued Date", active_lang)
    eval_lbl = tr("Evaluated By", active_lang)
    id_lbl = tr("Verification ID", active_lang)
    print_btn = tr("Print / Save as PDF", active_lang)

    return f"""<!DOCTYPE html>
<html lang="{active_lang}">
<head>
<meta charset="UTF-8">
<title>{APP_NAME} Certificate — {student_name}</title>
<style>
  @import url('https://fonts.googleapis.com/css2?family=Noto+Sans+Devanagari:wght@400;600;700&family=Noto+Sans+Kannada:wght@400;600;700&family=Noto+Sans+Malayalam:wght@400;600;700&family=Noto+Sans+Tamil:wght@400;600;700&family=Noto+Sans+Telugu:wght@400;600;700&family=Playfair+Display:ital,wght@0,600;0,700;1,600&family=Plus+Jakarta+Sans:wght@400;600;700&display=swap');
  body {{
    background: #FAF7F2;
    font-family: 'Plus Jakarta Sans', 'Noto Sans Tamil', 'Noto Sans Devanagari', 'Noto Sans Telugu', 'Noto Sans Malayalam', 'Noto Sans Kannada', sans-serif;
    display: flex;
    justify-content: center;
    align-items: center;
    min-height: 96vh;
    margin: 0;
  }}
  .cert-frame {{
    width: 860px;
    background: linear-gradient(145deg, #FFFFFF 0%, #FAF3EA 100%);
    border: 3px solid #C58957;
    outline: 8px solid #F3EAE0;
    border-radius: 18px;
    padding: 52px 64px;
    text-align: center;
    box-shadow: 0 18px 45px rgba(53, 37, 30, 0.12);
  }}
  .seal {{
    display: inline-block;
    background: #EAF2E8;
    color: #385E32;
    border: 1px solid #C5DEC0;
    border-radius: 999px;
    padding: 6px 18px;
    font-size: 12px;
    font-weight: 700;
  }}
  h1 {{
    font-family: 'Playfair Display', 'Noto Sans Tamil', 'Noto Sans Devanagari', 'Noto Sans Telugu', 'Noto Sans Malayalam', 'Noto Sans Kannada', serif;
    color: #35251E;
    font-size: 38px;
    margin: 16px 0 8px 0;
  }}
  .subtitle {{ color: #7A6E67; font-size: 15px; margin-bottom: 24px; }}
  .recipient {{
    font-family: 'Playfair Display', serif;
    font-size: 34px;
    font-style: italic;
    color: #B4713B;
    border-bottom: 2px solid #E5D5C3;
    display: inline-block;
    padding: 0 32px 8px 32px;
    margin: 8px 0 22px 0;
  }}
  .domain {{ font-size: 22px; font-weight: 700; color: #35251E; margin: 8px 0; }}
  .score-pill {{
    display: inline-block;
    background: #FAF1E4;
    border: 1px solid #DFC5A8;
    color: #8A4E1B;
    font-weight: 700;
    padding: 8px 22px;
    border-radius: 999px;
    margin-top: 12px;
    font-size: 15px;
  }}
  .footer-row {{
    display: flex;
    justify-content: space-between;
    margin-top: 44px;
    padding-top: 18px;
    border-top: 1px solid #E8DFD4;
    font-size: 13px;
    color: #6E615A;
  }}
  @media print {{
    body {{ background: #FFFFFF; }}
    .no-print {{ display: none; }}
  }}
</style>
</head>
<body>
  <div class="cert-frame">
    <div class="seal">🎓 {APP_NAME} • {seal_txt}</div>
    <h1>{title_txt}</h1>
    <div class="subtitle">{certifies_txt}</div>
    <div class="recipient">{student_name}</div>
    <div class="subtitle" style="margin-bottom:8px;">{proficiency_txt}</div>
    <div class="domain">{topic_disp}</div>
    <div class="score-pill">{score_lbl}: {score}%</div>
    <div class="footer-row">
      <div><strong>{date_lbl}:</strong> {date_str}</div>
      <div><strong>{eval_lbl}:</strong> {APP_NAME} Strands DecisionModel</div>
      <div><strong>{id_lbl}:</strong> CERT-{cert_code}</div>
    </div>
    <div class="no-print" style="margin-top: 24px;">
      <button onclick="window.print()" style="background:#C58957;color:#FFF;border:none;padding:10px 22px;border-radius:8px;font-weight:700;cursor:pointer;">
        🖨️ {print_btn}
      </button>
    </div>
  </div>
</body>
</html>"""
