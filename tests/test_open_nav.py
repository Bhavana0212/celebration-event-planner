"""Open nav batch: persistent header/footer, one-line open nav, LinkedIn in Contact, general FAQ."""
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
TEXT = (ROOT / "app.py").read_text()
CSS = (ROOT / "assets" / "professional-theme.css").read_text()

def test_nav_is_open_horizontal_not_dropdown():
    assert 'st.radio("Navigate"' in TEXT
    assert "horizontal=True" in TEXT
    assert "Navigate to a page" not in TEXT
    # CSS keeps the radio bar in one scrollable line, current page highlighted.
    assert "overflow-x: auto" in CSS
    assert "flex-wrap: nowrap" in CSS

def test_header_footer_are_persistent():
    # Header rendered at the start of main(), footer at the end, on every page.
    main = TEXT[TEXT.index("def main"):TEXT.index("# --- Info pages")]
    assert "pro-header" in main
    assert main.index("pro-header") < main.index("render_footer()")
    assert "position: sticky" in CSS
    assert "pro-footer" in CSS

def test_contact_has_linkedin_link():
    contact = TEXT[TEXT.index("def render_contact"):TEXT.index("def render_privacy_terms")]
    assert "https://www.linkedin.com/in/bhavana-shah-875a85137" in contact
    assert "Bhavana Shah on LinkedIn" in contact

def test_faq_is_general():
    faq = TEXT[TEXT.index("def render_faq"):TEXT.index("def render_reviews")]
    for q in ["What is this website?", "Who can use it?", "Is it free?",
              "Do I need an account or login?", "How do I start?",
              "Can I use it on my phone?"]:
        assert q in faq, q
