"""Celebration & Event Planner: rule-based planning engine with optional Gen AI ideas."""
from .ai import (MAX_AI_CALLS_PER_SESSION, AIUnavailableError, build_prompt,
                 generate_ideas, local_ideas)
from .engine import Plan, build_plan
from .export import to_ics, to_markdown
from .catalog import (CAKE_FLAVOURS, DECOR_SECTIONS, EVENT_TEMPLATES,
                      GAMES_LIBRARY, INVITATION_TEMPLATES, KIDS_ACTIVITIES,
                      MUSIC_LIBRARY, PRODUCTS, SAMPLE_VENDORS, THEMES)
from .extras import (day_schedule, games_for, invitation_text, item_list,
                     music_by_moment, vendor_checklist)
from .market import (ai_assistant_reply, budget_optimisation, lucky_draw_winner,
                     mailto_link, make_collage_png, make_event_website_html,
                     make_plan_pdf, make_qr_png, seating_assign, whatsapp_link)
from .models import (ACCESSIBILITY, CURRENCIES, DIETARY, EVENT_TYPES, MAX_BUDGET, MAX_CITY,
                     MAX_GUESTS, MAX_NOTES, VIBES, EventRequest, ValidationError)
from .utils import format_inr, format_money

__all__ = [
    "ACCESSIBILITY", "CURRENCIES", "DIETARY", "EVENT_TYPES", "VIBES", "MAX_BUDGET", "MAX_CITY",
    "MAX_GUESTS", "MAX_NOTES", "MAX_AI_CALLS_PER_SESSION", "AIUnavailableError",
    "EventRequest", "Plan", "ValidationError", "build_plan", "build_prompt",
    "CAKE_FLAVOURS", "DECOR_SECTIONS", "EVENT_TEMPLATES", "GAMES_LIBRARY",
    "INVITATION_TEMPLATES", "KIDS_ACTIVITIES", "MUSIC_LIBRARY", "PRODUCTS",
    "SAMPLE_VENDORS", "THEMES",
    "ai_assistant_reply", "budget_optimisation", "day_schedule", "format_inr",
    "format_money", "games_for", "generate_ideas", "invitation_text",
    "item_list", "local_ideas", "lucky_draw_winner", "mailto_link",
    "make_collage_png", "make_event_website_html", "make_plan_pdf",
    "make_qr_png", "music_by_moment", "seating_assign",
    "to_ics", "to_markdown", "vendor_checklist", "whatsapp_link",
]
