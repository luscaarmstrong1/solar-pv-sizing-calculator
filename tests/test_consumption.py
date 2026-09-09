from src.consumption import ConsumptionProfile, target_annual_energy_kwh


def test_consumption_summary_from_12_months():
    profile = ConsumptionProfile([100] * 12)
    assert profile.annual_kwh == 1200
    assert profile.average_monthly_kwh == 100
    assert round(profile.average_daily_kwh, 2) == 3.29


def test_target_annual_energy():
    assert target_annual_energy_kwh(1000, 0.9) == 900

