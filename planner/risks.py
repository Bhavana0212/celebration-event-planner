"""Rule-based risk detection from the user's context."""
from __future__ import annotations

from dataclasses import dataclass
from datetime import date

from .budget import BudgetSummary
from .models import EventRequest
from .timeline import days_until

RAIN_MONTHS = {6, 7, 8, 9}
PEAK_WEDDING_MONTHS = {11, 12, 1, 2}
_ORDER = {"High": 0, "Medium": 1, "Info": 2}


@dataclass(frozen=True)
class Risk:
    level: str  # High | Medium | Info
    message: str


def assess_risks(req: EventRequest, budget: BudgetSummary, today: date | None = None) -> tuple[Risk, ...]:
    today = today or date.today()
    days_left = days_until(req.event_date, today)
    min_lead = 90 if req.event_type == "Wedding" else 30
    risks: list[Risk] = []

    if days_left < 7:
        risks.append(Risk("High", f"Only {days_left} day(s) left. Prioritise venue, food and headcount first; "
                                  "keep the guest list small."))
    elif days_left < min_lead:
        risks.append(Risk("Medium", f"{req.event_type} events usually need {min_lead}+ days of lead time; "
                                    f"you have {days_left}. Book venue and caterer this week."))

    if budget.tier == "Very tight":
        risks.append(Risk("High", "Budget per guest is well below typical. " + budget.advice))
    elif budget.tier == "Tight":
        risks.append(Risk("Medium", "Budget per guest is on the low side. " + budget.advice))

    if req.outdoor and req.event_date.month in RAIN_MONTHS:
        risks.append(Risk("Medium", "Outdoor event in the rainy season: book a tent or indoor backup."))
    if req.outdoor and "Wheelchair access" in req.accessibility:
        risks.append(Risk("Medium", "Outdoor + wheelchair access: ensure firm, ramped paths and accessible restrooms."))
    if req.event_type == "Wedding" and req.event_date.month in PEAK_WEDDING_MONTHS:
        risks.append(Risk("Medium", "Peak wedding season: venues and photographers sell out early."))
    if req.guests > 200:
        risks.append(Risk("Medium", "Large crowd: plan entry flow, parking, security and first-aid."))
    if len(req.dietary) >= 3:
        risks.append(Risk("Medium", "Many dietary needs: use clearly labelled buffet stations and ask guests in the RSVP."))
    if req.event_date.weekday() >= 5:
        risks.append(Risk("Info", "Weekend dates usually cost 10-20% more at venues; a weekday could save money."))

    risks.sort(key=lambda r: _ORDER[r.level])
    return tuple(risks)
