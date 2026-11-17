"""NutriSport RAG — welcome page transitions to chat.

Run with:
    streamlit run app.py

Chat history stays in the Streamlit session.
"""

import os
from pathlib import Path

import streamlit as st

from src.pipeline import NutriSport
from src.ui_content import tips_for, ui_text
from src.ui_theme import stylesheet


ROOT = Path(__file__).resolve().parent


st.set_page_config(
    page_title="NutriSport · Votre assistant nutrition",
    page_icon="🥗",
    layout="wide",
    initial_sidebar_state="expanded"
)


st.markdown(
    stylesheet(
        ROOT / "assets" / "hero_nutrition.webp"
    ),
    unsafe_allow_html=True
)


# Session state
for key, initial in {
    "ns_lang": "fr",
    "ns_goal": "all",
    "ns_page": "home",
    "ns_turns": [],
    "ns_saved": [],
    "ns_tip": 0,
    "ns_mode": "hybrid",
    "ns_k": 3,
    "ns_provider": "auto"
}.items():

    if key not in st.session_state:
        st.session_state[key] = initial


@st.cache_resource(show_spinner=False)
def load_engine():
    """Load the retriever on first use."""

    return NutriSport()


def change_page(page):

    st.session_state.ns_page = page
    st.rerun()


def submit_question(question, language):

    question = (
        question or ""
    ).strip()

    if not question:
        return False

    try:

        with st.spinner(
            ui_text(language)["loading"]
        ):

            result = load_engine().ask(
                question,
                topic=st.session_state.ns_goal,
                language=language,
                mode=st.session_state.ns_mode,
                top_k=st.session_state.ns_k,
                provider=st.session_state.ns_provider,
                history=st.session_state.ns_turns[-2:]
            )

    except Exception as exc:

        st.error(
            f"Impossible de traiter cette question : {exc}"
        )

        return False

    st.session_state.ns_turns.append({
        "question": question,
        "goal": st.session_state.ns_goal,
        "language": language,
        "answer": result["answer"],
        "status": result["status"],
        "passages": result["passages"]
    })

    return True


def render_sources(
    passages,
    language,
    key
):

    t = ui_text(language)

    with st.expander(
        f"📚 {t['sources']} · {len(passages)}",
        expanded=False
    ):

        if not passages:

            st.caption(
                "Aucun passage retrouvé."
                if language == "fr"
                else "No matching passages."
            )

        for p in passages:

            st.markdown(
                f"**{p['source_title']}** · "
                f"{p.get('section', '')}"
            )

            st.write(
                p["text"]
            )

            st.caption(
                f"{p['chunk_id']} · "
                f"{p.get('provenance', 'document')}"
            )

            if p.get(
                "source_url", ""
            ).startswith("https://"):

                st.link_button(
                    t["source_link"],
                    p["source_url"]
                )

            st.divider()


def render_answer(
    turn,
    number,
    language
):

    with st.chat_message(
        "user",
        avatar="🧑"
    ):

        st.markdown(
            turn["question"]
        )

    with st.chat_message(
        "assistant",
        avatar="🥗"
    ):

        st.markdown(
            turn["answer"]
        )

        if turn["status"] in (
            "offline_extracts",
            "no_evidence"
        ):

            if turn["status"] == "offline_extracts":

                message = ui_text(
                    language
                )["offline"]

            else:

                message = (
                    "Aucune information pertinente "
                    "dans les sources disponibles."
                )

            st.caption(message)

        render_sources(
            turn["passages"],
            language,
            number
        )

        if st.button(
            f"🔖 {ui_text(language)['save']}",
            key=f"ns_save_{number}"
        ):

            saved_ids = {
                x["question"] + x["answer"]
                for x in st.session_state.ns_saved
            }

            current_id = (
                turn["question"]
                + turn["answer"]
            )

            if current_id not in saved_ids:

                st.session_state.ns_saved.append(
                    turn.copy()
                )

            st.toast(
                ui_text(language)["saved_ok"],
                icon="✅"
            )


lang = st.session_state.ns_lang
t = ui_text(lang)


# ===========================================
# SIDEBAR
# ===========================================

with st.sidebar:

    st.markdown(
        '<div class="ns-logo">'
        '<span>🥗</span>NutriSport '
        '<span style="color:#8df09a;font-size:1.3rem">'
        'RAG</span></div>',
        unsafe_allow_html=True
    )

    st.markdown(
        '<div class="ns-brand-caption">'
        'SMART NUTRITION COMPANION'
        '</div>',
        unsafe_allow_html=True
    )

    navigation = [
        ("home", "🏠 " + t["home"]),
        ("history", "💬 " + t["history"]),
        ("saved", "🔖 " + t["saved"])
    ]

    for page, label in navigation:

        if st.button(
            label,
            key=f"nav_{page}",
            use_container_width=True,
            type=(
                "primary"
                if st.session_state.ns_page == page
                else "secondary"
            )
        ):

            change_page(page)

    if st.button(
        "＋ " + t["new"],
        key="new_chat",
        use_container_width=True
    ):

        st.session_state.ns_turns = []
        st.session_state.ns_page = "home"

        st.rerun()

    st.markdown(
        '<div class="ns-side-label">'
        'PREFERENCES</div>',
        unsafe_allow_html=True
    )

    picked_lang = st.selectbox(
        "🌐 " + t["language"],
        options=[
            "fr",
            "en",
            "ar"
        ],
        format_func=lambda code: {
            "fr": "Français",
            "en": "English",
            "ar": "العربية"
        }[code],
        key="ns_lang"
    )

    if picked_lang != lang:

        lang = picked_lang
        t = ui_text(lang)

    with st.expander(
        "🔬 " + t["science"],
        expanded=False
    ):

        st.caption(
            "Réglages destinés à l'évaluation "
            "du projet (P2 / P3)."
        )

        st.selectbox(
            t["mode"],
            [
                "hybrid",
                "dense",
                "bm25"
            ],
            key="ns_mode",
            format_func=lambda v: {
                "hybrid": "Hybride (FAISS + BM25)",
                "dense": "FAISS",
                "bm25": "BM25"
            }[v]
        )

        st.select_slider(
            t["k"],
            options=[3, 5],
            key="ns_k"
        )

        st.radio(
            t["provider"],
            options=[
                "auto",
                "offline"
            ],
            key="ns_provider",
            format_func=lambda v: (
                "LLM via API (OpenRouter / Groq)"
                if v == "auto"
                else "Extraits documentaires (hors ligne)"
            )
        )

        if not (
            os.getenv("OPENROUTER_API_KEY")
            or os.getenv("XAI_API_KEY")
        ):

            st.caption(
                t["no_key"]
            )


# ===========================================
# HOME / CHAT
# ===========================================

if st.session_state.ns_page == "home":

    prompt = st.chat_input(
        t["ask_placeholder"],
        key="ns_question_input"
    )

    quick_prompt = None

    if not st.session_state.ns_turns:

        st.markdown(
            f"""
            <section class="ns-hero">
              <div class="ns-kicker">{t['hero_badge']}</div>
              <h1>{t['hero_title']}</h1>
              <p>{t['hero_subtitle']}</p>
              <div class="ns-hero-note">
                ✦ Nutrition sportive &nbsp;
                ✦ Sources scientifiques &nbsp;
                ✦ 3 langues
              </div>
            </section>
            """,
            unsafe_allow_html=True
        )

        st.markdown(
            f'<div class="ns-section-title">'
            f'💬 {t["ask"]}</div>',
            unsafe_allow_html=True
        )

        st.markdown(
            f'<div class="ns-section-description">'
            f'{t["ideas"]}</div>',
            unsafe_allow_html=True
        )

        examples = t[
            "question_examples"
        ]

        quick = st.columns(
            4,
            gap="small"
        )

        for i, (
            column,
            example
        ) in enumerate(
            zip(quick, examples)
        ):

            with column:

                if st.button(
                    example,
                    key=f"quick_{lang}_{i}",
                    use_container_width=True
                ):

                    quick_prompt = (
                        example.split(" ", 1)[1]
                        if " " in example
                        else example
                    )

        st.markdown(
            f'<div class="ns-section-title">'
            f'🎯 {t["goals"]}</div>',
            unsafe_allow_html=True
        )

        st.markdown(
            f'<div class="ns-section-description">'
            f'{t["goals_intro"]}</div>',
            unsafe_allow_html=True
        )

        cols = st.columns(
            3,
            gap="medium"
        )

        goal_data = [
            (
                "muscle",
                "💪",
                t["muscle"],
                t["muscle_detail"]
            ),
            (
                "weight",
                "⚖️",
                t["weight"],
                t["weight_detail"]
            ),
            (
                "all",
                "🥗",
                t["general"],
                t["general_detail"]
            )
        ]

        for col, (
            goal,
            emoji,
            title,
            description
        ) in zip(
            cols,
            goal_data
        ):

            with col:

                with st.container(
                    border=True
                ):

                    st.markdown(
                        f'<div class="ns-goal-icon">'
                        f'{emoji}</div>'
                        f'<div class="ns-goal-name">'
                        f'{title}</div>'
                        f'<div class="ns-goal-detail">'
                        f'{description}</div>',
                        unsafe_allow_html=True
                    )

                    selected = (
                        st.session_state.ns_goal
                        == goal
                    )

                    button_label = (
                        "✓ " + t["selected"]
                        if selected
                        else t["choose"] + " →"
                    )

                    if st.button(
                        button_label,
                        key=f"goal_{goal}",
                        use_container_width=True,
                        type=(
                            "primary"
                            if selected
                            else "secondary"
                        )
                    ):

                        st.session_state.ns_goal = goal

                        st.rerun()

        st.markdown(
            f'<div class="ns-section-title">'
            f'💡 {t["tips"]}</div>',
            unsafe_allow_html=True
        )

        tips = tips_for(
            lang
        )

        title, body, publisher, url = tips[
            st.session_state.ns_tip % len(tips)
        ]

        st.markdown(
            f'<section class="ns-tip">'
            f'<div class="ns-tip-label">'
            f'✦ NUTRISPORT</div>'
            f'<h3>{title}</h3>'
            f'<p>{body}</p>'
            f'<div class="ns-source-small">'
            f'Source : '
            f'<a href="{url}" target="_blank" '
            f'rel="noopener noreferrer">'
            f'{publisher}</a>'
            f'</div></section>',
            unsafe_allow_html=True
        )

        if st.button(
            t["next_tip"],
            key="next_tip",
            use_container_width=True
        ):

            st.session_state.ns_tip += 1
            st.rerun()

    if prompt or quick_prompt:

        if submit_question(
            prompt or quick_prompt,
            lang
        ):

            st.rerun()

    if st.session_state.ns_turns:

        st.markdown(
            "<style>"
            "[data-testid='stMainBlockContainer'] {"
            "max-width:900px !important;"
            "padding-bottom:7rem !important;"
            "}"
            "</style>",
            unsafe_allow_html=True
        )

        for i, turn in enumerate(
            st.session_state.ns_turns
        ):

            render_answer(
                turn,
                i,
                lang
            )


# ===========================================
# HISTORY PAGE
# ===========================================

elif st.session_state.ns_page == "history":

    st.markdown(
        f'<div class="ns-section-title">'
        f'💬 {t["history"]}</div>',
        unsafe_allow_html=True
    )

    st.markdown(
        f'<div class="ns-section-description">'
        f'{t["history_intro"]}</div>',
        unsafe_allow_html=True
    )

    if not st.session_state.ns_turns:

        st.info(
            t["history_empty"]
        )

    else:

        for i, turn in enumerate(
            reversed(
                st.session_state.ns_turns
            ),
            start=1
        ):

            number = (
                len(st.session_state.ns_turns)
                - i
            )

            render_answer(
                turn,
                number,
                lang
            )

    if st.button(
        "← " + t["back"],
        key="history_back"
    ):

        change_page("home")


# ===========================================
# SAVED RESPONSES
# ===========================================

elif st.session_state.ns_page == "saved":

    st.markdown(
        f'<div class="ns-section-title">'
        f'🔖 {t["saved"]}</div>',
        unsafe_allow_html=True
    )

    st.markdown(
        f'<div class="ns-section-description">'
        f'{t["saved_notes"]}</div>',
        unsafe_allow_html=True
    )

    if not st.session_state.ns_saved:

        st.info(
            t["save_empty"]
        )

    else:

        for i, turn in enumerate(
            st.session_state.ns_saved
        ):

            with st.container(
                border=True
            ):

                st.markdown(
                    "**"
                    + t["question"]
                    + " :** "
                    + turn["question"]
                )

                st.markdown(
                    turn["answer"]
                )

                render_sources(
                    turn["passages"],
                    lang,
                    f"saved_{i}"
                )

    if st.button(
        "← " + t["back"],
        key="saved_back"
    ):

        change_page("home")


st.markdown(
    f'<div class="ns-footer">'
    f'{t["disclaimer"]}</div>',
    unsafe_allow_html=True
)