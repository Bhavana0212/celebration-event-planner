"""Pages + stepper batch: top navbar, header/footer, info pages, journey graph, wizard-first Home."""
from pathlib import Path
ROOT = Path(__file__).resolve().parents[1]
TEXT = (ROOT / "app.py").read_text()
CSS = (ROOT / "assets" / "professional-theme.css").read_text()

def test_top_navbar_is_open_radio_and_footer_exists():
    # Open one-line nav, not a dropdown: segmented-control pills primary,
    # radio only as fallback, header/footer on every page.
    assert 'st.segmented_control("Navigate"' in TEXT
    assert 'st.selectbox("Navigate to a page"' not in TEXT
    assert "def render_footer" in TEXT
    assert "pro-footer" in CSS
    assert TEXT.count("render_footer()") >= 2  # defined AND called at the end of main()

def test_info_pages_exist():
    for page in ["About", "Services", "Pricing", "FAQ", "Reviews", "Contact", "Privacy & Terms"]:
        assert f'"{page}"' in TEXT, page
    assert "def render_about" in TEXT and "def render_services" in TEXT
    assert "def render_pricing" in TEXT and "def render_faq" in TEXT
    assert "def render_reviews" in TEXT and "def render_contact" in TEXT
    assert "def render_privacy_terms" in TEXT

def test_journey_is_stepper_not_pending_table():
    assert "stepper" in TEXT
    assert "○ Coming up" in TEXT
    assert "⏳ Pending" not in TEXT
    assert "Create plan first" not in TEXT

def test_wizard_before_journey_on_home():
    home = TEXT[TEXT.index("def render_home"):TEXT.index("def render_journey") if "def render_journey" in TEXT[TEXT.index("def render_home"):] else len(TEXT)]
    # Wizard/dashboard block appears before the journey call in render_home.
    assert home.index("render_event_wizard") < home.index("render_journey()")

def test_reviews_are_not_fake():
    assert "no verified customer reviews yet" in TEXT
