from src.generation import monthly_generation_kwh


def test_generation_increases_with_power():
    low = sum(monthly_generation_kwh(5, [5] * 12, 0.8))
    high = sum(monthly_generation_kwh(6, [5] * 12, 0.8))
    assert high > low

