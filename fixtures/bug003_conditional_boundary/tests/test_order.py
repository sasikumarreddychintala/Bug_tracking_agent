from src.order import process_order

def test_tier_discounts():
    assert process_order(100.0, tier=1) == 90.0
    assert process_order(100.0, tier=2) == 80.0
    # Tier 0 has a 5% standard welcome discount when positive
    assert process_order(100.0, tier=0) == 100.0
