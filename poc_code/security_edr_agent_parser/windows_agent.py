#!/usr/bin/env python3
"""Collect Windows endpoint telemetry and render a Falcon-style dashboard.

Default mode runs fixed PowerShell queries on Windows:
- Win32_Process process metadata without command-line arguments
- Get-Process CPU and memory metrics
- Get-NetTCPConnection LISTEN/ESTABLISHED sockets
- OS/computer metadata

Mock mode loads the same raw PowerShell-shaped JSON from --mock-file so the
parser, rule engine, and dashboard can be tested outside Windows.

It does not collect packet payloads, TLS contents, browser history, environment
variables, command-line arguments, file contents, registry contents, or secrets.
"""

from __future__ import annotations

import argparse
import hashlib
import html
import ipaddress
import json
import platform
import shutil
import socket
import subprocess
import sys
import time
from collections import Counter, defaultdict
from datetime import datetime
from pathlib import Path
from typing import Any


ROOT = Path(__file__).resolve().parent
DATA_DIR = ROOT / "data"
DEFAULT_MOCK_FILE = ROOT / "samples" / "mock_windows_powershell.json"
JSON_PATH = DATA_DIR / "latest_windows_telemetry.json"
DASHBOARD_PATH = ROOT / "dashboard_windows.html"
FALLBACK_TEMPLATE_PATH = ROOT / "dashboard_template.html"

MAX_VISIBLE_PROCESSES = 220
MAX_VISIBLE_CONNECTIONS = 320
COMMON_REMOTE_PORTS = {22, 53, 80, 123, 135, 139, 389, 443, 445, 3389, 5353, 5985, 5986}
SCRIPT_INTERPRETERS = {
    "cmd.exe",
    "powershell.exe",
    "pwsh.exe",
    "wscript.exe",
    "cscript.exe",
    "mshta.exe",
    "rundll32.exe",
    "regsvr32.exe",
}


POWERSHELL_COLLECTOR = r"""
$ErrorActionPreference = "Stop"
$processes = @(Get-CimInstance Win32_Process | Select-Object ProcessId, ParentProcessId, Name, CreationDate)
$metrics = @(Get-Process | Select-Object Id, ProcessName, CPU, WorkingSet64)
$tcp = @(Get-NetTCPConnection -State Listen, Established | Select-Object LocalAddress, LocalPort, RemoteAddress, RemotePort, State, OwningProcess, CreationTime)
$os = Get-CimInstance Win32_OperatingSystem | Select-Object Caption, Version, BuildNumber, LastBootUpTime
$computer = Get-CimInstance Win32_ComputerSystem | Select-Object Name, Manufacturer, Model, Domain
[ordered]@{
  processes = $processes
  process_metrics = $metrics
  tcp_connections = $tcp
  os = $os
  computer = $computer
} | ConvertTo-Json -Depth 5 -Compress
"""


def now_iso() -> str:
    return datetime.now().astimezone().isoformat(timespec="seconds")


def stable_hash(value: str, length: int = 12) -> str:
    return hashlib.sha256(value.encode("utf-8")).hexdigest()[:length]


def normalize_list(value: Any) -> list[Any]:
    if value is None:
        return []
    if isinstance(value, list):
        return value
    return [value]


def as_int(value: Any) -> int | None:
    if value in {None, ""}:
        return None
    try:
        return int(value)
    except (TypeError, ValueError):
        return None


def as_float(value: Any) -> float | None:
    if value in {None, ""}:
        return None
    try:
        return float(value)
    except (TypeError, ValueError):
        return None


def classify_ip(ip_text: str | None) -> str:
    if not ip_text:
        return "none"
    normalized = str(ip_text).strip()
    if normalized in {"*", "0.0.0.0", "::", "0:0:0:0:0:0:0:0"}:
        return "wildcard"
    try:
        ip = ipaddress.ip_address(normalized.split("%", 1)[0])
    except ValueError:
        return "unknown"
    if ip.is_loopback:
        return "loopback"
    if ip.is_link_local:
        return "link-local"
    if ip in ipaddress.ip_network("100.64.0.0/10"):
        return "tailnet-cgnat"
    if ip.is_private:
        return "private"
    if ip.is_multicast:
        return "multicast"
    if ip.is_global:
        return "external"
    return "reserved"


def find_powershell() -> str | None:
    for candidate in ("pwsh", "powershell.exe", "powershell"):
        found = shutil.which(candidate)
        if found:
            return found
    return None


def run_powershell(timeout: int = 18) -> dict[str, Any]:
    exe = find_powershell()
    if not exe:
        return {
            "ok": False,
            "args": ["powershell"],
            "returncode": None,
            "stdout": "",
            "stderr": "PowerShell executable not found",
            "duration_ms": 0,
            "input_mode": "powershell",
        }
    started = time.time()
    args = [exe, "-NoProfile", "-ExecutionPolicy", "Bypass", "-Command", POWERSHELL_COLLECTOR]
    try:
        completed = subprocess.run(args, capture_output=True, check=False, text=True, timeout=timeout)
        return {
            "ok": completed.returncode == 0,
            "args": [Path(exe).name, "-NoProfile", "-ExecutionPolicy", "Bypass", "-Command", "<collector>"],
            "returncode": completed.returncode,
            "stdout": completed.stdout,
            "stderr": completed.stderr.strip(),
            "duration_ms": round((time.time() - started) * 1000),
            "input_mode": "powershell",
        }
    except Exception as exc:  # pragma: no cover - defensive for Windows host execution
        return {
            "ok": False,
            "args": [Path(exe).name, "-NoProfile", "-ExecutionPolicy", "Bypass", "-Command", "<collector>"],
            "returncode": None,
            "stdout": "",
            "stderr": f"{type(exc).__name__}: {exc}",
            "duration_ms": round((time.time() - started) * 1000),
            "input_mode": "powershell",
        }


def read_mock(path: Path) -> dict[str, Any]:
    return json.loads(path.read_text(encoding="utf-8"))


def load_raw(args: argparse.Namespace) -> tuple[dict[str, Any], dict[str, Any]]:
    if args.mock or args.mock_file:
        path = Path(args.mock_file or DEFAULT_MOCK_FILE)
        started = time.time()
        raw = read_mock(path)
        command = {
            "ok": True,
            "args": ["mock-file", str(path)],
            "returncode": 0,
            "stderr": "",
            "duration_ms": round((time.time() - started) * 1000),
            "input_mode": "mock",
        }
        return raw, command

    command = run_powershell(timeout=args.timeout)
    if not command["ok"]:
        return {}, command
    try:
        return json.loads(command["stdout"]), command
    except json.JSONDecodeError as exc:
        command = {**command, "ok": False, "stderr": f"JSONDecodeError: {exc}"}
        return {}, command


def process_origin(name: str) -> str:
    lowered = name.lower()
    if lowered in {"system", "system.exe", "registry", "smss.exe", "csrss.exe", "wininit.exe", "services.exe", "lsass.exe"}:
        return "system"
    if lowered in SCRIPT_INTERPRETERS:
        return "script"
    if lowered.endswith(".exe"):
        return "application"
    return "unknown"


def build_processes(raw: dict[str, Any]) -> dict[int, dict[str, Any]]:
    metrics_by_pid: dict[int, dict[str, Any]] = {}
    for metric in normalize_list(raw.get("process_metrics")):
        pid = as_int(metric.get("Id"))
        if pid is None:
            continue
        metrics_by_pid[pid] = metric

    processes: dict[int, dict[str, Any]] = {}
    for proc in normalize_list(raw.get("processes")):
        pid = as_int(proc.get("ProcessId"))
        if pid is None:
            continue
        metric = metrics_by_pid.get(pid, {})
        name = proc.get("Name") or metric.get("ProcessName") or f"pid-{pid}"
        if name and not str(name).lower().endswith(".exe") and metric.get("ProcessName"):
            name = f"{metric['ProcessName']}.exe"
        working_set = as_float(metric.get("WorkingSet64"))
        processes[pid] = {
            "pid": pid,
            "ppid": as_int(proc.get("ParentProcessId")),
            "process_name": str(name),
            "process_origin": process_origin(str(name)),
            "cpu_seconds": as_float(metric.get("CPU")),
            "working_set_mb": round(working_set / 1024 / 1024, 1) if working_set is not None else None,
            "command_fingerprint": None,
            "created_at": proc.get("CreationDate"),
        }
    return processes


def build_connections(raw: dict[str, Any], processes: dict[int, dict[str, Any]], collected_at: str, agent_id: str) -> list[dict[str, Any]]:
    connections: list[dict[str, Any]] = []
    for item in normalize_list(raw.get("tcp_connections")):
        state = str(item.get("State") or "Unknown").upper()
        if state not in {"LISTEN", "ESTABLISHED"}:
            continue
        pid = as_int(item.get("OwningProcess")) or 0
        proc = processes.get(pid, {})
        src_ip = str(item.get("LocalAddress") or "")
        dst_ip = str(item.get("RemoteAddress") or "") if item.get("RemoteAddress") is not None else None
        event_id = f"flow-{len(connections) + 1:05d}"
        connections.append(
            {
                "event_id": event_id,
                "source": "windows_agent",
                "agent_id": agent_id,
                "event_time": item.get("CreationTime") or collected_at,
                "ingest_time": collected_at,
                "pid": pid,
                "process_name": proc.get("process_name", f"pid-{pid}"),
                "process_origin": proc.get("process_origin", "unknown"),
                "protocol": "TCP",
                "ip_version": "IPv6" if ":" in src_ip else "IPv4",
                "state": state,
                "src_ip": src_ip,
                "src_port": as_int(item.get("LocalPort")),
                "src_class": classify_ip(src_ip),
                "dst_ip": dst_ip,
                "dst_port": as_int(item.get("RemotePort")),
                "dst_class": classify_ip(dst_ip),
                "flow_status": "unknown",
                "packet_count": None,
                "byte_count": None,
                "duration_ms": None,
            }
        )
    return connections


def add_alert(
    alerts: list[dict[str, Any]],
    rule_id: str,
    name: str,
    severity: str,
    confidence: float,
    mitre_tactic: str,
    mitre_technique: str,
    reason: str,
    related_event_ids: list[str],
    created_at: str,
) -> None:
    alerts.append(
        {
            "alert_id": f"alert-{len(alerts) + 1:04d}",
            "rule_id": rule_id,
            "name": name,
            "severity": severity,
            "confidence": round(confidence, 2),
            "flow_status": "unknown",
            "mitre_tactic": mitre_tactic,
            "mitre_technique": mitre_technique,
            "reason": reason,
            "related_event_ids": related_event_ids[:20],
            "created_at": created_at,
        }
    )


def build_alerts(processes: dict[int, dict[str, Any]], connections: list[dict[str, Any]], collected_at: str) -> list[dict[str, Any]]:
    alerts: list[dict[str, Any]] = []
    by_pid_remote: dict[int, set[str]] = defaultdict(set)
    by_pid_events: dict[int, list[str]] = defaultdict(list)
    interpreter_events: dict[int, list[str]] = defaultdict(list)

    for conn in connections:
        process_name = str(conn["process_name"])
        if conn["state"] == "LISTEN" and conn["src_class"] in {"wildcard", "private", "tailnet-cgnat"}:
            severity = "high" if conn["src_class"] == "wildcard" else "medium"
            confidence = 0.74 if conn["src_class"] == "wildcard" else 0.58
            add_alert(
                alerts,
                "WIN-NET-001",
                "외부 접근 가능 LISTEN socket",
                severity,
                confidence,
                "Discovery",
                "Network Service Discovery",
                f"{process_name} PID {conn['pid']}가 {conn['src_ip']}:{conn['src_port']}에서 LISTEN 중",
                [conn["event_id"]],
                collected_at,
            )

        if conn["state"] == "ESTABLISHED" and conn["dst_ip"]:
            if conn["dst_class"] in {"external", "private", "tailnet-cgnat"}:
                by_pid_remote[conn["pid"]].add(str(conn["dst_ip"]))
                by_pid_events[conn["pid"]].append(conn["event_id"])
            if conn["dst_class"] == "external" and conn["dst_port"] and conn["dst_port"] not in COMMON_REMOTE_PORTS:
                add_alert(
                    alerts,
                    "WIN-NET-002",
                    "비표준 외부 remote port 연결",
                    "medium",
                    0.46,
                    "Command and Control",
                    "Non-Standard Port",
                    f"{process_name} PID {conn['pid']}가 external {conn['dst_ip']}:{conn['dst_port']}와 ESTABLISHED 상태",
                    [conn["event_id"]],
                    collected_at,
                )
            if process_name.lower() in SCRIPT_INTERPRETERS and conn["dst_class"] == "external":
                interpreter_events[conn["pid"]].append(conn["event_id"])

    for pid, event_ids in interpreter_events.items():
        proc = processes.get(pid, {})
        add_alert(
            alerts,
            "WIN-PROC-001",
            "Script interpreter network activity",
            "medium",
            0.55,
            "Execution",
            "Command and Scripting Interpreter",
            f"{proc.get('process_name', f'pid-{pid}')} PID {pid}가 external network connection을 보유",
            event_ids,
            collected_at,
        )

    for pid, remote_ips in by_pid_remote.items():
        if len(remote_ips) >= 4:
            proc = processes.get(pid, {})
            add_alert(
                alerts,
                "WIN-NET-003",
                "단일 process remote fan-out",
                "medium",
                0.52,
                "Command and Control",
                "Application Layer Protocol",
                f"{proc.get('process_name', f'pid-{pid}')} PID {pid}가 snapshot 시점에 {len(remote_ips)}개 remote IP와 연결됨",
                by_pid_events[pid],
                collected_at,
            )

    for proc in processes.values():
        memory_mb = proc.get("working_set_mb")
        if memory_mb is not None and memory_mb >= 1024:
            add_alert(
                alerts,
                "WIN-PROC-002",
                "높은 memory 사용 process",
                "low",
                0.38,
                "Impact",
                "Resource Hijacking",
                f"{proc['process_name']} PID {proc['pid']} working set {memory_mb:.1f}MB 관측",
                [],
                collected_at,
            )
    return alerts


def summarize(processes: dict[int, dict[str, Any]], connections: list[dict[str, Any]], alerts: list[dict[str, Any]]) -> dict[str, Any]:
    severity_counts = Counter(alert["severity"] for alert in alerts)
    rule_counts = Counter(alert["rule_id"] for alert in alerts)
    state_counts = Counter(conn["state"] for conn in connections)
    src_class_counts = Counter(conn["src_class"] for conn in connections)
    dst_class_counts = Counter(conn["dst_class"] for conn in connections if conn["dst_class"] != "none")
    remote_ports = Counter(str(conn["dst_port"]) for conn in connections if conn["dst_port"])
    process_conn_counts = Counter(conn["process_name"] for conn in connections)
    origins = Counter(proc["process_origin"] for proc in processes.values())
    return {
        "process_count": len(processes),
        "visible_process_count": min(len(processes), MAX_VISIBLE_PROCESSES),
        "connection_count": len(connections),
        "alert_count": len(alerts),
        "listen_count": state_counts.get("LISTEN", 0),
        "established_count": state_counts.get("ESTABLISHED", 0),
        "external_connection_count": sum(1 for conn in connections if conn["dst_class"] == "external"),
        "severity_counts": dict(severity_counts),
        "rule_counts": dict(rule_counts),
        "state_counts": dict(state_counts),
        "src_class_counts": dict(src_class_counts),
        "dst_class_counts": dict(dst_class_counts),
        "remote_ports": dict(remote_ports.most_common(12)),
        "process_connection_counts": dict(process_conn_counts.most_common(14)),
        "process_origins": dict(origins),
    }


def render_dashboard(payload: dict[str, Any]) -> None:
    if not FALLBACK_TEMPLATE_PATH.exists():
        return
    template = FALLBACK_TEMPLATE_PATH.read_text(encoding="utf-8")
    title = "Windows Endpoint EDR Dashboard"
    template = template.replace("<title>Local Endpoint EDR Dashboard</title>", f"<title>{title}</title>")
    template = template.replace("Local Falcon View", "Windows Falcon View")
    template = template.replace("실제 Mac telemetry", "실제 Windows telemetry")
    template = template.replace("현재 Mac에서", "현재 Windows endpoint에서")
    template = template.replace("Mac endpoint의 Process와 Network 흐름을 관제 화면으로 본다", "Windows endpoint의 Process와 Network 흐름을 관제 화면으로 본다")
    json_blob = html.escape(json.dumps(payload, ensure_ascii=False), quote=False)
    DASHBOARD_PATH.write_text(template.replace("__TELEMETRY_JSON__", json_blob), encoding="utf-8")


def build_payload(raw: dict[str, Any], command: dict[str, Any], mode: str, render: bool) -> dict[str, Any]:
    collected_at = now_iso()
    computer = raw.get("computer") or {}
    os_info = raw.get("os") or {}
    host_name = str(computer.get("Name") or socket.gethostname() or "windows-host")
    agent_id = f"win-{stable_hash(host_name + str(os_info.get('Version')))}"
    processes = build_processes(raw)
    connections = build_connections(raw, processes, collected_at, agent_id)
    visible_processes = sorted(
        processes.values(),
        key=lambda item: (
            -len([conn for conn in connections if conn["pid"] == item["pid"]]),
            -(item.get("working_set_mb") or 0),
            item["process_name"],
        ),
    )[:MAX_VISIBLE_PROCESSES]
    visible_connections = connections[:MAX_VISIBLE_CONNECTIONS]
    alerts = build_alerts(processes, connections, collected_at)
    payload = {
        "schema_version": "windows-edr-dashboard-v1",
        "source_real": mode == "real",
        "test_mode": mode == "mock",
        "collected_at": collected_at,
        "agent": {
            "agent_id": agent_id,
            "host_label": f"windows-{agent_id[-4:]}",
            "hostname_hash": stable_hash(host_name, 16),
            "os": {
                "ProductName": os_info.get("Caption") or "Windows",
                "ProductVersion": os_info.get("Version"),
                "BuildVersion": os_info.get("BuildNumber"),
                "Platform": platform.platform(),
            },
            "computer": {
                "manufacturer": computer.get("Manufacturer"),
                "model": computer.get("Model"),
                "domain_hash": stable_hash(str(computer.get("Domain")), 10) if computer.get("Domain") else None,
            },
            "uptime": None,
            "collection_mode": "metadata_only",
        },
        "privacy": {
            "included": [
                "process name",
                "pid",
                "parent pid",
                "cpu seconds when available",
                "working set memory when available",
                "TCP local/remote IP and port",
                "TCP state",
            ],
            "excluded": [
                "command-line arguments",
                "environment variables",
                "packet payload",
                "TLS contents",
                "browser history",
                "file contents",
                "registry contents",
                "real user name",
            ],
        },
        "collection_commands": [{key: value for key, value in command.items() if key != "stdout"}],
        "summary": summarize(processes, connections, alerts),
        "alerts": alerts,
        "connections": visible_connections,
        "processes": visible_processes,
        "data_quality": {
            "connection_limit": MAX_VISIBLE_CONNECTIONS,
            "process_limit": MAX_VISIBLE_PROCESSES,
            "connection_rows_visible": len(visible_connections),
            "process_rows_visible": len(visible_processes),
            "full_connection_rows": len(connections),
            "full_process_rows": len(processes),
            "limitations": [
                "Get-NetTCPConnection snapshot은 packet/byte count를 제공하지 않아 flow_status를 unknown으로 표시함",
                "관리자 권한 없이 접근 가능한 process/socket metadata만 수집함",
                "payload, TLS 복호화, command-line arguments, registry contents는 수집하지 않음",
                "mock mode는 parser/rule/dashboard 검증용이며 Windows 실제 실행 시 source_real=true로 생성됨",
            ],
        },
    }
    if render:
        render_dashboard(payload)
    return payload


def write_payload(payload: dict[str, Any], output: Path) -> None:
    output.parent.mkdir(parents=True, exist_ok=True)
    output.write_text(json.dumps(payload, ensure_ascii=False, indent=2), encoding="utf-8")


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Collect Windows endpoint telemetry or test with a mock PowerShell JSON fixture.")
    parser.add_argument("--mock", action="store_true", help="load the default mock fixture")
    parser.add_argument("--mock-file", help="load a specific mock PowerShell-shaped JSON fixture")
    parser.add_argument("--output", default=str(JSON_PATH), help="output telemetry JSON path")
    parser.add_argument("--render-dashboard", action="store_true", help="render dashboard_windows.html from the output")
    parser.add_argument("--timeout", type=int, default=18, help="PowerShell collection timeout seconds")
    return parser.parse_args()


def main() -> int:
    args = parse_args()
    raw, command = load_raw(args)
    mode = "mock" if args.mock or args.mock_file else "real"
    if not command["ok"]:
        print(f"collection failed: {command['stderr']}", file=sys.stderr)
        return 2
    payload = build_payload(raw, command, mode, args.render_dashboard)
    output = Path(args.output)
    write_payload(payload, output)
    print(f"wrote {output}")
    if args.render_dashboard and DASHBOARD_PATH.exists():
        print(f"wrote {DASHBOARD_PATH}")
    print(
        "snapshot:",
        f"{payload['summary']['process_count']} processes,",
        f"{payload['summary']['connection_count']} TCP sockets,",
        f"{payload['summary']['alert_count']} alerts,",
        f"source_real={payload['source_real']}",
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
