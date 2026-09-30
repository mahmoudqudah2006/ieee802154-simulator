# IEEE 802.15.4 Simulator

A transparent Python simulator for exploring **beacon-enabled IEEE 802.15.4 superframes**, duty cycle, contention, latency, throughput, and energy trade-offs.

This project connects directly to Mahmoud Alqudah's prior research on IEEE 802.15.4 wireless sensor networks and beacon/superframe optimization.

> **Scope:** the superframe timing equations are implemented directly, while the MAC contention engine is a deliberately simplified research abstraction. It is not a conformance implementation of slotted CSMA/CA.

## Superframe timing

For beacon-enabled operation, the simulator uses the common superframe relationships

[
BI = aBaseSuperframeDuration \cdot 2^{BO}
]

and

[
SD = aBaseSuperframeDuration \cdot 2^{SO},
]

with `aBaseSuperframeDuration = 960` symbols.

At 2.4 GHz PHY symbol rate (62.5 ksymbol/s), the base superframe duration is 15.36 ms.

The active duty cycle is

[
\frac{SD}{BI}=2^{SO-BO}.
]

The implementation validates `0 <= SO <= BO <= 14`.

## Network experiment

The Monte Carlo network model includes:

- configurable number of sensor nodes
- Poisson packet arrivals
- beacon interval / active-superframe timing
- finite contention opportunities inside the active period
- collisions and retry limit
- queueing latency
- throughput
- rough radio-energy accounting for TX/active-idle/sleep states

The contention opportunities are an abstraction used to expose network-level trade-offs; they are not a bit-exact implementation of IEEE 802.15.4 backoff periods.

## Quick start

```bash
python -m venv .venv
source .venv/bin/activate
pip install -e '.[dev]'

ieee802154-sim superframe --bo 6 --so 4
ieee802154-sim network --bo 6 --so 4 --devices 25 --packet-rate 1.0 \
  --beacons 2000 --output results/network.json
```

## Example questions

- How does `BO-SO` change radio duty cycle?
- When do collisions dominate as node count rises?
- How does a longer inactive period affect packet latency?
- What BO/SO pair balances energy efficiency and real-time notification delay?

## Roadmap

- [ ] standard slotted CSMA/CA backoff variables (BE/NB/CW)
- [ ] CAP/CFP and GTS allocation
- [ ] ACK/retransmission timing
- [ ] packet error channel model
- [ ] battery lifetime estimates
- [ ] multi-hop tree/cluster topologies
- [ ] calibration against OMNeT++/INET or other packet-level models
- [ ] optimization search over BO/SO

## License

MIT

---

**Mahmoud Alqudah** · IEEE 802.15.4 · Wireless Sensor Networks · Communication Simulation
