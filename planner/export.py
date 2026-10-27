"""Export a plan as Markdown (readable) or iCalendar (calendar reminders)."""
from __future__ import annotations

import hashlib
from datetime import date, timedelta

from .engine import Plan
from .utils import format_inr


def to_markdown(plan: Plan) -> str:
    r, b, lg = plan.request, plan.budget, plan.logistics
    out = [
        f"# {r.event_type} plan",
        f"- Date: {r.event_date.isoformat()} ({plan.days_left} days to go)",
        f"- Guests: {r.guests} | Vibe: {r.vibe} | {'Outdoor' if r.outdoor else 'Indoor'}",
        f"- Budget: {format_inr(r.budget)} ({format_inr(b.per_head)} per guest, {b.tier})",
        "",
        "## Budget",
        *[f"- {line.category}: {format_inr(line.amount)} ({line.share:.0%})" for line in b.lines],
        "",
        "## Checklist",
        *[f"- [ ] {t.due.isoformat()} - {t.title} ({t.category})" for t in plan.timeline],
        "",
        "## Logistics",
        f"- Venue capacity {lg.venue_capacity} (~{lg.venue_area_sqft} sq ft), {lg.tables} tables, {lg.chairs} chairs",
        f"- {lg.food_portions} food portions, {lg.drink_units} drinks, {lg.service_staff} service staff, "
        f"{lg.restrooms} restrooms, {lg.parking_spots} parking spots",
        "",
        "## Menu ideas",
        *[f"- {course}: {', '.join(dishes)}" for course, dishes in plan.menu.items()],
        "",
        "## Risks",
        *[f"- [{risk.level}] {risk.message}" for risk in plan.risks],
    ]
    return "\n".join(out) + "\n"


def _ics_escape(text: str) -> str:
    return (text.replace("\\", "\\\\").replace(";", "\\;").replace(",", "\\,")
            .replace("\r", "").replace("\n", "\\n"))


def to_ics(plan: Plan, stamp: date | None = None) -> str:
    """One all-day calendar event per checklist task."""
    stamp = stamp or date.today()
    lines = ["BEGIN:VCALENDAR", "VERSION:2.0", "PRODID:-//Celebration Event Planner//EN", "CALSCALE:GREGORIAN"]
    for task in plan.timeline:
        uid = hashlib.sha1(f"{plan.request.event_type}{task.title}{task.due}".encode()).hexdigest()[:16]
        lines += [
            "BEGIN:VEVENT",
            f"UID:{uid}@event-planner",
            f"DTSTAMP:{stamp:%Y%m%d}T000000Z",
            f"DTSTART;VALUE=DATE:{task.due:%Y%m%d}",
            f"DTEND;VALUE=DATE:{task.due + timedelta(days=1):%Y%m%d}",
            f"SUMMARY:{_ics_escape(task.title)}",
            f"CATEGORIES:{_ics_escape(task.category)}",
            "END:VEVENT",
        ]
    lines.append("END:VCALENDAR")
    return "\r\n".join(lines) + "\r\n"
