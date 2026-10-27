"""Market helpers: seating, lucky draw, budget optimisation, QR codes,
PDF export, event-website HTML, collage, and a rule-based AI assistant.

No payments, no real bookings, no 3D/AR here — those are deliberately
NOT faked. What these helpers do is real and testable in-app.
"""

from __future__ import annotations

import io
import math
import random
import urllib.parse
from collections import defaultdict


def seating_assign(guests: list[dict], seats_per_table: int = 8) -> dict[int, list[str]]:
    """Assign guests to tables, keeping the same group together where possible.

    Guests are dicts with at least 'Name' and optionally 'Group'.
    Returns {table_number: [names]}.
    """
    if seats_per_table < 1:
        raise ValueError("seats_per_table must be at least 1")
    by_group: dict[str, list[str]] = defaultdict(list)
    for g in guests:
        name = str(g.get("Name", "")).strip()
        if name:
            by_group[str(g.get("Group", "Other"))].append(name)
    tables: dict[int, list[str]] = {}
    table_no = 1
    current: list[str] = []
    for group in sorted(by_group):
        for name in by_group[group]:
            current.append(name)
            if len(current) >= seats_per_table:
                tables[table_no] = current
                table_no += 1
                current = []
    if current:
        tables[table_no] = current
    return tables


def lucky_draw_winner(attending_names: list[str], seed: int | None = None) -> str | None:
    """Pick a lucky-draw winner from attending guests. None if no one."""
    names = [n for n in attending_names if n]
    if not names:
        return None
    rng = random.Random(seed) if seed is not None else random.Random()
    return rng.choice(names)


def budget_optimisation(planned: dict[str, float], actual: dict[str, float]) -> list[str]:
    """Plain-language suggestions when actual spend exceeds planned spend."""
    tips = []
    for category, plan_amount in planned.items():
        spent = actual.get(category, 0.0)
        if spent > plan_amount:
            over = spent - plan_amount
            tips.append(
                f"{category} is over by {over:.2f}. Consider a simpler option, "
                "a package deal, or moving money from Contingency / Extras."
            )
    if not tips:
        tips.append("All categories are within plan so far. Keep Contingency untouched until event day.")
    return tips


def whatsapp_link(phone: str, message: str) -> str:
    """A real wa.me share link. Phone may be empty (then it opens WhatsApp with the text)."""
    digits = "".join(ch for ch in phone if ch.isdigit())
    base = f"https://wa.me/{digits}" if digits else "https://wa.me/"
    return base + "?text=" + urllib.parse.quote(message)


def mailto_link(email: str, subject: str, body: str) -> str:
    return ("mailto:" + urllib.parse.quote(email)
            + "?subject=" + urllib.parse.quote(subject)
            + "&body=" + urllib.parse.quote(body))


def ai_assistant_reply(question: str, event_type: str = "", guests: int = 0,
                       budget: float = 0.0) -> str:
    """Rule-based AI assistant (no external API call).

    It answers the most common planning questions with a checklist.
    It never pretends to be a live LLM, and it never invents a vendor,
    price or booking.
    """
    q = (question or "").lower()
    if "vendor" in q and ("cancel" in q or "not available" in q):
        return ("If a vendor cancels: 1) Check your backup vendor list and contracts. "
                "2) Ask the venue for its recommended vendor. 3) Simplify that item "
                "(e.g. a smaller cake, a playlist instead of a DJ) rather than cancelling the event. "
                "4) Tell guests only if the schedule actually changes.")
    if "rain" in q or "weather" in q:
        return ("Weather backup: book a tent or indoor backup, move the photo corner "
                "indoors, keep a towel / umbrella kit, and tell vendors the backup time "
                "at least a day before.")
    if "budget" in q and ("low" in q or "cut" in q or "save" in q):
        return ("To save money: cut the guest list first, choose a community hall, "
                "use a fixed-price menu, DIY decor for tables, and keep Contingency "
                "untouched until event day.")
    if "rain" in q:
        return "See the weather backup checklist in the Risks section."
    if "game" in q:
        return ("Pick games by age and place: kids outdoors — treasure hunt and relay; "
                "adults indoors — trivia and couple quiz; mixed family — bingo, charades "
                "and a photo challenge. Keep each game to 15–30 minutes.")
    if "food" in q or "menu" in q or "diet" in q:
        return ("Plan food for guests + 10% buffer, label every dish for dietary needs, "
                "and confirm allergens with the caterer. Keep a separate kids' menu "
                "and a sugar-free / allergy-safe option if needed.")
    if "seating" in q:
        return ("Seat families together, keep kids near parents, put elders near "
                "the stage but away from speakers, and keep the dance floor clear. "
                "Use the Seating tab to auto-assign tables by group.")
    return (
        f"Here is a quick plan for your {event_type or 'event'} "
        f"({guests} guests, budget {budget}): 1) Book venue and caterer first. "
        "2) Send invitations and track RSVPs. 3) Confirm vendors 3 days before. "
        "4) Follow the day schedule, and keep a backup plan for weather and vendors. "
        "Ask me about budget, rain, vendors, games, food or seating for a detailed checklist."
    )


def make_qr_png(text: str) -> bytes:
    """QR code PNG bytes for an event / RSVP link. Requires qrcode."""
    import qrcode

    img = qrcode.make(text)
    buf = io.BytesIO()
    img.save(buf, format="PNG")
    return buf.getvalue()


def make_plan_pdf(title: str, lines: list[str]) -> bytes:
    """Simple one-column PDF (reportlab) for a printable plan/checklist."""
    from reportlab.lib.pagesizes import A4
    from reportlab.lib.units import mm
    from reportlab.pdfgen import canvas

    buf = io.BytesIO()
    c = canvas.Canvas(buf, pagesize=A4)
    width, height = A4
    y = height - 20 * mm
    c.setFont("Helvetica-Bold", 16)
    c.drawString(20 * mm, y, title[:80])
    y -= 12 * mm
    c.setFont("Helvetica", 11)
    for line in lines:
        # Very simple wrapping at ~95 characters.
        text = line
        while text:
            chunk, text = text[:95], text[95:]
            if y < 20 * mm:
                c.showPage()
                c.setFont("Helvetica", 11)
                y = height - 20 * mm
            c.drawString(20 * mm, y, chunk)
            y -= 6 * mm
    c.showPage()
    c.save()
    return buf.getvalue()


def make_event_website_html(event_name: str, event_type: str, event_date: str,
                            city: str, schedule: list[tuple[str, str]]) -> str:
    """A single-file event website (HTML) the user can download and host anywhere.

    This is a real, working HTML page — not a hosted URL. Hosting it on a
    custom domain is a separate step (any static host works).
    """
    schedule_html = "".join(f"<li><b>{t}</b>: {d}</li>" for t, d in schedule)
    safe = lambda s: (s or "").replace("&", "&amp;").replace("<", "&lt;").replace(">", "&gt;")
    return f"""<!doctype html><html><head><meta charset='utf-8'>
<title>{safe(event_name)}</title>
<style>body{{font-family:system-ui,sans-serif;max-width:700px;margin:40px auto;padding:0 20px;line-height:1.6}}h1{{color:#3B115F}}</style>
</head><body>
<h1>🎉 {safe(event_name)}</h1>
<p><b>{safe(event_type)}</b> • {safe(event_date)} • {safe(city)}</p>
<h2>Schedule</h2><ul>{schedule_html}</ul>
<p>Please RSVP to the host. Thank you for celebrating with us!</p>
</body></html>"""


def make_collage_png(image_bytes_list: list[bytes]) -> bytes:
    """Grid collage from uploaded photos. Returns PNG bytes."""
    from PIL import Image

    if not image_bytes_list:
        raise ValueError("At least one photo is required for a collage.")
    thumbs = []
    for data in image_bytes_list[:9]:
        im = Image.open(io.BytesIO(data)).convert("RGB")
        im.thumbnail((400, 400))
        thumbs.append(im)
    cols = math.ceil(math.sqrt(len(thumbs)))
    rows = math.ceil(len(thumbs) / cols)
    cell = 400
    collage = Image.new("RGB", (cols * cell, rows * cell), "white")
    for i, im in enumerate(thumbs):
        x = (i % cols) * cell
        y = (i // cols) * cell
        collage.paste(im, (x, y))
    buf = io.BytesIO()
    collage.save(buf, format="PNG")
    return buf.getvalue()
