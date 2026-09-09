from src.module_model import corrected_voltage


def test_voc_increases_when_temperature_drops_with_negative_coefficient():
    assert corrected_voltage(50, -0.28, 5) > 50


def test_vmp_decreases_when_cell_temperature_rises_with_negative_coefficient():
    assert corrected_voltage(41.7, -0.32, 70) < 41.7


def test_vmp_reference_calculation_uses_vmp_coefficient():
    expected = 41.7 * (1 + (-0.32 / 100) * (70 - 25))
    assert corrected_voltage(41.7, -0.32, 70) == expected
