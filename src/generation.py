from __future__ import annotations

from .consumption import DAYS_IN_MONTH, MONTHS


def monthly_generation_kwh(dc_power_kwp: float, monthly_hsp: list[float], performance_ratio: float) -> list[float]:
    if dc_power_kwp <= 0:
        raise ValueError("DC power must be greater than zero.")
    if len(monthly_hsp) != 12:
        raise ValueError("monthly_hsp must contain 12 values.")
    if any(hsp <= 0 for hsp in monthly_hsp):
        raise ValueError("all HSP values must be greater than zero.")
    if not 0 < performance_ratio <= 1:
        raise ValueError("performance ratio must be greater than zero and at most one.")
    return [dc_power_kwp * hsp * days * performance_ratio for hsp, days in zip(monthly_hsp, DAYS_IN_MONTH)]


def monthly_balance(monthly_consumption_kwh: list[float], monthly_generation: list[float]) -> list[dict[str, float | str]]:
    if len(monthly_consumption_kwh) != 12 or len(monthly_generation) != 12:
        raise ValueError("monthly consumption and generation must contain 12 values.")
    rows = []
    for month, consumption, generation in zip(MONTHS, monthly_consumption_kwh, monthly_generation):
        surplus = max(generation - consumption, 0)
        deficit = max(consumption - generation, 0)
        coverage = generation / consumption if consumption > 0 else 0
        rows.append(
            {
                "month": month,
                "consumption_kwh": consumption,
                "generation_kwh": generation,
                "difference_kwh": generation - consumption,
                "coverage_pct": coverage,
                "surplus_kwh": surplus,
                "deficit_kwh": deficit,
            }
        )
    return rows

