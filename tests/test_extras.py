"""Tests for the merged extras: invitation, vendors, schedule, games,
music, items, currency, and the Community Event type."""

from datetime import date, timedelta

from planner import (day_schedule, format_money, games_for, invitation_text,
                     item_list, music_by_moment, vendor_checklist)
from planner import EventRequest, build_plan

TODAY = date(2026, 10, 26)


def _req(**overrides):
    data = dict(event_type="Birthday", guests=50, budget=100000.0,
                event_date=TODAY + timedelta(days=60), city="Toronto",
                vibe="Casual", event_name="Ava's Birthday", currency="CAD")
    data.update(overrides)
    return EventRequest(**data)


def test_invitation_contains_name_date_and_theme():
    text = invitation_text(_req(), "Space")
    assert "Ava's Birthday" in text
    assert "Space" in text
    assert "50 guests" in text


def test_community_event_builds_and_budgets():
    plan = build_plan(_req(event_type="Community Event"), TODAY)
    assert sum(line.amount for line in plan.budget.lines) == 100000.0
    assert plan.timeline  # includes community-specific tasks


def test_vendor_schedule_games_music_are_non_empty():
    assert vendor_checklist("Birthday")
    assert day_schedule("Wedding")
    assert games_for("Birthday")
    assert music_by_moment()


def test_item_list_scales_with_guests():
    items = {i["item"]: i["quantity"] for i in item_list(50)}
    assert items["Return gifts / Favours"] == 50
    assert items["Plates"] >= 50


def test_format_money_currencies():
    assert format_money(1000, "USD") == "$1,000"
    assert format_money(1000, "CAD") == "C$1,000"
    assert format_money(1000, "INR").startswith("₹")


def test_unknown_currency_is_rejected():
    import pytest

    from planner import ValidationError

    with pytest.raises(ValidationError):
        build_plan(_req(currency="XXX"), TODAY)
