"""Guest-count driven quantities and a dietary-aware menu."""
from __future__ import annotations

from dataclasses import dataclass
from math import ceil

from .models import DIETARY, EventRequest

CAKE_EVENTS = {"Birthday", "Anniversary", "Baby Shower", "Graduation"}
SQFT_PER_GUEST_INDOOR = 12
SQFT_PER_GUEST_OUTDOOR = 15


@dataclass(frozen=True)
class Logistics:
    venue_capacity: int
    venue_area_sqft: int
    food_portions: int
    drink_units: int
    cake_servings: int
    chairs: int
    tables: int
    service_staff: int
    restrooms: int
    parking_spots: int


def _scaled(guests: int, percent: int) -> int:
    """ceil(guests * percent / 100) using integer math (avoids float drift like 100*1.1)."""
    return -(-guests * percent // 100)


def plan_logistics(req: EventRequest) -> Logistics:
    g = req.guests
    capacity = _scaled(g, 110)
    sqft = SQFT_PER_GUEST_OUTDOOR if req.outdoor else SQFT_PER_GUEST_INDOOR
    return Logistics(
        venue_capacity=capacity,
        venue_area_sqft=capacity * sqft,
        food_portions=_scaled(g, 110),
        drink_units=g * 4,
        cake_servings=g if req.event_type in CAKE_EVENTS else 0,
        chairs=_scaled(g, 105),
        tables=ceil(g / 8),
        service_staff=max(2, ceil(g / 20)),
        restrooms=max(2, ceil(g / 50)),
        parking_spots=ceil(g / 3),
    )


_ALL = frozenset(DIETARY)
_V, _VG, _J, _H, _GF, _NF, _DB = (
    "Vegetarian", "Vegan", "Jain", "Halal", "Gluten-free", "Nut allergy", "Diabetic-friendly",
)

# (course, dish, diets it satisfies). "Nut allergy" means nut-free.
_MENU = (
    ("Starter", "Paneer tikka", frozenset({_V, _H, _GF, _NF})),
    ("Starter", "Hummus with veg crudités", frozenset({_V, _VG, _H, _GF, _NF, _DB})),
    ("Starter", "Chicken seekh kebab", frozenset({_H, _GF, _NF, _DB})),
    ("Starter", "Sprouts chaat (no onion/garlic)", frozenset({_V, _VG, _J, _H, _GF, _NF, _DB})),
    ("Main", "Dal tadka with jeera rice", frozenset({_V, _VG, _J, _H, _GF, _NF})),
    ("Main", "Paneer butter masala with naan", frozenset({_V, _H})),
    ("Main", "Veg pulao with raita", frozenset({_V, _H, _GF, _NF})),
    ("Main", "Chicken biryani", frozenset({_H, _GF, _NF})),
    ("Main", "Millet khichdi with vegetables", frozenset({_V, _VG, _J, _H, _GF, _NF, _DB})),
    ("Dessert", "Fresh fruit platter", _ALL),
    ("Dessert", "Gulab jamun", frozenset({_V, _H, _NF})),
    ("Dessert", "Coconut milk pudding", frozenset({_V, _VG, _J, _H, _GF, _NF})),
    ("Drink", "Fresh lime soda (sugar optional)", _ALL),
    ("Drink", "Mint-cucumber cooler", _ALL),
)
COURSES = ("Starter", "Main", "Dessert", "Drink")


def menu_suggestions(dietary: tuple[str, ...]) -> dict[str, tuple[str, ...]]:
    """Dishes that satisfy EVERY selected dietary requirement, grouped by course."""
    needed = set(dietary)
    menu: dict[str, tuple[str, ...]] = {}
    for course in COURSES:
        dishes = tuple(name for c, name, tags in _MENU if c == course and needed <= tags)
        menu[course] = dishes or (f"Ask the caterer for a custom option ({', '.join(sorted(needed))})",)
    return menu
