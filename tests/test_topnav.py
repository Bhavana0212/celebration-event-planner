"""Top nav + wizard: navigation is at the top, sidebar has no form, wizard creates a plan."""
from pathlib import Path
from streamlit.testing.v1 import AppTest

APP = str(Path(__file__).resolve().parents[1] / "app.py")

def test_top_navigation_exists():
    at = AppTest.from_file(APP, default_timeout=60).run()
    assert not at.exception
    assert any(s.label == "Navigate to a page" for s in at.selectbox)

def test_sidebar_has_no_form_and_wizard_lands_on_plan():
    at = AppTest.from_file(APP, default_timeout=60).run()
    assert not at.exception
    assert len(at.sidebar.button) == 0, "premium polish: sidebar must not hold a duplicate form"
    # Walk the 7-step wizard with defaults, then create the plan.
    for _ in range(6):
        at.button(key="wiz_next").click().run()
        assert not at.exception
    at.button(key="wiz_create").click().run()
    assert not at.exception
    assert at.session_state.get("plan") is not None
    assert at.session_state.get("nav_section") == "Plan"
    texts = " ".join(str(x.value) for x in at.subheader)
    assert "Full plan at a glance" in texts
