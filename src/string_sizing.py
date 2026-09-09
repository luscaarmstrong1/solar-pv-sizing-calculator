from __future__ import annotations

import math
from dataclasses import dataclass

from .inverter_model import Inverter
from .module_model import PVModule, corrected_current, corrected_voltage


@dataclass(frozen=True)
class StringDesign:
    modules_per_string: int | None
    total_strings: int
    strings_per_mppt: list[int]
    mppt_string_modules: list[list[int]]
    voc_string_v: float
    vmp_string_hot_v: float
    vmp_string_cold_v: float
    imp_per_mppt_a: list[float]
    isc_per_mppt_a: list[float]
    max_imp_per_input_a: float
    max_isc_per_input_a: float
    nmax_modules_per_string: int
    nmin_modules_per_string: int
    valid: bool
    message: str


def max_modules_per_string(module: PVModule, inverter: Inverter, minimum_temperature_c: float, voltage_margin: float = 1.0) -> int:
    if not 0 < voltage_margin <= 1:
        raise ValueError("voltage margin must be greater than zero and at most one.")
    voc_cold = corrected_voltage(module.voc_v, module.voc_temp_coeff_pct_c, minimum_temperature_c)
    return math.floor((inverter.max_dc_voltage_v * voltage_margin) / voc_cold)


def min_modules_per_string(module: PVModule, inverter: Inverter, maximum_cell_temperature_c: float) -> int:
    vmp_hot = corrected_voltage(module.vmp_v, module.vmp_temp_coeff_pct_c, maximum_cell_temperature_c)
    return math.ceil(inverter.mppt_min_voltage_v / vmp_hot)


def distribute_strings(total_strings: int, mppt_count: int, inputs_per_mppt: int) -> list[int]:
    if total_strings < 1:
        raise ValueError("at least one string is required.")
    capacity = mppt_count * inputs_per_mppt
    if total_strings > capacity:
        # Still return a distribution so validation can report the exact overload.
        distribution = [inputs_per_mppt] * mppt_count
        overflow = total_strings - capacity
        distribution[-1] += overflow
        return distribution
    result = [0] * mppt_count
    for idx in range(total_strings):
        result[idx % mppt_count] += 1
    return result


def design_strings(
    module_count: int,
    module: PVModule,
    inverter: Inverter,
    minimum_temperature_c: float,
    maximum_cell_temperature_c: float = 70.0,
    max_voltage_utilization_pct: float = 1.0,
) -> StringDesign:
    nmax = max_modules_per_string(module, inverter, minimum_temperature_c, max_voltage_utilization_pct)
    nmin = min_modules_per_string(module, inverter, maximum_cell_temperature_c)

    voc_cold_module = corrected_voltage(module.voc_v, module.voc_temp_coeff_pct_c, minimum_temperature_c)
    vmp_hot_module = corrected_voltage(module.vmp_v, module.vmp_temp_coeff_pct_c, maximum_cell_temperature_c)
    vmp_cold_module = corrected_voltage(module.vmp_v, module.vmp_temp_coeff_pct_c, minimum_temperature_c)
    imp_module = corrected_current(module.imp_a, module.effective_imp_temp_coeff_pct_c, maximum_cell_temperature_c)
    isc_module = corrected_current(module.isc_a, module.isc_temp_coeff_pct_c, maximum_cell_temperature_c)

    def invalid(message: str) -> StringDesign:
        return StringDesign(
            modules_per_string=None,
            total_strings=0,
            strings_per_mppt=[0] * inverter.mppt_count,
            mppt_string_modules=[[] for _ in range(inverter.mppt_count)],
            voc_string_v=0,
            vmp_string_hot_v=0,
            vmp_string_cold_v=0,
            imp_per_mppt_a=[0] * inverter.mppt_count,
            isc_per_mppt_a=[0] * inverter.mppt_count,
            max_imp_per_input_a=0,
            max_isc_per_input_a=0,
            nmax_modules_per_string=nmax,
            nmin_modules_per_string=nmin,
            valid=False,
            message=message,
        )

    if module_count < 1:
        return invalid("Nenhum módulo informado para alocação.")
    if nmax < nmin:
        return invalid("Nenhuma configuração de strings compatível encontrada para os parâmetros informados.")

    max_strings = inverter.mppt_count * inverter.inputs_per_mppt
    candidates: list[tuple[tuple[float, ...], list[list[int]]]] = []

    def search(mppt_index: int, remaining_modules: int, allocation: list[list[int]]) -> None:
        if mppt_index == inverter.mppt_count:
            if remaining_modules == 0 and any(allocation):
                flat = [mods for mppt in allocation for mods in mppt]
                if len(flat) <= max_strings:
                    avg = module_count / len(flat)
                    mppt_totals = [sum(mppt) for mppt in allocation]
                    active_totals = [value for value in mppt_totals if value > 0]
                    mppt_balance = max(active_totals) - min(active_totals) if len(active_totals) > 1 else 0
                    voltage_mid = (inverter.mppt_min_voltage_v + inverter.mppt_max_voltage_v) / 2
                    voltage_deviation = sum(abs((mods * vmp_hot_module) - voltage_mid) for mods in flat) / len(flat)
                    asymmetry = max(flat) - min(flat)
                    score = (
                        mppt_balance,
                        asymmetry,
                        voltage_deviation,
                        len(flat),
                        sum(abs(mods - avg) for mods in flat),
                    )
                    candidates.append((score, [list(mppt) for mppt in allocation]))
            return

        max_local_strings = min(inverter.inputs_per_mppt, remaining_modules // nmin if nmin > 0 else 0)
        options: list[list[int]] = [[]]
        for string_count in range(1, max_local_strings + 1):
            for modules_per_string in range(nmin, nmax + 1):
                total = string_count * modules_per_string
                if total <= remaining_modules:
                    options.append([modules_per_string] * string_count)
        options.sort(key=lambda item: (len(item) == 0, abs(sum(item) - remaining_modules / max(1, inverter.mppt_count - mppt_index)), len(item)))
        for option in options:
            allocation.append(option)
            search(mppt_index + 1, remaining_modules - sum(option), allocation)
            allocation.pop()

    search(0, module_count, [])
    if not candidates:
        return invalid("Nenhuma configuração de strings compatível encontrada para os parâmetros informados.")

    allocation = min(candidates, key=lambda item: item[0])[1]
    flat_modules = [mods for mppt in allocation for mods in mppt]
    total_strings = len(flat_modules)
    strings_per_mppt = [len(mppt) for mppt in allocation]
    max_modules = max(flat_modules)
    max_strings_on_mppt = max(strings_per_mppt)
    return StringDesign(
        modules_per_string=flat_modules[0] if len(set(flat_modules)) == 1 else None,
        total_strings=total_strings,
        strings_per_mppt=strings_per_mppt,
        mppt_string_modules=allocation,
        voc_string_v=max_modules * voc_cold_module,
        vmp_string_hot_v=max_modules * vmp_hot_module,
        vmp_string_cold_v=max_modules * vmp_cold_module,
        imp_per_mppt_a=[strings * imp_module for strings in strings_per_mppt],
        isc_per_mppt_a=[strings * isc_module for strings in strings_per_mppt],
        max_imp_per_input_a=imp_module,
        max_isc_per_input_a=isc_module,
        nmax_modules_per_string=nmax,
        nmin_modules_per_string=nmin,
        valid=True,
        message="Configuração de strings compatível encontrada com alocação inteira dos módulos.",
    )
