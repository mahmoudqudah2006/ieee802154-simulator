from __future__ import annotations

from dataclasses import dataclass

A_BASE_SUPERFRAME_DURATION_SYMBOLS = 960
A_NUM_SUPERFRAME_SLOTS = 16
DEFAULT_SYMBOL_RATE = 62_500.0


@dataclass(frozen=True, slots=True)
class SuperframeConfig:
    beacon_order: int
    superframe_order: int
    symbol_rate: float = DEFAULT_SYMBOL_RATE

    def __post_init__(self) -> None:
        if not 0 <= self.superframe_order <= self.beacon_order <= 14:
            raise ValueError("orders must satisfy 0 <= SO <= BO <= 14")
        if self.symbol_rate <= 0:
            raise ValueError("symbol_rate must be positive")

    @property
    def beacon_interval_s(self) -> float:
        return A_BASE_SUPERFRAME_DURATION_SYMBOLS * (2**self.beacon_order) / self.symbol_rate

    @property
    def active_duration_s(self) -> float:
        return A_BASE_SUPERFRAME_DURATION_SYMBOLS * (2**self.superframe_order) / self.symbol_rate

    @property
    def inactive_duration_s(self) -> float:
        return self.beacon_interval_s - self.active_duration_s

    @property
    def slot_duration_s(self) -> float:
        return self.active_duration_s / A_NUM_SUPERFRAME_SLOTS

    @property
    def duty_cycle(self) -> float:
        return self.active_duration_s / self.beacon_interval_s

    def to_dict(self) -> dict[str, float | int]:
        return {
            "beacon_order": self.beacon_order,
            "superframe_order": self.superframe_order,
            "beacon_interval_ms": self.beacon_interval_s * 1000.0,
            "active_duration_ms": self.active_duration_s * 1000.0,
            "inactive_duration_ms": self.inactive_duration_s * 1000.0,
            "slot_duration_ms": self.slot_duration_s * 1000.0,
            "duty_cycle": self.duty_cycle,
        }
