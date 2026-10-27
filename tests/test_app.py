from pathlib import Path

from streamlit.testing.v1 import AppTest

APP = str(Path(__file__).resolve().parents[1] / "app.py")


def test_app_loads_without_errors():
    at = AppTest.from_file(APP, default_timeout=30).run()
    assert not at.exception
    assert at.title[0].value.endswith("Celebration & Event Planner")


def test_submitting_form_builds_plan():
    # v3 uses sidebar navigation (radio), not tabs. Just check the form
    # submit does not crash and a plan is created in session state.
    at = AppTest.from_file(APP, default_timeout=30).run()
    at.sidebar.button[0].click().run()
    assert not at.exception
    assert at.session_state.get("plan") is not None
