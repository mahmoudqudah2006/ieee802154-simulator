from __future__ import annotations

from collections import deque
from typing import Any

import numpy as np

from .superframe import SuperframeConfig


def simulate_network(
    config: SuperframeConfig,
    *,
    devices: int = 20,
    packet_rate_hz: float = 1.0,
    beacons: int = 1000,
    contention_opportunities: int = 32,
    max_retries: int = 3,
    packet_bytes: int = 80,
    phy_rate_bps: float = 250_000.0,
    tx_power_mw: float = 52.0,
    idle_power_mw: float = 35.0,
    sleep_power_mw: float = 0.05,
    seed: int = 7,
) -> dict[str, Any]:
    if devices <= 0 or beacons <= 0 or contention_opportunities <= 0:
        raise ValueError("devices, beacons, and contention_opportunities must be positive")
    rng = np.random.default_rng(seed)
    queues = [deque() for _ in range(devices)]
    retries = np.zeros(devices, dtype=int)
    generated = delivered = collisions = dropped = attempts = 0
    latencies: list[float] = []
    total_energy_mj = 0.0
    tx_time_s = packet_bytes * 8.0 / phy_rate_bps

    for beacon in range(beacons):
        interval_start = beacon * config.beacon_interval_s
        mean_arrivals = packet_rate_hz * config.beacon_interval_s
        for device in range(devices):
            count = int(rng.poisson(mean_arrivals))
            generated += count
            for _ in range(count):
                # Aggregate arrivals from the preceding beacon interval at the beacon boundary.
                created = max(
                    0.0,
                    interval_start - float(rng.uniform(0.0, config.beacon_interval_s)),
                )
                queues[device].append(created)

        active_devices = [index for index, queue in enumerate(queues) if queue]
        for _ in range(max_retries + 1):
            contenders = [device for device in active_devices if queues[device]]
            if not contenders:
                break
            choices = {
                device: int(rng.integers(0, contention_opportunities))
                for device in contenders
            }
            by_slot: dict[int, list[int]] = {}
            for device, slot in choices.items():
                by_slot.setdefault(slot, []).append(device)
                attempts += 1

            for slot, slot_devices in by_slot.items():
                if len(slot_devices) == 1:
                    device = slot_devices[0]
                    created = queues[device].popleft()
                    success_time = interval_start + (
                        (slot + 1) / contention_opportunities * config.active_duration_s
                    )
                    latencies.append(max(success_time - created, 0.0))
                    delivered += 1
                    retries[device] = 0
                else:
                    collisions += len(slot_devices)
                    for device in slot_devices:
                        retries[device] += 1
                        if retries[device] > max_retries and queues[device]:
                            queues[device].popleft()
                            dropped += 1
                            retries[device] = 0

        baseline_mj = devices * (
            config.active_duration_s * idle_power_mw
            + config.inactive_duration_s * sleep_power_mw
        )
        tx_increment_mj = attempts * tx_time_s * max(tx_power_mw - idle_power_mw, 0.0)
        total_energy_mj += baseline_mj + tx_increment_mj
        attempts = 0

    latency = np.asarray(latencies, dtype=float)
    duration_s = beacons * config.beacon_interval_s
    queued = sum(len(queue) for queue in queues)
    return {
        "generated": generated,
        "delivered": delivered,
        "dropped": dropped,
        "queued_at_end": queued,
        "delivery_ratio": delivered / generated if generated else 0.0,
        "collided_attempts": collisions,
        "mean_latency_ms": float(latency.mean() * 1000.0) if len(latency) else None,
        "p95_latency_ms": float(np.percentile(latency, 95) * 1000.0) if len(latency) else None,
        "throughput_kbps": delivered * packet_bytes * 8.0 / duration_s / 1000.0,
        "energy_mj": total_energy_mj,
        "energy_per_delivered_packet_mj": total_energy_mj / delivered if delivered else None,
    }
