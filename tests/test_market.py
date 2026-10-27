"""Tests for market helpers: seating, lucky draw, budget tips, QR, PDF, website HTML, collage."""

from planner.market import (ai_assistant_reply, budget_optimisation,
                            lucky_draw_winner, make_collage_png,
                            make_event_website_html, make_plan_pdf,
                            make_qr_png, seating_assign, whatsapp_link)


def test_seating_keeps_groups_and_respects_size():
    guests = [{"Name": f"Family{i}", "Group": "Family"} for i in range(5)]
    guests += [{"Name": f"Friend{i}", "Group": "Friends"} for i in range(5)]
    tables = seating_assign(guests, seats_per_table=8)
    assert sum(len(v) for v in tables.values()) == 10
    assert all(len(v) <= 8 for v in tables.values())


def test_lucky_draw_and_empty():
    assert lucky_draw_winner(["Asha", "Ravi"], seed=1) in ("Asha", "Ravi")
    assert lucky_draw_winner([]) is None


def test_budget_optimisation_flags_overrun():
    tips = budget_optimisation({"Venue": 100.0}, {"Venue": 150.0})
    assert any("Venue" in t and "over" in t for t in tips)
    assert budget_optimisation({"Venue": 100.0}, {"Venue": 50.0})


def test_whatsapp_link_encodes_message():
    link = whatsapp_link("", "Hello world")
    assert link.startswith("https://wa.me/")
    assert "Hello%20world" in link


def test_qr_pdf_website_and_collage_are_real_bytes():
    assert make_qr_png("Test event")[:8] == b"\x89PNG\r\n\x1a\n"
    assert make_plan_pdf("Plan", ["Task 1", "Task 2"])[:5] == b"%PDF-"
    html = make_event_website_html("Ava's Birthday", "Birthday", "2026-11-15", "Toronto", [("Welcome", "Arrive")])
    assert "Ava's Birthday" in html and "Welcome" in html
    # A tiny red PNG as a fake photo, for the collage test.
    from PIL import Image
    import io
    buf = io.BytesIO()
    Image.new("RGB", (10, 10), "red").save(buf, format="PNG")
    collage = make_collage_png([buf.getvalue(), buf.getvalue()])
    assert collage[:8] == b"\x89PNG\r\n\x1a\n"


def test_ai_assistant_answers_common_questions():
    assert "tent" in ai_assistant_reply("What if it rains?", "Birthday", 50, 800).lower()
    assert "guest list" in ai_assistant_reply("How do I save budget?", "Birthday", 50, 800).lower()
