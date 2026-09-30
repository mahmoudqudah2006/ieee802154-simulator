from __future__ import annotations

import argparse
import json
from pathlib import Path

from .network import simulate_network
from .superframe import SuperframeConfig


def main() -> None:
    parser = argparse.ArgumentParser(description="IEEE 802.15.4 superframe research simulator")
    sub = parser.add_subparsers(dest="command", required=True)

    superframe = sub.add_parser("superframe")
    superframe.add_argument("--bo", type=int, required=True)
    superframe.add_argument("--so", type=int, required=True)

    network = sub.add_parser("network")
    network.add_argument("--bo", type=int, required=True)
    network.add_argument("--so", type=int, required=True)
    network.add_argument("--devices", type=int, default=20)
    network.add_argument("--packet-rate", type=float, default=1.0)
    network.add_argument("--beacons", type=int, default=1000)
    network.add_argument("--seed", type=int, default=7)
    network.add_argument("--output", type=Path, default=Path("results/network.json"))
    args = parser.parse_args()

    config = SuperframeConfig(args.bo, args.so)
    if args.command == "superframe":
        print(json.dumps(config.to_dict(), indent=2))
        return
    result = {"superframe": config.to_dict(), "network": simulate_network(
        config,
        devices=args.devices,
        packet_rate_hz=args.packet_rate,
        beacons=args.beacons,
        seed=args.seed,
    )}
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(json.dumps(result, indent=2), encoding="utf-8")
    print(json.dumps(result, indent=2))


if __name__ == "__main__":
    main()
