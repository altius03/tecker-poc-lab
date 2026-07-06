from __future__ import annotations

import gzip
import hashlib
import json
import ssl
import urllib.error
import urllib.request
from datetime import datetime
from pathlib import Path
from typing import Any

from .config import LATEST_PIPELINE_DIR, PIPELINE_RUNS_DIR, POC_NAME


def build_pipeline_bundle(
    payload: dict[str, Any],
    *,
    ship_url: str | None = None,
    customer_id: str = "demo-customer",
    device_id: str = "",
    agent_version: str = "0.1.0",
    client_cert: str | None = None,
    client_key: str | None = None,
) -> dict[str, Any]:
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    run_dir = PIPELINE_RUNS_DIR / timestamp
    latest_dir = LATEST_PIPELINE_DIR
    run_dir.mkdir(parents=True, exist_ok=True)
    latest_dir.mkdir(parents=True, exist_ok=True)

    sanitized = _pipeline_payload(payload)
    raw = json.dumps(sanitized, ensure_ascii=False, sort_keys=True).encode("utf-8")
    compressed = gzip.compress(raw, compresslevel=6)

    latest_path = latest_dir / "telemetry_bundle.json.gz"
    run_path = run_dir / "telemetry_bundle.json.gz"
    latest_path.write_bytes(compressed)
    run_path.write_bytes(compressed)

    delivery = {
        "compression": "gzip",
        "raw_bytes": len(raw),
        "compressed_bytes": len(compressed),
        "compression_ratio": round(len(compressed) / max(1, len(raw)), 3),
        "sha256": hashlib.sha256(compressed).hexdigest(),
        "latest_bundle_path": str(latest_path),
        "run_bundle_path": str(run_path),
        "headers": _telemetry_headers(customer_id, device_id, agent_version),
        "ship_url": ship_url or "",
        "ship_status": "not_requested",
        "auth_mode": "mtls" if client_cert else "none",
    }
    if ship_url:
        delivery.update(
            _ship_bundle(
                ship_url,
                compressed,
                headers=_telemetry_headers(customer_id, device_id, agent_version),
                client_cert=client_cert,
                client_key=client_key,
            )
        )
    return delivery


def _pipeline_payload(payload: dict[str, Any]) -> dict[str, Any]:
    return {
        "status": payload.get("status"),
        "generated_at": payload.get("generated_at"),
        "summary": payload.get("summary", {}),
        "alerts": payload.get("alerts", []),
        "incidents": payload.get("incidents", []),
        "endpoint_risk": payload.get("endpoint_risk", []),
        "ai_predictions": payload.get("ai_predictions", {}),
        "response_plan": payload.get("response_plan", {}),
        "siem_analysis": payload.get("siem_analysis", {}),
        "telemetry_context": payload.get("telemetry_context", {}),
    }


def _telemetry_headers(customer_id: str, device_id: str, agent_version: str) -> dict[str, str]:
    return {
        "Content-Type": "application/json",
        "Content-Encoding": "gzip",
        "X-EDR-PoC": POC_NAME,
        "X-EDR-Agent-Version": agent_version,
        "X-EDR-Customer-Id": customer_id,
        "X-EDR-Device-Id": device_id or "unknown-device",
        "X-EDR-Envelope-Version": "2026-07-telemetry-v1",
    }


def _ship_bundle(
    ship_url: str,
    compressed: bytes,
    *,
    headers: dict[str, str],
    client_cert: str | None = None,
    client_key: str | None = None,
) -> dict[str, Any]:
    request = urllib.request.Request(
        ship_url,
        data=compressed,
        method="POST",
        headers=headers,
    )
    context = None
    if client_cert:
        context = ssl.create_default_context()
        context.load_cert_chain(certfile=client_cert, keyfile=client_key)
    try:
        with urllib.request.urlopen(request, timeout=8, context=context) as response:
            response.read()
            return {"ship_status": "sent", "ship_http_status": response.status}
    except (urllib.error.URLError, TimeoutError, OSError, ssl.SSLError) as error:
        return {"ship_status": "failed", "ship_error": str(error)}
