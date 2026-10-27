from datetime import date, timedelta

import pytest

from planner import EventRequest

TODAY = date(2026, 10, 26)


@pytest.fixture
def today():
    return TODAY


@pytest.fixture
def make_request():
    """Factory for valid requests; override any field per test."""
    def _make(**overrides):
        data = dict(event_type="Birthday", guests=50, budget=100000.0,
                    event_date=TODAY + timedelta(days=60), city="Toronto", vibe="Casual")
        data.update(overrides)
        return EventRequest(**data)
    return _make
