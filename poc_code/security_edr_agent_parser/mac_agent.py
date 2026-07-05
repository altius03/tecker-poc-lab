#!/usr/bin/env python3
"""Collect local macOS endpoint telemetry and render the static dashboard.

This intentionally collects metadata only:
- process name, pid, parent pid, cpu%, memory%
- TCP LISTEN/ESTABLISHED socket metadata from lsof
- macOS version and uptime

It does not collect command-line arguments, environment variables, payloads,
browser history, DNS history, TLS contents, file contents, or packet captures.
"""

from __future__ import annotations

import hashlib
import html
import ipaddress
import json
import os
import re
import socket
import subprocess
import sys
import time
import argparse
from collections import Counter, defaultdict
from datetime import datetime
from pathlib import Path
from typing import Any


ROOT = Path(__file__).resolve().parent
DATA_DIR = ROOT / "data"
TEMPLATE_PATH = ROOT / "dashboard_template.html"
JSON_PATH = DATA_DIR / "latest_mac_telemetry.json"
DASHBOARD_PATH = ROOT / "dashboard.html"

MAX_VISIBLE_PROCESSES = 180
MAX_VISIBLE_CONNECTIONS = 260
COMMON_REMOTE_PORTS = {22, 53, 80, 123, 443, 5228, 8009, 8384, 22000, 22067}


def now_iso() -> str:
    return datetime.now().astimezone().isoformat(timespec="seconds")


def stable_hash(value: str, length: int = 12) -> str:
    return hashlib.sha256(value.encode("utf-8")).hexdigest()[:length]


def run_command(args: list[str], timeout: int = 8) -> dict[str, Any]:
    started = time.time()
    try:
        completed = subprocess.run(
            args,
            capture_output=True,
            check=False,
            text=True,
            timeout=timeout,
        )
        return {
            "args": args,
            "ok": completed.returncode == 0,
            "returncode": completed.returncode,
            "stdout": completed.stdout,
            "stderr": completed.stderr.strip(),
            "duration_ms": round((time.time() - started) * 1000),
        }
    except Exception as exc:  # pragma: no cover - defensive for local tooling
        return {
            "args": args,
            "ok": False,
            "returncode": None,
            "stdout": "",
            "stderr": f"{type(exc).__name__}: {exc}",
            "duration_ms": round((time.time() - started) * 1000),
        }


def file_command(args: list[str], path: str | None) -> dict[str, Any] | None:
    if not path:
        return None
    started = time.time()
    try:
        text = Path(path).read_text(encoding="utf-8", errors="replace")
        return {
            "args": args,
            "ok": True,
            "returncode": 0,
            "stdout": text,
            "stderr": "",
            "duration_ms": round((time.time() - started) * 1000),
            "input_mode": "shell_wrapper",
        }
    except Exception as exc:
        return {
            "args": args,
            "ok": False,
            "returncode": None,
            "stdout": "",
            "stderr": f"{type(exc).__name__}: {exc}",
            "duration_ms": round((time.time() - started) * 1000),
            "input_mode": "shell_wrapper",
        }


def basename_from_command(command: str) -> str:
    clean = command.replace("\\x20", " ")
    if not clean:
        return "unknown"
    base = os.path.basename(clean)
    if base in {"MacOS", "Contents"}:
        return clean.split("/")[-1] or "unknown"
    return base or clean


def process_origin(command: str) -> str:
    if command.startswith("/System/") or command.startswith("/usr/libexec/"):
        return "system"
    if command.startswith("/Applications/") or ".app/Contents/" in command:
        return "application"
    if command.startswith("/usr/") or command.startswith("/bin/") or command.startswith("/sbin/"):
        return "unix"
    if command.startswith("/Users/"):
        return "user"
    if command.startswith("-"):
        return "shell"
    return "other"


def parse_ps(stdout: str) -> dict[int, dict[str, Any]]:
    processes: dict[int, dict[str, Any]] = {}
    for raw in stdout.splitlines():
        line = raw.strip()
        if not line:
            continue
        parts = line.split(None, 4)
        if len(parts) < 5:
            continue
        try:
            pid = int(parts[0])
            ppid = int(parts[1])
            cpu = float(parts[2])
            mem = float(parts[3])
        except ValueError:
            continue
        command = parts[4]
        name = basename_from_command(command)
        processes[pid] = {
            "pid": pid,
            "ppid": ppid,
            "process_name": name,
            "process_origin": process_origin(command),
            "cpu_percent": cpu,
            "mem_percent": mem,
            "command_fingerprint": stable_hash(command),
        }
    return processes


def parse_endpoint(endpoint: str) -> dict[str, Any]:
    endpoint = endpoint.strip()
    if endpoint == "*":
        return {"ip": "*", "port": None, "class": "wildcard"}
    if endpoint.startswith("[") and "]:" in endpoint:
        ip_text, port_text = endpoint[1:].split("]:", 1)
    elif ":" in endpoint:
        ip_text, port_text = endpoint.rsplit(":", 1)
    else:
        return {"ip": endpoint, "port": None, "class": classify_ip(endpoint)}
    port = int(port_text) if port_text.isdigit() else None
    return {"ip": ip_text, "port": port, "class": classify_ip(ip_text)}


def classify_ip(ip_text: str) -> str:
    if ip_text in {"*", "0.0.0.0", "::"}:
        return "wildcard"
    try:
        ip = ipaddress.ip_address(ip_text.split("%", 1)[0])
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


def parse_lsof(stdout: str, processes: dict[int, dict[str, Any]], collected_at: str, agent_id: str) -> list[dict[str, Any]]:
    connections: list[dict[str, Any]] = []
    for raw in stdout.splitlines():
        if raw.startswith("COMMAND") or not raw.strip():
            continue
        parts = raw.split(None, 8)
        if len(parts) < 9 or parts[7] != "TCP":
            continue
        command, pid_text, _user, _fd, ip_version, *_rest, name_field = parts
        try:
            pid = int(pid_text)
        except ValueError:
            continue
        status_match = re.search(r"\(([^)]+)\)$", name_field)
        status = status_match.group(1) if status_match else "UNKNOWN"
        address_part = name_field[: status_match.start()].strip() if status_match else name_field.strip()
        if "->" in address_part:
            local_text, remote_text = address_part.split("->", 1)
        else:
            local_text, remote_text = address_part, ""

        local = parse_endpoint(local_text)
        remote = parse_endpoint(remote_text) if remote_text else {"ip": None, "port": None, "class": "none"}
        proc = processes.get(pid, {})
        process_name = proc.get("process_name") or basename_from_command(command)
        source = "local_agent"
        event_id = f"flow-{len(connections) + 1:05d}"
        connections.append(
            {
                "event_id": event_id,
                "source": source,
                "agent_id": agent_id,
                "event_time": collected_at,
                "ingest_time": collected_at,
                "pid": pid,
                "process_name": process_name,
                "process_origin": proc.get("process_origin", "unknown"),
                "protocol": "TCP",
                "ip_version": ip_version,
                "state": status,
                "src_ip": local["ip"],
                "src_port": local["port"],
                "src_class": local["class"],
                "dst_ip": remote["ip"],
                "dst_port": remote["port"],
                "dst_class": remote["class"],
                "flow_status": "unknown",
                "packet_count": None,
                "byte_count": None,
                "duration_ms": None,
            }
        )
    return connections


def derive_processes_from_connections(connections: list[dict[str, Any]]) -> dict[int, dict[str, Any]]:
    derived: dict[int, dict[str, Any]] = {}
    for conn in connections:
        pid = conn["pid"]
        if pid in derived:
            continue
        derived[pid] = {
            "pid": pid,
            "ppid": None,
            "process_name": conn["process_name"],
            "process_origin": conn.get("process_origin", "unknown"),
            "cpu_percent": None,
            "mem_percent": None,
            "command_fingerprint": None,
            "derived_from": "lsof_socket_owner",
        }
    return derived


def alert(
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

    for conn in connections:
        if conn["state"] != "LISTEN":
            continue
        if conn["src_class"] == "wildcard":
            severity = "high"
            confidence = 0.74
            reason = f"{conn['process_name']} PID {conn['pid']}가 모든 interface에서 TCP {conn['src_port']} LISTEN 중"
        elif conn["src_class"] in {"private", "tailnet-cgnat"}:
            severity = "medium"
            confidence = 0.58
            reason = f"{conn['process_name']} PID {conn['pid']}가 loopback이 아닌 {conn['src_ip']}:{conn['src_port']}에서 LISTEN 중"
        else:
            continue
        alert(
            alerts,
            "NET-001",
            "외부 접근 가능 LISTEN socket",
            severity,
            confidence,
            "Discovery",
            "Network Service Discovery",
            reason,
            [conn["event_id"]],
            collected_at,
        )

    by_pid_remote: dict[int, set[str]] = defaultdict(set)
    by_pid_events: dict[int, list[str]] = defaultdict(list)
    for conn in connections:
        if conn["state"] != "ESTABLISHED" or not conn["dst_ip"]:
            continue
        if conn["dst_class"] in {"external", "private", "tailnet-cgnat"}:
            by_pid_remote[conn["pid"]].add(str(conn["dst_ip"]))
            by_pid_events[conn["pid"]].append(conn["event_id"])
        if conn["dst_class"] == "external" and conn["dst_port"] and conn["dst_port"] not in COMMON_REMOTE_PORTS:
            alert(
                alerts,
                "NET-002",
                "비표준 외부 remote port 연결",
                "medium",
                0.46,
                "Command and Control",
                "Non-Standard Port",
                f"{conn['process_name']} PID {conn['pid']}가 external {conn['dst_ip']}:{conn['dst_port']}와 ESTABLISHED 상태",
                [conn["event_id"]],
                collected_at,
            )

    for pid, remote_ips in by_pid_remote.items():
        if len(remote_ips) >= 4:
            proc = processes.get(pid, {})
            process_name = proc.get("process_name", f"pid-{pid}")
            alert(
                alerts,
                "NET-003",
                "단일 process remote fan-out",
                "medium",
                0.52,
                "Command and Control",
                "Application Layer Protocol",
                f"{process_name} PID {pid}가 snapshot 시점에 {len(remote_ips)}개 remote IP와 연결됨",
                by_pid_events[pid],
                collected_at,
            )

    for proc in sorted(processes.values(), key=lambda item: item.get("cpu_percent") or 0, reverse=True)[:20]:
        if proc.get("cpu_percent") is not None and proc["cpu_percent"] >= 20.0:
            alert(
                alerts,
                "PROC-001",
                "높은 CPU 사용 process",
                "low",
                0.38,
                "Impact",
                "Resource Hijacking",
                f"{proc['process_name']} PID {proc['pid']} CPU {proc['cpu_percent']:.1f}% 관측",
                [],
                collected_at,
            )

    return alerts


def summarize(
    processes: dict[int, dict[str, Any]],
    visible_processes: list[dict[str, Any]],
    connections: list[dict[str, Any]],
    alerts: list[dict[str, Any]],
) -> dict[str, Any]:
    severity_counts = Counter(alert["severity"] for alert in alerts)
    rule_counts = Counter(alert["rule_id"] for alert in alerts)
    state_counts = Counter(conn["state"] for conn in connections)
    src_class_counts = Counter(conn["src_class"] for conn in connections)
    dst_class_counts = Counter(conn["dst_class"] for conn in connections if conn["dst_class"] != "none")
    remote_ports = Counter(str(conn["dst_port"]) for conn in connections if conn["dst_port"])
    process_conn_counts = Counter(conn["process_name"] for conn in connections)
    origins = Counter(proc["process_origin"] for proc in visible_processes)
    return {
        "process_count": len(processes),
        "visible_process_count": len(visible_processes),
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
    template = TEMPLATE_PATH.read_text(encoding="utf-8")
    json_blob = html.escape(json.dumps(payload, ensure_ascii=False), quote=False)
    DASHBOARD_PATH.write_text(template.replace("__TELEMETRY_JSON__", json_blob), encoding="utf-8")


def stdin_command(args: list[str], enabled: bool) -> dict[str, Any] | None:
    if not enabled:
        return None
    started = time.time()
    text = sys.stdin.read()
    return {
        "args": args,
        "ok": True,
        "returncode": 0,
        "stdout": text,
        "stderr": "",
        "duration_ms": round((time.time() - started) * 1000),
        "input_mode": "stdin",
    }


def collect(args: argparse.Namespace | None = None) -> dict[str, Any]:
    collected_at = now_iso()
    hostname = socket.gethostname()
    agent_id = f"mac-{stable_hash(hostname)}"

    args = args or argparse.Namespace(ps_file=None, ps_stdin=False, lsof_file=None, sw_vers_file=None, uptime_file=None)
    ps_result = stdin_command(["ps", "-axo", "pid=,ppid=,%cpu=,%mem=,comm="], args.ps_stdin) or file_command(
        ["ps", "-axo", "pid=,ppid=,%cpu=,%mem=,comm="], args.ps_file
    ) or run_command(
        ["ps", "-axo", "pid=,ppid=,%cpu=,%mem=,comm="]
    )
    lsof_result = file_command(["lsof", "-nP", "-iTCP", "-sTCP:ESTABLISHED", "-sTCP:LISTEN"], args.lsof_file) or run_command(
        ["lsof", "-nP", "-iTCP", "-sTCP:ESTABLISHED", "-sTCP:LISTEN"]
    )
    sw_vers_result = file_command(["sw_vers"], args.sw_vers_file) or run_command(["sw_vers"])
    uptime_result = file_command(["uptime"], args.uptime_file) or run_command(["uptime"])

    processes = parse_ps(ps_result["stdout"])
    connections = parse_lsof(lsof_result["stdout"], processes, collected_at, agent_id)
    if not processes:
        processes = derive_processes_from_connections(connections)
    visible_connections = connections[:MAX_VISIBLE_CONNECTIONS]
    connected_pids = {conn["pid"] for conn in connections}
    visible_processes = sorted(
        processes.values(),
        key=lambda item: (
            item["pid"] not in connected_pids,
            -(item.get("cpu_percent") or 0),
            -(item.get("mem_percent") or 0),
            item["process_name"],
        ),
    )[:MAX_VISIBLE_PROCESSES]
    alerts = build_alerts(processes, connections, collected_at)

    os_lines = [line.split(":\t", 1) for line in sw_vers_result["stdout"].splitlines() if ":\t" in line]
    os_info = {key.strip(): value.strip() for key, value in os_lines}
    included_fields = [
        "process name",
        "pid",
        "TCP local/remote IP and port",
        "TCP state",
    ]
    if ps_result["ok"]:
        included_fields[2:2] = ["parent pid", "cpu percent", "memory percent"]
    payload = {
        "schema_version": "mac-edr-dashboard-v1",
        "source_real": True,
        "collected_at": collected_at,
        "agent": {
            "agent_id": agent_id,
            "host_label": f"local-mac-{agent_id[-4:]}",
            "hostname_hash": stable_hash(hostname, 16),
            "os": os_info,
            "uptime": uptime_result["stdout"].strip(),
            "collection_mode": "metadata_only",
        },
        "privacy": {
            "included": included_fields,
            "excluded": [
                "command-line arguments",
                "environment variables",
                "packet payload",
                "TLS contents",
                "browser history",
                "file contents",
                "DNS query history",
                "real user name",
            ],
        },
        "collection_commands": [
            {key: value for key, value in ps_result.items() if key != "stdout"},
            {key: value for key, value in lsof_result.items() if key != "stdout"},
            {key: value for key, value in sw_vers_result.items() if key != "stdout"},
            {key: value for key, value in uptime_result.items() if key != "stdout"},
        ],
        "summary": summarize(processes, visible_processes, connections, alerts),
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
                "lsof snapshot은 연결 시작 시각과 packet/byte count를 제공하지 않아 flow_status를 unknown으로 표시함",
                "sudo 권한 없이 접근 가능한 socket만 수집함",
                "payload와 TLS 복호화는 수행하지 않음",
            ]
            + ([] if ps_result["ok"] else ["현재 실행 환경에서 ps 수집이 제한되어 process 목록은 lsof socket owner 기반으로 축소됨"]),
        },
    }
    return payload


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Collect local macOS metadata and render dashboard.html")
    parser.add_argument("--ps-file", help="pre-collected ps output")
    parser.add_argument("--ps-stdin", action="store_true", help="read pre-collected ps output from stdin")
    parser.add_argument("--lsof-file", help="pre-collected lsof output")
    parser.add_argument("--sw-vers-file", help="pre-collected sw_vers output")
    parser.add_argument("--uptime-file", help="pre-collected uptime output")
    return parser.parse_args()


def main() -> None:
    DATA_DIR.mkdir(parents=True, exist_ok=True)
    payload = collect(parse_args())
    JSON_PATH.write_text(json.dumps(payload, ensure_ascii=False, indent=2), encoding="utf-8")
    render_dashboard(payload)
    print(f"wrote {JSON_PATH}")
    print(f"wrote {DASHBOARD_PATH}")
    print(
        "snapshot:",
        f"{payload['summary']['process_count']} processes,",
        f"{payload['summary']['connection_count']} TCP sockets,",
        f"{payload['summary']['alert_count']} alerts",
    )


if __name__ == "__main__":
    main()
