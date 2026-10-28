"""Celebration-vibe + page-wise batch: festive palette, no truncation layout, tabs, short Home."""
from pathlib import Path
ROOT = Path(__file__).resolve().parents[1]
TEXT = (ROOT / "app.py").read_text()
CSS = (ROOT / "assets" / "professional-theme.css").read_text()
CFG = (ROOT / ".streamlit" / "config.toml").read_text()

def test_celebration_palette_not_forest():
    assert "#E91E8C" in CFG  # vivid popping pink, not serious Forest
    assert "#FFF5F9" in CFG  # bright pink-tinted background
    assert "#FFB800" in CSS  # gold accent
    assert "#24352E" not in CFG

def test_header_wraps_and_metrics_not_truncated():
    assert "flex-wrap: wrap" in CSS
    assert "white-space: normal" in CSS

def test_plan_uses_tabs_and_home_is_short():
    assert 'st.tabs(["Overview", "Budget & Checklist", "Invitation & Day Plan", "My tasks & Notes"])' in TEXT
    assert "Explore everything — tap any card" not in TEXT  # 14 long cards removed from Home
    assert "More about this planner" in TEXT
