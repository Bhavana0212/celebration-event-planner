"""Tests for the audit-fix batch: event time, expanded catalogues, templates."""
from datetime import date, timedelta

from planner import DECOR_SECTIONS, EVENT_TEMPLATES, GAMES_LIBRARY, EventRequest


def test_event_time_is_stored_and_validated():
    req = EventRequest("Birthday", 50, 100000.0, date.today() + timedelta(days=30),
                       "Toronto", "Casual", (), (), False, "",
                       event_name="Test", currency="CAD", event_time="18:30")
    assert req.validated(date.today()).event_time == "18:30"
    # Default stays empty, so older constructions still work.
    req2 = EventRequest("Birthday", 50, 100000.0, date.today() + timedelta(days=30))
    assert req2.validated(date.today()).event_time == ""


def test_event_time_bad_format_rejected():
    req = EventRequest("Birthday", 50, 100000.0, date.today() + timedelta(days=30),
                       event_name="Test", event_time="6pm")
    try:
        req.validated(date.today())
    except Exception as exc:
        assert "HH:MM" in str(exc)
    else:
        raise AssertionError("bad event time should be rejected")


def test_decor_sections_expanded():
    assert "Centrepiece & table numbers" in DECOR_SECTIONS
    assert "Backdrop & ceiling" in DECOR_SECTIONS
    assert "Photo booth & welcome sign" in DECOR_SECTIONS


def test_games_library_expanded():
    names = {g["name"] for g in GAMES_LIBRARY}
    assert "Team Building Challenge" in names
    assert "Couples Dance" in names
    assert "Kids Talent Show" in names
    assert len(GAMES_LIBRARY) >= 13


def test_event_templates_expanded():
    names = {t["name"] for t in EVENT_TEMPLATES}
    assert "Baby Shower — Garden" in names
    assert "Corporate Party — Minimalist" in names
    assert "Graduation — Rainbow / Fun" in names
