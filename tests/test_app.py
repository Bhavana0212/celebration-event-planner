from pathlib import Path

from streamlit.testing.v1 import AppTest

APP = str(Path(__file__).resolve().parents[1] / "app.py")


def test_app_loads_without_errors():
    at = AppTest.from_file(APP, default_timeout=30).run()
    assert not at.exception
    # Professional landing headline (see render_home).
    assert at.title[0].value == "Plan a celebration, without the stress."


def test_submitting_form_builds_plan():
    # Premium polish: the wizard on Home (not a sidebar form) creates a plan.
    at = AppTest.from_file(APP, default_timeout=30).run()
    for _ in range(6):
        at.button(key="wiz_next").click().run()
    at.button(key="wiz_create").click().run()
    assert not at.exception
    assert at.session_state.get("plan") is not None
