"""Features that were in the first Streamlit build but not in the
rule-based engine: invitation, vendor checklist, day schedule, games,
music, and a guest-scaled item list.

All functions are pure and tested. They take the validated EventRequest
(or just an event type) and return plain data the UI can render.
"""

from __future__ import annotations

import math

from .models import EventRequest

VENDORS = {
    "Wedding": ["Venue", "Caterer", "Decorator", "Photographer",
                "Videographer", "DJ / Band", "Cake / Dessert"],
    "Birthday": ["Venue", "Caterer", "Decorator", "Photographer",
                 "DJ", "Cake Shop", "Games Host"],
    "Anniversary": ["Venue", "Caterer", "Decorator", "Photographer", "DJ", "Cake Shop"],
    "Baby Shower": ["Venue", "Caterer", "Decorator", "Photographer", "Cake Shop"],
    "Corporate Party": ["Venue", "Caterer", "Decorator", "Photographer", "Sound / AV", "Host / MC"],
    "Festival / Cultural": ["Venue", "Caterer", "Decorator", "Photographer", "Sound System", "Performers"],
    "Graduation": ["Venue", "Caterer", "Decorator", "Photographer", "DJ"],
    "Community Event": ["Venue", "Caterer", "Decorator", "Photographer", "Sound System", "Volunteers"],
    "Engagement": ["Venue", "Caterer", "Decorator", "Photographer", "DJ", "Cake Shop"],
    "Retirement": ["Venue", "Caterer", "Decorator", "Photographer", "Host / MC"],
    "Housewarming": ["Caterer", "Decorator", "Photographer"],
    "Farewell": ["Venue", "Caterer", "Decorator", "DJ"],
    "Holiday Party": ["Venue", "Caterer", "Decorator", "DJ", "Photographer"],
    "Dinner Party": ["Caterer", "Decorator"],
    "Surprise Party": ["Venue", "Caterer", "Decorator", "Cake Shop", "Photographer"],
    "Family Reunion": ["Venue", "Caterer", "Decorator", "Photographer", "Sound System"],
    "School / College Event": ["Venue", "Caterer", "Decorator", "Sound / AV", "Host / MC"],
    "Sports Celebration": ["Venue", "Caterer", "Decorator", "DJ", "Photographer"],
}

DAY_SCHEDULE = {
    "Wedding": [
        ("Welcome & seating", "Guests arrive, music, photos"),
        ("Ceremony / Main moment", "The central celebration"),
        ("Photos & congratulations", "Family and group photos"),
        ("Dinner", "Catering service and speeches"),
        ("Cake / Dessert", "Cutting and serving"),
        ("Dance & celebration", "DJ / band, open dance floor"),
        ("Thank-you & close", "Favours, goodbyes, wrap-up"),
    ],
    "Birthday": [
        ("Welcome & photos", "Guests arrive, photo corner"),
        ("Games begin", "See the Games section for the full list"),
        ("Cake cutting", "Singing, photos, serving"),
        ("Food & music", "Dinner / snacks and background music"),
        ("Free play & dance", "Open time for guests"),
        ("Thank-you & gifts", "Return gifts and goodbyes"),
    ],
    "Community Event": [
        ("Registration & welcome", "Sign-in, name tags, welcome music"),
        ("Opening & introductions", "Host welcome and agenda"),
        ("Activities & games", "See the Games section for the full list"),
        ("Food & social time", "Shared meal and conversation"),
        ("Main programme", "Performances, awards or talks"),
        ("Thank-you & close", "Volunteer thanks and clean-up plan"),
    ],
}
_DEFAULT_SCHEDULE = [
    ("Welcome", "Guests arrive, music, photos"),
    ("Main programme", "The central celebration"),
    ("Food & social time", "Shared meal and conversation"),
    ("Entertainment", "Games, music or performances"),
    ("Thank-you & close", "Goodbyes and wrap-up"),
]

GAMES = {
    "Wedding": [
        ("Couple quiz", "20 min", "Guests guess answers about the couple"),
        ("Photo scavenger hunt", "30 min", "Teams find photo moments around the venue"),
        ("Dance floor challenge", "20 min", "Friendly dance-off, all ages welcome"),
    ],
    "Birthday": [
        ("Treasure hunt", "20 min", "Clues themed to the party theme"),
        ("Balloon pop relay", "15 min", "Team relay, high energy"),
        ("Musical chairs", "15 min", "Classic, works for mixed ages"),
        ("DIY craft station", "All evening", "A quiet corner for kids who want to make something"),
    ],
    "Community Event": [
        ("Team trivia", "20 min", "Neighbourhood and general-knowledge rounds"),
        ("Relay games", "25 min", "Mixed-age teams, outdoors if possible"),
        ("Talent showcase", "30 min", "Open-mic style, sign up in advance"),
    ],
    "Corporate Party": [
        ("Icebreaker bingo", "20 min", "Cross-team mixing"),
        ("Team trivia", "20 min", "Fun, work-friendly rounds"),
        ("Awards with fun categories", "20 min", "Light-hearted team awards"),
    ],
}
_DEFAULT_GAMES = [
    ("Team trivia", "20 min", "Mixed-age teams, easy to run"),
    ("Photo challenge", "20 min", "Teams capture themed photos"),
]

MUSIC_BY_MOMENT = [
    ("Welcome", "Soft, upbeat background music while guests arrive"),
    ("Games / Activities", "High-energy tracks to keep energy up"),
    ("Cake / Main moment", "A celebratory mix for the big moment"),
    ("Dinner / Social", "Relaxed background music for conversation"),
    ("Dance time", "Party hits everyone can dance to"),
    ("Wind-down", "Chill songs as the event closes"),
]


def _ceil_to_10(n: float) -> int:
    return int(math.ceil(n / 10.0) * 10)


def invitation_text(req: EventRequest, theme: str = "") -> str:
    """Ready-to-copy invitation text. No personal data beyond the inputs."""
    name = req.event_name.strip() or f"{req.event_type} Celebration"
    return (
        f"You're invited!\n\n{name} — {req.event_type}\n"
        f"Date: {req.event_date.isoformat()}\n"
        f"City: {req.city or 'To be confirmed'}\n"
        f"Vibe: {req.vibe}{' (Outdoor)' if req.outdoor else ''}\n"
        + (f"Theme: {theme.strip()}\n" if theme.strip() else "")
        + f"\nJoin us for a celebration with {req.guests} guests. "
          "Please RSVP so we can plan food, seating and return gifts for everyone."
    )


def vendor_checklist(event_type: str) -> list[str]:
    return list(VENDORS.get(event_type, VENDORS["Community Event"]))


def day_schedule(event_type: str) -> list[tuple[str, str]]:
    return list(DAY_SCHEDULE.get(event_type, _DEFAULT_SCHEDULE))


def games_for(event_type: str) -> list[tuple[str, str, str]]:
    return list(GAMES.get(event_type, _DEFAULT_GAMES))


def music_by_moment() -> list[tuple[str, str]]:
    return list(MUSIC_BY_MOMENT)


def item_list(guests: int) -> list[dict]:
    """Shopping quantities scaled from the guest count, with a 10% buffer."""
    return [
        {"item": "Plates", "quantity": _ceil_to_10(guests * 1.1), "unit": "pieces"},
        {"item": "Cups / Glasses", "quantity": _ceil_to_10(guests * 1.1), "unit": "pieces"},
        {"item": "Napkins", "quantity": _ceil_to_10(guests * 1.2), "unit": "pieces"},
        {"item": "Balloons / Decor pieces", "quantity": guests * 2, "unit": "pieces"},
        {"item": "Cake / Dessert servings", "quantity": guests, "unit": "servings"},
        {"item": "Return gifts / Favours", "quantity": guests, "unit": "pieces"},
        {"item": "Chairs / Seating", "quantity": guests, "unit": "pieces"},
    ]
