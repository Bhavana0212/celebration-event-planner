"""Design improvement batch, corrected: nav is segmented-control pills with NO radio circles at all (radio + CSS hiding failed live); journey tracker is an icon progress bar with a filled line; journey cards have a single number only."""
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
TEXT = (ROOT / "app.py").read_text()
CSS = (ROOT / "assets" / "professional-theme.css").read_text()

def test_nav_is_segmented_control_pills_no_radio_circles():
    assert 'st.segmented_control("Navigate"' in TEXT
    assert "stSegmentedControl" in CSS
    assert "border-radius: 999px" in CSS
    # Radio is only a fallback for very old Streamlit, never the primary nav.
    assert TEXT.index('st.segmented_control("Navigate"') < TEXT.index('st.radio("Navigate"')

def test_nav_is_one_scrollable_row_not_wrapped():
    # Live check found the 22 pills wrapping onto 3 rows; force nowrap.
    assert "flex-wrap: nowrap !important" in CSS
    assert "width: max-content" in CSS
    assert "overflow-x: auto" in CSS

def test_header_is_clean_white_bar():
    assert "box-shadow" in CSS
    assert ".pro-header" in CSS

def test_journey_tracker_uses_icons_and_filled_line():
    # Circle contains the step icon, done is a check; caption explains gold ring = next.
    assert 'mark = "✓" if is_done else icon' in TEXT
    assert "gold ring = your next step" in TEXT
    assert ".track-step.done::before" in CSS
    assert "background: #E91E8C" in CSS
    assert ".progress-tracker" in CSS

def test_progress_bar_is_planner_colours():
    assert "stProgress" in CSS
    assert "#E91E8C" in CSS and "#FFB800" in CSS

def test_journey_cards_have_single_number_only():
    # JOURNEY_STEPS titles already contain "1. ", "2. ", etc.
    assert '"**{i + 1}. {title}**"' not in TEXT
    assert '"**{title}**"' in TEXT
