from ieee802154.network import simulate_network
from ieee802154.superframe import SuperframeConfig


def test_single_device_has_no_collisions() -> None:
    result = simulate_network(
        SuperframeConfig(3, 3),
        devices=1,
        packet_rate_hz=2.0,
        beacons=200,
        seed=4,
    )
    assert result["collided_attempts"] == 0
    assert result["delivered"] > 0
