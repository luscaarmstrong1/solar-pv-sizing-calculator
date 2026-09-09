from __future__ import annotations

from dataclasses import dataclass


@dataclass(frozen=True)
class PVModule:
    name: str
    power_wp: float
    voc_v: float
    vmp_v: float
    isc_a: float
    imp_a: float
    voc_temp_coeff_pct_c: float
    vmp_temp_coeff_pct_c: float
    pmax_temp_coeff_pct_c: float
    isc_temp_coeff_pct_c: float
    imp_temp_coeff_pct_c: float | None
    area_m2: float
    noct_c: float | None = None

    def __post_init__(self) -> None:
        if self.power_wp <= 0:
            raise ValueError("module power must be greater than zero.")
        if self.voc_v <= self.vmp_v:
            raise ValueError("module Voc must be greater than Vmp.")
        if self.isc_a < self.imp_a:
            raise ValueError("module Isc must be greater than or equal to Imp.")
        if self.area_m2 <= 0:
            raise ValueError("module area must be greater than zero.")

    @property
    def effective_imp_temp_coeff_pct_c(self) -> float:
        return 0.0 if self.imp_temp_coeff_pct_c is None else self.imp_temp_coeff_pct_c


def corrected_voltage(stc_voltage: float, temp_coeff_pct_c: float, cell_temperature_c: float, stc_temperature_c: float = 25.0) -> float:
    """Temperature-correct voltage using coefficient convention %/degC."""
    if stc_voltage <= 0:
        raise ValueError("STC voltage must be greater than zero.")
    return stc_voltage * (1 + (temp_coeff_pct_c / 100) * (cell_temperature_c - stc_temperature_c))


def corrected_current(stc_current: float, temp_coeff_pct_c: float, cell_temperature_c: float, stc_temperature_c: float = 25.0) -> float:
    if stc_current <= 0:
        raise ValueError("STC current must be greater than zero.")
    return stc_current * (1 + (temp_coeff_pct_c / 100) * (cell_temperature_c - stc_temperature_c))
