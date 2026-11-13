"""NutriSport RAG — user-first Streamlit experience.

The visible interface is intentionally focused on nutrition questions. For the
professor's demo, P2 search settings are available in a closed sidebar expander.
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
    initial_sidebar_state="expanded",
)
st.markdown(stylesheet(ROOT / "assets" / "hero_nutrition.webp"), unsafe_allow_html=True)

for key, initial in {
    "ns_lang": "fr",
    "ns_goal": "all",
    "ns_page": "home",
    "ns_turns": [],
    "ns_saved": [],
    "ns_tip": 0,
    "ns_mode": "hybrid",
    "ns_k": 3,
    "ns_provider": "auto",
}.items():
    if key not in st.session_state:
        st.session_state[key] = initial


@st.cache_resource(show_spinner=False)
def load_engine():
    """Lazy initialize embeddings/FAISS on the first question, not at page load."""
    return NutriSport()


def change_page(page):
    st.session_state.ns_page = page
    st.rerun()


def submit_question(question, language):
    question = (question or "").strip()
    if not question:
        return
    try:
        with st.spinner(ui_text(language)["loading"]):
            result = load_engine().ask(
                question,
                topic=st.session_state.ns_goal,
                language=language,
                mode=st.session_state.ns_mode,
                top_k=st.session_state.ns_k,
                provider=st.session_state.ns_provider,
            )
    except Exception as exc:
        st.error(f"Impossible de traiter cette question : {exc}")
        return
    st.session_state.ns_turns.append({
        "question": question,
        "goal": st.session_state.ns_goal,
        "language": language,
        "answer": result["answer"],
        "status": result["status"],
        "passages": result["passages"],
    })


def render_sources(passages, language, key):
    t = ui_text(language)
    with st.expander(f"📚 {t['sources']} · {len(passages)}", expanded=False):
        if not passages:
            st.caption("Aucun passage retrouvé." if language == "fr" else "No matching passages.")
        for p in passages:
            st.markdown(f"**{p['source_title']}** · {p.get('section', '')}")
            st.write(p["text"])
            st.caption(f"{p['chunk_id']} · {p.get('provenance', 'document')}")
            if p.get("source_url", "").startswith("https://"):
                st.link_button(t["source_link"], p["source_url"])
            st.divider()


def render_answer(turn, number, language):
    with st.chat_message("user", avatar="🧑"):
        st.markdown(turn["question"])
    with st.chat_message("assistant", avatar="🥗"):
        st.markdown(turn["answer"])
        if turn["status"] in ("offline_extracts", "no_evidence"):
            st.caption(ui_text(language)["offline"] if turn["status"] == "offline_extracts" else "Aucune information pertinente dans les sources disponibles.")
        render_sources(turn["passages"], language, number)
        if st.button(f"🔖 {ui_text(language)['save']}", key=f"ns_save_{number}"):
            saved_ids = {x["question"] + x["answer"] for x in st.session_state.ns_saved}
            if turn["question"] + turn["answer"] not in saved_ids:
                st.session_state.ns_saved.append(turn.copy())
            st.toast(ui_text(language)["saved_ok"], icon="✅")


lang = st.session_state.ns_lang
t = ui_text(lang)

with st.sidebar:
    st.markdown('<div class="ns-logo"><span>🥗</span>NutriSport <span style="color:#8df09a;font-size:1.3rem">RAG</span></div>', unsafe_allow_html=True)
    st.markdown('<div class="ns-brand-caption">SMART NUTRITION COMPANION</div>', unsafe_allow_html=True)

    navigation = [
        ("home", "🏠 " + t["home"]),
        ("history", "💬 " + t["history"]),
        ("saved", "🔖 " + t["saved"]),
    ]
    for page, label in navigation:
        if st.button(label, key=f"nav_{page}", use_container_width=True,
                     type="primary" if st.session_state.ns_page == page else "secondary"):
            change_page(page)

    if st.button("＋ " + t["new"], key="new_chat", use_container_width=True):
        st.session_state.ns_turns = []
        st.session_state.ns_page = "home"
        st.rerun()

    st.markdown('<div class="ns-side-label">PREFERENCES</div>', unsafe_allow_html=True)
    picked_lang = st.selectbox(
        "🌐 " + t["language"],
        options=["fr", "en", "ar"],
        format_func=lambda code: {"fr": "Français", "en": "English", "ar": "العربية"}[code],
        key="ns_lang",
    )
    if picked_lang != lang:
        lang = picked_lang
        t = ui_text(lang)

    with st.expander("🔬 " + t["science"], expanded=False):
        st.caption("Réglages destinés à l'évaluation du projet (P2 / P3).")
        st.selectbox(t["mode"], ["hybrid", "dense", "bm25"], key="ns_mode",
                     format_func=lambda v: {"hybrid": "Hybride (FAISS + BM25)", "dense": "FAISS", "bm25": "BM25"}[v])
        st.select_slider(t["k"], options=[3, 5], key="ns_k")
        st.radio(t["provider"], options=["auto", "offline"], key="ns_provider",
                 format_func=lambda v: "Grok xAI" if v == "auto" else "Extraits documentaires (hors ligne)")
        if not os.getenv("XAI_API_KEY"):
            st.caption(t["no_key"])

if st.session_state.ns_page == "home":
    st.markdown(f"""
    <section class="ns-hero">
      <div class="ns-kicker">{t['hero_badge']}</div>
      <h1>{t['hero_title']}</h1>
      <p>{t['hero_subtitle']}</p>
      <div class="ns-hero-note">✦ Nutrition sportive &nbsp; ✦ Sources scientifiques &nbsp; ✦ 3 langues</div>
    </section>""", unsafe_allow_html=True)

    st.markdown(f'<div class="ns-section-title">💬 {t["ask"]}</div>', unsafe_allow_html=True)
    prompt = st.chat_input(t["ask_placeholder"], key="ns_question_input")

    st.markdown(f'<div class="ns-section-description">{t["ideas"]}</div>', unsafe_allow_html=True)
    examples = t["question_examples"]
    quick = st.columns(4, gap="small")
    quick_prompt = None
    for i, (column, example) in enumerate(zip(quick, examples)):
        with column:
            if st.button(example, key=f"quick_{lang}_{i}", use_container_width=True):
                quick_prompt = example.split(" ", 1)[1] if " " in example else example

    st.markdown(f'<div class="ns-section-title">🎯 {t["goals"]}</div>', unsafe_allow_html=True)
    st.markdown(f'<div class="ns-section-description">{t["goals_intro"]}</div>', unsafe_allow_html=True)
    cols = st.columns(3, gap="medium")
    goal_data = [
        ("muscle", "💪", t["muscle"], t["muscle_detail"]),
        ("weight", "⚖️", t["weight"], t["weight_detail"]),
        ("all", "🥗", t["general"], t["general_detail"]),
    ]
    for col, (goal, emoji, title, description) in zip(cols, goal_data):
        with col:
            with st.container(border=True):
                st.markdown(f'<div class="ns-goal-icon">{emoji}</div><div class="ns-goal-name">{title}</div><div class="ns-goal-detail">{description}</div>', unsafe_allow_html=True)
                if st.button("✓ " + t["selected"] if st.session_state.ns_goal == goal else t["choose"] + " →",
                             key=f"goal_{goal}", use_container_width=True,
                             type="primary" if st.session_state.ns_goal == goal else "secondary"):
                    st.session_state.ns_goal = goal
                    st.rerun()

    prompt_to_process = prompt or quick_prompt
    if prompt_to_process:
        submit_question(prompt_to_process, lang)

    left, right = st.columns([1.9, 1], gap="large")
    with left:
        st.markdown(f'<div class="ns-section-title">✨ {t["answer"]}</div>', unsafe_allow_html=True)
        if not st.session_state.ns_turns:
            st.markdown(f'''<section class="ns-panel ns-empty"><div class="ns-empty-icon">💬</div>
              <h3>{t['empty_title']}</h3><p>{t['empty_body']}</p></section>''', unsafe_allow_html=True)
        for i, turn in enumerate(st.session_state.ns_turns):
            render_answer(turn, i, lang)
    with right:
        st.markdown(f'<div class="ns-section-title">💡 {t["tips"]}</div>', unsafe_allow_html=True)
        tips = tips_for(lang)
        title, body, publisher, url = tips[st.session_state.ns_tip % len(tips)]
        st.markdown(f'''<section class="ns-tip"><div class="ns-tip-label">✦ NUTRISPORT</div>
          <h3>{title}</h3><p>{body}</p>
          <div class="ns-source-small">Source : <a href="{url}" target="_blank" rel="noopener noreferrer">{publisher}</a></div>
          </section>''', unsafe_allow_html=True)
        if st.button(t["next_tip"], key="next_tip", use_container_width=True):
            st.session_state.ns_tip = (st.session_state.ns_tip + 1) % len(tips)
            st.rerun()

elif st.session_state.ns_page == "history":
    st.markdown(f'<div class="ns-section-title">💬 {t["history"]}</div>', unsafe_allow_html=True)
    st.markdown(f'<div class="ns-section-description">{t["history_intro"]}</div>', unsafe_allow_html=True)
    if not st.session_state.ns_turns:
        st.info(t["history_empty"])
    else:
        for i, turn in enumerate(reversed(st.session_state.ns_turns), start=1):
            number = len(st.session_state.ns_turns) - i
            render_answer(turn, number, lang)
    if st.button("← " + t["back"], key="history_back"):
        change_page("home")

elif st.session_state.ns_page == "saved":
    st.markdown(f'<div class="ns-section-title">🔖 {t["saved"]}</div>', unsafe_allow_html=True)
    st.markdown(f'<div class="ns-section-description">{t["saved_notes"]}</div>', unsafe_allow_html=True)
    if not st.session_state.ns_saved:
        st.info(t["save_empty"])
    else:
        for i, turn in enumerate(st.session_state.ns_saved):
            with st.container(border=True):
                st.markdown("**" + t["question"] + " :** " + turn["question"])
                st.markdown(turn["answer"])
                render_sources(turn["passages"], lang, f"saved_{i}")
    if st.button("← " + t["back"], key="saved_back"):
        change_page("home")

st.markdown(f'<div class="ns-footer">{t["disclaimer"]}</div>', unsafe_allow_html=True)
