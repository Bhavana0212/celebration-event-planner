"""Context-aware budget allocation.

Each event type starts from a base split. The split is then adjusted for the
vibe, dietary needs, accessibility needs and indoor/outdoor setting, and
re-normalised so the lines always add up to exactly the user's budget.
"""
from __future__ import annotations

from dataclasses import dataclass

from .models import EventRequest

CATEGORIES = (
    "Venue",
    "Catering",
    "Decor",
    "Entertainment",
    "Photography",
    "Invitations & Gifts",
    "Contingency",
)

# Shares in CATEGORIES order; each row sums to 1.0.
BASE_SHARES = {
    "Birthday":            (0.20, 0.35, 0.12, 0.10, 0.06, 0.07, 0.10),
    "Wedding":             (0.25, 0.30, 0.12, 0.08, 0.10, 0.05, 0.10),
    "Anniversary":         (0.22, 0.33, 0.13, 0.10, 0.07, 0.05, 0.10),
    "Baby Shower":         (0.18, 0.32, 0.17, 0.10, 0.05, 0.08, 0.10),
    "Corporate Party":     (0.30, 0.30, 0.08, 0.12, 0.05, 0.05, 0.10),
    "Festival / Cultural": (0.15, 0.35, 0.20, 0.12, 0.05, 0.03, 0.10),
    "Graduation":          (0.20, 0.38, 0.10, 0.08, 0.08, 0.06, 0.10),
    "Community Event":     (0.18, 0.34, 0.16, 0.12, 0.05, 0.05, 0.10),
    "Engagement":          (0.24, 0.30, 0.13, 0.08, 0.09, 0.06, 0.10),
    "Retirement":          (0.20, 0.35, 0.10, 0.10, 0.06, 0.09, 0.10),
    "Housewarming":        (0.15, 0.35, 0.18, 0.08, 0.04, 0.10, 0.10),
    "Farewell":            (0.18, 0.35, 0.12, 0.12, 0.05, 0.08, 0.10),
    "Holiday Party":       (0.20, 0.35, 0.15, 0.12, 0.05, 0.03, 0.10),
    "Dinner Party":        (0.15, 0.45, 0.10, 0.08, 0.05, 0.07, 0.10),
    "Surprise Party":      (0.20, 0.35, 0.12, 0.10, 0.06, 0.07, 0.10),
    "Family Reunion":      (0.18, 0.38, 0.12, 0.08, 0.06, 0.08, 0.10),
    "School / College Event": (0.15, 0.30, 0.15, 0.18, 0.05, 0.07, 0.10),
    "Sports Celebration":  (0.20, 0.32, 0.10, 0.18, 0.05, 0.05, 0.10),
}

# Typical comfortable spend per guest (INR) used to judge feasibility.
BASELINE_PER_HEAD = {
    "Birthday": 1200,
    "Wedding": 2500,
    "Anniversary": 1800,
    "Baby Shower": 1500,
    "Corporate Party": 2000,
    "Festival / Cultural": 1000,
    "Graduation": 1500,
    "Community Event": 1200,
    "Engagement": 2000,
    "Retirement": 1500,
    "Housewarming": 1200,
    "Farewell": 1300,
    "Holiday Party": 1300,
    "Dinner Party": 1500,
    "Surprise Party": 1200,
    "Family Reunion": 1200,
    "School / College Event": 800,
    "Sports Celebration": 1000,
}

VIBE_ADJUST = {
    "Casual": {"Venue": 0.9},
    "Elegant": {"Decor": 1.25, "Venue": 1.1},
    "Fun & Playful": {"Entertainment": 1.3},
    "Traditional": {"Decor": 1.1, "Catering": 1.05},
    "Minimalist": {"Decor": 0.7},
}

TIER_ADVICE = {
    "Very tight": "Budget is far below typical. Cut the guest list, choose a home/community venue, "
                  "go with a simple menu and DIY decor.",
    "Tight": "Workable with care. Pick off-peak dates, a fixed-price menu and borrow or rent decor.",
    "Comfortable": "Healthy budget. Keep the contingency untouched and negotiate package deals.",
    "Generous": "Room to upgrade. Consider premium venue, live entertainment or a videographer.",
}


@dataclass(frozen=True)
class BudgetLine:
    category: str
    share: float
    amount: float


@dataclass(frozen=True)
class BudgetSummary:
    lines: tuple[BudgetLine, ...]
    per_head: float
    tier: str
    advice: str


def _multipliers(req: EventRequest) -> dict[str, float]:
    m = {c: 1.0 for c in CATEGORIES}
    for category, factor in VIBE_ADJUST[req.vibe].items():
        m[category] *= factor
    m["Catering"] *= 1 + 0.04 * min(len(req.dietary), 3)
    m["Venue"] *= 1 + 0.03 * min(len(req.accessibility), 3)
    if req.outdoor:  # tents/rentals and weather backup
        m["Decor"] *= 1.1
        m["Venue"] *= 1.05
        m["Contingency"] *= 1.2
    return m


def classify_tier(per_head: float, event_type: str) -> str:
    ratio = per_head / BASELINE_PER_HEAD.get(event_type, BASELINE_PER_HEAD["Community Event"])
    if ratio < 0.6:
        return "Very tight"
    if ratio < 0.9:
        return "Tight"
    if ratio < 1.5:
        return "Comfortable"
    return "Generous"


def allocate_budget(req: EventRequest) -> BudgetSummary:
    """Split the budget across categories based on the event context."""
    base = dict(zip(CATEGORIES, BASE_SHARES.get(req.event_type, BASE_SHARES["Community Event"])))
    mult = _multipliers(req)
    raw = {c: base[c] * mult[c] for c in CATEGORIES}
    total = sum(raw.values())

    lines: list[BudgetLine] = []
    allocated = 0.0
    for i, category in enumerate(CATEGORIES):
        share = raw[category] / total
        if i == len(CATEGORIES) - 1:  # last line absorbs rounding drift
            amount = round(req.budget - allocated, 2)
        else:
            amount = round(req.budget * share, 2)
            allocated += amount
        lines.append(BudgetLine(category, share, amount))

    per_head = req.budget / req.guests
    tier = classify_tier(per_head, req.event_type)
    return BudgetSummary(tuple(lines), per_head, tier, TIER_ADVICE[tier])
