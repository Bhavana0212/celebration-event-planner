from datetime import date, timedelta

import pytest

from planner.budget import allocate_budget
from planner.logistics import menu_suggestions, plan_logistics
from planner.risks import assess_risks


def test_logistics_scale_with_guests(make_request):
    lg = plan_logistics(make_request(guests=100))
    assert lg.food_portions == 110 and lg.chairs == 105 and lg.tables == 13
    assert lg.service_staff == 5 and lg.restrooms == 2 and lg.parking_spots == 34


def test_logistics_minimums_and_cake(make_request):
    lg = plan_logistics(make_request(guests=1, event_type="Corporate Party"))
    assert lg.service_staff == 2 and lg.restrooms == 2 and lg.cake_servings == 0


def test_outdoor_needs_more_space(make_request):
    assert plan_logistics(make_request(outdoor=True)).venue_area_sqft > plan_logistics(make_request()).venue_area_sqft


def test_menu_respects_all_constraints():
    menu = menu_suggestions(("Vegan", "Halal"))
    flat = [d for dishes in menu.values() for d in dishes]
    assert "Paneer tikka" not in flat and "Chicken biryani" not in flat
    assert "Millet khichdi with vegetables" in flat


def test_menu_jain_and_no_filter():
    assert "Sprouts chaat (no onion/garlic)" in menu_suggestions(("Jain",))["Starter"]
    assert len(menu_suggestions(())["Main"]) > 3


def test_menu_fallback_when_nothing_matches():
    menu = menu_suggestions(("Jain", "Diabetic-friendly", "Halal", "Gluten-free", "Vegan"))
    assert all(menu[c] for c in menu)


def levels(risks):
    return [r.level for r in risks]


def test_short_notice_is_high_risk(make_request, today):
    req = make_request(event_date=today + timedelta(days=3))
    assert levels(assess_risks(req, allocate_budget(req), today))[0] == "High"


def test_wedding_needs_longer_lead(make_request, today):
    req = make_request(event_type="Wedding", event_date=today + timedelta(days=60), budget=1_000_000)
    assert any("90+" in r.message for r in assess_risks(req, allocate_budget(req), today))


def test_tight_budget_flagged(make_request, today):
    req = make_request(guests=200, budget=20000)
    assert any("Budget" in r.message and r.level == "High" for r in assess_risks(req, allocate_budget(req), today))


def test_rain_and_weekend(make_request, today):
    req = make_request(outdoor=True, event_date=date(2027, 7, 10), budget=500000)
    msgs = " ".join(r.message for r in assess_risks(req, allocate_budget(req), today))
    assert "rainy" in msgs
    sat = make_request(event_date=date(2026, 12, 26))
    assert any(r.level == "Info" for r in assess_risks(sat, allocate_budget(sat), today))


def test_outdoor_wheelchair_and_many_diets(make_request, today):
    req = make_request(outdoor=True, accessibility=("Wheelchair access",), dietary=("Vegan", "Jain", "Halal"))
    msgs = " ".join(r.message for r in assess_risks(req, allocate_budget(req), today))
    assert "wheelchair" in msgs and "dietary" in msgs


def test_risks_sorted_by_severity(make_request, today):
    req = make_request(event_date=today + timedelta(days=3), guests=300, budget=30000)
    order = {"High": 0, "Medium": 1, "Info": 2}
    ranks = [order[r.level] for r in assess_risks(req, allocate_budget(req), today)]
    assert ranks == sorted(ranks)
