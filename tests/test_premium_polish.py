"""Premium polish batch: Forest/Champagne/Ivory theme, wizard, dashboard, no sidebar form."""
from pathlib import Path
ROOT = Path(__file__).resolve().parents[1]
TEXT = (ROOT / "app.py").read_text()
CSS = (ROOT / "assets" / "professional-theme.css").read_text()
CFG = (ROOT / ".streamlit" / "config.toml").read_text()

def test_forest_champagne_ivory_palette():
    assert "#24352E" in CFG and "#F7F3ED" in CFG and "#30343B" in CFG
    assert "#C6A477" in CSS  # champagne accent
    assert "Georgia" in CSS  # editorial serif headings

def test_wizard_and_dashboard_present():
    assert "WIZARD_STEPS" in TEXT
    assert "Step {step} of {len(WIZARD_STEPS)}" in TEXT or "Step " in TEXT
    assert "render_event_wizard" in TEXT
    assert "render_dashboard" in TEXT
    assert "Your dashboard" in TEXT
    assert "Explore all celebrations" in TEXT
    # Wizard steps in reference order
    assert '"Occasion"' in TEXT and '"Review"' in TEXT
