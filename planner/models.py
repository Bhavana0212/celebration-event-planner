"""Domain model and input validation for an event request."""
from __future__ import annotations

import re
from dataclasses import dataclass, replace
from datetime import date

from .utils import clean_text

EVENT_TYPES = (
    "Birthday",
    "Wedding",
    "Anniversary",
    "Baby Shower",
    "Corporate Party",
    "Festival / Cultural",
    "Graduation",
    "Community Event",
)
CURRENCIES = ("INR", "USD", "CAD", "GBP", "EUR")
CURRENCY_SYMBOLS = {"INR": "₹", "USD": "$", "CAD": "C$", "GBP": "£", "EUR": "€"}
VIBES = ("Casual", "Elegant", "Fun & Playful", "Traditional", "Minimalist")
DIETARY = (
    "Vegetarian",
    "Vegan",
    "Jain",
    "Halal",
    "Gluten-free",
    "Nut allergy",
    "Diabetic-friendly",
)
ACCESSIBILITY = (
    "Wheelchair access",
    "Step-free entry",
    "Seating for elders",
    "Sign-language / captions",
    "Quiet space",
    "Kid-friendly area",
)

MAX_GUESTS = 1000
MAX_BUDGET = 100_000_000
MAX_CITY = 80
MAX_NOTES = 500

_CITY_RE = re.compile(r"^[\w\s.,'\-]+$", re.UNICODE)


class ValidationError(ValueError):
    """Raised when the supplied event details are invalid."""


@dataclass(frozen=True)
class EventRequest:
    """Everything the planner needs to know about the celebration."""

    event_type: str
    guests: int
    budget: float
    event_date: date
    city: str = ""
    vibe: str = "Casual"
    dietary: tuple[str, ...] = ()
    accessibility: tuple[str, ...] = ()
    outdoor: bool = False
    notes: str = ""
    # Added in the merged market version. Defaults keep every existing
    # construction (positional or keyword) working unchanged.
    event_name: str = ""
    currency: str = "INR"

    def validated(self, today: date | None = None) -> "EventRequest":
        """Return a sanitised copy, or raise ValidationError listing every problem."""
        today = today or date.today()
        errors: list[str] = []

        if self.event_type not in EVENT_TYPES:
            errors.append("Unknown event type")
        if self.vibe not in VIBES:
            errors.append("Unknown vibe")
        if not isinstance(self.guests, int) or not 1 <= self.guests <= MAX_GUESTS:
            errors.append(f"Guests must be between 1 and {MAX_GUESTS}")
        if not 0 < self.budget <= MAX_BUDGET:  # also rejects NaN
            errors.append("Budget must be greater than 0 and realistic")
        if self.event_date < today:
            errors.append("Event date cannot be in the past")

        city = clean_text(self.city, MAX_CITY)
        if city and not _CITY_RE.match(city):
            errors.append("City contains unsupported characters")

        dietary = self._known(self.dietary, DIETARY, "dietary option", errors)
        access = self._known(self.accessibility, ACCESSIBILITY, "accessibility option", errors)
        if self.currency not in CURRENCIES:
            errors.append("Unknown currency")

        if errors:
            raise ValidationError("; ".join(errors))
        return replace(
            self,
            city=city,
            dietary=dietary,
            accessibility=access,
            notes=clean_text(self.notes, MAX_NOTES),
            event_name=clean_text(self.event_name, 120),
        )

    @staticmethod
    def _known(values, allowed, label: str, errors: list[str]) -> tuple[str, ...]:
        unknown = [v for v in values if v not in allowed]
        if unknown:
            errors.append(f"Unknown {label}: {', '.join(map(str, unknown))}")
        return tuple(dict.fromkeys(values))
