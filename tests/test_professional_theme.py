"""Professional theme batch: separated CSS, deep-magenta config, header."""
from pathlib import Path
ROOT = Path(__file__).resolve().parents[1]
TEXT = (ROOT / "app.py").read_text()
CSS = (ROOT / "assets" / "professional-theme.css").read_text()
CFG = (ROOT / ".streamlit" / "config.toml").read_text()

def test_theme_file_and_loader():
    assert "load_professional_theme" in TEXT
    assert "professional-theme.css" in TEXT
    assert ".pro-header" in CSS
    assert ".block-container" in CSS
    assert "1180px" in CSS

def test_config_is_professional_not_generic():
    assert "#9D174D" in CFG
    assert "#111827" in CFG
    assert "#F9FAFB" in CFG
