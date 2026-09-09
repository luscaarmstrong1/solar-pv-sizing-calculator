from __future__ import annotations

from dataclasses import dataclass

from .consumption import DAYS_IN_MONTH


@dataclass(frozen=True)
class SolarResource:
    monthly_hsp: list[float]

    def __post_init__(self) -> None:
        if len(self.monthly_hsp) != 12:
            raise ValueError("monthly_hsp must contain 12 values.")
        if any(value <= 0 for value in self.monthly_hsp):
            raise ValueError("all HSP values must be greater than zero.")

    @classmethod
    def from_average_hsp(cls, average_hsp: float) -> "SolarResource":
        if average_hsp <= 0:
            raise ValueError("average HSP must be greater than zero.")
        return cls([float(average_hsp)] * 12)

    @property
    def annual_weighted_average_hsp(self) -> float:
        return sum(hsp * days for hsp, days in zip(self.monthly_hsp, DAYS_IN_MONTH)) / 365


def compound_performance_ratio(losses: dict[str, float]) -> float:
    """Return PR from fractional losses, e.g. 0.05 for 5%."""
    pr = 1.0
    for name, loss in losses.items():
        if not 0 <= loss < 1:
            raise ValueError(f"loss '{name}' must be between 0 and 100%.")
        pr *= 1 - loss
    return pr

