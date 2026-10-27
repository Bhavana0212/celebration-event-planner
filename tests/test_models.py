from datetime import timedelta

import pytest

from planner import MAX_NOTES, ValidationError
from planner.utils import clean_text, format_inr


def test_valid_request_passes(make_request, today):
    assert make_request().validated(today).guests == 50


@pytest.mark.parametrize("override", [
    {"guests": 0}, {"guests": 5000}, {"budget": 0}, {"budget": -5}, {"budget": float("nan")},
    {"event_type": "Rave"}, {"vibe": "Chaos"}, {"dietary": ("Keto",)}, {"accessibility": ("Moat",)},
    {"city": "<script>alert(1)</script>"},
])
def test_invalid_inputs_rejected(make_request, today, override):
    with pytest.raises(ValidationError):
        make_request(**override).validated(today)


def test_past_date_rejected(make_request, today):
    with pytest.raises(ValidationError, match="past"):
        make_request(event_date=today - timedelta(days=1)).validated(today)


def test_all_errors_reported_together(make_request, today):
    with pytest.raises(ValidationError) as exc:
        make_request(guests=0, budget=0).validated(today)
    assert "Guests" in str(exc.value) and "Budget" in str(exc.value)


def test_notes_are_sanitised_and_capped(make_request, today):
    req = make_request(notes="hi\x00\x07   there\n\n" + "x" * 1000).validated(today)
    assert "\x00" not in req.notes and len(req.notes) <= MAX_NOTES


def test_duplicate_options_removed(make_request, today):
    req = make_request(dietary=("Vegan", "Vegan")).validated(today)
    assert req.dietary == ("Vegan",)


def test_format_inr_grouping():
    assert format_inr(999) == "₹999"
    assert format_inr(100000) == "₹1,00,000"
    assert format_inr(1234567) == "₹12,34,567"
    assert format_inr(-2500) == "-₹2,500"


def test_clean_text():
    assert clean_text(None, 10) == ""
    assert clean_text("a\x00  b", 10) == "a b"
