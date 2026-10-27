import pytest

from planner import EVENT_TYPES
from planner.budget import BASE_SHARES, allocate_budget, classify_tier


def share(summary, category):
    return next(line.share for line in summary.lines if line.category == category)


@pytest.mark.parametrize("event_type", EVENT_TYPES)
def test_base_shares_sum_to_one(event_type):
    assert sum(BASE_SHARES[event_type]) == pytest.approx(1.0)


@pytest.mark.parametrize("event_type", EVENT_TYPES)
@pytest.mark.parametrize("budget", [1000, 33333.33, 250000, 9_999_999])
def test_amounts_always_add_up_to_budget(make_request, event_type, budget):
    summary = allocate_budget(make_request(event_type=event_type, budget=budget))
    assert sum(line.amount for line in summary.lines) == pytest.approx(budget, abs=0.01)
    assert sum(line.share for line in summary.lines) == pytest.approx(1.0)


def test_dietary_needs_raise_catering_share(make_request):
    plain = allocate_budget(make_request())
    diet = allocate_budget(make_request(dietary=("Vegan", "Halal", "Jain")))
    assert share(diet, "Catering") > share(plain, "Catering")


def test_outdoor_raises_contingency(make_request):
    assert share(allocate_budget(make_request(outdoor=True)), "Contingency") > \
           share(allocate_budget(make_request()), "Contingency")


def test_vibe_changes_split(make_request):
    elegant = allocate_budget(make_request(vibe="Elegant"))
    minimal = allocate_budget(make_request(vibe="Minimalist"))
    assert share(elegant, "Decor") > share(minimal, "Decor")


def test_accessibility_raises_venue_share(make_request):
    assert share(allocate_budget(make_request(accessibility=("Wheelchair access",))), "Venue") > \
           share(allocate_budget(make_request()), "Venue")


@pytest.mark.parametrize("per_head,tier", [(100, "Very tight"), (900, "Tight"), (1500, "Comfortable"), (3000, "Generous")])
def test_tiers(per_head, tier):
    assert classify_tier(per_head, "Birthday") == tier


def test_per_head(make_request):
    assert allocate_budget(make_request(guests=100, budget=50000)).per_head == 500
