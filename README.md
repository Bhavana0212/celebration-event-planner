# 🎉 Celebration & Event Planner — v3 Market Platform

**Hack2Skill Virtual: PromptWars — Challenge 5**
**By Bhavana Shah**

See `FEATURE_COVERAGE.md` for an honest map of what v3 does, what is
partial/simulated, and what is a next phase (payments, 3D/AR, real accounts,
real bookings). Do not claim next-phase features as done.

A smart assistant that turns a few details about an event into a complete,
context-aware plan — and a website you can actually launch: a landing page,
a plan builder, guest and vendor managers, a budget tracker, and exports.

This repo merges two builds:
- **The rule-based engine** (from the other `event-planner` project): budget
  tiers, risks, logistics, dietary-safe menu, countdown checklist,
  Markdown + `.ics` export, optional Gemini ideas, CI, and 90 tests.
- **The first Streamlit build**: invitation, vendor checklist, day schedule,
  games, music, item list and personalised ideas.

## What it does

Enter event name, type, guests, budget, currency, date, city, theme, vibe,
dietary and accessibility needs, and whether it is outdoor. You get:

- 🏠 **Landing page** — what it does, how it works, try a sample plan
- 📋 **My events** — save several events in your browser session and reload them
- ✉️ **Invitation** — ready-to-copy text, plus download
- 👥 **Real guest list** — add names, groups, RSVP status and dietary notes; CSV export
- 💰 **Budget** — context-aware split (vibe, dietary, accessibility, outdoor),
  tier + advice, chart + table, **and an actual-vs-planned tracker**
- ✅ **Vendor checklist + vendor manager** — tick standard vendors, add your own
  with price, status and contact, see total quoted spend
- 🗓️ **Countdown checklist** — due dates, overdue tasks pulled to “Do now”, progress bar
- 🎮 **Schedule & fun** — day schedule, games, music by moment, shopping list with tick-off
- ⚠️ **Risks** — lead time, tight budget, rain season, outdoor + wheelchair,
  peak wedding season, large crowds, many dietary needs, weekend premium
- ✨ **Ideas** — offline ideas, plus optional Gemini ideas (capped at 5 per session)
- ⬇️ **Export** — Markdown plan, `.ics` calendar reminders, invitation, guest CSV, plan JSON

Event types: Birthday, Wedding, Anniversary, Baby Shower, Corporate Party,
Festival / Cultural, Graduation, **Community Event**.
Currencies: INR, USD, CAD, GBP, EUR.

## How it works

```
app.py (Streamlit UI: landing, tabs, managers, tracker)
  └─ planner.build_plan(EventRequest)
       ├─ models.py     validation + sanitising + currency
       ├─ budget.py     allocation + tier (vibe/dietary/access/outdoor adjusted)
       ├─ timeline.py   adaptive countdown checklist
       ├─ logistics.py  quantities + dietary-safe menu
       ├─ risks.py      rule-based risk alerts
       ├─ extras.py     invitation, vendors, day schedule, games, music, items
       ├─ export.py     Markdown + .ics
       └─ ai.py         optional Gemini ideas (+ offline fallback)
```

Budget shares are re-normalised so the lines **always sum exactly to the budget**
(last line absorbs rounding). Plans are pure functions of (request, today),
so identical inputs are cached.

## Run locally

```bash
pip install -r requirements-dev.txt
streamlit run app.py
pytest -q
```

Optional AI ideas: set `GEMINI_API_KEY` (env var or `.streamlit/secrets.toml`,
see `secrets.toml.example`). Without it, offline ideas are used.

## Deploy on Streamlit Community Cloud

1. Push this repo (public, single `main` branch) to GitHub. Keep it under 10 MB.
2. Go to share.streamlit.io → **New app** → pick the repo, branch `main`, file `app.py`.
3. Click **Deploy**. (Optional) Settings → Secrets → `GEMINI_API_KEY=...`
4. Add a custom domain later in Streamlit Cloud settings if you want a branded launch URL.

## Launch checklist — what “ready to launch” means here

✅ Ready now: free, no-account planner, landing page, full plan builder,
guest/vendor/budget tracking, exports, tests, CI, privacy note in-app.

⏳ Not in v1 (do not claim these yet): user accounts and login, a database
that persists across devices, email/SMS RSVP sending, vendor booking or
payments, and a vendor marketplace. Those need a backend, auth, and payment
provider — they are the honest next phase, not hidden in this code.

To launch v1: deploy on Streamlit Cloud, set the app to public, test the
sample plan on a phone, upload a demo video (YouTube Unlisted or Drive),
and link it from your Hack2Skill submission and LinkedIn post.

## Tests

```bash
pytest -q
```

101 tests: validation, budget invariants, timeline urgency, logistics maths,
menu filtering, risks, prompt-injection fencing, exports, extras (invitation,
games, music, items, currency, Community Event), and Streamlit AppTest smoke tests.
CI runs them on every push (`.github/workflows/ci.yml`).

## Quality focus areas

- **Code quality:** small single-purpose modules, frozen dataclasses, type hints.
- **Security:** strict allow-list validation, control-character stripping, length caps,
  no `unsafe_allow_html`, API key only from env/secrets (git-ignored), user notes
  fenced as untrusted data in the AI prompt, AI calls capped at 5 per session,
  errors never leak provider details.
- **Efficiency:** pure functions, `st.cache_data` on plans, forms avoid reruns while typing,
  AI only on demand, tiny dependency set.
- **Accessibility:** labelled inputs with help text, high-contrast theme, risk levels
  shown with text + icon (never colour alone), chart data duplicated in a table,
  keyboard-operable native widgets, sensible heading order.
- **Problem alignment:** dynamic decisions from user context (see the table in the
  original engine README, now extended with invitation, guests, vendors, games,
  music, items and actual spend tracking).

## Gen AI usage

- **Google Gemini** (`google-genai`, model `gemini-2.5-flash`) writes creative
  theme/activity ideas in the Ideas tab, using the validated plan summary as context.
- The core planning is rule-based; if there is no key or the API fails, the app
  falls back to offline ideas and keeps working.
- Built with AI-assisted coding (Muse), including the merged extras and tests.

## Assumptions

- Per-guest baselines and cost shares are typical planning heuristics, not quotes.
- Space: 12 sq ft/guest indoor, 15 outdoor; 8 guests per table; 3 guests per vehicle;
  ~4 drinks per guest; 10% food buffer.
- Seasons are India-centric in the original risk rules (rain Jun–Sep, peak wedding
  Nov–Feb); weekend premium is 10–20%.
- Menu is a small illustrative catalogue; always confirm allergens with the caterer.
- Lead times: 30+ days (90+ for weddings).
- Currency conversion is not done — the app splits the number you enter, in the
  currency you choose.
