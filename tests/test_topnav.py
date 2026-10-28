"""Top nav + main form: navigation is at the top, form is on Home, submit lands on Plan."""
from pathlib import Path
from streamlit.testing.v1 import AppTest

APP = str(Path(__file__).resolve().parents[1] / "app.py")

def test_top_navigation_exists():
    at = AppTest.from_file(APP, default_timeout=60).run()
    assert not at.exception
    assert any(r.label == "Choose a section" for r in at.radio)

def test_sidebar_submit_lands_on_plan_with_full_plan():
    at = AppTest.from_file(APP, default_timeout=60).run()
    at.sidebar.button[0].click().run()
    assert not at.exception
    assert at.session_state.get("plan") is not None
    assert at.session_state.get("nav_section") == "Plan"
    texts = " ".join(str(x.value) for x in at.subheader)
    assert "Full plan at a glance" in texts
