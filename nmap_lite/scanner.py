"""Runs nmap as a subprocess and parses its XML output into plain dicts."""

import subprocess
import tempfile
import os
import xml.etree.ElementTree as ET
from dataclasses import dataclass, field
from typing import Optional


class NmapNotFoundError(RuntimeError):
    pass


class NmapExecutionError(RuntimeError):
    pass


@dataclass
class PortResult:
    port: int
    protocol: str  # tcp / udp
    state: str     # open / closed / filtered / open|filtered / etc.
    service: Optional[str] = None
    reason: Optional[str] = None


@dataclass
class ScanResult:
    target: str
    scan_type: str          # syn / tcp / udp
    raw_args: list = field(default_factory=list)
    ports: list = field(default_factory=list)  # list[PortResult]
    host_up: bool = True
    error: Optional[str] = None


# Default flag presets. Override with custom args if desired.
SCAN_PRESETS = {
    "syn": ["-sS", "-T4", "-p-"],
    "tcp": ["-sT", "-T4", "-p-"],
    "udp": ["-sU", "-T4", "--top-ports", "1000"],
}


def _check_nmap_available():
    try:
        subprocess.run(
            ["nmap", "-V"], capture_output=True, check=True, timeout=10
        )
    except FileNotFoundError:
        raise NmapNotFoundError(
            "nmap binary not found on PATH. Install nmap first."
        )
    except subprocess.CalledProcessError as e:
        raise NmapNotFoundError(f"nmap exists but failed to run: {e}")


def run_single_scan(target: str, scan_type: str, extra_args=None) -> ScanResult:
    """
    Run nmap once against `target` using the preset (or override) args for
    `scan_type`, parse the XML output, and return a ScanResult.

    scan_type must be one of: 'syn', 'tcp', 'udp'
    extra_args: optional list of args that REPLACES the preset entirely.
    """
    _check_nmap_available()

    if scan_type not in SCAN_PRESETS:
        raise ValueError(f"Unknown scan_type '{scan_type}'. Use one of {list(SCAN_PRESETS)}")

    args = list(extra_args) if extra_args else list(SCAN_PRESETS[scan_type])

    # SYN and UDP scans require raw sockets -> need root/cap_net_raw.
    needs_privilege = scan_type in ("syn", "udp")

    with tempfile.NamedTemporaryFile(suffix=".xml", delete=False) as tmp:
        xml_path = tmp.name

    cmd = ["nmap"] + args + ["-oX", xml_path, target]

    try:
        proc = subprocess.run(
            cmd, capture_output=True, text=True, timeout=60 * 30
        )
    except subprocess.TimeoutExpired:
        os.unlink(xml_path) if os.path.exists(xml_path) else None
        return ScanResult(target=target, scan_type=scan_type, raw_args=args,
                           error="Scan timed out after 30 minutes.")

    if proc.returncode != 0:
        hint = ""
        if needs_privilege and "requires root privileges" in (proc.stderr or "").lower():
            hint = " (this scan type needs root / sudo / cap_net_raw)"
        err_msg = (proc.stderr or proc.stdout or "Unknown nmap error").strip()
        if os.path.exists(xml_path):
            os.unlink(xml_path)
        return ScanResult(target=target, scan_type=scan_type, raw_args=args,
                           error=f"nmap exited with code {proc.returncode}{hint}: {err_msg}")

    try:
        result = _parse_xml(xml_path, target, scan_type, args)
    finally:
        if os.path.exists(xml_path):
            os.unlink(xml_path)

    return result


def _parse_xml(xml_path: str, target: str, scan_type: str, args: list) -> ScanResult:
    tree = ET.parse(xml_path)
    root = tree.getroot()

    host_el = root.find("host")
    if host_el is None:
        # Host did not respond / down
        return ScanResult(target=target, scan_type=scan_type, raw_args=args,
                           host_up=False, ports=[])

    status_el = host_el.find("status")
    host_up = (status_el is not None and status_el.get("state") == "up")

    ports = []
    ports_el = host_el.find("ports")
    if ports_el is not None:
        for port_el in ports_el.findall("port"):
            portid = int(port_el.get("portid"))
            protocol = port_el.get("protocol")
            state_el = port_el.find("state")
            state = state_el.get("state") if state_el is not None else "unknown"
            reason = state_el.get("reason") if state_el is not None else None
            service_el = port_el.find("service")
            service = service_el.get("name") if service_el is not None else None

            ports.append(PortResult(
                port=portid, protocol=protocol, state=state,
                service=service, reason=reason
            ))

    return ScanResult(target=target, scan_type=scan_type, raw_args=args,
                       host_up=host_up, ports=ports)


def run_repeated_scans(target: str, scan_type: str, repeats: int = 3, extra_args=None):
    """Run the same scan `repeats` times, returning a list of ScanResult."""
    results = []
    for i in range(repeats):
        results.append(run_single_scan(target, scan_type, extra_args=extra_args))
    return results
