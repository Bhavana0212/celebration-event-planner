# Feature coverage — honest map for v3

This file maps the requested Basic → Ultra-Advanced list to what v3
actually does, what is partial / simulated, and what is deliberately NOT
claimed yet. Do not use this file to claim a feature that is marked Next phase.

## Implemented and working in v3

- **Level 1 — Basic:** Home, local profile, create/edit/duplicate/delete
  (in-session) events, 8 occasions, date/time, venue, guest count, dashboard,
  multiple events, checklist add/tick, countdown, calendar (.ics), notes,
  reminders, budget calculator, mobile-friendly Streamlit layout.
- **Level 2 — Planning:** Themes + colour palettes, inspiration notes,
  mood-board notes, decor planners (balloon, flower, stage, table, lighting,
  entrance, DIY), decoration shopping list + budget, indoor/outdoor,
  venue comparison (sample directory), seating planner, 2D floor-plan
  schematic, timeline builder (engine + custom tasks).
- **Level 3 — Budget & finance:** 18 categories, estimated vs actual,
  paid / unpaid / advance, vendor quotations, remaining budget, per-guest
  cost, warning alerts, receipt names recorded, CSV + PDF expense report,
  charts, shared budget (collaborator names).
- **Level 4 — Guests & invitations:** Guest name/email/phone, groups,
  categories, invitation templates + custom text, WhatsApp link, email link,
  RSVP Accept/Decline/Maybe/Pending, plus-one, dietary, accessibility,
  kids count, reminders, QR code, check-in, attendance report, seating
  assignment, thank-you template.
- **Level 5 — Food & catering:** Menu planner by meal, cake flavour + size
  calculator, beverages, kids' menu, veg/vegan/allergy menu filtering,
  guest-based quantities, caterer comparison, buffet/serving schedule,
  leftover plan.
- **Level 6 — Music, games & entertainment:** Playlist creator + song
  requests, music by moment, DJ in vendor directory, games library with
  age/place filters, rules/materials/duration, quiz builder, scavenger-hunt
  builder, lucky draw, prize planning (in games + budget), schedule builder.
- **Level 7 — Kids:** Age-group activities, themes, craft, face painting,
  magic/clown/bouncy-castle in vendor directory, return-gift planner,
  goodie-bag checklist, child safety checklist, parent contact in guest list.
- **Level 8 — Vendors, shopping & logistics:** Vendor directory (sample),
  ratings/reviews (user notes), price comparison, booking status,
  contracts (file names recorded), payment milestones via expenses,
  contact sheet, shopping catalogue + cart (estimates), delivery/return
  reminders as checklist tasks, parking/transport planner, weather checklist.
- **Level 9 — Collaboration & automation:** Collaborators with roles
  (names only), task assignment via guest/vendor names in notes, deadlines
  and priorities in checklist, file upload names recorded, in-app reminders,
  overdue alerts, RSVP follow-up list, calendar sync (.ics), PDF export,
  guest CSV, printable checklist (PDF/Markdown), run sheet, offline access
  via downloads, change history (in-session edits only).
- **Level 10 — AI:** Rule-based AI assistant chatbot, AI-generated plan
  from a prompt, theme/decor/colour recommendations, budget optimisation,
  expense prediction tips, food quantities, menu, playlist, games by age
  and group size, timeline, invitation writing, seating suggestions,
  vendor shortlist (filtered directory), shopping list, weather backup,
  accessibility suggestions, last-minute problem-solving checklists,
  plan adjustments on budget/guest-count change, plus optional Gemini
  creative ideas (capped, with offline fallback).
- **Level 12 — Post-event:** Photo gallery (session uploads), collage maker,
  guestbook, wishes, highlights notes, thank-you template, final expense
  report, vendor reviews, what-worked notes, duplicate event, save as template.
- **Level 13 — Security/admin (v3 scope):** Input validation, sanitising,
  length caps, no hard-coded secrets, secrets via env/Streamlit Secrets,
  private-by-default session data, data export + session delete, accessible
  interface, responsive layout, SEO page title/description.

## Partial / simulated (labelled as such in the app)

- **Accounts:** Local profile only. No OAuth, email verification, password
  reset, or two-factor authentication — those need a backend.
- **Shopping / payments:** Catalogue + cart totals are planning estimates.
  No checkout, payment gateway, shipping, refunds or commissions.
- **Vendor bookings:** Directory + status + milestones only. No real
  booking, contract signature, or vendor dashboard.
- **Language:** Currency choice is real; full UI translation is not yet
  done (preference is recorded for future i18n).
- **Event website:** A downloadable single-file HTML page, not a hosted
  custom URL. Host it on any static host for a real URL.
- **Live features:** Live day, polls and check-in work in one browser
  session. Real multi-user live sync needs a backend / database.

## Next phase — NOT in v3, do not claim these

- 3D venue visualisation, drag-and-drop 3D floor plan, AR decoration preview,
  virtual venue tours (v3 has a 2D schematic only).
- Real payment gateway, vendor subscription plans, marketplace commissions,
  gift-registry purchases, refund/cancellation processing.
- Real email/SMS sending, push notifications, live multi-user collaboration.
- Vendor marketplace with real listings, bookings and payouts.
- Multi-user admin panel, content moderation at scale, analytics backend.
- Full multi-language UI, regional tradition templates beyond the current
  theme/vibe system.

## Why this split?

Streamlit Cloud + a single repo can genuinely deliver a full planning
platform (levels 1–10, plus post-event) with no backend. The next-phase
items above need a database, authentication, payments and real-time
infrastructure — building them as fake buttons would mislead users and
evaluators, so they are listed honestly as the next phase instead.

## Audit-fix batch (2026-10-27, party theme)
- Party theme: festive magenta (#C026D3) primary, light pink secondary, white background, hero banner on Home — not a corporate navy theme.
- Event time: collected in the sidebar, stored on EventRequest, saved with saved events, loaded back, and shown in the saved-event list.
- Custom tasks in Plan: add / tick off / delete, alongside the engine checklist.
- Guests: CSV import (Name column, optional Email/Phone/Group/RSVP) with duplicate skip, plus duplicate warning on manual add.
- Food: numeric leftover tracker (planned vs used = leftover, Packed/Donated/Discarded).
- Music & Games: score tracker with sorted leaderboard and leader line.
- Profile: session backup download (JSON) and restore upload — a file the user keeps, not server backup.
- Catalog: 3 new decor sections, 3 new games, 3 new event templates (Baby Shower, Corporate Party, Graduation).
- Tests: 112 passed (107 previous + 5 new audit-fix tests).
- Still next phase, not faked: real accounts/OAuth, real payments/checkout, real vendor bookings, 3D/AR, live multi-user sync, email/SMS sending, hosted custom event URLs.

## Market batch (2026-10-27, after the full 200+ feature list check)
- Event types expanded 8 -> 18: Engagement, Retirement, Housewarming, Farewell,
  Holiday Party, Dinner Party, Surprise Party, Family Reunion, School / College
  Event, Sports Celebration added, each with its own budget split (sums to 1.0)
  and per-guest baseline, vendor checklist and timeline tasks where applicable.
  Budget code now falls back to Community Event instead of crashing on an
  unknown type. 169 tests pass (162 + 7 new market-batch tests).
- Multi-day events: optional End date in the sidebar form, validated
  (end >= start), saved with saved events, loaded back, and shown as a range.
- Custom tasks now have a Priority (High / Medium / Low) shown next to the title.
- Venue comparison: sample venues now carry capacity + indoor/outdoor, and a
  side-by-side comparison table is shown in Vendors & Shopping before the
  directory, with a note that real venue booking is not done by this app.
- Home metrics are now dynamic (event-type and budget-category counts from
  code, not hard-coded numbers). Themes added: Superhero, Princess / Fairy,
  Dinosaur. Templates added for Engagement, Retirement, Housewarming,
  Holiday Party, Surprise Party and Family Reunion (13+ templates total).
- Local Streamlit HTTP 200 verified for this batch.
- STILL next phase, NOT faked by this batch: real sign-up/login/OAuth,
  email verification, password reset, 2FA, real payments/checkout, real
  vendor/venue bookings, real email/SMS/push sending, live multi-user sync,
  3D/AR floor planning, hosted custom event URLs, vendor marketplace with
  payouts, admin panel at scale, full multi-language UI. Those need a
  backend, database, auth and payment provider — a Streamlit patch cannot
  honestly deliver them, and adding fake buttons for them would mislead
  users. Market launch as a free, no-account, single-session planner is
  real today; the super-platform version is a rebuild, not a patch.

## Mock previews batch (2026-10-27)
- New 15th section "Previews (Mock)", works without a plan, from Home quick-access too.
- 7 previews, every one labelled MOCK PREVIEW: Login/Account, Checkout & Payments,
  Vendor Booking, 3D Floor Plan (labelled illustration, not interactive 3D),
  Live Multi-user Collaboration, Email/SMS Notifications, Admin Dashboard.
- Safety: no password input and no card-number input anywhere in previews;
  action buttons are disabled; sample names/prices/stats only; nothing is
  created, booked, charged, sent or saved to a server. Real features will
  replace each preview in the free-backend version.
- Tests: 172 pass (169 + 3 new preview tests); AppTest navigation to
  Previews verified with no exception.
- NOT yet on GitHub/live at commit time: the previous market-batch web upload
  was still running, so this mock batch is committed locally and will be
  uploaded after that upload finishes, to avoid conflicting web edits.

## Top-nav + main-form batch (2026-10-27)
- Navigation moved to the TOP of the page: a horizontal "Choose a section"
  menu, so a person can pick any section as they like without opening the
  sidebar hamburger menu (the old mobile pain point).
- Event form is now ALSO on the Home page, right under the headline
  ("Step 1 — Create your plan here"), with the same fields as the sidebar
  form. The sidebar form is kept for desktop, but is no longer required.
- Submitting either form, or "Try a sample birthday plan", now goes
  straight to the Plan page (previously it stayed on Home, which looked
  like nothing had happened).
- Plan page now has "Full plan at a glance": invitation text ready to
  copy, day schedule, vendors to book, guest-scaled shopping/item list,
  games for the event type, and music by moment — on top of the existing
  budget split, checklist, risks, logistics and menu.
- Tests: 174 pass (172 + 2 new top-nav tests); AppTest verified top nav
  exists, sidebar submit lands on Plan, and the full-plan heading +
  invitation appear.

## Best-in-market batch (2026-10-27, after Eventbrite / Partiful / Zola comparison)
- Honest positioning on Home: Eventbrite = paid public tickets (with fees),
  Partiful = stylish casual invites, Zola = weddings only with a real gift
  shop. This planner's edge, stated plainly: free, no account, every event
  type, budget+guests+vendors+food+games+seating+memories in one place,
  with structured data (dietary filters the menu, plus-ones counted,
  budget always adds up). It does NOT sell tickets or gifts.
- Plan readiness dashboard on Home (when a plan exists): guests listed,
  attending, expenses tracked, vendors added, plus a simple progress bar
  over 4 areas — labelled as a progress count, not a quality score.
- Stylish invitation preview card on Plan (theme colours, event name,
  date/time, city, guests, theme) — Partiful-style design, but share via
  the existing WhatsApp/email links; the app sends nothing itself.
- RSVP summary chart on Guests (Attending/Pending/Maybe/Declined counts).
- Wedding-only checklist on Plan when event type is Wedding: ceremony,
  reception, outfits, rings, shot list, honeymoon-fund tracker (no purchase),
  transport/accommodation, rehearsal dinner.
- Tests: 177 pass (174 + 3 new best-batch tests).
- NOT yet uploaded at commit time: the top-nav GitHub upload was still
  running, so this batch uploads after it to avoid conflicting web edits.

## My own additions batch (2026-10-27, user said "add something of your own")
- One-click sample plans for Wedding (Aarav & Meera's Wedding, 150 guests,
  Elegant Gold) and Community Festival (Neighbourhood Summer Festival,
  200 guests, outdoor, Rainbow / Fun) on Home, next to the birthday
  sample — so a visitor can see a full plan for three occasions in one tap.
- WhatsApp plan summary on Plan: one link with event, date/time, city,
  guests, budget, next three tasks and top budget lines — the app sends
  nothing itself, the user sends it from their own WhatsApp.
- One-time celebration: balloons once when a plan first opens in a
  session, then never again in that session (session flag, not on every
  Plan view).
- Tests: 179 pass (177 + 2 new my-additions tests).
- NOT yet uploaded at commit time: the best-in-market GitHub upload was
  still running, so this batch uploads after it to avoid conflicting
  web edits.

## Easily-accessible batch (2026-10-27, after searching best event sites for usability)
- Research learnings applied (EventCreate/RSVPify fast onboarding, Luma
  under-2-minute event page with no account for guests, Partiful single-page
  setup vs multi-tab setup, and standard usability rules: one clear hero,
  one clear CTA, tell the visitor exactly what to do next, short forms,
  step-by-step instructions before the task):
  - Home hero "First time here? Start here — 3 steps, about 2 minutes"
    with a 1-tap example button at the very top, before any form.
  - Main form labelled: only 5 things needed (name, type, guests, budget,
    date); everything else optional and skippable.
  - "What to do on each page — in plain words" guide on Home, plus a
    30-second "How to use this website" expander with the exact 5 steps.
  - Empty-state guidance moved to the TOP when a section is opened
    without a plan (previously a warning after the whole Home page).
- Tests: 181 pass (179 + 2 new accessibility tests).
- NOT yet uploaded at commit time: the best-in-market GitHub upload was
  still running (after a re-grant), so this batch uploads after it to
  avoid conflicting web edits.

## Professional theme batch (2026-10-28, user: replace Streamlit generic theme)
- Well-architected split: look is now separate from logic —
  assets/professional-theme.css holds the theme, planner/ holds the
  engine, app.py holds screens. Theme loads via load_professional_theme()
  at the start of main(); if the CSS file is missing, the app still
  works with Streamlit's default look (no crash).
- Professional look (still festive, not corporate navy): deep magenta
  accent #9D174D (was bright #C026D3), white background, light-grey
  sidebar #F9FAFB, dark text #111827, Inter/system font stack, content
  capped at 1180px with breathing room, card-style metrics (white card,
  border, soft shadow, rounded corners), rounded buttons with a magenta
  gradient primary button, rounded inputs with magenta focus ring,
  rounded expanders/alerts.
- Proper layout: a slim professional site header at the top of every
  page (brand + "Free · No account · Every event, one plan"), then the
  horizontal section menu, then the page content — like a real product
  header, not a bare Streamlit page.
- Tests: 183 pass (181 + 2 new professional-theme tests); AppTest run
  verified: no exception, theme <style> and pro-header markdown present.
- NOT yet uploaded at commit time: the best-in-market GitHub upload was
  still running, so this batch uploads after it to avoid conflicting
  web edits. Files to upload: app.py, .streamlit/config.toml,
  assets/professional-theme.css (new), tests/test_professional_theme.py
  (new), FEATURE_COVERAGE.md.

## Step-by-step journey batch (2026-10-28, user: steps one by one, start to end, event fully set)
- New "Complete journey — start to end, step by step" section at the top
  of Home, in the user's exact sequence: 1 Celebration planning,
  2 Guest list, 3 Budget, 4 Invitation, 5 Decor, 6 Food & Cake,
  7 Music & Games, 8 Vendors & Shopping, 9 Seating, 10 Kids & Return
  gifts, 11 Live Event Day, 12 Thank you & Memories.
- Each step has an "Open →" button that goes straight to that section
  (via the existing pending_section mechanism); before a plan exists,
  steps 2–12 honestly say "Create plan first" instead of opening an
  empty section.
- Progress is honest, not faked: a progress bar + "X of 12 steps done"
  + "Next step" line, computed from real session data only (plan,
  real_guests, expenses, decor_shopping/mood_notes, menu inputs,
  playlist/song requests/scores, custom_vendors/cart, seating,
  goodie_items, announcements/poll, guestbook/photos/gifts). Steps 1
  and 4 are ready with the plan itself, because the plan generates
  the checklist and the invitation — that is stated in the caption.
- When all 12 are done: "🎉 All steps done — your event is fully set!"
- Tests: 185 pass (183 + 2 new journey tests); AppTest verified: no
  exception, journey subheader + 0/12 progress with no plan, and after
  the 1-tap sample plan the journey buttons appear.
- NOT yet uploaded at commit time: the professional-theme GitHub upload
  was still running, so this batch uploads after it to avoid
  conflicting web edits.

## Premium polish + wizard batch (2026-10-28, user chose Streamlit premium polish, submission safe)
- Palette switched to the reference premium palette: Forest #24352E
  (primary/buttons/headings), Champagne #C6A477 (accent line),
  Ivory #F7F3ED (panels/sidebar), White, Charcoal #30343B (text),
  with editorial serif (Georgia) headings and clean sans body,
  14-16px card radius, 44px minimum touch targets on buttons.
- Sidebar duplicate form REMOVED: the old design had the same long
  form in the sidebar and on Home, which dominated mobile screens.
  Sidebar is now only a short workspace guide (current event + days
  to go, if a plan exists). Event creation lives only on Home.
- 7-step event creation wizard (reference design): 1 Occasion,
  2 Date & location, 3 Guests, 4 Style, 5 Budget, 6 Services,
  7 Review — with "Step X of 7" progress, Back/Continue, auto-save
  into wizard_data on every step (going Back never loses answers),
  and only the final "Create my full plan" button builds the plan
  and lands on Plan with "Full plan at a glance".
- Customer dashboard when a plan exists (reference design): Home
  shows "Your dashboard" with upcoming celebration + days to go,
  planning progress (journey steps done), budget planned / spent /
  remaining, guests attending, next action, and quick actions
  (See my full plan, Add a guest, Add an expense). The wizard then
  sits inside "Create a different event" instead of replacing the
  dashboard. With no plan, Home shows "Explore all celebrations"
  (Wedding / Birthday / Corporate Party / Baby Shower) that start
  the wizard with that occasion pre-chosen.
- Honest limit, unchanged: this is still Streamlit underneath —
  polished, grouped and wizard-guided, but not a CELESTIA-level
  custom site. That rebuild stays a post-submission phase.
- Tests: 187 pass (185 + 2 new premium-polish tests); old sidebar
  and main-form tests updated to the wizard flow (sidebar has no
  button, wizard walk creates a plan and lands on Plan).
- NOT yet uploaded at commit time: upload this batch now (it is the
  current batch), then live-verify.

## 2026-10-28 — Celebration-vibe + page-wise batch (user feedback on live screenshots)
- Theme back to festive: magenta #C026D3 / warm ivory #FFF7ED / gold #F59E0B / pink #FDF2F8. Forest/Champagne was too serious, no celebration feeling.
- Header no longer clipped: pro-header wraps (flex-wrap), brand wraps, block-container top padding 2.5rem (3rem on mobile).
- Metrics no longer truncated on mobile: Plan, dashboard, readiness, Home stats and logistics now use 2-3 columns instead of 4-5 across.
- Page-wise, not one long page: Home's 14 quick cards removed (top menu + journey already navigate); Why/How/What/templates/FAQ/saved-events moved into one collapsed "More about this planner" expander, so Home on first look is hero + wizard/dashboard + journey + explore only. Plan split into 4 tabs: Overview / Budget & Checklist / Invitation & Day Plan / My tasks & Notes.
- 190 tests pass (new test_celebration_vibe.py; older Forest palette tests updated, readiness test updated to dashboard heading).

## 2026-10-28 — Pages + stepper + navbar batch (user feedback: no more one long page)
- Top navbar is now one dropdown "Navigate to a page" (22 pages) instead of 20 wrapping radio buttons; header bar on top, footer bar on every page (brand, page list, free/no-account note).
- New info pages (work without a plan): About, Services (12 services, each opens its page), Pricing (Free plan; future ideas labelled NOT available, no price promised), FAQ, Reviews (honest: no verified reviews yet; session-only reviews, not published), Contact (GitHub + live links, WhatsApp draft link — app sends nothing), Privacy & Terms (session-only data, no account, no tracking).
- Journey is now a horizontal process graph (Step 1 → Step 2 → …): ✓ done, ▶ next step, numbered coming up — plus 3-column step cards with Open buttons. No "Pending" table, no "Create plan first" column.
- Form first on Home: wizard/dashboard now sit right after the hero and example button, journey comes after — nobody scrolls to the bottom to fill a form. Content lives between header and footer.
- 195 tests pass (new test_pages_stepper.py; topnav test updated to the selectbox navbar).

## 2026-10-28 — Popping colours batch (user feedback: colours should pop more)
- Vivid popping palette: primary #E91E8C (bright pink), gradient buttons pink → orange #FF7A00, gold accent #FFB800, bright pink-tinted background #FFF5F9, sidebar #FFE4F1. No extra cost, theme files only.

## 2026-10-28 — Footer fix (live check found footer missing)
- render_footer() was defined but never called in main() — fixed: it now runs at the end of every page (Home, Plan, info pages, all sections). AppTest confirms the pro-footer block renders.

## 2026-10-28 — Open nav + persistent header/footer batch (user feedback: video looked like slides, need actual page-by-page work)
- Nav is NO LONGER a dropdown: it is an open, horizontal, one-line scrollable radio bar ("Navigate", horizontal=True, CSS flex-wrap: nowrap + overflow-x: auto), Facebook top-bar style as reference only — every page visible, current page highlighted, scroll left/right on mobile.
- Header/footer pattern like YouTube: pro-header is sticky at the top and render_footer() runs at the end of main() on every page, so header and footer stay exactly the same while only the middle page content changes — Home shows its form/wizard/dashboard, Plan shows its 4 tabs, Guests shows guest form, and so on, page by page.
- Contact now includes Bhavana Shah's LinkedIn link (https://www.linkedin.com/in/bhavana-shah-875a85137), opening in the user's own app/browser; app still sends nothing.
- FAQ is now general questions (What is this website? Who can use it? Is it free? Do I need an account? How do I start? Can I use it on my phone? plus wedding, privacy, keep-plan, booking/payment honesty).
- Tests: new test_open_nav.py (4 tests); test_topnav and test_pages_stepper updated from selectbox to open radio nav. Total local test count to be re-checked after a full run — do not quote 195 until that run passes.
