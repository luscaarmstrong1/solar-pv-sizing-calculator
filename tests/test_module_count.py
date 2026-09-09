from src.pv_sizing import installed_dc_power_kwp, module_count


def test_module_count_rounds_up():
    assert module_count(5.01, 550) == 10


def test_installed_power_equals_modules_times_wp():
    assert installed_dc_power_kwp(10, 550) == 5.5

