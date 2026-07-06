from __future__ import annotations

from collections import Counter, defaultdict
from datetime import datetime
from ipaddress import ip_address
from typing import Any


def build_siem_analysis(result: dict[str, Any]) -> dict[str, Any]:
    events = result.get("events", [])
    alerts = result.get("alerts", [])
    incidents = result.get("incidents", [])
    endpoint_risk = result.get("endpoint_risk", [])
    summary = result.get("summary", {})

    return {
        "edr_state": _edr_state(summary, alerts, incidents),
        "time_window": _time_window(events, alerts),
        "event_type_distribution": _distribution(events, "event_type"),
        "source_distribution": _distribution(events, "source"),
        "query_findings": _query_findings(events, alerts, incidents, summary),
        "topology": _topology(events, alerts, endpoint_risk),
        "analyst_notes": _analyst_notes(summary, alerts, incidents),
    }


def _edr_state(summary: dict[str, Any], alerts: list[dict[str, Any]], incidents: list[dict[str, Any]]) -> dict[str, Any]:
    highest = int(summary.get("highest_risk_score", 0) or 0)
    critical_alerts = sum(1 for alert in alerts if alert.get("severity") == "critical")
    warning_alerts = sum(1 for alert in alerts if alert.get("severity") == "warning")
    dlq_count = int(summary.get("dlq_event_count", 0) or 0)
    if highest >= 80 or critical_alerts or incidents:
        level = "RED"
        reason = "critical endpoint risk 또는 incident가 존재합니다."
    elif highest >= 60 or warning_alerts:
        level = "AMBER"
        reason = "warning 수준 alert가 존재합니다."
    elif dlq_count:
        level = "YELLOW"
        reason = "탐지 위험은 낮지만 schema DLQ 확인이 필요합니다."
    else:
        level = "GREEN"
        reason = "현재 sample window에서는 고위험 alert가 없습니다."
    return {
        "level": level,
        "reason": reason,
        "highest_risk_score": highest,
        "critical_alert_count": critical_alerts,
        "warning_alert_count": warning_alerts,
        "dlq_event_count": dlq_count,
    }


def _time_window(events: list[dict[str, Any]], alerts: list[dict[str, Any]]) -> dict[str, Any]:
    values = [item.get("event_time") for item in [*events, *alerts] if item.get("event_time")]
    parsed = sorted(_parse_time(value) for value in values)
    if not parsed:
        return {"first_event_at": "", "last_event_at": "", "duration_minutes": 0}
    duration = int((parsed[-1] - parsed[0]).total_seconds() // 60)
    return {
        "first_event_at": parsed[0].isoformat(),
        "last_event_at": parsed[-1].isoformat(),
        "duration_minutes": duration,
    }


def _distribution(events: list[dict[str, Any]], field: str) -> list[dict[str, Any]]:
    counter = Counter(str(event.get(field) or "unknown") for event in events)
    return [{"name": name, "count": count} for name, count in counter.most_common()]


def _query_findings(
    events: list[dict[str, Any]],
    alerts: list[dict[str, Any]],
    incidents: list[dict[str, Any]],
    summary: dict[str, Any],
) -> list[dict[str, Any]]:
    rules = Counter(alert.get("rule_id") for alert in alerts)
    findings = [
        {
            "query_id": "Q001",
            "title": "악성 destination 접속",
            "severity": _severity_for_count(rules.get("R001", 0), "critical"),
            "count": rules.get("R001", 0),
            "logic": "DNS, network, L7 event의 domain/IP를 threat signature와 비교합니다.",
        },
        {
            "query_id": "Q002",
            "title": "다운로드 -> 실행 -> C2 -> 유출 chain",
            "severity": "critical" if incidents else "info",
            "count": len(incidents),
            "logic": "file_download, process_start, beaconing, large outbound transfer를 host별 시간순으로 연결합니다.",
        },
        {
            "query_id": "Q003",
            "title": "대용량 outbound transfer",
            "severity": _severity_for_count(rules.get("R005", 0) + rules.get("R008", 0), "warning"),
            "count": rules.get("R005", 0) + rules.get("R008", 0),
            "logic": "bytes_out, VPN 상태, destination ASN을 함께 확인합니다.",
        },
        {
            "query_id": "Q004",
            "title": "L7 decrypted metadata policy hit",
            "severity": _severity_for_count(rules.get("R009", 0) + rules.get("R010", 0), "suspicious"),
            "count": rules.get("R009", 0) + rules.get("R010", 0),
            "logic": "복호화된 URL, app action, URL category를 policy/signature와 비교합니다.",
        },
        {
            "query_id": "Q005",
            "title": "수집 품질 DLQ",
            "severity": _severity_for_count(int(summary.get("dlq_event_count", 0) or 0), "warning"),
            "count": int(summary.get("dlq_event_count", 0) or 0),
            "logic": "필수 field 누락, 지원하지 않는 event_type, datetime 오류를 추적합니다.",
        },
    ]
    return findings


def _topology(
    events: list[dict[str, Any]],
    alerts: list[dict[str, Any]],
    endpoint_risk: list[dict[str, Any]],
) -> dict[str, Any]:
    risk_by_host = {row["host_id"]: row for row in endpoint_risk}
    alerted_event_ids = {event_id for alert in alerts for event_id in alert.get("event_ids", [])}
    nodes: dict[str, dict[str, Any]] = {}
    edges: dict[tuple[str, str], dict[str, Any]] = {}

    for event in events:
        host = event.get("host_id") or "unknown-host"
        host_row = risk_by_host.get(host, {})
        _ensure_node(
            nodes,
            host,
            {
                "id": host,
                "label": host,
                "group": "computer",
                "status": _status_from_severity(host_row.get("severity")),
                "risk_score": host_row.get("risk_score", 0),
            },
        )

        destination = event.get("domain") or event.get("dst_ip")
        if not destination:
            continue
        destination = str(destination)
        group = "inside" if _is_internal_destination(destination) else "outside"
        node_id = "우리 내부 서비스" if group == "inside" else destination
        status = "alert" if event.get("event_id") in alerted_event_ids else "not_detected"
        _ensure_node(
            nodes,
            node_id,
            {
                "id": node_id,
                "label": node_id,
                "group": group,
                "status": status,
                "risk_score": 0,
            },
        )
        key = (host, node_id)
        if key not in edges:
            edges[key] = {
                "source": host,
                "target": node_id,
                "event_count": 0,
                "bytes_out": 0,
                "status": "not_detected",
            }
        edges[key]["event_count"] += 1
        edges[key]["bytes_out"] += int(event.get("bytes_out") or 0)
        if status == "alert":
            edges[key]["status"] = "alert"

    return {
        "nodes": list(nodes.values()),
        "edges": sorted(edges.values(), key=lambda row: (row["source"], row["target"])),
    }


def _analyst_notes(summary: dict[str, Any], alerts: list[dict[str, Any]], incidents: list[dict[str, Any]]) -> list[str]:
    notes: list[str] = []
    if incidents:
        notes.append("다운로드, 실행, C2, 유출로 이어지는 attack chain 후보가 있습니다.")
    if any(alert.get("rule_id") in {"R009", "R010"} for alert in alerts):
        notes.append("L7 metadata에서 URL 또는 application action 기반 policy hit가 발생했습니다.")
    if int(summary.get("dlq_event_count", 0) or 0):
        notes.append("DLQ event가 있어 agent producer 또는 parser schema mapping 검토가 필요합니다.")
    if not notes:
        notes.append("현재 window에서는 고위험 분석 근거가 제한적입니다.")
    return notes


def _ensure_node(nodes: dict[str, dict[str, Any]], node_id: str, node: dict[str, Any]) -> None:
    if node_id not in nodes:
        nodes[node_id] = node
        return
    if node.get("status") == "alert":
        nodes[node_id]["status"] = "alert"
    nodes[node_id]["risk_score"] = max(int(nodes[node_id].get("risk_score") or 0), int(node.get("risk_score") or 0))


def _is_internal_destination(value: str) -> bool:
    if value.endswith(".company.test"):
        return True
    try:
        return ip_address(value).is_private
    except ValueError:
        return False


def _severity_for_count(count: int, severity_when_present: str) -> str:
    return severity_when_present if count else "info"


def _status_from_severity(severity: str | None) -> str:
    if severity in {"critical", "warning", "suspicious"}:
        return "alert"
    return "not_detected"


def _parse_time(value: str) -> datetime:
    return datetime.fromisoformat(value.replace("Z", "+00:00"))
