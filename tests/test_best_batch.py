"""Best-in-market batch: differentiators, readiness, invitation card, RSVP chart, wedding checklist."""
from pathlib import Path
TEXT = (Path(__file__).resolve().parents[1] / "app.py").read_text()

def test_differentiators_honest():
    assert "Eventbrite" in TEXT and "Partiful" in TEXT and "Zola" in TEXT
    assert "does NOT sell tickets" in TEXT

def test_readiness_and_invitation_card():
    assert "Your plan readiness" in TEXT
    assert "Stylish invitation preview" in TEXT

def test_rsvp_chart_and_wedding():
    assert "RSVP summary (chart)" in TEXT
    assert "Wedding planner" in TEXT
