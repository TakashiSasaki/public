from __future__ import annotations

from dataclasses import dataclass
import ipaddress
import platform
import re
import socket
import subprocess


@dataclass(frozen=True, slots=True)
class InterfaceInfo:
    name: str
    ipv4_addresses: tuple[str, ...]
    ipv6_addresses: tuple[str, ...]

    @property
    def addresses(self) -> tuple[str, ...]:
        return self.ipv4_addresses + self.ipv6_addresses


def _dedupe_keep_order(values: list[str]) -> list[str]:
    seen: set[str] = set()
    deduped: list[str] = []
    for value in values:
        if value in seen:
            continue
        seen.add(value)
        deduped.append(value)
    return deduped


def _split_ip_versions(values: list[str]) -> tuple[tuple[str, ...], tuple[str, ...]]:
    ipv4: list[str] = []
    ipv6: list[str] = []
    for value in values:
        try:
            parsed = ipaddress.ip_address(value)
        except ValueError:
            continue
        if parsed.version == 4:
            ipv4.append(value)
        elif parsed.version == 6:
            ipv6.append(value)
    return tuple(_dedupe_keep_order(ipv4)), tuple(_dedupe_keep_order(ipv6))


def _collect_ips_with_psutil() -> dict[str, list[str]] | None:
    try:
        import psutil
    except ImportError:
        return None

    result: dict[str, list[str]] = {}
    for name, entries in psutil.net_if_addrs().items():
        values: list[str] = []
        for entry in entries:
            if entry.family not in (socket.AF_INET, socket.AF_INET6):
                continue
            address = entry.address.split("%", 1)[0]
            if address:
                values.append(address)
        result[name] = _dedupe_keep_order(values)
    return result


def _collect_ips_windows() -> dict[str, list[str]]:
    try:
        output = subprocess.check_output(
            ["ipconfig"],
            text=True,
            encoding="utf-8",
            errors="replace",
        )
    except (OSError, subprocess.CalledProcessError):
        return {}

    ip_re = re.compile(r"([0-9]{1,3}(?:\.[0-9]{1,3}){3}|[0-9a-fA-F:]+)")
    current: str | None = None
    result: dict[str, list[str]] = {}
    for raw_line in output.splitlines():
        line = raw_line.rstrip()
        stripped = line.strip()
        if not stripped:
            continue
        if not raw_line.startswith(" ") and stripped.endswith(":"):
            heading = stripped[:-1].strip()
            lower = heading.lower()
            if "adapter" in lower:
                heading = heading.split("adapter", 1)[1].strip()
            current = heading
            result.setdefault(current, [])
            continue
        if current is None:
            continue
        if ":" not in stripped:
            continue
        _, value = stripped.split(":", 1)
        value = value.strip().split("(", 1)[0].strip()
        if not value:
            continue
        if ip_re.fullmatch(value):
            result[current].append(value.split("%", 1)[0])

    return {name: _dedupe_keep_order(values) for name, values in result.items()}


def _collect_ips_windows_by_index() -> dict[int, list[str]]:
    command = (
        "Get-NetIPAddress -AddressFamily IPv4,IPv6 "
        "| Select-Object InterfaceIndex,IPAddress "
        "| ConvertTo-Json -Compress"
    )
    for shell_cmd in (["pwsh", "-NoProfile", "-Command", command], ["powershell", "-NoProfile", "-Command", command]):
        try:
            output = subprocess.check_output(
                shell_cmd,
                text=True,
                encoding="utf-8",
                errors="replace",
            ).strip()
        except (OSError, subprocess.CalledProcessError):
            continue
        if not output:
            continue
        try:
            import json

            parsed = json.loads(output)
        except Exception:
            continue

        rows = parsed if isinstance(parsed, list) else [parsed]
        result: dict[int, list[str]] = {}
        for row in rows:
            if not isinstance(row, dict):
                continue
            index = row.get("InterfaceIndex")
            address = row.get("IPAddress")
            if not isinstance(index, int) or not isinstance(address, str):
                continue
            cleaned = address.split("%", 1)[0]
            if not cleaned:
                continue
            result.setdefault(index, []).append(cleaned)
        return {idx: _dedupe_keep_order(values) for idx, values in result.items()}
    return {}


def _collect_ips_linux() -> dict[str, list[str]]:
    try:
        output = subprocess.check_output(
            ["ip", "-o", "addr", "show"],
            text=True,
            encoding="utf-8",
            errors="replace",
        )
    except (OSError, subprocess.CalledProcessError):
        return {}

    result: dict[str, list[str]] = {}
    for line in output.splitlines():
        parts = line.split()
        if len(parts) < 4:
            continue
        name = parts[1]
        family = parts[2]
        if family not in ("inet", "inet6"):
            continue
        address = parts[3].split("/", 1)[0]
        result.setdefault(name, []).append(address.split("%", 1)[0])
    return {name: _dedupe_keep_order(values) for name, values in result.items()}


def _collect_ips_macos() -> dict[str, list[str]]:
    try:
        output = subprocess.check_output(
            ["ifconfig"],
            text=True,
            encoding="utf-8",
            errors="replace",
        )
    except (OSError, subprocess.CalledProcessError):
        return {}

    current: str | None = None
    result: dict[str, list[str]] = {}
    for raw_line in output.splitlines():
        line = raw_line.rstrip()
        if not line:
            continue
        if not raw_line.startswith("\t") and ":" in line:
            current = line.split(":", 1)[0]
            result.setdefault(current, [])
            continue
        if current is None:
            continue
        stripped = line.strip()
        if stripped.startswith("inet "):
            parts = stripped.split()
            if len(parts) >= 2:
                result[current].append(parts[1])
        elif stripped.startswith("inet6 "):
            parts = stripped.split()
            if len(parts) >= 2:
                result[current].append(parts[1].split("%", 1)[0])

    return {name: _dedupe_keep_order(values) for name, values in result.items()}


def _collect_interface_ips() -> dict[str, list[str]]:
    psutil_result = _collect_ips_with_psutil()
    if psutil_result is not None:
        return psutil_result

    system = platform.system().lower()
    if system == "windows":
        return _collect_ips_windows()
    if system == "linux":
        return _collect_ips_linux()
    if system == "darwin":
        return _collect_ips_macos()
    return {}


def list_interfaces() -> list[InterfaceInfo]:
    try:
        indexed_names = socket.if_nameindex()
    except OSError:
        indexed_names = []

    ip_map = _collect_interface_ips()
    windows_index_map = _collect_ips_windows_by_index() if platform.system().lower() == "windows" else {}

    if not indexed_names:
        return [InterfaceInfo(name="all (0.0.0.0)", ipv4_addresses=("0.0.0.0",), ipv6_addresses=())]

    deduped_names = _dedupe_keep_order([name for _, name in indexed_names])
    name_to_index: dict[str, int] = {}
    for index, name in indexed_names:
        name_to_index.setdefault(name, index)

    resolved: list[InterfaceInfo] = []
    for name in deduped_names:
        index = name_to_index.get(name)
        addresses = windows_index_map.get(index, []) if index is not None else []
        if not addresses:
            addresses = ip_map.get(name, [])
        if not addresses:
            lower_name = name.lower()
            merged: list[str] = []
            for key, values in ip_map.items():
                lower_key = key.lower()
                if lower_name in lower_key or lower_key in lower_name:
                    merged.extend(values)
            addresses = _dedupe_keep_order(merged)
        ipv4_addresses, ipv6_addresses = _split_ip_versions(addresses)
        resolved.append(
            InterfaceInfo(
                name=name,
                ipv4_addresses=ipv4_addresses,
                ipv6_addresses=ipv6_addresses,
            )
        )
    return resolved
