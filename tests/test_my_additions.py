"""My own additions: wedding/community samples, WhatsApp summary, one-time balloons."""
from pathlib import Path
TEXT = (Path(__file__).resolve().parents[1] / "app.py").read_text()

def test_sample_wedding_and_community():
    assert "Try a sample wedding plan" in TEXT
    assert "Try a sample community festival plan" in TEXT
    assert "Aarav & Meera's Wedding" in TEXT
    assert "Neighbourhood Summer Festival" in TEXT

def test_whatsapp_summary_and_balloons():
    assert "Share your plan summary" in TEXT
    assert "celebrated_plan" in TEXT
    assert "st.balloons()" in TEXT
