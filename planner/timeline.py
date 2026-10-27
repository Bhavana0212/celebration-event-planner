"""Countdown checklist that adapts to how much time is left."""
from __future__ import annotations

from dataclasses import dataclass
from datetime import date, timedelta

from .models import EventRequest

# (title, category, days before the event). Negative = after the event.
_COMMON = (
    ("Confirm final budget and guest list", "Planning", 90),
    ("Book the venue", "Venue", 80),
    ("Book caterer and finalise the menu", "Catering", 60),
    ("Hire photographer / videographer", "Vendors", 55),
    ("Book music / entertainment", "Vendors", 50),
    ("Send invitations", "Guests", 35),
    ("Order decor and supplies", "Decor", 25),
    ("Confirm RSVPs and headcount", "Guests", 14),
    ("Finalise seating plan and run-of-show", "Planning", 7),
    ("Reconfirm every vendor (time, place, payment)", "Vendors", 3),
    ("Pack the event-day kit (tape, scissors, chargers, first-aid)", "Logistics", 1),
    ("Event day: set-up, vendor check-in, enjoy!", "Event day", 0),
    ("Send thank-you notes and share photos", "Follow-up", -3),
)

_EVENT_TASKS = {
    "Wedding": (
        ("Book officiant / priest and confirm auspicious date", "Planning", 100),
        ("Plan outfits and schedule fittings", "Planning", 75),
        ("Arrange accommodation for out-of-town guests", "Guests", 45),
    ),
    "Birthday": (
        ("Plan games and activities", "Entertainment", 21),
        ("Order the cake", "Catering", 14),
    ),
    "Anniversary": (("Prepare a memory montage or surprise", "Entertainment", 21),),
    "Baby Shower": (("Set up gift registry and plan games", "Entertainment", 30),),
    "Corporate Party": (
        ("Get management sign-off on budget and agenda", "Planning", 70),
        ("Share agenda and dress code with attendees", "Guests", 10),
        ("Test AV, microphones and projector", "Logistics", 5),
    ),
    "Festival / Cultural": (
        ("Check permits (loudspeaker, community hall, fire safety)", "Planning", 30),
        ("Arrange ritual / puja materials and volunteers", "Logistics", 10),
    ),
    "Graduation": (
        ("Confirm ceremony schedule with the institution", "Planning", 30),
        ("Prepare slideshow and photo wall", "Decor", 14),
    ),
    "Community Event": (
        ("Confirm community hall / permits", "Planning", 30),
        ("Recruit volunteers and assign roles", "Logistics", 21),
        ("Share the event in community groups", "Guests", 14),
    ),
}


@dataclass(frozen=True)
class Task:
    title: str
    category: str
    due: date
    days_before: int
    urgent: bool

    @property
    def status(self) -> str:
        if self.urgent:
            return "Do now"
        return "After event" if self.days_before < 0 else "Scheduled"


def days_until(event_date: date, today: date | None = None) -> int:
    return (event_date - (today or date.today())).days


def _conditional_specs(req: EventRequest) -> list[tuple[str, str, int]]:
    specs: list[tuple[str, str, int]] = []
    if req.dietary:
        specs.append(("Collect dietary needs in RSVPs and brief the caterer", "Catering", 30))
    if req.accessibility:
        specs.append(("Visit venue to verify accessibility features", "Venue", 45))
    if req.outdoor:
        specs.append(("Arrange weather backup (tent / indoor plan B)", "Venue", 20))
    if req.guests > 150:
        specs.append(("Plan parking, crowd flow and security", "Logistics", 21))
    return specs


def build_timeline(req: EventRequest, today: date | None = None) -> tuple[Task, ...]:
    """Tasks sorted by due date. Overdue pre-event tasks are pulled to today and flagged."""
    today = today or date.today()
    specs = [*_COMMON, *_EVENT_TASKS.get(req.event_type, ()), *_conditional_specs(req)]

    tasks: list[Task] = []
    for title, category, days_before in specs:
        due = req.event_date - timedelta(days=days_before)
        urgent = days_before > 0 and due < today
        tasks.append(Task(title, category, today if urgent else due, days_before, urgent))
    tasks.sort(key=lambda t: (t.due, -t.days_before, t.title))
    return tuple(tasks)
