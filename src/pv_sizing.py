from __future__ import annotations

import math


def required_pv_power_kwp(target_annual_kwh: float, average_hsp: float, performance_ratio: float) -> float:
    if target_annual_kwh <= 0:
        raise ValueError("target annual energy must be greater than zero.")
    if average_hsp <= 0:
        raise ValueError("HSP must be greater than zero.")
    if not 0 < performance_ratio <= 1:
        raise ValueError("performance ratio must be greater than zero and at most one.")
    return target_annual_kwh / (average_hsp * 365 * performance_ratio)


def module_count(required_power_kwp: float, module_power_wp: float) -> int:
    if required_power_kwp <= 0:
        raise ValueError("required PV power must be greater than zero.")
    if module_power_wp <= 0:
        raise ValueError("module power must be greater than zero.")
    return math.ceil(required_power_kwp * 1000 / module_power_wp)


def installed_dc_power_kwp(number_of_modules: int, module_power_wp: float) -> float:
    if number_of_modules < 1:
        raise ValueError("at least one module is required.")
    if module_power_wp <= 0:
        raise ValueError("module power must be greater than zero.")
    return number_of_modules * module_power_wp / 1000


def dc_ac_ratio(dc_power_kwp: float, inverter_power_kw: float) -> float:
    if dc_power_kwp <= 0:
        raise ValueError("DC power must be greater than zero.")
    if inverter_power_kw <= 0:
        raise ValueError("inverter AC power must be greater than zero.")
    return dc_power_kwp / inverter_power_kw


def module_area_m2(number_of_modules: int, module_area_m2_value: float, occupation_factor: float = 1.15) -> tuple[float, float]:
    if number_of_modules < 1:
        raise ValueError("at least one module is required.")
    if module_area_m2_value <= 0:
        raise ValueError("module area must be greater than zero.")
    if occupation_factor < 1:
        raise ValueError("occupation factor should be at least 1.")
    module_area = number_of_modules * module_area_m2_value
    return module_area, module_area * occupation_factor

