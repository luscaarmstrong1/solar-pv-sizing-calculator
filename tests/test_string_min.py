from src.inverter_model import Inverter
from src.module_model import PVModule, corrected_voltage
from src.string_sizing import min_modules_per_string


def test_nmin_reaches_mppt_minimum_at_hot_condition():
    module = PVModule("Demo", 550, 50, 42, 14, 13, -0.28, -0.32, -0.35, 0.05, None, 2.5)
    inverter = Inverter("Inv", 6, 9, 1000, 180, 160, 850, 2, 2, 16, 30, 20, 40)
    nmin = min_modules_per_string(module, inverter, 70)
    assert nmin * corrected_voltage(module.vmp_v, module.vmp_temp_coeff_pct_c, 70) >= inverter.mppt_min_voltage_v
