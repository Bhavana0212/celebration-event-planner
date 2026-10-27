"""Small, dependency-free helpers shared across the planner."""
from __future__ import annotations

import re

_CONTROL_RE = re.compile(r"[\x00-\x08\x0b-\x1f\x7f]")


def format_inr(value: float) -> str:
    """Format a number as Indian Rupees using lakh/crore digit grouping."""
    n = int(round(value))
    digits = str(abs(n))
    if len(digits) > 3:
        head, tail = digits[:-3], digits[-3:]
        parts: list[str] = []
        while len(head) > 2:
            parts.insert(0, head[-2:])
            head = head[:-2]
        if head:
            parts.insert(0, head)
        digits = ",".join(parts + [tail])
    return f"{'-' if n < 0 else ''}₹{digits}"


_SYMBOLS = {"INR": "₹", "USD": "$", "CAD": "C$", "GBP": "£", "EUR": "€"}


def format_money(value: float, currency: str = "INR") -> str:
    """Format money in the chosen currency. INR keeps lakh/crore grouping."""
    if currency == "INR":
        return format_inr(value)
    symbol = _SYMBOLS.get(currency, currency + " ")
    n = int(round(value))
    return f"{'-' if n < 0 else ''}{symbol}{abs(n):,}"


def clean_text(text: str | None, max_len: int) -> str:
    """Strip control characters, collapse whitespace and cap the length."""
    text = _CONTROL_RE.sub("", text or "")
    return " ".join(text.split())[:max_len]
