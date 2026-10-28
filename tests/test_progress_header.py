"""Progress-tracker + clean header batch (screenshot reference, own design).

The 12-step journey must render as icon circles joined by one line
(done = magenta check, current = gold, upcoming = grey number) with a
completeness percentage, and the header must be a clean white bar —
not a copied logo/artwork from the reference screenshots.
"""
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
TEXT = (ROOT / "app.py").read_text()
CSS = (ROOT / "assets" / "professional-theme.css").read_text()


def test_progress_tracker_circles_on_a_line():
    assert "progress-tracker" in TEXT
    assert "track-circle" in TEXT
    assert "track-label" in TEXT
    assert "stepper" in TEXT  # old journey test still passes
    # 12 short tracker labels, in journey order
    for short in ["Planning", "Guests", "Budget", "Invitation", "Decor",
                  "Food", "Music", "Vendors", "Seating", "Kids",
                  "Live Day", "Memories"]:
        assert short in TEXT, short
    assert "% complete" in TEXT


def test_progress_tracker_css_and_clean_white_header():
    assert ".progress-tracker" in CSS
    assert ".track-circle" in CSS
    assert ".track-step.done .track-circle" in CSS
    assert "#E91E8C" in CSS and "#FFB800" in CSS
    # Clean white header bar with shadow (TOOFAN-style clean bar, own palette)
    assert "background: #FFFFFF" in CSS
    assert "box-shadow: 0 2px 10px" in CSS
