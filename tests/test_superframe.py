import pytest

from ieee802154.superframe import SuperframeConfig


def test_base_superframe_at_bo_so_zero() -> None:
    config = SuperframeConfig(0, 0)
    assert config.beacon_interval_s == pytest.approx(0.01536)
    assert config.active_duration_s == pytest.approx(0.01536)
    assert config.duty_cycle == pytest.approx(1.0)


def test_duty_cycle() -> None:
    config = SuperframeConfig(6, 4)
    assert config.duty_cycle == pytest.approx(0.25)


def test_invalid_order_rejected() -> None:
    with pytest.raises(ValueError):
        SuperframeConfig(2, 3)
