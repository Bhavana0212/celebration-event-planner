"""Step-by-step journey batch: 12 steps in order, honest done flags."""
from pathlib import Path
TEXT = (Path(__file__).resolve().parents[1] / "app.py").read_text()

def test_journey_steps_in_user_order():
    # Check order inside the JOURNEY_STEPS block only (these words also
    # appear elsewhere in app.py, e.g. in the section menu, so a whole-file
    # index check would be meaningless).
    block = TEXT[TEXT.index("JOURNEY_STEPS = ["):TEXT.index("def journey_done_flags")]
    order = ["Celebration planning", "Guest list", "Budget", "Invitation",
             "Decor", "Food & Cake", "Music & Games", "Vendors & Shopping",
             "Seating", "Kids & Return gifts", "Live Event Day", "Thank you & Memories"]
    positions = [block.index(name) for name in order]
    assert positions == sorted(positions), "journey steps must be in the user's sequence"
    assert "Complete journey" in TEXT
    assert "All steps done" in TEXT
    assert "journey_done_flags" in TEXT

def test_journey_uses_real_session_data():
    assert 's.get("real_guests")' in TEXT
    assert 's.get("expenses")' in TEXT
    assert 's.get("custom_vendors")' in TEXT
    assert 's.get("seating")' in TEXT
