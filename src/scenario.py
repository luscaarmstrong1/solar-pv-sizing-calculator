from __future__ import annotations

import json
from pathlib import Path

import yaml

from .consumption import ConsumptionProfile, target_annual_energy_kwh
from .generation import monthly_balance, monthly_generation_kwh
from .inverter_model import Inverter
from .module_model import PVModule
from .pv_sizing import dc_ac_ratio, installed_dc_power_kwp, module_area_m2, module_count, required_pv_power_kwp
from .solar_resource import SolarResource, compound_performance_ratio
from .string_sizing import design_strings
from .validation import validate_system, worst_status


def load_yaml(path: str | Path) -> dict:
    with open(path, "r", encoding="utf-8") as file:
        return yaml.safe_load(file)


def run_scenario(config: dict) -> dict:
    consumption = ConsumptionProfile(config["monthly_consumption_kwh"])
    solar = SolarResource(config["monthly_hsp"])
    losses = config.get("losses", {})
    pr = compound_performance_ratio(losses) if losses else float(config["performance_ratio"])
    target = target_annual_energy_kwh(consumption.annual_kwh, float(config["coverage_target"]))
    required_kwp = required_pv_power_kwp(target, solar.annual_weighted_average_hsp, pr)
    module = PVModule(**config["module"])
    inverter = Inverter(**config["inverter"])
    modules = module_count(required_kwp, module.power_wp)
    dc_kwp = installed_dc_power_kwp(modules, module.power_wp)
    module_area, technical_area = module_area_m2(modules, module.area_m2, float(config.get("occupation_factor", 1.15)))
    generation = monthly_generation_kwh(dc_kwp, solar.monthly_hsp, pr)
    balance = monthly_balance(consumption.monthly_kwh, generation)
    string_design = design_strings(
        modules,
        module,
        inverter,
        float(config["minimum_temperature_c"]),
        float(config.get("maximum_cell_temperature_c", 70.0)),
        float(config.get("max_voltage_utilization_pct", 1.0)),
    )
    validations = validate_system(
        dc_kwp,
        inverter,
        string_design,
        modules,
        sum(generation),
        target,
        float(config.get("dc_ac_min", 0.8)),
        float(config.get("dc_ac_max", 1.35)),
        config.get("available_area_m2"),
        technical_area,
        float(config.get("max_voltage_utilization_pct", 1.0)),
    )
    return {
        "scenario_name": config.get("scenario_name", "Base scenario"),
        "consumption": {
            "annual_kwh": consumption.annual_kwh,
            "average_monthly_kwh": consumption.average_monthly_kwh,
            "average_daily_kwh": consumption.average_daily_kwh,
            "coverage_target": config["coverage_target"],
            "target_annual_kwh": target,
        },
        "resource": {"average_hsp": solar.annual_weighted_average_hsp, "performance_ratio": pr},
        "sizing": {
            "required_pv_power_kwp": required_kwp,
            "module_count": modules,
            "installed_dc_power_kwp": dc_kwp,
            "module_area_m2": module_area,
            "technical_area_m2": technical_area,
            "dc_ac_ratio": dc_ac_ratio(dc_kwp, inverter.ac_power_kw),
            "annual_generation_kwh": sum(generation),
            "annual_coverage_pct": sum(generation) / consumption.annual_kwh,
        },
        "module": module.__dict__,
        "inverter": inverter.__dict__,
        "strings": string_design.__dict__,
        "monthly": balance,
        "validations": [item.__dict__ for item in validations],
        "technical_status": worst_status(validations),
        "warnings": [item.message for item in validations if item.status != "OK"],
    }


def save_results(results: dict, output_dir: str | Path) -> None:
    output_dir = Path(output_dir)
    output_dir.mkdir(parents=True, exist_ok=True)
    (output_dir / "sizing_results.json").write_text(json.dumps(results, indent=2), encoding="utf-8")
    monthly_rows = results["monthly"]
    headers = list(monthly_rows[0].keys())
    lines = [",".join(headers)]
    for row in monthly_rows:
        lines.append(",".join(str(row[key]) for key in headers))
    (output_dir / "monthly_generation.csv").write_text("\n".join(lines), encoding="utf-8")


def render_markdown_report(results: dict) -> str:
    warnings = results["warnings"] or ["Nenhum alerta técnico para os limites preliminares configurados."]
    conclusion = (
        "A configuração preliminar está tecnicamente compatível dentro das verificações configuradas."
        if results["technical_status"] == "OK"
        else "A configuração exige revisão técnica antes de uso porque uma ou mais verificações retornaram atenção ou incompatibilidade."
    )
    strings = results["strings"]
    allocation = []
    for mppt_index, string_modules in enumerate(strings["mppt_string_modules"], start=1):
        if string_modules:
            allocation.append(f"MPPT {mppt_index}: " + ", ".join(f"String {idx + 1}: {modules} módulos" for idx, modules in enumerate(string_modules)))
        else:
            allocation.append(f"MPPT {mppt_index}: sem strings")
    return f"""# Relatório de Pré-Dimensionamento Fotovoltaico

## Dados de Entrada

Cenário: {results["scenario_name"]}

Consumo anual: {results["consumption"]["annual_kwh"]:.0f} kWh
Meta de atendimento: {results["consumption"]["coverage_target"]:.0%}
HSP média ponderada: {results["resource"]["average_hsp"]:.2f} h/dia
Performance Ratio: {results["resource"]["performance_ratio"]:.1%}

## Dimensionamento Energético

Potência FV requerida: {results["sizing"]["required_pv_power_kwp"]:.2f} kWp
Potência CC instalada: {results["sizing"]["installed_dc_power_kwp"]:.2f} kWp
Geração anual estimada: {results["sizing"]["annual_generation_kwh"]:.0f} kWh
Atendimento anual estimado: {results["sizing"]["annual_coverage_pct"]:.1%}

## Arranjo Fotovoltaico

Módulo: {results["module"]["name"]}
Potência do módulo: {results["module"]["power_wp"]:.0f} Wp
Quantidade de módulos: {results["sizing"]["module_count"]}
Área técnica: {results["sizing"]["technical_area_m2"]:.1f} m2

## Inverter

Inversor: {results["inverter"]["name"]}
Potência CA: {results["inverter"]["ac_power_kw"]:.2f} kW
Relação CC/CA: {results["sizing"]["dc_ac_ratio"]:.2f}

## Strings

Alocação:
{chr(10).join(f"- {item}" for item in allocation)}
Total de strings: {strings["total_strings"]}
Voc da string em frio: {strings["voc_string_v"]:.1f} V
Vmp da string em quente: {strings["vmp_string_hot_v"]:.1f} V
Vmp da string em frio: {strings["vmp_string_cold_v"]:.1f} V

## Geração

A geração mensal está disponível em `outputs/monthly_generation.csv`.

## Alertas

{chr(10).join(f"- {warning}" for warning in warnings)}

## Conclusão

{conclusion}

Este é um modelo preliminar de pré-dimensionamento fotovoltaico conectado à rede. Ele não substitui projeto executivo, vistoria de campo, análise estrutural, estudo detalhado de sombreamento, estudo de proteção, aprovação da concessionária, ART ou revisão do engenheiro responsável.
"""
