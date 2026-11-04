"""
Language Selection Gateway for VidyaVerse
Minimalist, human-crafted bilingual typography honoring regional scholarly heritage.
"""

import streamlit as st

from components.navbar import (
    APP_NAME,
    BRAND_MARK_SVG,
    CUSTOM_CSS,
    _load_asset_b64,
    render_ai_artwork,
    render_footer,
)

LANGUAGE_GATEWAY_CARDS = [
    {
        "code": "en",
        "native_name": "English",
        "english_label": "Standard Academic English",
        "script_badge": "Latin Script",
        "culture_ribbon": "Collegiate & Academic Tradition",
        "image": "lang_en.jpg",
        "fallback_image": "hero_learning_studio.jpg",
        "prof_desc": "Clear, precise academic instruction across computer science, cloud computing, and software engineering.",
        "native_welcome": "Learn computer science, algorithms, and cloud engineering in concise academic English.",
        "cta_label": "Continue in English →",
    },
    {
        "code": "ta",
        "native_name": "தமிழ்",
        "english_label": "Tamil · Madurai Sangam Heritage",
        "script_badge": "தமிழ் எழுத்து",
        "culture_ribbon": "மதுரைத் தமிழ்ச் சங்க மரபு",
        "image": "lang_ta.jpg",
        "fallback_image": "madurai_meenakshi_dawn.jpg",
        "prof_desc": "Honoring Madurai's historic Sangam scholarly tradition — study programming, data structures, and cloud engineering natively in Tamil.",
        "native_welcome": "செம்மொழியாம் தமிழில் கணினி அறிவியல், அல்காரிதங்கள் மற்றும் கிளவுட் தொழில்நுட்பங்களைக் கற்றுத் தேர்ச்சி பெறுங்கள்.",
        "cta_label": "தமிழில் தொடரவும் · Enter in Tamil →",
    },
    {
        "code": "hi",
        "native_name": "हिन्दी",
        "english_label": "Hindi · Devanagari",
        "script_badge": "देवनागरी लिपि",
        "culture_ribbon": "हिन्दी ज्ञान परम्परा",
        "image": "lang_hi.jpg",
        "fallback_image": "study_flashcards_plan.jpg",
        "prof_desc": "Comprehensive technical education, coding labs, and adaptive quizzes explained in natural, clear Hindi.",
        "native_welcome": "अनुकूली क्विज़, कोडिंग लैब और व्यक्तिगत मार्गदर्शन के साथ अपनी मातृभाषा हिन्दी में तकनीकी विषयों को समझें।",
        "cta_label": "हिन्दी में प्रवेश करें · Enter in Hindi →",
    },
    {
        "code": "te",
        "native_name": "తెలుగు",
        "english_label": "Telugu · Deccan Tradition",
        "script_badge": "తెలుగు లిపి",
        "culture_ribbon": "తెలుగు విద్యా సంప్రదాయం",
        "image": "lang_te.jpg",
        "fallback_image": "coding_lab_sandbox.jpg",
        "prof_desc": "In-depth conceptual study, algorithm explanations, and interview preparations natively presented in Telugu.",
        "native_welcome": "అడాప్టివ్ పరీక్షలు, కోడింగ్ ల్యాబ్ మరియు వ్యక్తిగత మార్గదర్శకంతో తెలుగు భాషలో సాంకేతిక నైపుణ్యాలను సాధించండి.",
        "cta_label": "తెలుగులో కొనసాగండి · Enter in Telugu →",
    },
    {
        "code": "ml",
        "native_name": "മലയാളം",
        "english_label": "Malayalam · Kerala Heritage",
        "script_badge": "മലയാള ലിപി",
        "culture_ribbon": "കേരളീയ വിജ്ഞാന പാരമ്പര്യം",
        "image": "lang_ml.jpg",
        "fallback_image": "study_flashcards_plan.jpg",
        "prof_desc": "Structured computer science concepts, database normalization, and cloud architecture articulated clearly in Malayalam.",
        "native_welcome": "അഡാപ്റ്റീവ് പരീക്ഷകളും കോഡിംഗ് ലാബും ഉപയോഗിച്ച് മലയാളത്തിൽ സാങ്കേതിക വിഷയങ്ങൾ ആഴത്തിൽ പഠിക്കൂ.",
        "cta_label": "മലയാളത്തിൽ തുടരുക · Enter in Malayalam →",
    },
    {
        "code": "kn",
        "native_name": "ಕನ್ನಡ",
        "english_label": "Kannada · Karnataka Heritage",
        "script_badge": "ಕನ್ನಡ ಲಿಪಿ",
        "culture_ribbon": "ಕನ್ನಡ ವಿದ್ಯಾ ಪರಂಪರೆ",
        "image": "lang_kn.jpg",
        "fallback_image": "hero_learning_studio.jpg",
        "prof_desc": "Practice programming algorithms, SQL databases, and cloud engineering directly in expressive Kannada.",
        "native_welcome": "ಅಡಾಪ್ಟಿವ್ ರಸಪ್ರಶ್ನೆಗಳು, ಕೋಡಿಂಗ್ ಲ್ಯಾಬ್ ಮತ್ತು ಶಿಕ್ಷಕರ ನೆರವಿನೊಂದಿಗೆ ಕನ್ನಡದಲ್ಲಿ ಪರಿಣತಿ ಸಾಧಿಸಿ.",
        "cta_label": "ಕನ್ನಡದಲ್ಲಿ ಮುಂದುವರಿಯಿರಿ · Enter in Kannada →",
    },
]


def _resolve_card_image_uri(primary_file: str, fallback_file: str) -> str | None:
    return _load_asset_b64(primary_file) or _load_asset_b64(fallback_file)


def render_language_gateway() -> None:
    """Renders a clean human-crafted bilingual language selection screen."""
    st.markdown(CUSTOM_CSS, unsafe_allow_html=True)

    st.markdown(
        """
        <style>
            .gateway-topbar {
                background: #FFFFFF;
                border: 1px solid #E5DFD5;
                border-radius: 12px;
                padding: 0.85rem 1.25rem;
                display: flex;
                justify-content: space-between;
                align-items: center;
                flex-wrap: wrap;
                gap: 12px;
                margin-bottom: 1.1rem;
            }
            .gateway-hero {
                background: #FFFFFF;
                border: 1px solid #E5DFD5;
                border-radius: 14px;
                padding: 2rem 2.2rem;
                margin-bottom: 1.6rem;
            }
            .gateway-pillar {
                background: #FAF8F5;
                border: 1px solid #E5DFD5;
                border-radius: 8px;
                padding: 0.65rem 0.85rem;
                font-size: 0.82rem;
                color: #44403C;
            }
            .lang-card-img-wrap {
                border-radius: 8px;
                overflow: hidden;
                border: 1px solid #E5DFD5;
                margin-bottom: 0.65rem;
                background: #F4F1EC;
            }
            .lang-card-img-wrap img {
                width: 100%;
                aspect-ratio: 16 / 9;
                height: auto;
                object-fit: cover;
                display: block;
            }
            .culture-ribbon-pill {
                font-size: 0.74rem;
                font-weight: 600;
                color: #78716C;
                margin-bottom: 0.45rem;
                display: block;
                white-space: nowrap;
                overflow: hidden;
                text-overflow: ellipsis;
            }
            .lang-native-title {
                font-size: 1.35rem;
                font-weight: 700;
                color: #1C1917;
                line-height: 1.2;
            }
            .lang-eng-sub {
                font-size: 0.78rem;
                font-weight: 500;
                color: #78716C;
                margin-top: 1px;
            }
            .lang-prof-copy {
                font-size: 0.84rem;
                color: #57534E;
                line-height: 1.5;
                min-height: 60px;
                margin: 0.5rem 0 0.6rem 0;
            }
            .lang-native-quote {
                background: #FAF8F5;
                border: 1px solid #EAE5DC;
                border-left: 3px solid #9A4A27;
                border-radius: 6px;
                padding: 0.55rem 0.75rem;
                font-size: 0.82rem;
                color: #292524;
                line-height: 1.5;
                min-height: 52px;
                margin-bottom: 0.75rem;
            }
        </style>
        """,
        unsafe_allow_html=True,
    )

    top_l, top_r = st.columns([4.2, 1], vertical_alignment="center")
    with top_l:
        st.markdown(
            f"""
            <div class="gateway-topbar">
                <div style="display:flex; align-items:center; gap:12px;">
                    {BRAND_MARK_SVG}
                    <div>
                        <div class="creamy-title">{APP_NAME}</div>
                        <div style="font-size: 0.8rem; color: #78716C; margin-top: 1px;">
                            Multilingual Technical Learning Platform · Madurai Edition
                        </div>
                    </div>
                </div>
                <div style="display:flex; align-items:center; gap:8px;">
                    <span class="agent-pill">Strands Engine Active</span>
                    <span class="almond-badge">6 Regional Editions</span>
                </div>
            </div>
            """,
            unsafe_allow_html=True,
        )
    with top_r:
        if st.session_state.get("user") is None:
            st.page_link("pages/3_Authentication.py", label="Sign In", use_container_width=True)
        else:
            if st.button("Open Home →", key="gw_skip_home", use_container_width=True):
                st.session_state.language_chosen = True
                st.rerun()

    st.markdown("<div style='height: 6px;'></div>", unsafe_allow_html=True)

    st.markdown('<div class="gateway-hero">', unsafe_allow_html=True)
    h_left, h_right = st.columns([1.35, 1], vertical_alignment="center")
    with h_left:
        st.markdown(
            f"""
            <div class="hero-eyebrow">LANGUAGE &amp; REGIONAL SCHOLARSHIP</div>
            <div class="hero-headline" style="font-size: 1.95rem; margin-bottom: 0.55rem;">
                Select Your Medium of Instruction
            </div>
            <div class="hero-sub" style="font-size: 0.94rem; margin-bottom: 1rem;">
                Welcome to <strong>{APP_NAME}</strong>. Choose the language in which you think and learn most effectively.
                All assessments, explanations, coding lab hints, study decks, and tutor interactions will adapt to your choice.
            </div>
            """,
            unsafe_allow_html=True,
        )
        p1, p2, p3 = st.columns(3)
        with p1:
            st.markdown(
                '<div class="gateway-pillar"><strong>Native Terminology</strong><br><span style="font-size:0.75rem;color:#78716C;">Full localized explanations</span></div>',
                unsafe_allow_html=True,
            )
        with p2:
            st.markdown(
                '<div class="gateway-pillar"><strong>Code Preservation</strong><br><span style="font-size:0.75rem;color:#78716C;">Exact code syntax preserved</span></div>',
                unsafe_allow_html=True,
            )
        with p3:
            st.markdown(
                '<div class="gateway-pillar"><strong>Guided Tutor</strong><br><span style="font-size:0.75rem;color:#78716C;">24/7 concept clarification</span></div>',
                unsafe_allow_html=True,
            )
    with h_right:
        render_ai_artwork("madurai_meenakshi_dawn.jpg", max_height_px=230, caption="Madurai Temple Architecture")
    st.markdown("</div>", unsafe_allow_html=True)

    st.markdown(
        """
        <div style="display:flex; justify-content:space-between; align-items:flex-end; flex-wrap:wrap; margin: 0.4rem 0 0.9rem 0;">
            <div>
                <h3 style="font-family: 'Source Serif 4', Georgia, serif; color: #1C1917; margin: 0; font-size: 1.25rem;">
                    Select Language to Enter
                </h3>
                <div style="color: #78716C; font-size: 0.88rem; margin-top: 2px;">
                    Click any card below to launch the learning platform in your preferred language.
                </div>
            </div>
            <span class="almond-badge">Can be changed anytime from the top bar</span>
        </div>
        """,
        unsafe_allow_html=True,
    )

    current_pref = st.session_state.get("lang", "en")
    for row_idx in range(0, len(LANGUAGE_GATEWAY_CARDS), 3):
        cols = st.columns(3)
        for col, card in zip(cols, LANGUAGE_GATEWAY_CARDS[row_idx : row_idx + 3]):
            with col:
                with st.container(border=True):
                    img_uri = _resolve_card_image_uri(card["image"], card["fallback_image"])
                    img_block = (
                        f'<div class="lang-card-img-wrap"><img src="{img_uri}" alt="{card["english_label"]}"></div>'
                        if img_uri
                        else ""
                    )
                    active_tag = (
                        '<span class="pista-badge" style="font-size:0.72rem;">Current</span>'
                        if card["code"] == current_pref and st.session_state.get("language_chosen")
                        else f'<span class="almond-badge" style="font-size:0.72rem;">{card["script_badge"]}</span>'
                    )
                    st.markdown(
                        f"""
                        {img_block}
                        <div class="culture-ribbon-pill">{card["culture_ribbon"]}</div>
                        <div style="display:flex; justify-content:space-between; align-items:flex-start; gap:8px;">
                            <div>
                                <div class="lang-native-title">{card["native_name"]}</div>
                                <div class="lang-eng-sub">{card["english_label"]}</div>
                            </div>
                            {active_tag}
                        </div>
                        <div class="lang-prof-copy">{card["prof_desc"]}</div>
                        <div class="lang-native-quote">{card["native_welcome"]}</div>
                        """,
                        unsafe_allow_html=True,
                    )
                    if st.button(
                        card["cta_label"],
                        key=f"gateway_pick_{card['code']}",
                        type="primary",
                        use_container_width=True,
                    ):
                        st.session_state.lang = card["code"]
                        st.session_state.language_chosen = True
                        st.rerun()

    render_footer()
