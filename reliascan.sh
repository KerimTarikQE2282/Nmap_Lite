#!/usr/bin/env bash
#
# reliascan.sh — bash launcher for the reliascan consistency-checked scanner.
#
# EDUCATIONAL USE ONLY. You are responsible for ensuring you have explicit
# authorization to scan any target you pass to this script.
#
# Usage:
#   ./reliascan.sh <target> [extra python args...]
#
# Examples:
#   ./reliascan.sh 127.0.0.1
#   ./reliascan.sh 192.168.1.10 --scans syn tcp --repeats 5
#   ./reliascan.sh 10.0.0.5 --scans udp --json-out report.json --yes
#
set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"

# --- Resolve a python3 interpreter ---
if command -v python3 >/dev/null 2>&1; then
    PYTHON_BIN="python3"
else
    echo "[!] python3 not found on PATH. Please install Python 3." >&2
    exit 1
fi

# --- Check for nmap binary early, with a friendly install hint ---
if ! command -v nmap >/dev/null 2>&1; then
    echo "[!] nmap is not installed or not on PATH." >&2
    echo "    Install it with:" >&2
    echo "      Debian/Ubuntu : sudo apt-get install nmap" >&2
    echo "      Fedora/RHEL   : sudo dnf install nmap" >&2
    echo "      macOS (brew)  : brew install nmap" >&2
    exit 1
fi

# --- Require at least one argument (the target) ---
if [ "$#" -lt 1 ]; then
    echo "Usage: $0 <target> [--scans syn tcp udp] [--repeats N] [--json-out PATH] [--hide-consistent] [--yes]" >&2
    exit 1
fi

# --- Note on privileges ---
# SYN (-sS) and UDP (-sU) scans require raw socket access (root / sudo / cap_net_raw).
# TCP connect (-sT) scans do not. If the user requests syn/udp without enough
# privilege, nmap itself will report the error and reliascan will surface it
# per-run rather than failing silently.
if [ "$EUID" -ne 0 ]; then
    echo "[i] Note: not running as root. SYN and UDP scans typically require"
    echo "    root/sudo privileges (cap_net_raw). TCP connect scans will work fine."
    echo ""
fi

cd "$SCRIPT_DIR"
exec "$PYTHON_BIN" -m reliascan.cli "$@"
