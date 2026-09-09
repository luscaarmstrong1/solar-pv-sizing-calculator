from __future__ import annotations

from pathlib import Path
import sys

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

from src.scenario import load_yaml, render_markdown_report, run_scenario, save_results



def main() -> None:
    config = load_yaml(ROOT / "config" / "default_scenario.yaml")
    results = run_scenario(config)
    save_results(results, ROOT / "outputs")
    (ROOT / "outputs" / "sizing_report.md").write_text(render_markdown_report(results), encoding="utf-8")
    print(f"Cenário: {results['scenario_name']}")
    print(f"Potência FV requerida: {results['sizing']['required_pv_power_kwp']:.2f} kWp")
    print(f"Módulos: {results['sizing']['module_count']}")
    print(f"Potência CC instalada: {results['sizing']['installed_dc_power_kwp']:.2f} kWp")
    print(f"Relação CC/CA: {results['sizing']['dc_ac_ratio']:.2f}")
    print(f"Geração anual: {results['sizing']['annual_generation_kwh']:.0f} kWh")
    print(f"Status técnico: {results['technical_status']}")


if __name__ == "__main__":
    main()
