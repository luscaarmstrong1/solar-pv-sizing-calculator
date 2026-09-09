import copy
from pathlib import Path

from src.scenario import load_yaml, run_scenario


def test_inverter_max_dc_power_is_preserved_as_datasheet_limit():
    project_root = Path(__file__).resolve().parents[1]
    config = load_yaml(project_root / "config" / "default_scenario.yaml")
    config = copy.deepcopy(config)
    config["inverter"]["max_dc_power_kwp"] = 4.0

    result = run_scenario(config)

    assert result["inverter"]["max_dc_power_kwp"] == 4.0
    assert result["technical_status"] == "INCOMPATIBLE"
