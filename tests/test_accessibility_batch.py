"""Easily-accessible batch: hero start-here, page guide, empty-state guidance."""
from pathlib import Path
TEXT = (Path(__file__).resolve().parents[1] / "app.py").read_text()

def test_hero_start_here():
    assert "First time here? Start here" in TEXT
    assert "See an example first" in TEXT
    assert "Only 5 things are needed" in TEXT

def test_page_guide_and_empty_state():
    assert "What to do on each page" in TEXT
    assert "How to use this website in 30 seconds" in TEXT
    assert "First step: create a plan on Home below" in TEXT
