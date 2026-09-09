from src.pv_sizing import required_pv_power_kwp


def test_required_power_from_annual_energy():
    assert round(required_pv_power_kwp(7300, 5, 0.8), 2) == 5.00

