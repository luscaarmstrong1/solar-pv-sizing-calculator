from __future__ import annotations

from dataclasses import dataclass


MONTHS = [
    "Janeiro",
    "Fevereiro",
    "Março",
    "Abril",
    "Maio",
    "Junho",
    "Julho",
    "Agosto",
    "Setembro",
    "Outubro",
    "Novembro",
    "Dezembro",
]

DAYS_IN_MONTH = [31, 28, 31, 30, 31, 30, 31, 31, 30, 31, 30, 31]


@dataclass(frozen=True)
class ConsumptionProfile:
    monthly_kwh: list[float]

    def __post_init__(self) -> None:
        if len(self.monthly_kwh) != 12:
            raise ValueError("monthly_kwh deve conter 12 valores.")
        if any(value < 0 for value in self.monthly_kwh):
            raise ValueError("os consumos mensais não podem ser negativos.")
        if sum(self.monthly_kwh) <= 0:
            raise ValueError("o consumo anual deve ser maior que zero.")

    @classmethod
    def from_average_monthly(cls, average_monthly_kwh: float) -> "ConsumptionProfile":
        if average_monthly_kwh <= 0:
            raise ValueError("o consumo médio mensal deve ser maior que zero.")
        return cls([float(average_monthly_kwh)] * 12)

    @property
    def annual_kwh(self) -> float:
        return sum(self.monthly_kwh)

    @property
    def average_monthly_kwh(self) -> float:
        return self.annual_kwh / 12

    @property
    def average_daily_kwh(self) -> float:
        return self.annual_kwh / 365


def target_annual_energy_kwh(annual_consumption_kwh: float, coverage_target: float) -> float:
    if annual_consumption_kwh <= 0:
        raise ValueError("o consumo anual deve ser maior que zero.")
    if not 0 < coverage_target <= 1.5:
        raise ValueError("a meta de atendimento deve ficar entre 0 e 150%.")
    return annual_consumption_kwh * coverage_target
