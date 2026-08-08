"""Formats ConsistencyReport objects for terminal display and JSON export."""

import json
from dataclasses import asdict


def print_report(report, show_consistent=True):
    print(f"\n--- {report.scan_type.upper()} scan consistency report for {report.target} ---")
    print(f"Runs: {report.runs} | Host up in {report.host_up_in_runs}/{report.runs} usable runs")

    if report.errors:
        print(f"\n[!] {len(report.errors)} run(s) errored out:")
        for e in report.errors:
            print(f"    - {e}")

    if not report.verdicts:
        print("\nNo ports recorded (host may be down or all ports filtered/closed).")
        return

    flaky = report.flaky_ports
    consistent = report.consistent_ports

    if flaky:
        print(f"\n[FLAKY] {len(flaky)} port(s) with inconsistent results across runs:")
        for v in flaky:
            svc = f" ({v.service_hint})" if v.service_hint else ""
            states_str = ", ".join(f"{s}x{c}" for s, c in v.states_seen.items())
            print(f"    {v.port}/{v.protocol}{svc}: {states_str}  "
                  f"-> dominant='{v.dominant_state}' confidence={v.confidence}")
    else:
        print("\n[FLAKY] None — all observed ports were stable across runs.")

    if show_consistent and consistent:
        print(f"\n[CONSISTENT] {len(consistent)} port(s) stable across all runs:")
        for v in consistent:
            svc = f" ({v.service_hint})" if v.service_hint else ""
            print(f"    {v.port}/{v.protocol}{svc}: {v.dominant_state}")


def report_to_dict(report):
    d = asdict(report)
    return d


def save_json(reports: list, path: str):
    """reports: list of ConsistencyReport (e.g. one per scan_type)."""
    data = [report_to_dict(r) for r in reports]
    with open(path, "w") as f:
        json.dump(data, f, indent=2)
    print(f"\n[+] JSON report saved to {path}")
