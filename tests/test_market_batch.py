"""Market batch: 18 event types, multi-day end date, venue comparison data."""
from datetime import date, timedelta
import pytest
from planner import EventRequest, ValidationError
from planner.budget import allocate_budget, BASE_SHARES
from planner.catalog import EVENT_TEMPLATES, SAMPLE_VENDORS, THEMES

TODAY = date(2026, 10, 27)

def req_for(et, end=None):
    return EventRequest(et, 50, 100000.0, TODAY + timedelta(days=60), "Toronto",
                        "Casual", (), (), False, "", event_name="Test", currency="CAD",
                        end_date=end).validated(TODAY)

def test_all_event_types_have_budget_share_summing_to_one():
    from planner.models import EVENT_TYPES
    assert len(EVENT_TYPES) == 18
    for et, shares in BASE_SHARES.items():
        assert abs(sum(shares) - 1.0) < 1e-9, et

def test_every_event_type_allocates_exact_budget():
    from planner.models import EVENT_TYPES
    for et in EVENT_TYPES:
        b = allocate_budget(req_for(et))
        assert abs(sum(line.amount for line in b.lines) - 100000.0) < 0.01, et
        assert b.per_head == 2000.0

def test_end_date_before_start_rejected():
    with pytest.raises(ValidationError):
        req_for("Birthday", end=TODAY + timedelta(days=10))

def test_end_date_after_start_accepted():
    r = req_for("Birthday", end=TODAY + timedelta(days=62))
    assert r.end_date == TODAY + timedelta(days=62)

def test_new_templates_use_valid_event_types():
    from planner.models import EVENT_TYPES
    for t in EVENT_TEMPLATES:
        assert t["event_type"] in EVENT_TYPES
    assert len(EVENT_TEMPLATES) >= 13

def test_venue_comparison_has_capacity():
    venues = [v for v in SAMPLE_VENDORS if v["category"] == "Venue"]
    assert venues and all(v.get("capacity") for v in venues)

def test_new_themes_exist():
    assert "Superhero" in THEMES and "Princess / Fairy" in THEMES and "Dinosaur" in THEMES
