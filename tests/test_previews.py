"""Mock previews: section exists, labels present, no password/card inputs."""
from pathlib import Path
APP = Path(__file__).resolve().parents[1] / "app.py"
TEXT = APP.read_text()

def test_previews_section_listed():
    assert '"Previews (Mock)"' in TEXT

def test_every_preview_labelled_mock():
    for label in ("Login / Account — MOCK PREVIEW", "Checkout & Payments — MOCK PREVIEW",
                  "Vendor Booking — MOCK PREVIEW", "3D Floor Plan — MOCK PREVIEW",
                  "Live Multi-user Collaboration — MOCK PREVIEW",
                  "Email / SMS Notifications — MOCK PREVIEW", "Admin Dashboard — MOCK PREVIEW"):
        assert label in TEXT, label

def test_no_real_password_or_card_input_in_previews():
    # The previews function must not contain a password or card input widget.
    start = TEXT.index("def render_previews()")
    end = TEXT.index("def main()", start)
    body = TEXT[start:end]
    assert "type=\"password\"" not in body
    assert "card number" not in body.lower().replace("no card details", "")
    assert "disabled=True" in body
