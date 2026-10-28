"""Celebration & Event Planner — v3 market platform (Streamlit).

Hack2Skill Virtual: PromptWars, Challenge 5, by Bhavana Shah.

What v3 adds over v2, in plain terms:
- Home / landing, profile (local), and a multi-event dashboard
- Guests with email/phone, plus-one, dietary, accessibility, RSVP, check-in,
  seating, QR invitations, WhatsApp / email share links, thank-you messages
- Full budget: 18 categories, estimated vs actual, paid/unpaid, advances,
  per-guest cost, warnings, expense report, receipts (file names recorded)
- Food & cake planner, music playlist + song requests, games library with
  filters, quiz & scavenger-hunt builders, lucky draw
- Kids' activities by age, return-gift planner, child safety checklist
- Decor studio: themes, colour palettes, mood board, decor planners,
  decoration shopping list and budget
- Vendor directory (sample + your own), price comparison, reviews,
  booking status, payment milestones, contracts (file names recorded)
- Shopping catalogue + cart (planning estimates, NOT a real checkout)
- Seating planner + 2D floor-plan schematic (tables, not 3D/AR)
- Live event day: run sheet, check-in counter, vendor status, announcements, polls
- Post-event: photo gallery, collage maker, guestbook, gifts registry,
  final report, vendor reviews, duplicate / save as template
- AI Assistant: rule-based chatbot + optional Gemini ideas (capped, fallback)
- Export: Markdown, .ics, CSV, JSON, invitation, event website HTML, PDF plan

Honestly NOT in v3 (see README / FEATURE_COVERAGE.md):
real accounts / OAuth, real payments, real vendor bookings, 3D/AR,
live multi-user sync, email/SMS sending. Those need a backend and
payment provider and are listed as the next phase — they are not faked here.
Data in v3 lives in the browser session unless you download it.
"""

from __future__ import annotations

import csv
import io
import json
import os
import random
from datetime import date, timedelta

import pandas as pd
import streamlit as st

from planner import (
    ACCESSIBILITY, CAKE_FLAVOURS, CURRENCIES, DECOR_SECTIONS, DIETARY,
    EVENT_TEMPLATES, EVENT_TYPES, GAMES_LIBRARY, INVITATION_TEMPLATES,
    KIDS_ACTIVITIES, MAX_AI_CALLS_PER_SESSION, MAX_BUDGET, MAX_CITY,
    MAX_GUESTS, MAX_NOTES, MUSIC_LIBRARY, PRODUCTS, SAMPLE_VENDORS, THEMES,
    VIBES, AIUnavailableError, EventRequest, Plan, ValidationError,
    ai_assistant_reply, budget_optimisation, build_plan, day_schedule,
    format_money, games_for, generate_ideas, invitation_text, item_list,
    local_ideas, lucky_draw_winner, mailto_link, make_collage_png,
    make_event_website_html, make_plan_pdf, make_qr_png, music_by_moment,
    seating_assign, to_ics, to_markdown, vendor_checklist, whatsapp_link,
)

st.set_page_config(
    page_title="Celebration & Event Planner",
    page_icon="🎉",
    layout="wide",
    menu_items={"About": "Celebration & Event Planner — plan weddings, birthdays and community events, start to finish."},
)

RISK_LABEL = {"High": "🔴 High risk", "Medium": "🟠 Medium risk", "Info": "🔵 Tip"}
STATUS_ICON = {"Do now": "⚠️ Do now", "Scheduled": "🗓️ Scheduled", "After event": "💌 After event"}
RSVP_OPTIONS = ("Attending", "Pending", "Declined", "Maybe")
BUDGET_CATEGORIES = ["Venue", "Catering", "Cake", "Decor", "Music", "Entertainment",
                     "Photography", "Videography", "Invitation", "Outfit", "Gifts",
                     "Kids' Activities", "Transport", "Accommodation", "Rental",
                     "Staff", "Taxes & Fees", "Emergency Fund"]
SECTIONS = ["Home", "Plan", "Guests & Invites", "Budget & Expenses",
            "Food & Cake", "Music & Games", "Kids", "Decor & Design",
            "Vendors & Shopping", "Seating & Floor Plan", "Live Event Day",
            "Post-Event & Memories", "AI Assistant", "Profile & Settings",
            "Previews (Mock)"]


@st.cache_data(show_spinner=False, max_entries=64)
def cached_plan(request: EventRequest, today: date) -> Plan:
    return build_plan(request, today)


def money(value: float, currency: str) -> str:
    return format_money(value, currency)


def get_api_key() -> str | None:
    key = os.environ.get("GEMINI_API_KEY")
    if key:
        return key
    try:
        return st.secrets.get("GEMINI_API_KEY")
    except Exception:
        return None


def store(key: str, default):
    return st.session_state.setdefault(key, default)


def plan_or_none() -> Plan | None:
    return st.session_state.get("plan")


def sidebar_plan_form() -> EventRequest | None:
    with st.sidebar:
        st.header("Start planning")
        st.caption("Step 1 — Tell us about your event. Step 2 — Get your full plan.")
        with st.form("event_form"):
            event_name = st.text_input("Event name", "Ava's 10th Birthday Bash", max_chars=120)
            event_type = st.selectbox("Event type", EVENT_TYPES)
            guests = st.number_input("Number of guests", 1, MAX_GUESTS, 50, step=5)
            budget = st.number_input("Total budget", 1000, MAX_BUDGET, 100000, step=5000)
            currency = st.selectbox("Currency", CURRENCIES, index=0)
            event_date = st.date_input("Event date", date.today() + timedelta(days=60),
                                       min_value=date.today())
            end_date = st.date_input("End date (optional, for multi-day events)", value=None,
                                     min_value=date.today())
            event_time = st.time_input("Event time (optional)", value=None)
            city = st.text_input("City (optional)", max_chars=MAX_CITY)
            theme = st.text_input("Theme (optional)", "Space")
            vibe = st.selectbox("Vibe", VIBES)
            outdoor = st.checkbox("Outdoor venue")
            dietary = st.multiselect("Dietary needs", DIETARY)
            access = st.multiselect("Accessibility needs", ACCESSIBILITY)
            notes = st.text_area("Anything else? (optional)", max_chars=MAX_NOTES)
            submitted = st.form_submit_button("Create my plan", type="primary")
        st.caption("Tip: the same form is also at the top of the Home page, and the section menu is now at the top of the page too — no sidebar hunting needed. Data lives in this browser session unless you download it.")
    if not submitted:
        return None
    # Sidebar form is kept for desktop, but the same form is also on Home,
    # so mobile users never have to hunt for the sidebar hamburger menu.
    st.session_state["pending_section"] = "Plan"
    st.session_state["theme"] = theme
    time_text = event_time.strftime("%H:%M") if event_time else ""
    st.session_state["event_time"] = time_text
    return EventRequest(event_type, int(guests), float(budget), event_date, city, vibe,
                        tuple(dietary), tuple(access), outdoor, notes,
                        event_name=event_name, currency=currency, event_time=time_text,
                        end_date=end_date)


def render_home(plan: Plan | None) -> None:
    # Professional landing: one clear headline, one clear action, then
    # services as clean cards — the pattern used by professional event
    # planning sites (white space, simple navigation, no clutter).
    st.caption("CELEBRATION & EVENT PLANNER  ·  HACK2SKILL CHALLENGE 5")
    if os.path.exists("assets/hero-banner.webp"):
        st.image("assets/hero-banner.webp", width="stretch",
                 caption="Birthdays, weddings, festivals and more — planned in one place.")
    st.title("Plan a celebration, without the stress.")
    st.write("Birthdays, weddings, festivals and community events — tell us about "
             "your party, and get a complete plan — budget, guests, vendors, food, "
             "music and games — in minutes. No account needed.")
    st.subheader("Step 1 — Create your plan here (no sidebar needed)")
    st.caption("Fill this form and click 'Create my full plan'. Your complete plan — "
               "invitation, budget, checklist, schedule, vendors, food, games and shopping list — "
               "will open on the Plan page right away.")
    with st.form("event_form_main"):
        m_name = st.text_input("Event name", "Ava's 10th Birthday Bash", max_chars=120, key="main_event_name")
        m_type = st.selectbox("Event type", EVENT_TYPES, key="main_event_type")
        m_guests = st.number_input("Number of guests", 1, MAX_GUESTS, 50, step=5, key="main_guests")
        m_budget = st.number_input("Total budget", 1000, MAX_BUDGET, 100000, step=5000, key="main_budget")
        m_currency = st.selectbox("Currency", CURRENCIES, index=0, key="main_currency")
        m_date = st.date_input("Event date", date.today() + timedelta(days=60),
                               min_value=date.today(), key="main_event_date")
        m_time = st.time_input("Event time (optional)", value=None, key="main_event_time")
        m_city = st.text_input("City (optional)", max_chars=MAX_CITY, key="main_city")
        m_theme = st.text_input("Theme (optional)", "Space", key="main_theme")
        m_vibe = st.selectbox("Vibe", VIBES, key="main_vibe")
        m_outdoor = st.checkbox("Outdoor venue", key="main_outdoor")
        m_dietary = st.multiselect("Dietary needs", DIETARY, key="main_dietary")
        m_access = st.multiselect("Accessibility needs", ACCESSIBILITY, key="main_access")
        m_notes = st.text_area("Anything else? (optional)", max_chars=MAX_NOTES, key="main_notes")
        m_submitted = st.form_submit_button("Create my full plan", type="primary")
    if m_submitted:
        try:
            m_req = EventRequest(m_type, int(m_guests), float(m_budget), m_date, m_city, m_vibe,
                                 tuple(m_dietary), tuple(m_access), m_outdoor, m_notes,
                                 event_name=m_name, currency=m_currency,
                                 event_time=m_time.strftime("%H:%M") if m_time else "")
            st.session_state["theme"] = m_theme
            st.session_state["plan"] = cached_plan(m_req.validated(date.today()), date.today())
            st.session_state.pop("ai_text", None)
            st.session_state["pending_section"] = "Plan"
            st.success(f"Done! Your full plan for **{m_name}** is ready — opening it now.")
            st.rerun()
        except ValidationError as exc:
            st.error(f"Please fix: {exc}")
    if plan is not None:
        if st.button("See my full plan →", type="primary", key="see_full_plan"):
            st.session_state["pending_section"] = "Plan"
            st.rerun()
    if st.button("Try a sample birthday plan", type="primary"):
        req = EventRequest("Birthday", 50, 100000.0, date.today() + timedelta(days=60),
                           "Toronto", "Fun & Playful", (), (), False,
                           "Space theme, kids love science",
                           event_name="Ava's 10th Birthday Bash", currency="CAD")
        st.session_state["theme"] = "Space"
        st.session_state["plan"] = cached_plan(req.validated(date.today()), date.today())
        st.session_state.pop("ai_text", None)
        st.session_state["pending_section"] = "Plan"
        st.rerun()
    st.caption("Or create your own plan from the form above — no sidebar needed.")
    st.subheader("Explore everything — tap any card, no searching in the sidebar")
    st.caption("If you have no plan yet, tapping a card opens it with a sample birthday plan, "
               "so you can see every feature at first look. Then create your own plan from the form above.")
    quick = {
        "Plan": "Budget split, checklist, risks, logistics and menu.",
        "Guests & Invites": "Guest list, RSVP, invitations, WhatsApp, email and QR.",
        "Budget & Expenses": "Planned vs actual spending, paid/unpaid, reports.",
        "Food & Cake": "Menu, dietary-safe dishes, cake size, leftover tracker.",
        "Music & Games": "Playlist, song requests, games, quiz, scores, lucky draw.",
        "Kids": "Age-wise activities, themes, goodie bags, safety checklist.",
        "Decor & Design": "Themes, colours, decor planners and shopping list.",
        "Vendors & Shopping": "Sample vendors, your vendors, shopping cart (estimates).",
        "Seating & Floor Plan": "Group-wise seating and a 2D floor-plan schematic.",
        "Live Event Day": "Run sheet, check-in, polls, announcements, incidents.",
        "Post-Event & Memories": "Photos, collage, guestbook, gifts, final report.",
        "AI Assistant": "Ask about your event, get ideas and budget tips.",
        "Profile & Settings": "Your local profile, backup/restore, pricing preview.",
        "Previews (Mock)": "Mock views of login, checkout, booking, 3D plan and admin — preview only, nothing real happens here.",
    }
    cols = st.columns(2)
    for i, (section, desc) in enumerate(quick.items()):
        with cols[i % 2].container(border=True):
            st.write(f"**{section}**")
            st.write(desc)
            if st.button(f"Open {section}", key=f"quick_{section}"):
                if plan is None:
                    req = EventRequest("Birthday", 50, 100000.0, date.today() + timedelta(days=60),
                                       "Toronto", "Fun & Playful", (), (), False,
                                       "Space theme, kids love science",
                                       event_name="Ava's 10th Birthday Bash", currency="CAD")
                    st.session_state["theme"] = "Space"
                    st.session_state["plan"] = cached_plan(req.validated(date.today()), date.today())
                # Do NOT set nav_section here: the top radio with that
                # key is already instantiated by the time Home renders.
                # main() picks pending_section up before creating the radio.
                st.session_state["pending_section"] = section
                st.rerun()
    if plan is not None:
        st.success(f"Current event: **{plan.request.event_name or plan.request.event_type}** — "
                   f"{plan.days_left} days to go. Use the section menu at the top of the page to manage it.")
    with st.container(border=True):
        c1, c2, c3, c4 = st.columns(4)
        c1.metric("Event types", str(len(EVENT_TYPES)))
        c2.metric("Budget categories", str(len(BUDGET_CATEGORIES)))
        c3.metric("Sample vendors", str(len(SAMPLE_VENDORS)))
        c4.metric("Games in library", str(len(GAMES_LIBRARY)))
    st.subheader("How it works")
    a, b, c = st.columns(3)
    with a.container(border=True):
        st.write("**1. Tell us about your event**")
        st.write("Guests, budget, date, vibe, and dietary or accessibility needs.")
    with b.container(border=True):
        st.write("**2. Get your full plan**")
        st.write("Budget, checklist, menu, risks, seating, games and music — instantly.")
    with c.container(border=True):
        st.write("**3. Run it live**")
        st.write("Check guests in, track vendors, share updates, then save memories.")
    st.subheader("What you get")
    d, e, f, g = st.columns(4)
    with d.container(border=True):
        st.write("**Budget, clearly**")
        st.write("A split that always adds up to your total, plus actual spending.")
    with e.container(border=True):
        st.write("**Guests, organised**")
        st.write("RSVP, dietary needs, seating and check-in in one list.")
    with f.container(border=True):
        st.write("**Vendors, compared**")
        st.write("Prices, status and contacts — no spreadsheets needed.")
    with g.container(border=True):
        st.write("**The day itself**")
        st.write("A run sheet, live polls and announcements for event day.")
    st.subheader("Start from a template")
    for t in EVENT_TEMPLATES:
        if st.button(f"Use template: {t['name']}", key=f"tpl_{t['name']}"):
            req = EventRequest(t["event_type"], t["guests"], 100000.0,
                               date.today() + timedelta(days=60), "Toronto", "Fun & Playful",
                               (), (), False, "", event_name=t["name"], currency="CAD")
            st.session_state["theme"] = t["theme"]
            st.session_state["plan"] = cached_plan(req.validated(date.today()), date.today())
            st.rerun()
    st.subheader("Questions, answered")
    with st.expander("Do I need an account to use this?"):
        st.write("No. Everything works in your browser session, with no sign-up.")
    with st.expander("Is my event data private?"):
        st.write("Yes. It stays in this browser session unless you download it. "
                 "No event is published by this app.")
    with st.expander("Do I need an AI key?"):
        st.write("No. Offline ideas work without a key. A Gemini key only adds "
                 "extra creative ideas, and is optional.")
    st.divider()
    st.caption("Built for Hack2Skill Virtual: PromptWars, Challenge 5 · By Bhavana Shah")
    st.subheader("My events (this browser session)")
    if plan is not None and st.button("💾 Save current event"):
        saved = store("saved_events", [])
        r = plan.request
        saved.append({"event_name": r.event_name, "event_type": r.event_type, "guests": r.guests,
                      "budget": r.budget, "event_date": r.event_date.isoformat(), "city": r.city,
                      "vibe": r.vibe, "dietary": list(r.dietary), "accessibility": list(r.accessibility),
                      "outdoor": r.outdoor, "notes": r.notes, "currency": r.currency,
                      "event_time": r.event_time,
                      "end_date": r.end_date.isoformat() if r.end_date else "",
                      "theme": st.session_state.get("theme", "")})
        st.success("Saved in this session. Download it from Post-Event / Export to keep it.")
    for i, saved in enumerate(store("saved_events", [])):
        col1, col2, col3, col4 = st.columns([3, 1, 1, 1])
        _ed = saved.get("end_date") or ""
        col1.write(f"**{saved['event_name'] or saved['event_type']}** — {saved['event_type']}, {saved['event_date']}{(' to ' + _ed) if _ed else ''}{', ' + saved['event_time'] if saved.get('event_time') else ''}, {saved['guests']} guests")
        if col2.button("Load", key=f"load_{i}"):
            req = EventRequest(saved["event_type"], saved["guests"], saved["budget"],
                               date.fromisoformat(saved["event_date"]), saved["city"], saved["vibe"],
                               tuple(saved["dietary"]), tuple(saved["accessibility"]),
                               saved["outdoor"], saved["notes"], event_name=saved["event_name"],
                               currency=saved["currency"], event_time=saved.get("event_time", ""),
                               end_date=date.fromisoformat(saved["end_date"]) if saved.get("end_date") else None)
            st.session_state["theme"] = saved.get("theme", "")
            st.session_state["plan"] = cached_plan(req.validated(date.today()), date.today())
            st.rerun()
        if col3.button("Duplicate", key=f"dup_{i}"):
            copy = dict(saved)
            copy["event_name"] = (saved["event_name"] or saved["event_type"]) + " (Copy)"
            store("saved_events", []).append(copy)
            st.rerun()
        if col4.button("Delete", key=f"del_{i}"):
            store("saved_events", []).pop(i)
            st.rerun()


def render_plan(plan: Plan) -> None:
    r, b = plan.request, plan.budget
    cur = r.currency
    c1, c2, c3, c4 = st.columns(4)
    c1.metric("Days to go", plan.days_left)
    c2.metric("Guests", r.guests)
    c3.metric("Budget per guest", money(b.per_head, cur))
    c4.metric("Budget level", b.tier)
    st.info(b.advice)
    st.subheader("Your next three actions")
    for task in plan.timeline[:3]:
        st.markdown(f"- **{task.title}** ({STATUS_ICON[task.status]}, by {task.due:%d %b %Y})")
    high = [x for x in plan.risks if x.level == "High"]
    if high:
        st.error(f"{len(high)} high-risk item(s) need attention. See Risks in the Plan details below.")
    st.subheader("Budget at a glance")
    df = pd.DataFrame([{"Category": line.category, "Share": f"{line.share:.0%}",
                        "Amount": money(line.amount, cur)} for line in b.lines])
    st.dataframe(df, hide_index=True, use_container_width=True)
    st.subheader("Checklist (tick to track)")
    tdf = pd.DataFrame([{"Done": False, "Due": t.due, "Task": t.title, "Category": t.category,
                         "Status": STATUS_ICON[t.status]} for t in plan.timeline])
    edited = st.data_editor(tdf, hide_index=True, use_container_width=True,
                            disabled=["Due", "Task", "Category", "Status"],
                            column_config={"Due": st.column_config.DateColumn(format="DD MMM YYYY")},
                            key=f"tasks_{hash(plan.request)}")
    done = int(edited["Done"].sum())
    st.progress(done / len(tdf) if len(tdf) else 0.0, text=f"{done} of {len(tdf)} tasks done")
    st.subheader("My tasks — add, tick off, delete")
    st.caption("Your own tasks, in this session, alongside the engine checklist above.")
    tasks = store("custom_tasks", [])
    with st.form("add_task", clear_on_submit=True):
        t1, t2, t3 = st.columns([3, 1, 1])
        t_title = t1.text_input("Task title *", max_chars=120)
        t_due = t2.date_input("Due date (optional)", value=None)
        t_pri = t3.selectbox("Priority", ["High", "Medium", "Low"], index=1)
        if st.form_submit_button("Add task"):
            if t_title.strip():
                tasks.append({"title": t_title.strip(), "due": t_due.isoformat() if t_due else "", "done": False, "priority": t_pri})
                st.success(f"Added: {t_title.strip()}")
    for i, t in enumerate(list(tasks)):
        c1, c2, c3 = st.columns([1, 5, 1])
        if c1.checkbox("", value=t["done"], key=f"task_done_{i}"):
            tasks[i]["done"] = True
        else:
            tasks[i]["done"] = False
        c2.write(f"{t['title']} [{t.get('priority', 'Medium')}]{' — due ' + t['due'] if t.get('due') else ''}")
        if c3.button("Delete", key=f"task_del_{i}"):
            tasks.pop(i)
            st.rerun()
    if tasks:
        st.write(f"{sum(1 for t in tasks if t['done'])} of {len(tasks)} of my tasks done.")
    st.subheader("Risks")
    if not plan.risks:
        st.success("No major risks detected.")
    for risk in plan.risks:
        box = {"High": st.error, "Medium": st.warning, "Info": st.info}[risk.level]
        box(f"**{RISK_LABEL[risk.level]}:** {risk.message}")
    st.subheader("Logistics & menu")
    lg = plan.logistics
    cols = st.columns(5)
    items = [("Venue capacity", lg.venue_capacity), ("Area (sq ft)", lg.venue_area_sqft),
             ("Food portions", lg.food_portions), ("Drinks", lg.drink_units),
             ("Cake servings", lg.cake_servings), ("Chairs", lg.chairs),
             ("Tables of 8", lg.tables), ("Service staff", lg.service_staff),
             ("Restrooms", lg.restrooms), ("Parking spots", lg.parking_spots)]
    for i, (label, value) in enumerate(items):
        cols[i % 5].metric(label, value)
    for course, dishes in plan.menu.items():
        st.markdown(f"**{course}:** " + "; ".join(dishes))
    st.caption("Always confirm allergens with your caterer.")
    st.subheader("Full plan at a glance — invitation, schedule, vendors, shopping, games, music")
    st.caption("Everything from your details, on one page — so you do not have to open every section to see the plan.")
    st.markdown("**Invitation (ready to copy)**")
    st.text_area("Your invitation", invitation_text(plan.request, st.session_state.get("theme", "")), height=150, key="fullplan_invite")
    st.markdown("**Day schedule**")
    for title, detail in day_schedule(plan.request.event_type):
        st.write(f"- **{title}:** {detail}")
    st.markdown("**Vendors to book**")
    for vendor in vendor_checklist(plan.request.event_type):
        st.write(f"- {vendor}")
    st.markdown("**Shopping / item list (scaled by guests)**")
    for item in item_list(plan.request.guests):
        st.write(f"- {item}")
    st.markdown("**Games for this event**")
    for name, duration, detail in games_for(plan.request.event_type):
        st.write(f"- **{name}** ({duration}) — {detail}")
    st.markdown("**Music by moment**")
    for moment, note in music_by_moment():
        st.write(f"- **{moment}:** {note}")
    st.subheader("Notes & reminders")
    st.text_area("Your notes for this event", key="plan_notes", height=120,
                 help="Stored only in this browser session.")
    if st.button("Add a reminder"):
        st.session_state.setdefault("reminders", []).append("Reminder added — check this list before event day.")
    for rem in st.session_state.get("reminders", []):
        st.write(f"- {rem}")


def render_guests(plan: Plan) -> None:
    st.subheader("Guest list — name, email, phone, group, plus-one, dietary, accessibility")
    guests = store("real_guests", [])
    with st.form("add_guest", clear_on_submit=True):
        c1, c2, c3 = st.columns(3)
        name = c1.text_input("Guest name *", max_chars=80)
        email = c2.text_input("Email (optional)", max_chars=120)
        phone = c3.text_input("Phone (optional)", max_chars=30)
        c4, c5, c6 = st.columns(3)
        group = c4.selectbox("Group", ["Family", "Friends", "Kids", "Colleagues", "Community", "Other"])
        category = c5.selectbox("Category", ["Family", "Friends", "Colleagues"])
        rsvp = c6.selectbox("RSVP", RSVP_OPTIONS, index=1)
        c7, c8, c9 = st.columns(3)
        plus_one = c7.number_input("Accompanying guests", 0, 10, 0)
        kids = c8.number_input("Kids attending", 0, 10, 0)
        dietary = c9.text_input("Dietary / accessibility note", max_chars=120)
        if st.form_submit_button("Add guest"):
            if name.strip() and any(g.get("Name", "").lower() == name.strip().lower() and g.get("Email", "").lower() == email.strip().lower() for g in guests):
                st.warning("This guest (same name and email) is already in the list — not added again.")
            elif name.strip():
                guests.append({"Name": name.strip(), "Email": email.strip(), "Phone": phone.strip(),
                               "Group": group, "Category": category, "RSVP": rsvp,
                               "PlusOne": int(plus_one), "Kids": int(kids), "Dietary": dietary.strip(),
                               "CheckedIn": False, "Table": 0})
                st.success(f"Added {name.strip()}.")
            else:
                st.warning("Enter a guest name first.")
    st.subheader("Import guests from CSV")
    st.caption("CSV with a Name column (Email, Phone, Group, RSVP optional). Duplicates by name + email are skipped.")
    csv_file = st.file_uploader("Upload guest CSV", type=["csv"], key="guest_csv")
    if csv_file is not None and st.button("Import guests"):
        try:
            import_df = pd.read_csv(csv_file)
            if "Name" not in import_df.columns:
                st.error("CSV needs a Name column.")
            else:
                added, skipped = 0, 0
                for _, row in import_df.iterrows():
                    nm = str(row.get("Name", "")).strip()
                    em = str(row.get("Email", "")).strip() if pd.notna(row.get("Email")) else ""
                    if not nm:
                        continue
                    if any(g.get("Name", "").lower() == nm.lower() and g.get("Email", "").lower() == em.lower() for g in guests):
                        skipped += 1
                        continue
                    guests.append({"Name": nm, "Email": em, "Phone": str(row.get("Phone", "")).strip() if pd.notna(row.get("Phone")) else "",
                                   "Group": str(row.get("Group", "Other")).strip() or "Other", "Category": "Friends", "RSVP": str(row.get("RSVP", "Pending")).strip() or "Pending",
                                   "PlusOne": 0, "Kids": 0, "Dietary": "", "CheckedIn": False, "Table": 0})
                    added += 1
                st.success(f"Imported {added} guest(s), skipped {skipped} duplicate(s).")
        except Exception as exc:
            st.error(f"Could not import CSV: {exc}")
    if guests:
        df = pd.DataFrame(guests)
        edited = st.data_editor(df, hide_index=True, use_container_width=True, key="guest_editor",
                                column_config={"RSVP": st.column_config.SelectboxColumn(options=list(RSVP_OPTIONS))})
        st.session_state["real_guests"] = edited.to_dict("records")
        counts = edited["RSVP"].value_counts().to_dict() if "RSVP" in edited else {}
        c1, c2, c3, c4 = st.columns(4)
        c1.metric("Listed guests", len(edited))
        c2.metric("Attending", counts.get("Attending", 0))
        c3.metric("Pending / Maybe", counts.get("Pending", 0) + counts.get("Maybe", 0))
        c4.metric("Checked in", int(edited["CheckedIn"].sum()) if "CheckedIn" in edited else 0)
        buf = io.StringIO()
        edited.to_csv(buf, index=False)
        st.download_button("⬇️ Download guest list (CSV)", buf.getvalue(), "guest-list.csv", "text/csv")
        st.divider()
        st.subheader("Invitations — templates, WhatsApp, email, QR")
        template = st.selectbox("Invitation template", INVITATION_TEMPLATES)
        theme = st.session_state.get("theme", "")
        invite = invitation_text(plan.request, theme) + f"\n\nStyle: {template}"
        st.text_area("Invitation text (edit and copy)", invite, height=180, key="invite_text")
        st.download_button("⬇️ Download invitation", invite, "invitation.txt", "text/plain")
        st.markdown(f"[Share on WhatsApp]({whatsapp_link('', invite)})  •  "
                    f"[Share by email]({mailto_link('', 'You are invited!', invite)})")
        st.caption("WhatsApp / email links open your own app — no message is sent by this website.")
        try:
            qr = make_qr_png(f"{plan.request.event_name or plan.request.event_type} — {plan.request.event_date.isoformat()}")
            st.image(qr, width=200, caption="QR code for this event (scan to see the event name and date)")
            st.download_button("⬇️ Download QR code", qr, "event-qr.png", "image/png")
        except Exception as exc:  # qrcode is optional at runtime
            st.caption(f"QR code unavailable: {exc}")
        st.subheader("RSVP follow-up & thank-you messages")
        pending = [g["Name"] for g in guests if g.get("RSVP") in ("Pending", "Maybe")]
        st.write("Pending / Maybe guests to follow up: " + (", ".join(pending) if pending else "None — all confirmed or declined."))
        st.text_area("Thank-you message template",
                     "Thank you so much for celebrating with us! It meant a lot to have you there. 💛",
                     key="thanks_template")
    else:
        st.info("No guests added yet. Add your first guest above.")


def render_budget(plan: Plan) -> None:
    cur = plan.request.currency
    st.subheader("Budget by category — planned")
    planned = {}
    for cat in BUDGET_CATEGORIES:
        # Start from the engine split for the closest categories, otherwise 0.
        planned[cat] = 0.0
    engine_map = {"Venue": "Venue", "Catering": "Catering", "Decor": "Decor",
                  "Entertainment": "Music & Entertainment"}
    for line in plan.budget.lines:
        if line.category in planned:
            planned[line.category] = line.amount
    # Distribute any unmapped engine amount to Emergency Fund so the total still matches.
    mapped_total = sum(planned.values())
    if plan.request.budget > mapped_total:
        planned["Emergency Fund"] += round(plan.request.budget - mapped_total, 2)
    df = pd.DataFrame([{"Category": k, "Planned": v} for k, v in planned.items()])
    st.dataframe(df, hide_index=True, use_container_width=True)
    st.bar_chart(df.set_index("Category")["Planned"], y_label=f"Amount ({cur})")
    st.metric("Total planned", money(sum(planned.values()), cur))
    st.metric("Per-guest cost", money(plan.request.budget / max(plan.request.guests, 1), cur))
    st.divider()
    st.subheader("Expenses — estimated vs actual, paid / unpaid, advances")
    expenses = store("expenses", [])
    with st.form("add_expense", clear_on_submit=True):
        c1, c2, c3 = st.columns(3)
        desc = c1.text_input("Expense description *", max_chars=120)
        cat = c2.selectbox("Category", BUDGET_CATEGORIES)
        amount = c3.number_input("Amount", min_value=0.0, value=0.0, step=10.0)
        c4, c5, c6 = st.columns(3)
        status = c4.selectbox("Status", ["Paid", "Unpaid", "Advance paid"])
        vendor = c5.text_input("Vendor (optional)", max_chars=80)
        due = c6.date_input("Due date (optional)", value=None)
        if st.form_submit_button("Add expense"):
            if desc.strip():
                expenses.append({"Description": desc.strip(), "Category": cat, "Amount": float(amount),
                                 "Status": status, "Vendor": vendor.strip(),
                                 "Due": due.isoformat() if due else ""})
            else:
                st.warning("Enter a description first.")
    if expenses:
        edf = pd.DataFrame(expenses)
        st.data_editor(edf, hide_index=True, use_container_width=True, key="expense_editor")
        total_actual = sum(float(x.get("Amount", 0) or 0) for x in expenses)
        paid = sum(float(x.get("Amount", 0) or 0) for x in expenses if x.get("Status") == "Paid")
        st.metric("Total actual / committed", money(total_actual, cur))
        st.metric("Paid so far", money(paid, cur))
        st.metric("Remaining vs total budget", money(plan.request.budget - total_actual, cur))
        if total_actual > plan.request.budget:
            st.error("⚠️ Over budget overall. See optimisation tips below.")
        actual_by_cat = {}
        for x in expenses:
            actual_by_cat[x["Category"]] = actual_by_cat.get(x["Category"], 0.0) + float(x["Amount"] or 0)
        for tip in budget_optimisation(planned, actual_by_cat):
            st.write(f"- {tip}")
        buf = io.StringIO()
        edf.to_csv(buf, index=False)
        st.download_button("⬇️ Download expense report (CSV)", buf.getvalue(), "expense-report.csv", "text/csv")
        try:
            pdf = make_plan_pdf(f"Expense Report — {plan.request.event_name or plan.request.event_type}",
                                [f"{x['Description']} — {x['Category']} — {x['Amount']} — {x['Status']}" for x in expenses])
            st.download_button("⬇️ Download expense report (PDF)", pdf, "expense-report.pdf", "application/pdf")
        except Exception as exc:
            st.caption(f"PDF export unavailable: {exc}")
    else:
        st.info("No expenses added yet.")
    st.subheader("Receipts")
    uploaded = st.file_uploader("Upload a receipt (recorded by name only, not stored on a server)",
                                type=["png", "jpg", "jpeg", "pdf"], key="receipt_upload")
    if uploaded is not None:
        receipts = store("receipts", [])
        receipts.append({"File": uploaded.name, "Size bytes": uploaded.size})
        st.success(f"Recorded receipt: {uploaded.name}. Keep the original file — this demo does not store uploads on a server.")
    if store("receipts", []):
        st.table(store("receipts", []))
    st.subheader("Shared budget")
    st.write("Add family members who share the budget (names only, in this session).")
    with st.form("add_collaborator_budget", clear_on_submit=True):
        name = st.text_input("Family member name", max_chars=80)
        role = st.selectbox("Role", ["Host", "Co-host", "Family member", "Helper"])
        if st.form_submit_button("Add collaborator"):
            if name.strip():
                store("collaborators", []).append({"Name": name.strip(), "Role": role})
    if store("collaborators", []):
        st.table(store("collaborators", []))


def render_food(plan: Plan) -> None:
    st.subheader("Menu planner")
    for course in ["Breakfast", "Lunch", "Dinner", "Snacks", "Main course", "Desserts", "Beverages"]:
        dishes = st.text_input(f"{course} (comma separated)", key=f"menu_{course}",
                               placeholder="e.g. Dal, Rice, Salad" if course == "Main course" else "")
        if dishes.strip():
            st.write(f"✓ {course}: {dishes.strip()}")
    st.subheader("Dietary-safe menu (from the engine)")
    if plan.request.dietary:
        st.caption("Filtered to satisfy: " + ", ".join(plan.request.dietary))
    for course, dishes in plan.menu.items():
        st.markdown(f"**{course}:** " + "; ".join(dishes))
    st.caption("Always confirm allergens with your caterer.")
    st.subheader("Cake planner")
    flavour = st.selectbox("Cake flavour", CAKE_FLAVOURS)
    servings = st.number_input("Cake servings needed", 1, 1000, int(plan.request.guests), step=10)
    kg = max(1, round(servings / 10))
    st.metric("Suggested cake size", f"{kg} kg (about 10 servings per kg)")
    st.write(f"Flavour: **{flavour}** • Design ideas: themed topper, photo print, floral, or minimalist.")
    st.subheader("Food quantity & serving schedule")
    lg = plan.logistics
    st.write(f"Food portions: **{lg.food_portions}** (guests + 10% buffer) • Drinks: **{lg.drink_units}** (about 4 per guest)")
    st.write("Serving schedule: welcome drinks on arrival, main course at the main meal time, "
             "dessert / cake at the main moment, and a late snack if the event runs long.")
    st.write("Leftover plan: pack leftovers in labelled boxes, donate unopened food where local rules allow, "
             "and note actual consumption for next time in Post-Event.")
    st.subheader("Leftover tracker (numbers, not just a plan)")
    leftovers = store("leftovers", [])
    with st.form("add_leftover", clear_on_submit=True):
        l1, l2, l3, l4 = st.columns(4)
        l_item = l1.text_input("Item *", max_chars=80)
        l_planned = l2.number_input("Planned portions", 0, 10000, 0)
        l_used = l3.number_input("Actually used", 0, 10000, 0)
        l_action = l4.selectbox("Action", ["Packed", "Donated", "Discarded"])
        if st.form_submit_button("Add leftover record"):
            if l_item.strip():
                leftovers.append({"Item": l_item.strip(), "Planned": int(l_planned), "Used": int(l_used),
                                  "Leftover": int(l_planned) - int(l_used), "Action": l_action})
    if leftovers:
        st.table(leftovers)
    st.subheader("Caterer comparison")
    caterers = [v for v in SAMPLE_VENDORS if v["category"] == "Caterer"]
    if caterers:
        st.table(caterers)
    st.caption("Sample caterers only — add your real caterer in Vendors & Shopping.")


def render_music_games(plan: Plan) -> None:
    st.subheader("Playlist creator")
    playlist = store("playlist", [])
    with st.form("add_song", clear_on_submit=True):
        c1, c2 = st.columns(2)
        song = c1.text_input("Song / track *", max_chars=120)
        moment = c2.selectbox("Moment", [m for m, _ in MUSIC_LIBRARY])
        if st.form_submit_button("Add to playlist"):
            if song.strip():
                playlist.append({"Song": song.strip(), "Moment": moment})
    if playlist:
        st.table(playlist)
    st.subheader("Music library by moment")
    for moment, note in music_by_moment():
        st.write(f"**{moment}:** {note}")
    st.subheader("Song requests from guests")
    req_song = st.text_input("Guest song request", max_chars=120, key="song_request")
    if st.button("Add song request") and req_song.strip():
        store("song_requests", []).append(req_song.strip())
        st.success("Song request added.")
    for s in store("song_requests", []):
        st.write(f"- {s}")
    st.divider()
    st.subheader("Games library — filter by age and place")
    age_f = st.selectbox("Age group", ["All", "Kids", "Teens", "Adults", "Family"])
    place_f = st.selectbox("Place", ["All", "Indoor", "Outdoor"])
    filtered = [g for g in GAMES_LIBRARY if (age_f == "All" or g["age"] == age_f) and (place_f == "All" or g["place"] == place_f)]
    if filtered:
        st.table(filtered)
    else:
        st.info("No games match those filters — try All / All.")
    st.subheader("Games for this event type")
    for name, duration, detail in games_for(plan.request.event_type):
        st.write(f"**{name}** ({duration}) — {detail}")
    st.subheader("Quiz / trivia creator")
    with st.form("add_quiz", clear_on_submit=True):
        q = st.text_input("Question *", max_chars=200)
        a = st.text_input("Answer", max_chars=200)
        if st.form_submit_button("Add question"):
            if q.strip():
                store("quiz", []).append({"Question": q.strip(), "Answer": a.strip()})
    if store("quiz", []):
        st.table(store("quiz", []))
    st.subheader("Scavenger hunt creator")
    with st.form("add_clue", clear_on_submit=True):
        clue = st.text_input("Clue *", max_chars=200)
        if st.form_submit_button("Add clue"):
            if clue.strip():
                store("clues", []).append(clue.strip())
    for clue in store("clues", []):
        st.write(f"- {clue}")
    st.subheader("Lucky draw")
    attending = [g["Name"] for g in store("real_guests", []) if g.get("RSVP") == "Attending"]
    if st.button("🎲 Pick a lucky-draw winner"):
        winner = lucky_draw_winner(attending)
        st.success(f"Winner: **{winner}**" if winner else "Add attending guests first (Guests & Invites tab).")
    st.caption("Lucky draw is random in this session — use it for fun, not for a paid lottery.")
    st.subheader("Score tracker & leaderboard")
    scores = store("game_scores", [])
    with st.form("add_score", clear_on_submit=True):
        s1, s2, s3 = st.columns(3)
        s_team = s1.text_input("Team / player *", max_chars=80)
        s_game = s2.text_input("Game", max_chars=80)
        s_pts = s3.number_input("Points", 0, 10000, 0)
        if st.form_submit_button("Add score"):
            if s_team.strip():
                scores.append({"Team / player": s_team.strip(), "Game": s_game.strip(), "Points": int(s_pts)})
    if scores:
        board = sorted(scores, key=lambda x: x["Points"], reverse=True)
        st.table(board)
        st.success(f"Leader: **{board[0]['Team / player']}** with {board[0]['Points']} points.")


def render_kids(plan: Plan) -> None:
    st.subheader("Kids' activities by age")
    age = st.selectbox("Age group", list(KIDS_ACTIVITIES.keys()))
    for act in KIDS_ACTIVITIES[age]:
        st.write(f"- {act}")
    st.subheader("Kids' themes")
    for theme in ["Space", "Superhero", "Princess / Fairy", "Animal", "Dinosaur", "Sports", "Science", "Art & Craft"]:
        st.write(f"- {theme}")
    st.subheader("Return gift / goodie bag planner")
    st.write(f"Goodie bags needed: **{plan.request.guests}** (one per guest, or one per child — adjust below).")
    gift_items = st.text_area("Goodie bag items (one per line)", "Sticker sheet\nSmall toy\nChocolate\nColouring book", key="goodie_items")
    st.write("Goodie bag checklist:")
    for item in gift_items.splitlines():
        if item.strip():
            st.checkbox(item.strip(), key=f"goodie_{item.strip()}")
    st.subheader("Child safety checklist")
    for item in ["Parent contact and authorised pickup recorded for each child",
                 "Allergy information collected and shared with caterer",
                 "First-aid kit on site", "Safe play area, no sharp / small hazards for toddlers",
                 "Quiet / nap area available", "Emergency contacts displayed"]:
        st.checkbox(item, key=f"safety_{item}")
    st.subheader("Kids' entertainer booking")
    entertainers = [v for v in SAMPLE_VENDORS if v["category"] == "Kids' Entertainer"]
    if entertainers:
        st.table(entertainers)
    st.caption("Sample only — add your real entertainer in Vendors & Shopping.")


def render_decor(plan: Plan) -> None:
    st.subheader("Theme & colour palette")
    theme = st.selectbox("Theme", list(THEMES.keys()), index=list(THEMES.keys()).index(st.session_state.get("theme", "Space")) if st.session_state.get("theme", "Space") in THEMES else 0)
    st.session_state["theme"] = theme
    palette = THEMES[theme]
    st.write("Colours: " + ", ".join(palette["colors"]))
    for colour in palette["colors"]:
        st.color_picker(colour, colour, key=f"colour_{colour}")
    st.write("Theme ideas:")
    for idea in palette["ideas"]:
        st.write(f"- {idea}")
    st.subheader("Mood board")
    st.write("Save inspiration notes for this theme (text mood board in v3 — photo mood boards are in Post-Event gallery).")
    mood = st.text_area("Mood board notes", key="mood_notes", height=120,
                        placeholder="e.g. Gold + white, fairy lights, flower arch, photo corner")
    if mood.strip():
        st.success("Mood board note saved in this session.")
    st.subheader("Decoration planners")
    for section, items in DECOR_SECTIONS.items():
        with st.expander(section):
            for item in items:
                st.checkbox(item, key=f"decor_{section}_{item}")
    st.subheader("Decoration shopping list & budget")
    decor_items = store("decor_shopping", [])
    with st.form("add_decor_item", clear_on_submit=True):
        c1, c2 = st.columns(2)
        item = c1.text_input("Decoration item *", max_chars=80)
        price = c2.number_input("Estimated price", min_value=0.0, value=0.0, step=10.0)
        if st.form_submit_button("Add to decoration list"):
            if item.strip():
                decor_items.append({"Item": item.strip(), "Price": float(price)})
    if decor_items:
        st.table(decor_items)
        st.metric("Decoration list total", money(sum(float(x["Price"]) for x in decor_items), plan.request.currency))
    st.write("Indoor / outdoor: " + ("Outdoor — see weather backup in Plan / Risks." if plan.request.outdoor else "Indoor."))
    st.caption("3D / AR decoration preview is NOT in v3 — the 2D floor plan is in Seating & Floor Plan, and 3D/AR is a premium next phase.")


def render_vendors_shopping(plan: Plan) -> None:
    st.subheader("Venue comparison — sample venues, side by side")
    st.caption("Sample venues only, with capacity and starting price, so you can compare before you contact a real venue. Real venue booking is not done by this app.")
    venues = [v for v in SAMPLE_VENDORS if v["category"] == "Venue"]
    if venues:
        st.table([{k: v.get(k, "") for k in ("name", "city", "capacity", "indoor", "rating", "price_from", "available")} for v in venues])
        st.write(f"For {plan.request.guests} guests, venues above with capacity under your guest count will feel tight — check capacity before shortlisting.")
    st.subheader("Vendor directory — search, filter, compare")
    cat_f = st.selectbox("Vendor category", ["All"] + sorted({v["category"] for v in SAMPLE_VENDORS}))
    city_f = st.text_input("City filter (optional)", placeholder="e.g. Toronto")
    vendors = [v for v in SAMPLE_VENDORS if (cat_f == "All" or v["category"] == cat_f)
               and (not city_f.strip() or city_f.strip().lower() in v["city"].lower())]
    if vendors:
        st.table(vendors)
    else:
        st.info("No sample vendors match. Add your own below.")
    st.subheader("My vendors — booking, reviews, milestones")
    my_vendors = store("custom_vendors", [])
    with st.form("add_vendor2", clear_on_submit=True):
        c1, c2, c3 = st.columns(3)
        name = c1.text_input("Vendor / service *", max_chars=80)
        price = c2.number_input("Quoted price", min_value=0.0, value=0.0, step=10.0)
        status = c3.selectbox("Status", ["To book", "Booked", "Paid", "Cancelled"])
        contact = st.text_input("Contact (optional)", max_chars=120)
        review = st.text_input("Your review / rating note (optional)", max_chars=200)
        if st.form_submit_button("Add vendor"):
            if name.strip():
                my_vendors.append({"Vendor": name.strip(), "Price": float(price), "Status": status,
                                   "Contact": contact.strip(), "Review": review.strip()})
    if my_vendors:
        st.table(my_vendors)
        st.metric("Total quoted vendor spend", money(sum(float(x["Price"]) for x in my_vendors), plan.request.currency))
        st.write("Payment milestones: record deposit / milestone / balance in the expense tracker (Budget & Expenses) "
                 "with the vendor name, so paid vs unpaid stays in one place.")
    st.subheader("Standard vendor checklist")
    for vendor in vendor_checklist(plan.request.event_type):
        st.checkbox(vendor, key=f"vendor_{vendor}")
    st.divider()
    st.subheader("Shopping catalogue & cart (planning estimates — NOT a real checkout)")
    cart = store("cart", [])
    for product in PRODUCTS:
        c1, c2 = st.columns([4, 1])
        c1.write(f"**{product['name']}** — {product['category']} — {money(product['price'], plan.request.currency)}")
        if c2.button("Add to cart", key=f"cart_{product['name']}"):
            cart.append(product)
            st.rerun()
    if cart:
        st.table(cart)
        st.metric("Cart total (estimate)", money(sum(float(p["price"]) for p in cart), plan.request.currency))
        st.caption("No payment is taken here. For a real launch, checkout needs a payment provider, shipping and returns — see README.")
        if st.button("Clear cart"):
            st.session_state["cart"] = []
            st.rerun()
    st.subheader("Event-day contact sheet")
    contacts = [{"Role": "Host", "Name": plan.request.event_name or "Host", "Note": "Owns the timeline"}]
    for v in my_vendors:
        contacts.append({"Role": "Vendor", "Name": v["Vendor"], "Note": v.get("Contact", "")})
    st.table(contacts)
    buf = io.StringIO()
    pd.DataFrame(contacts).to_csv(buf, index=False)
    st.download_button("⬇️ Download contact sheet (CSV)", buf.getvalue(), "contact-sheet.csv", "text/csv")


def render_seating(plan: Plan) -> None:
    st.subheader("Seating assignment — auto-assign by group")
    guests = store("real_guests", [])
    seats = st.number_input("Seats per table", 2, 20, 8)
    if st.button("Auto-assign tables"):
        tables = seating_assign(guests, int(seats))
        st.session_state["seating"] = tables
        st.success(f"Assigned {len(guests)} guests to {len(tables)} tables.")
    seating = st.session_state.get("seating", {})
    if seating:
        for table_no, names in seating.items():
            st.write(f"**Table {table_no}:** " + ", ".join(names))
        # Manual table override in the guest editor (Guests tab, Table column).
        st.caption("To move a guest, change their Table number in Guests & Invites, then re-assign here if needed.")
    else:
        st.info("Add guests first (Guests & Invites), then auto-assign tables here.")
    st.subheader("2D floor-plan schematic (not 3D/AR)")
    st.write("Tables are shown as a grid below. This is a planning schematic — drag-and-drop 3D floor planning is a premium next phase.")
    n_tables = len(seating) if seating else 6
    cols = st.columns(3)
    for i in range(n_tables):
        with cols[i % 3]:
            names = seating.get(i + 1, []) if seating else []
            st.markdown(f"**Table {i + 1}**\n\n" + ("<br>".join(names) if names else "—"))
    st.subheader("Parking & transport")
    lg = plan.logistics
    st.write(f"Parking spots (about 1 per 3 guests): **{lg.parking_spots}**")
    st.write("Transport plan: note shuttle / carpool / taxi instructions in your invitation and contact sheet.")
    st.write("Weather contingency: " + ("Outdoor — book a tent or indoor backup (see Risks)." if plan.request.outdoor else "Indoor — no weather backup needed, but keep a backup vendor list."))


def render_live(plan: Plan) -> None:
    st.subheader("Live event day dashboard")
    st.write("Use this on event day: run sheet, check-ins, vendor status, announcements and polls.")
    st.subheader("Minute-by-minute run sheet")
    for title, detail in day_schedule(plan.request.event_type):
        st.write(f"**{title}:** {detail}")
    guests = store("real_guests", [])
    if guests:
        checked = sum(1 for g in guests if g.get("CheckedIn"))
        st.metric("Checked in", f"{checked} / {len(guests)}")
        st.progress(checked / len(guests) if guests else 0.0)
    else:
        st.info("Add guests and tick CheckedIn in Guests & Invites to see live attendance here.")
    st.subheader("Vendor status (live)")
    for v in store("custom_vendors", []):
        st.write(f"- **{v['Vendor']}**: {v['Status']}")
    if not store("custom_vendors", []):
        st.info("No custom vendors added yet.")
    st.subheader("Live announcements")
    ann = st.text_input("Announcement", max_chars=200, key="live_ann")
    if st.button("Post announcement") and ann.strip():
        store("announcements", []).append(ann.strip())
    for a in store("announcements", []):
        st.success(a)
    st.subheader("Live poll")
    with st.form("create_poll", clear_on_submit=True):
        q = st.text_input("Poll question *", max_chars=200)
        if st.form_submit_button("Create poll"):
            if q.strip():
                store("poll", {"question": q.strip(), "votes": {"👍 Yes": 0, "👎 No": 0, "🤷 Maybe": 0}})
    poll = st.session_state.get("poll")
    if poll:
        st.write(f"**{poll['question']}**")
        for option in poll["votes"]:
            if st.button(f"Vote: {option}", key=f"vote_{option}"):
                poll["votes"][option] += 1
                st.rerun()
        st.bar_chart(poll["votes"])
    st.subheader("Emergency & incident log")
    st.write("Emergency contacts: keep the host, venue manager and first-aid contact on the contact sheet. "
             "Log any incident below in this session.")
    incident = st.text_input("Incident / issue log", max_chars=200, key="incident")
    if st.button("Log incident") and incident.strip():
        store("incidents", []).append(incident.strip())
    for inc in store("incidents", []):
        st.write(f"- {inc}")


def render_post_event(plan: Plan) -> None:
    st.subheader("Photo gallery & collage")
    uploaded = st.file_uploader("Upload event photos (shown only in this session)",
                                type=["png", "jpg", "jpeg"], accept_multiple_files=True, key="photo_upload")
    photos = store("photos", [])
    if uploaded:
        for f in uploaded:
            data = f.read()
            if data not in photos:
                photos.append(data)
    if photos:
        cols = st.columns(3)
        for i, data in enumerate(photos):
            with cols[i % 3]:
                st.image(data, width=200)
        if st.button("Make a photo collage"):
            try:
                collage = make_collage_png(photos)
                st.image(collage, caption="Photo collage")
                st.download_button("⬇️ Download collage", collage, "collage.png", "image/png")
            except Exception as exc:
                st.caption(f"Collage unavailable: {exc}")
    else:
        st.info("No photos uploaded yet.")
    st.subheader("Guestbook & wishes")
    with st.form("guestbook", clear_on_submit=True):
        author = st.text_input("Your name", max_chars=80)
        wish = st.text_area("Your wish / message", max_chars=500)
        if st.form_submit_button("Add to guestbook"):
            if author.strip() and wish.strip():
                store("guestbook", []).append({"From": author.strip(), "Message": wish.strip()})
    for entry in store("guestbook", []):
        st.write(f"**{entry['From']}**: {entry['Message']}")
    st.subheader("Gift registry & received tracker")
    gifts = store("gifts", [])
    with st.form("add_gift", clear_on_submit=True):
        c1, c2, c3 = st.columns(3)
        gift = c1.text_input("Gift / item *", max_chars=120)
        reserved = c2.selectbox("Status", ["Wishlist", "Reserved", "Received"])
        giver = c3.text_input("From (optional)", max_chars=80)
        if st.form_submit_button("Add gift"):
            if gift.strip():
                gifts.append({"Gift": gift.strip(), "Status": reserved, "From": giver.strip()})
    if gifts:
        st.table(gifts)
    st.subheader("Final expense report & vendor reviews")
    expenses = store("expenses", [])
    if expenses:
        total = sum(float(x.get("Amount", 0) or 0) for x in expenses)
        st.metric("Final total spent (from Budget tracker)", money(total, plan.request.currency))
        st.metric("Budget", money(plan.request.budget, plan.request.currency))
        st.metric("Remaining", money(plan.request.budget - total, plan.request.currency))
    else:
        st.info("Add expenses in Budget & Expenses to see the final report here.")
    for v in store("custom_vendors", []):
        st.write(f"**{v['Vendor']}** — Status: {v['Status']} — Review: {v.get('Review', 'No review yet')}")
    st.subheader("What worked / what didn't, and reusable template")
    st.text_area("What worked", key="worked_notes", height=100)
    st.text_area("What didn't work / to improve next time", key="didnt_notes", height=100)
    if st.button("Save this event as a template"):
        templates = store("my_templates", [])
        templates.append({"name": plan.request.event_name or plan.request.event_type,
                          "event_type": plan.request.event_type, "guests": plan.request.guests,
                          "theme": st.session_state.get("theme", "")})
        st.success("Template saved in this session.")
    for t in store("my_templates", []):
        st.write(f"- Template: **{t['name']}** ({t['event_type']}, {t['guests']} guests)")
    st.divider()
    st.subheader("Export everything")
    st.download_button("Download plan (Markdown)", to_markdown(plan), "event-plan.md", "text/markdown")
    st.download_button("Download reminders (.ics)", to_ics(plan), "event-plan.ics", "text/calendar")
    try:
        pdf = make_plan_pdf(f"Event Plan — {plan.request.event_name or plan.request.event_type}",
                            [f"{t.title} — due {t.due.isoformat()}" for t in plan.timeline])
        st.download_button("⬇️ Download plan (PDF)", pdf, "event-plan.pdf", "application/pdf")
    except Exception as exc:
        st.caption(f"PDF export unavailable: {exc}")
    html = make_event_website_html(plan.request.event_name or plan.request.event_type,
                                   plan.request.event_type, plan.request.event_date.isoformat(),
                                   plan.request.city, day_schedule(plan.request.event_type))
    st.download_button("⬇️ Download event website (HTML)", html, "event-website.html", "text/html")
    st.caption("Host that HTML file on any static host for a custom event page. A hosted custom URL is not created by this app.")


def render_ai(plan: Plan) -> None:
    st.subheader("AI Assistant — ask about your event")
    st.write("Rule-based assistant in v3: it answers budget, rain, vendor, games, food and seating "
             "questions with checklists. For creative ideas, use Gemini below (optional, capped).")
    q = st.text_input("Ask a question", placeholder="e.g. What if it rains? How do I save budget?",
                      key="ai_question")
    if st.button("Ask AI Assistant") and q.strip():
        answer = ai_assistant_reply(q, plan.request.event_type, plan.request.guests, plan.request.budget)
        st.session_state["ai_answer"] = answer
    if st.session_state.get("ai_answer"):
        st.info(st.session_state["ai_answer"])
    st.subheader("AI-generated plan from a prompt")
    prompt = st.text_area("Describe your event in one paragraph",
                          "A birthday party for 50 guests, $800 budget, space theme",
                          key="ai_prompt")
    if st.button("Generate ideas from this prompt"):
        st.write(ai_assistant_reply(prompt, plan.request.event_type, plan.request.guests, plan.request.budget))
    st.subheader("Quick ideas (works offline)")
    for idea in local_ideas(plan.request):
        st.markdown(f"- {idea}")
    st.subheader("AI-powered ideas (Gemini)")
    key = get_api_key()
    used = st.session_state.get("ai_calls", 0)
    if not key:
        st.caption("Add GEMINI_API_KEY in Streamlit secrets to enable Gemini ideas. Offline ideas above still apply.")
        return
    if used >= MAX_AI_CALLS_PER_SESSION:
        st.caption("AI idea limit reached for this session.")
        return
    if st.button("Generate AI ideas"):
        st.session_state["ai_calls"] = used + 1
        with st.spinner("Thinking up ideas..."):
            try:
                st.session_state["ai_text"] = generate_ideas(plan, key)
            except AIUnavailableError:
                st.session_state["ai_text"] = None
                st.warning("The AI service is temporarily unavailable. The offline ideas above still apply.")
    if st.session_state.get("ai_text"):
        st.markdown(st.session_state["ai_text"])
    st.subheader("AI budget optimisation")
    planned = {line.category: line.amount for line in plan.budget.lines}
    actual = {}
    for x in store("expenses", []):
        actual[x["Category"]] = actual.get(x["Category"], 0.0) + float(x["Amount"] or 0)
    for tip in budget_optimisation(planned, actual):
        st.write(f"- {tip}")


def render_profile(plan: Plan | None) -> None:
    st.subheader("Profile (local, v3)")
    st.write("v3 profiles are local to this browser session. Real accounts with OAuth, "
             "email verification and two-factor authentication need a backend — see README.")
    profile = store("profile", {"name": "Bhavana Shah", "email": "sbhavana1997@gmail.com", "city": "Toronto"})
    profile["name"] = st.text_input("Name", profile["name"])
    profile["email"] = st.text_input("Email", profile["email"])
    profile["city"] = st.text_input("City", profile["city"])
    profile["language"] = st.selectbox("Language (UI labels in v3 are English; this is a preference for future i18n)",
                                       ["English", "Hindi (Roman)", "Other"])
    profile["theme_mode"] = st.selectbox("Light / dark mode preference", ["Light", "Dark", "System"])
    st.caption("Light / dark mode in Streamlit Cloud is set by the viewer's own Streamlit theme setting — this preference is recorded for a future custom theme.")
    st.subheader("Privacy & data")
    st.write("- Event is private by default in this session (no public link is created by the app).")
    st.write("- Download your data from Post-Event / Export before closing the tab, or it is lost.")
    if st.button("🗑️ Delete all my session data", type="secondary"):
        for key in list(st.session_state.keys()):
            del st.session_state[key]
        st.rerun()
    st.subheader("Session backup & restore (file you keep)")
    st.caption("No server backup exists in v3 — download this JSON file to keep your session, and upload it back to restore it.")
    backup = {k: v for k, v in st.session_state.items() if k in ("saved_events", "real_guests", "custom_vendors", "expenses", "playlist", "custom_tasks", "leftovers", "game_scores")}
    st.download_button("⬇️ Download session backup (JSON)", json.dumps(backup, default=str, indent=2), "event-planner-backup.json", "application/json")
    up = st.file_uploader("Restore session backup (JSON)", type=["json"], key="backup_json")
    if up is not None and st.button("Restore backup"):
        try:
            data = json.load(up)
            for k, v in data.items():
                if k in ("saved_events", "real_guests", "custom_vendors", "expenses", "playlist", "custom_tasks", "leftovers", "game_scores"):
                    st.session_state[k] = v
            st.success("Backup restored in this session.")
        except Exception as exc:
            st.error(f"Could not restore backup: {exc}")
    st.subheader("Pricing (preview — no payment taken here)")
    st.table([{"Plan": "Free", "Price": "₹0 / $0", "Includes": "Full planner, guests, budget, exports"},
              {"Plan": "Premium", "Price": "Coming soon", "Includes": "Templates marketplace, advanced analytics, priority support"},
              {"Plan": "Pro / Business", "Price": "Coming soon", "Includes": "Vendor dashboard, team workspace, custom event websites"}])
    st.caption("Pricing is a preview page only. Payment gateway integration is a next phase and is NOT active in v3.")
    if plan is not None:
        st.subheader("Admin view (your own data only, v3)")
        st.write(f"Saved events: {len(store('saved_events', []))} • Guests: {len(store('real_guests', []))} • "
                 f"Vendors: {len(store('custom_vendors', []))} • Expenses: {len(store('expenses', []))}")
        st.write("Content moderation in v3: you can delete your own guests, vendors and expenses from their sections. "
                 "A multi-user admin panel needs a backend and is a next phase.")

def render_previews() -> None:
    """Mock previews of future features — clearly labelled, no real actions.

    Safety rules for every preview below:
    - No password or card-number input field exists anywhere here.
    - Every action button is disabled, or only shows a "preview only" message.
    - Nothing is created, booked, charged, sent or saved to a server.
    - Sample names, prices and stats are illustrative only.
    """
    st.subheader("Previews (Mock) — how future features will look")
    st.warning("⚠️ MOCK PREVIEW ONLY — Nothing on this page creates an account, "
               "takes a payment, books a vendor, sends a message, or saves data "
               "to a server. These are views to show the design until the free "
               "backend (Supabase) version is built. Real features will replace "
               "each preview, one by one.")
    st.caption("Works without a plan — open this section from Home any time.")

    with st.expander("1. Login / Account — MOCK PREVIEW", expanded=True):
        st.write("**Mock sign-in screen (design only)**")
        st.write("Email: sample@example.com  •  Password: ••••••••  (not a real form — no password field here)")
        st.button("Sign in with Google (mock — disabled)", disabled=True)
        st.button("Sign in (mock — disabled)", disabled=True)
        st.write("After real login, this page will show: your events on any device, "
                 "profile photo, and saved payment methods via a secure provider — none of that exists yet.")
        st.caption("Preview only: no account is created and no password is collected or sent anywhere.")

    with st.expander("2. Checkout & Payments — MOCK PREVIEW"):
        st.write("**Mock order summary (sample prices, not a real cart)**")
        st.table([{"Item": "Balloon Arch Kit (sample)", "Qty": "1", "Price": "₹2,500 (sample)"},
                  {"Item": "Photo Booth Props (sample)", "Qty": "1", "Price": "₹1,500 (sample)"},
                  {"Item": "Total (sample)", "Qty": "—", "Price": "₹4,000 (sample)"}])
        st.button("Pay now (mock — disabled, no payment taken)", disabled=True)
        st.caption("Preview only: no card details are collected here, no payment gateway is connected, "
                   "and no money moves. Real checkout needs a payment provider and will always charge its own transaction fee.")

    with st.expander("3. Vendor Booking — MOCK PREVIEW"):
        st.write("**Mock booking request (sample vendor, sample status)**")
        st.table([{"Vendor": "Dream Venue Hall (sample)", "Date": "Sample date", "Status": "Request sent (mock sample)"},
                  {"Vendor": "Tasty Bites Catering (sample)", "Date": "Sample date", "Status": "Awaiting reply (mock sample)"}])
        st.button("Request booking (mock — disabled)", disabled=True)
        st.caption("Preview only: no vendor is contacted and no booking is made. Real bookings will be database records in the backend version.")

    with st.expander("4. 3D Floor Plan — MOCK PREVIEW"):
        st.write("**Mock 3D-style view (illustration, not interactive 3D)**")
        st.write("Imagine this room from above, tilted: Stage at the back, 6 round tables in the middle, "
                 "dance floor in front, entrance on the right, photo booth in the corner.")
        cols = st.columns(3)
        for i, label in enumerate(["🎤 Stage", "🪑 Table 1", "🪑 Table 2", "💃 Dance floor", "🪑 Table 3", "📸 Photo booth"]):
            with cols[i % 3]:
                st.markdown(f"**{label}**")
        st.caption("Preview only: this is a labelled layout, not a drag-and-drop 3D editor. Real 3D/AR is a premium next phase.")

    with st.expander("5. Live Multi-user Collaboration — MOCK PREVIEW"):
        st.write("**Mock collaborators (sample people, not live users)**")
        st.table([{"Name": "Sample co-host", "Role": "Co-host (sample)", "Status": "Online (mock sample)"},
                  {"Name": "Sample family member", "Role": "Helper (sample)", "Status": "Editing checklist (mock sample)"}])
        st.write("Sample comment: \"I booked the cake shop\" — sample co-host (mock sample)")
        st.caption("Preview only: no other user is actually online. Real live sync needs a backend database.")

    with st.expander("6. Email / SMS Notifications — MOCK PREVIEW"):
        st.write("**Mock notifications (samples, nothing is sent)**")
        st.write("- 📧 Sample: \"Reminder: venue payment due in 3 days\" (mock sample, not sent)")
        st.write("- 📱 Sample: \"RSVP from 5 guests still pending\" (mock sample, not sent)")
        st.caption("Preview only: this app sends no email or SMS today. Real notifications need a backend + messaging provider.")

    with st.expander("7. Admin Dashboard — MOCK PREVIEW"):
        st.write("**Mock business stats (sample numbers)**")
        c1, c2, c3 = st.columns(3)
        c1.metric("Sample events planned", "1,240 (sample)")
        c2.metric("Sample vendors listed", "86 (sample)")
        c3.metric("Sample orders", "312 (sample)")
        st.caption("Preview only: these are sample numbers, not real analytics. A real admin panel needs a backend.")



def main() -> None:
    request = sidebar_plan_form()
    if request is not None:
        try:
            st.session_state["plan"] = cached_plan(request.validated(date.today()), date.today())
            st.session_state.pop("ai_text", None)
        except ValidationError as exc:
            st.error(f"Please fix: {exc}")
    plan = plan_or_none()
    # Quick-access cards on Home set pending_section; apply it BEFORE
    # the radio widget is created, otherwise Streamlit rejects the change.
    if st.session_state.get("pending_section"):
        st.session_state["nav_section"] = st.session_state.pop("pending_section")
    # TOP navigation bar: a horizontal menu at the top of the page, so a
    # person can pick any section as they like — no sidebar hamburger hunt,
    # especially on mobile. The sidebar still holds the (optional) plan form.
    st.caption("Choose a section below — tap any name, it opens at once.")
    section = st.radio("Choose a section", SECTIONS, horizontal=True, key="nav_section")
    with st.sidebar:
        st.divider()
        st.caption("Celebration & Event Planner · Hack2Skill Challenge 5")
    if section == "Home":
        render_home(plan)
    elif section == "Previews (Mock)":
        render_previews()
    elif plan is None:
        render_home(None)
        st.warning("Create a plan from the sidebar form (or try a sample plan on Home) to use this section.")
    elif section == "Plan":
        render_plan(plan)
    elif section == "Guests & Invites":
        render_guests(plan)
    elif section == "Budget & Expenses":
        render_budget(plan)
    elif section == "Food & Cake":
        render_food(plan)
    elif section == "Music & Games":
        render_music_games(plan)
    elif section == "Kids":
        render_kids(plan)
    elif section == "Decor & Design":
        render_decor(plan)
    elif section == "Vendors & Shopping":
        render_vendors_shopping(plan)
    elif section == "Seating & Floor Plan":
        render_seating(plan)
    elif section == "Live Event Day":
        render_live(plan)
    elif section == "Post-Event & Memories":
        render_post_event(plan)
    elif section == "AI Assistant":
        render_ai(plan)
    elif section == "Profile & Settings":
        render_profile(plan)
    elif section == "Previews (Mock)":
        render_previews()


main()
