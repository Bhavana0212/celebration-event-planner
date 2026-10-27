from datetime import timedelta

from planner.timeline import build_timeline, days_until


def titles(tasks):
    return [t.title for t in tasks]


def test_sorted_by_due_date(make_request, today):
    tasks = build_timeline(make_request(), today)
    assert [t.due for t in tasks] == sorted(t.due for t in tasks)


def test_plenty_of_time_has_no_urgent_tasks(make_request, today):
    tasks = build_timeline(make_request(event_date=today + timedelta(days=200)), today)
    assert not any(t.urgent for t in tasks)


def test_short_notice_flags_overdue_tasks(make_request, today):
    tasks = build_timeline(make_request(event_date=today + timedelta(days=10)), today)
    venue = next(t for t in tasks if t.title == "Book the venue")
    assert venue.urgent and venue.due == today and venue.status == "Do now"


def test_event_day_and_followup_never_urgent(make_request, today):
    tasks = build_timeline(make_request(event_date=today), today)
    for t in tasks:
        if t.days_before <= 0:
            assert not t.urgent


def test_conditional_tasks(make_request, today):
    base = titles(build_timeline(make_request(), today))
    rich = titles(build_timeline(make_request(outdoor=True, dietary=("Vegan",),
                                              accessibility=("Quiet space",), guests=300), today))
    assert not any("weather" in t for t in base)
    for keyword in ("weather", "dietary", "accessibility", "parking"):
        assert any(keyword in t for t in rich)


def test_event_specific_tasks(make_request, today):
    assert any("officiant" in t for t in titles(build_timeline(make_request(event_type="Wedding"), today)))
    assert any("cake" in t for t in titles(build_timeline(make_request(event_type="Birthday"), today)))


def test_days_until(today):
    assert days_until(today + timedelta(days=5), today) == 5
