from __future__ import annotations

import copy
from pathlib import Path
import sys

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

from src.scenario import load_yaml, run_scenario



def scenario_variant(name: str, overrides: dict) -> dict:
    base = load_yaml(ROOT / "config" / "default_scenario.yaml")
    merged = copy.deepcopy(base)
    merged["scenario_name"] = name
    for key, value in overrides.items():
        if isinstance(value, dict) and isinstance(merged.get(key), dict):
            merged[key].update(value)
        else:
            merged[key] = value
    return merged


def main() -> None:
    cases = [
        scenario_variant("Caso A - Residencial", {}),
        scenario_variant("Caso B - Comercial", {"monthly_consumption_kwh": [1800] * 12, "inverter": {"ac_power_kw": 20, "max_dc_power_kwp": 30}}),
        scenario_variant("Caso C - Pequeno industrial", {"monthly_consumption_kwh": [5200] * 12, "inverter": {"ac_power_kw": 50, "max_dc_power_kwp": 75}}),
        scenario_variant("Caso D - Inversor incompatível", {"inverter": {"ac_power_kw": 3, "max_dc_power_kwp": 3.6}}),
        scenario_variant("Caso E - Tensão de string excessiva", {"inverter": {"max_dc_voltage_v": 220, "mppt_min_voltage_v": 200, "mppt_max_voltage_v": 210}}),
        scenario_variant("Caso F - Corrente MPPT excessiva", {"inverter": {"max_operating_current_per_mppt_a": 10, "max_short_circuit_current_per_mppt_a": 12}}),
    ]
    for case in cases:
        result = run_scenario(case)
        print(f"{result['scenario_name']}: {result['technical_status']} | {len(result['warnings'])} alerta(s)")


if __name__ == "__main__":
    main()
