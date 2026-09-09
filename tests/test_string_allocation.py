from src.inverter_model import Inverter
from src.module_model import PVModule
from src.string_sizing import design_strings


def test_string_design_allocates_exact_module_count_without_fictitious_modules():
    module = PVModule("Demo", 550, 50, 42, 14, 13, -0.28, -0.32, -0.35, 0.05, None, 2.5)
    inverter = Inverter("Inv", 6, 9, 1000, 180, 120, 850, 2, 2, 16, 30, 20, 40)

    design = design_strings(11, module, inverter, 5, 70)

    assert design.valid
    assert sum(sum(mppt) for mppt in design.mppt_string_modules) == 11
    assert design.total_strings == sum(len(mppt) for mppt in design.mppt_string_modules)


def test_string_design_returns_invalid_when_no_integer_configuration_exists():
    module = PVModule("Demo", 550, 50, 42, 14, 13, -0.28, -0.32, -0.35, 0.05, None, 2.5)
    inverter = Inverter("Inv", 6, 9, 250, 180, 240, 245, 1, 1, 16, 30, 20, 40)

    design = design_strings(11, module, inverter, 5, 70)

    assert not design.valid
    assert "Nenhuma configuração" in design.message
