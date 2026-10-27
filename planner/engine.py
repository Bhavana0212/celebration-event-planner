"""Orchestrates all planning rules into one immutable Plan."""
from __future__ import annotations

from dataclasses import dataclass
from datetime import date

from .budget import BudgetSummary, allocate_budget
from .logistics import Logistics, menu_suggestions, plan_logistics
from .models import EventRequest
from .risks import Risk, assess_risks
from .timeline import Task, build_timeline, days_until


@dataclass(frozen=True)
class Plan:
    request: EventRequest
    days_left: int
    budget: BudgetSummary
    timeline: tuple[Task, ...]
    logistics: Logistics
    menu: dict
    risks: tuple[Risk, ...]


def build_plan(req: EventRequest, today: date | None = None) -> Plan:
    """Validate the request and compute every part of the plan."""
    today = today or date.today()
    req = req.validated(today)
    budget = allocate_budget(req)
    return Plan(
        request=req,
        days_left=days_until(req.event_date, today),
        budget=budget,
        timeline=build_timeline(req, today),
        logistics=plan_logistics(req),
        menu=menu_suggestions(req.dietary),
        risks=assess_risks(req, budget, today),
    )
