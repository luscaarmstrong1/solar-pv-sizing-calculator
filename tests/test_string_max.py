from src.inverter_model import Inverter
from src.module_model import PVModule, corrected_voltage
from src.string_sizing import max_modules_per_string


def test_nmax_never_exceeds_inverter_vdc_max():
    module = PVModule("Demo", 550, 50, 42, 14, 13, -0.28, -0.32, -0.35, 0.05, None, 2.5)
    inverter = Inverter("Inv", 6, 9, 1000, 180, 160, 850, 2, 2, 16, 30, 20, 40)
    nmax = max_modules_per_string(module, inverter, 0)
    assert nmax * corrected_voltage(module.voc_v, module.voc_temp_coeff_pct_c, 0) <= inverter.max_dc_voltage_v
