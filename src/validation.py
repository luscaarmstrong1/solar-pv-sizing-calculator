from __future__ import annotations

from dataclasses import dataclass

from .inverter_model import Inverter
from .pv_sizing import dc_ac_ratio
from .string_sizing import StringDesign


@dataclass(frozen=True)
class ValidationItem:
    item: str
    status: str
    message: str


def worst_status(items: list[ValidationItem]) -> str:
    if any(item.status == "INCOMPATIBLE" for item in items):
        return "INCOMPATIBLE"
    if any(item.status == "ATTENTION" for item in items):
        return "ATTENTION"
    return "OK"


def validate_system(
    dc_power_kwp: float,
    inverter: Inverter,
    string_design: StringDesign,
    module_count: int,
    generation_annual_kwh: float,
    target_annual_kwh: float,
    dc_ac_min: float = 0.8,
    dc_ac_max: float = 1.35,
    available_area_m2: float | None = None,
    required_area_m2: float | None = None,
    max_voltage_utilization_pct: float = 1.0,
) -> list[ValidationItem]:
    items: list[ValidationItem] = []
    ratio = dc_ac_ratio(dc_power_kwp, inverter.ac_power_kw)
    items.append(
        ValidationItem(
            "DC power",
            "OK" if dc_power_kwp <= inverter.max_dc_power_kwp else "INCOMPATIBLE",
            f"Potência CC instalada {dc_power_kwp:.2f} kWp versus limite do inversor {inverter.max_dc_power_kwp:.2f} kWp.",
        )
    )
    items.append(
        ValidationItem(
            "DC/AC ratio",
            "OK" if dc_ac_min <= ratio <= dc_ac_max else "ATTENTION",
            f"Relação CC/CA {ratio:.2f}; faixa preliminar configurada de {dc_ac_min:.2f} a {dc_ac_max:.2f}.",
        )
    )
    items.append(
        ValidationItem(
            "String maximum voltage",
            "OK" if string_design.voc_string_v <= inverter.max_dc_voltage_v * max_voltage_utilization_pct else "INCOMPATIBLE",
            f"Voc da string em frio {string_design.voc_string_v:.1f} V versus limite configurado {inverter.max_dc_voltage_v * max_voltage_utilization_pct:.1f} V.",
        )
    )
    items.append(
        ValidationItem(
            "Startup voltage",
            "OK" if string_design.vmp_string_hot_v >= inverter.startup_voltage_v else "ATTENTION",
            f"Vmp da string em quente {string_design.vmp_string_hot_v:.1f} V versus tensão de partida {inverter.startup_voltage_v:.1f} V.",
        )
    )
    items.append(
        ValidationItem(
            "MPPT minimum voltage",
            "OK" if string_design.vmp_string_hot_v >= inverter.mppt_min_voltage_v else "INCOMPATIBLE",
            f"Vmp da string em quente {string_design.vmp_string_hot_v:.1f} V versus tensão mínima MPPT {inverter.mppt_min_voltage_v:.1f} V.",
        )
    )
    items.append(
        ValidationItem(
            "MPPT maximum voltage",
            "OK" if string_design.vmp_string_cold_v <= inverter.mppt_max_voltage_v else "INCOMPATIBLE",
            f"Vmp da string em frio {string_design.vmp_string_cold_v:.1f} V versus tensão máxima MPPT {inverter.mppt_max_voltage_v:.1f} V.",
        )
    )
    max_imp = max(string_design.imp_per_mppt_a)
    max_isc = max(string_design.isc_per_mppt_a)
    mppt_imp_limit = inverter.max_operating_current_per_mppt_a
    mppt_isc_limit = inverter.max_short_circuit_current_per_mppt_a
    input_imp_limit = inverter.max_operating_current_per_input_a
    input_isc_limit = inverter.max_short_circuit_current_per_input_a
    if input_imp_limit is not None:
        items.append(
            ValidationItem(
                "Input operating current",
                "OK" if string_design.max_imp_per_input_a <= input_imp_limit else "INCOMPATIBLE",
                f"Imp máxima por entrada {string_design.max_imp_per_input_a:.1f} A versus limite {input_imp_limit:.1f} A.",
            )
        )
    if input_isc_limit is not None:
        items.append(
            ValidationItem(
                "Input short-circuit current",
                "OK" if string_design.max_isc_per_input_a <= input_isc_limit else "INCOMPATIBLE",
                f"Isc máxima por entrada {string_design.max_isc_per_input_a:.1f} A versus limite {input_isc_limit:.1f} A.",
            )
        )
    items.append(
        ValidationItem(
            "MPPT operating current",
            "OK" if mppt_imp_limit is None or max_imp <= mppt_imp_limit else "INCOMPATIBLE",
            f"Imp máxima por MPPT {max_imp:.1f} A versus limite {mppt_imp_limit if mppt_imp_limit is not None else 'não informado'}.",
        )
    )
    items.append(
        ValidationItem(
            "MPPT short-circuit current",
            "OK" if mppt_isc_limit is None or max_isc <= mppt_isc_limit else "INCOMPATIBLE",
            f"Isc máxima por MPPT {max_isc:.1f} A versus limite {mppt_isc_limit if mppt_isc_limit is not None else 'não informado'}.",
        )
    )
    total_input_capacity = inverter.mppt_count * inverter.inputs_per_mppt
    items.append(
        ValidationItem(
            "Available inputs",
            "OK" if string_design.total_strings <= total_input_capacity else "INCOMPATIBLE",
            f"{string_design.total_strings} strings necessárias versus {total_input_capacity} entradas disponíveis.",
        )
    )
    items.append(
        ValidationItem(
            "Module allocation",
            "OK" if sum(sum(mppt) for mppt in string_design.mppt_string_modules) == module_count else "INCOMPATIBLE",
            f"{module_count} módulos alocados exatamente em {string_design.total_strings} strings.",
        )
    )
    items.append(
        ValidationItem(
            "Energy target",
            "OK" if generation_annual_kwh >= target_annual_kwh else "ATTENTION",
            f"Geração anual {generation_annual_kwh:.0f} kWh versus meta {target_annual_kwh:.0f} kWh.",
        )
    )
    if available_area_m2 is not None and required_area_m2 is not None:
        items.append(
            ValidationItem(
                "Available area",
                "OK" if available_area_m2 >= required_area_m2 else "INCOMPATIBLE",
                f"Área técnica necessária {required_area_m2:.1f} m² versus área disponível {available_area_m2:.1f} m².",
            )
        )
    return items
    if not string_design.valid:
        items.append(ValidationItem("String allocation", "INCOMPATIBLE", string_design.message))
        return items
