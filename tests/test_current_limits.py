from src.inverter_model import Inverter
from src.module_model import PVModule
from src.string_sizing import design_strings


def test_parallel_strings_raise_mppt_current():
    module = PVModule("Demo", 550, 50, 42, 14, 13, -0.28, -0.32, -0.35, 0.05, None, 2.5)
    inverter = Inverter("Inv", 6, 20, 1000, 180, 160, 850, 1, 3, 16, 60, 20, 80)
    design = design_strings(30, module, inverter, 5)
    assert max(design.isc_per_mppt_a) > module.isc_a
