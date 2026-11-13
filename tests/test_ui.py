"""No frontend dependency required for checking presentation resources."""
from pathlib import Path
from src.ui_content import ui_text, tips_for
from src.ui_theme import stylesheet


def test_three_languages_have_all_ui_keys():
    master = set(ui_text('fr'))
    for language in ('en', 'ar'):
        values = ui_text(language)
        assert set(values) == master
        assert len(values['question_examples']) == 4


def test_tips_are_source_linked():
    for language in ('fr', 'en', 'ar'):
        tips = tips_for(language)
        assert len(tips) == 4
        for title, body, publisher, url in tips:
            assert title and body and publisher and url.startswith('https://')


def test_hero_is_local_image():
    root = Path(__file__).resolve().parents[1]
    p = root / 'assets' / 'hero_nutrition.webp'
    assert p.exists() and p.stat().st_size > 1000
    css = stylesheet(p)
    assert 'data:image/webp;base64,' in css
    assert '.ns-hero' in css
    assert '@keyframes' in css


def test_app_keeps_user_controls_simple():
    root = Path(__file__).resolve().parents[1]
    app = (root / 'app.py').read_text(encoding='utf-8')
    assert 'st.chat_input(' in app
    assert 'st.expander(' in app
    assert 'render_sources(' in app
    assert 'st.session_state.ns_saved' in app
