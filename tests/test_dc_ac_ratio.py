from src.pv_sizing import dc_ac_ratio


def test_dc_ac_ratio():
    assert dc_ac_ratio(7.2, 6) == 1.2

