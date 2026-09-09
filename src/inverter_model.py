from __future__ import annotations

from dataclasses import dataclass


@dataclass(frozen=True)
class Inverter:
    name: str
    ac_power_kw: float
    max_dc_power_kwp: float
    max_dc_voltage_v: float
    startup_voltage_v: float
    mppt_min_voltage_v: float
    mppt_max_voltage_v: float
    mppt_count: int
    inputs_per_mppt: int
    max_operating_current_per_input_a: float | None = None
    max_operating_current_per_mppt_a: float | None = None
    max_short_circuit_current_per_input_a: float | None = None
    max_short_circuit_current_per_mppt_a: float | None = None

    def __post_init__(self) -> None:
        if self.ac_power_kw <= 0:
            raise ValueError("inverter AC power must be greater than zero.")
        if self.max_dc_power_kwp <= 0:
            raise ValueError("maximum DC power must be greater than zero.")
        if self.max_dc_voltage_v <= self.mppt_max_voltage_v:
            raise ValueError("maximum DC voltage must be greater than MPPT maximum voltage.")
        if self.mppt_min_voltage_v <= 0 or self.mppt_max_voltage_v <= self.mppt_min_voltage_v:
            raise ValueError("MPPT voltage window is invalid.")
        if self.startup_voltage_v <= 0:
            raise ValueError("startup voltage must be greater than zero.")
        if self.mppt_count < 1 or self.inputs_per_mppt < 1:
            raise ValueError("MPPT count and inputs per MPPT must be positive integers.")
        current_limits = [
            self.max_operating_current_per_input_a,
            self.max_operating_current_per_mppt_a,
            self.max_short_circuit_current_per_input_a,
            self.max_short_circuit_current_per_mppt_a,
        ]
        if any(value is not None and value <= 0 for value in current_limits):
            raise ValueError("current limits must be greater than zero when provided.")
