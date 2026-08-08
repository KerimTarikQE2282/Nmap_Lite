"""
Compares multiple ScanResult objects (same target/scan_type, N repeats)
and classifies each observed port by consistency across runs.
"""

from collections import Counter, defaultdict
from dataclasses import dataclass, field


@dataclass
class PortVerdict:
    port: int
    protocol: str
    states_seen: dict       # state -> count, e.g. {"open": 3} or {"open": 2, "filtered": 1}
    verdict: str            # "consistent" or "flaky"
    dominant_state: str     # most common state
    confidence: float       # dominant_state_count / total_runs
    service_hint: str = None


@dataclass
class ConsistencyReport:
    target: str
    scan_type: str
    runs: int
    errors: list = field(default_factory=list)   # any per-run errors encountered
    host_up_in_runs: int = 0
    verdicts: list = field(default_factory=list)  # list[PortVerdict]

    @property
    def consistent_ports(self):
        return [v for v in self.verdicts if v.verdict == "consistent"]

    @property
    def flaky_ports(self):
        return [v for v in self.verdicts if v.verdict == "flaky"]


def check_consistency(results: list) -> ConsistencyReport:
    """
    results: list[ScanResult] — all for the same target+scan_type, ideally
    `repeats` runs long (some may have errored out).
    """
    if not results:
        raise ValueError("No results provided")

    target = results[0].target
    scan_type = results[0].scan_type
    total_runs = len(results)

    errors = [r.error for r in results if r.error]
    usable_runs = [r for r in results if not r.error]
    host_up_count = sum(1 for r in usable_runs if r.host_up)

    # port -> list of states observed (one entry per run that saw this port)
    port_states = defaultdict(list)
    port_service = {}

    for r in usable_runs:
        for p in r.ports:
            key = (p.port, p.protocol)
            port_states[key].append(p.state)
            if p.service:
                port_service[key] = p.service

    verdicts = []
    for (port, protocol), states in sorted(port_states.items()):
        counts = Counter(states)
        dominant_state, dominant_count = counts.most_common(1)[0]
        # "consistent" only if every usable run reported the same state
        # for this port AND the port appeared in every usable run.
        is_consistent = (
            len(counts) == 1 and len(states) == len(usable_runs)
        )
        confidence = dominant_count / len(usable_runs) if usable_runs else 0.0

        verdicts.append(PortVerdict(
            port=port,
            protocol=protocol,
            states_seen=dict(counts),
            verdict="consistent" if is_consistent else "flaky",
            dominant_state=dominant_state,
            confidence=round(confidence, 2),
            service_hint=port_service.get((port, protocol)),
        ))

    return ConsistencyReport(
        target=target,
        scan_type=scan_type,
        runs=total_runs,
        errors=errors,
        host_up_in_runs=host_up_count,
        verdicts=verdicts,
    )
