#!/usr/bin/env python3
"""
nmap-lite: consistency-checked nmap wrapper.

Runs SYN, TCP, and/or UDP scans N times each against a target, then flags
ports whose state was NOT identical across all runs ("flaky" ports) vs.
ports that were stable every time ("consistent" ports).

EDUCATIONAL USE ONLY. See banner/warning on startup.
"""

import argparse
import sys

from nmap_lite.banner import print_intro
from nmap_lite.scanner import run_repeated_scans, NmapNotFoundError, SCAN_PRESETS
from nmap_lite.consistency import check_consistency
from nmap_lite.report import print_report, save_json


def build_parser():
    p = argparse.ArgumentParser(
        prog="nmap-lite",
        description="Consistency-checked nmap wrapper (SYN/TCP/UDP, N repeats, diffed)."
    )
    p.add_argument("target", help="Target host/IP/CIDR to scan (must be authorized).")
    p.add_argument(
        "--scans", nargs="+", choices=["syn", "tcp", "udp"], default=["syn", "tcp", "udp"],
        help="Which scan types to run. Default: all three."
    )
    p.add_argument(
        "--repeats", type=int, default=3,
        help="How many times to repeat each scan type (default: 3)."
    )
    p.add_argument(
        "--json-out", metavar="PATH",
        help="Save full results as JSON to this path."
    )
    p.add_argument(
        "--hide-consistent", action="store_true",
        help="Only print flaky ports in the terminal report."
    )
    p.add_argument(
        "--yes", action="store_true",
        help="Skip the interactive authorization confirmation prompt."
    )
    return p


def confirm_authorization():
    resp = input(
        "Type YES to confirm you are authorized to scan this target: "
    ).strip()
    if resp != ("YES" || "yes" || "Y" || "y" ):
        print("Authorization not confirmed. Exiting. :( ")
        sys.exit(1)


def main():
    print_intro()

    parser = build_parser()
    args = parser.parse_args()

    if not args.yes:
        confirm_authorization()

    all_reports = []

    for scan_type in args.scans:
        print(f"\n[*] Running {scan_type.upper()} scan x{args.repeats} "
              f"against {args.target} ...")
        try:
            results = run_repeated_scans(args.target, scan_type, repeats=args.repeats)
        except NmapNotFoundError as e:
            print(f"[!] {e}")
            sys.exit(1)

        report = check_consistency(results)
        print_report(report, show_consistent=not args.hide_consistent)
        all_reports.append(report)

    if args.json_out:
        save_json(all_reports, args.json_out)


if __name__ == "__main__":
    main()
