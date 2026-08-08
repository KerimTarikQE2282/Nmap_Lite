# Reliascan

A consistency-checked `nmap` wrapper. Reliascan runs SYN, TCP, and/or UDP
scans **N times each** against a target, then diffs the results per-port to
tell you which ports were **stable** across every run vs. which ones were
**flaky** (returned a different state from one run to the next).

This is useful for spotting unreliable network conditions, rate-limiting,
IDS interference, or unstable services during a scan — a single nmap run
can't tell you whether a result you got was a fluke.

> **EDUCATIONAL USE ONLY.** Only scan systems you own or have explicit
> written authorization to test. See [Disclaimer](#disclaimer) below.

## Features

- Runs SYN (`-sS`), TCP connect (`-sT`), and/or UDP (`-sU`) scans, repeated
  a configurable number of times each
- Classifies every observed port as **consistent** (same state in every
  run) or **flaky** (state varied across runs), with a confidence score
- Human-readable terminal report, plus optional full JSON export
- Interactive authorization confirmation before scanning (skippable with
  `--yes` for scripted use)

## Requirements

- Python 3
- [`nmap`](https://nmap.org/) installed and on your `PATH`
- Root / `sudo` / `cap_net_raw` privileges for SYN and UDP scans (TCP
  connect scans work without elevated privileges)

## Installation

```bash
git clone <this-repo-url>
cd reliascan
chmod +x reliascan.sh
```

No other dependencies — Reliascan only uses the Python standard library.

## Usage

```bash
./reliascan.sh <target> [options]
```

### Examples

```bash
# Full default scan (SYN + TCP + UDP, 3 repeats each)
./reliascan.sh 127.0.0.1

# Only SYN and TCP scans, 5 repeats each
./reliascan.sh 192.168.1.10 --scans syn tcp --repeats 5

# UDP scan, save results to JSON, skip the confirmation prompt
./reliascan.sh 10.0.0.5 --scans udp --json-out report.json --yes
```

Or run it directly as a Python module:

```bash
python3 -m reliascan.cli <target> [options]
```

### Options

| Flag | Description |
|---|---|
| `target` | Target host/IP/CIDR to scan (required) |
| `--scans {syn,tcp,udp}` | Which scan types to run (default: all three) |
| `--repeats N` | How many times to repeat each scan type (default: 3) |
| `--json-out PATH` | Save full results as JSON to this path |
| `--hide-consistent` | Only print flaky ports in the terminal report |
| `--yes` | Skip the interactive authorization confirmation prompt |

### Sample output

```
--- SYN scan consistency report for 192.168.1.10 ---
Runs: 3 | Host up in 3/3 usable runs

[FLAKY] 1 port(s) with inconsistent results across runs:
    8080/tcp (http): openx2, filteredx1  -> dominant='open' confidence=0.67

[CONSISTENT] 2 port(s) stable across all runs:
    22/tcp (ssh): open
    443/tcp (https): open
```

## Project layout

```
reliascan.sh          # bash launcher (checks deps, forwards to the CLI)
reliascan/
  cli.py               # argument parsing + orchestration
  banner.py            # startup banner + legal warning
  scanner.py           # runs nmap, parses XML output
  consistency.py       # diffs repeated runs, classifies ports
  report.py            # terminal + JSON report formatting
```

## Disclaimer

This tool is provided strictly for **educational purposes** and for use
against systems you **own** or have **explicit written authorization** to
test. Scanning networks or hosts without permission may violate applicable
laws (e.g. the U.S. Computer Fraud and Abuse Act, the UK Computer Misuse
Act, or local equivalents) and/or the target's terms of service.

The author(s) assume no liability for any illegal, unauthorized, or
malicious use of this tool. See [LICENSE](LICENSE) for the full MIT license
and disclaimer text.

## License

MIT — see [LICENSE](LICENSE).
