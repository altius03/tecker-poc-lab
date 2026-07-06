from __future__ import annotations

import compileall
import json
import subprocess
import sys
from datetime import datetime
from pathlib import Path
from typing import Any


BASE_DIR = Path(__file__).resolve().parents[1]
LATEST_RESULT_PATH = BASE_DIR / "outputs" / "latest" / "result.json"
VERIFICATION_DIR = BASE_DIR / "outputs" / "verification"
DASHBOARD_INDEX_PATH = BASE_DIR / "dashboard" / "index.html"
DASHBOARD_DATA_PATH = BASE_DIR / "dashboard" / "data" / "latest-result.js"
LATEST_REPORT_MD_PATH = BASE_DIR / "outputs" / "reports" / "latest" / "security_report.md"
LATEST_REPORT_HTML_PATH = BASE_DIR / "outputs" / "reports" / "latest" / "security_report.html"
LATEST_PIPELINE_BUNDLE_PATH = BASE_DIR / "outputs" / "pipeline" / "latest" / "telemetry_bundle.json.gz"


def main() -> int:
    checks: list[dict[str, Any]] = []
    checks.append(_check_compile())
    checks.append(_check_unit_tests())
    checks.append(_check_cli_default_run())
    result = _read_latest_result()
    checks.append(_check_result_contract(result))
    checks.append(_check_dashboard_artifacts())
    checks.append(_check_report_artifacts(result))
    checks.append(_check_pipeline_artifacts(result))

    report = _build_report(checks, result)
    paths = _write_report(report)
    _print_summary(report, paths)
    return 1 if any(check["status"] == "fail" for check in checks) else 0


def _check_compile() -> dict[str, Any]:
    ok = compileall.compile_dir(str(BASE_DIR / "src"), quiet=1, force=True)
    return {
        "name": "python_compile",
        "status": "pass" if ok else "fail",
        "details": "src modules compile successfully." if ok else "At least one src module failed to compile.",
    }


def _check_unit_tests() -> dict[str, Any]:
    completed = subprocess.run(
        [sys.executable, "-m", "unittest", "discover", "-s", "tests"],
        cwd=BASE_DIR,
        text=True,
        capture_output=True,
        timeout=30,
    )
    return {
        "name": "unit_tests",
        "status": "pass" if completed.returncode == 0 else "fail",
        "details": (completed.stdout + completed.stderr).strip(),
    }


def _check_cli_default_run() -> dict[str, Any]:
    completed = subprocess.run(
        [sys.executable, "-m", "src.run"],
        cwd=BASE_DIR,
        text=True,
        capture_output=True,
        timeout=30,
    )
    return {
        "name": "cli_default_run",
        "status": "pass" if completed.returncode == 0 else "fail",
        "details": {
            "returncode": completed.returncode,
            "stdout": completed.stdout.strip(),
            "stderr": completed.stderr.strip(),
        },
    }


def _check_result_contract(result: dict[str, Any]) -> dict[str, Any]:
    failures: list[str] = []
    if result.get("status") != "success":
        failures.append(f"status is {result.get('status')!r}, expected success")
    if result.get("decision") != "needs_security_review":
        failures.append(f"decision is {result.get('decision')!r}, expected needs_security_review")

    summary = result.get("summary", {})
    if summary.get("input_event_count", 0) < 50:
        failures.append("input_event_count below 50")
    if summary.get("valid_event_count", 0) < 50:
        failures.append("valid_event_count below 50")
    if summary.get("dlq_event_count", 0) < 1:
        failures.append("invalid event was not sent to DLQ")
    if summary.get("alert_count", 0) < 8:
        failures.append("alert_count below expected rule coverage")
    if summary.get("l7_event_count", 0) < 2:
        failures.append("L7 event coverage missing")
    if summary.get("decryption_event_count", 0) < 1:
        failures.append("decryption event coverage missing")
    if summary.get("response_action_count", 0) < 1:
        failures.append("response actions were not generated")
    if summary.get("ai_prediction_count", 0) < 1:
        failures.append("AI predictions were not generated")

    rules = {alert.get("rule_id") for alert in result.get("alerts", [])}
    for rule_id in {"R001", "R002", "R003", "R004", "R005", "R006", "R007", "R008", "R009", "R010", "R011"}:
        if rule_id not in rules:
            failures.append(f"missing rule alert: {rule_id}")

    incident_tactics = {
        mapping.get("tactic")
        for incident in result.get("incidents", [])
        for mapping in incident.get("mitre_mapping", [])
    }
    for tactic in {"Initial Access", "Execution", "Command and Control", "Exfiltration"}:
        if tactic not in incident_tactics:
            failures.append(f"missing MITRE tactic: {tactic}")

    serialized = json.dumps(result, ensure_ascii=False)
    if (
        "김테커" in serialized
        or "private message body should never be retained" in serialized
        or "sample body must be removed" in serialized
        or "이 메시지 본문" in serialized
    ):
        failures.append("privacy-sensitive sample value leaked into result")

    return {
        "name": "result_contract",
        "status": "pass" if not failures else "fail",
        "details": "result JSON satisfies PoC contract." if not failures else failures,
    }


def _check_dashboard_artifacts() -> dict[str, Any]:
    failures: list[str] = []
    if not DASHBOARD_INDEX_PATH.exists():
        failures.append(f"missing dashboard index: {DASHBOARD_INDEX_PATH}")
    if not DASHBOARD_DATA_PATH.exists():
        failures.append(f"missing dashboard data script: {DASHBOARD_DATA_PATH}")
    elif "window.SIEM_RESULT" not in DASHBOARD_DATA_PATH.read_text(encoding="utf-8"):
        failures.append("dashboard data script does not define window.SIEM_RESULT")

    return {
        "name": "dashboard_artifacts",
        "status": "pass" if not failures else "fail",
        "details": "dashboard index and latest-result.js are present." if not failures else failures,
    }


def _check_report_artifacts(result: dict[str, Any]) -> dict[str, Any]:
    failures: list[str] = []
    if not LATEST_REPORT_MD_PATH.exists():
        failures.append(f"missing report markdown: {LATEST_REPORT_MD_PATH}")
    elif "Security EDR Agent Parser 분석 보고서" not in LATEST_REPORT_MD_PATH.read_text(encoding="utf-8"):
        failures.append("markdown report title is missing")
    if not LATEST_REPORT_HTML_PATH.exists():
        failures.append(f"missing report html: {LATEST_REPORT_HTML_PATH}")
    elif "<html" not in LATEST_REPORT_HTML_PATH.read_text(encoding="utf-8"):
        failures.append("html report is not valid-looking HTML")
    if not result.get("report"):
        failures.append("result JSON does not include report paths")

    return {
        "name": "report_artifacts",
        "status": "pass" if not failures else "fail",
        "details": "latest Markdown/HTML reports are present." if not failures else failures,
    }


def _check_pipeline_artifacts(result: dict[str, Any]) -> dict[str, Any]:
    failures: list[str] = []
    delivery = result.get("pipeline_delivery", {})
    if not delivery:
        failures.append("result JSON does not include pipeline_delivery")
    if not LATEST_PIPELINE_BUNDLE_PATH.exists():
        failures.append(f"missing gzip pipeline bundle: {LATEST_PIPELINE_BUNDLE_PATH}")
    elif LATEST_PIPELINE_BUNDLE_PATH.stat().st_size <= 0:
        failures.append("gzip pipeline bundle is empty")
    if delivery.get("compression") != "gzip":
        failures.append("pipeline compression is not gzip")

    return {
        "name": "pipeline_artifacts",
        "status": "pass" if not failures else "fail",
        "details": "gzip telemetry bundle is present." if not failures else failures,
    }


def _read_latest_result() -> dict[str, Any]:
    if not LATEST_RESULT_PATH.exists():
        return {}
    return json.loads(LATEST_RESULT_PATH.read_text(encoding="utf-8"))


def _build_report(checks: list[dict[str, Any]], result: dict[str, Any]) -> dict[str, Any]:
    has_fail = any(check["status"] == "fail" for check in checks)
    return {
        "generated_at": datetime.now().isoformat(timespec="seconds"),
        "poc_name": "security_edr_agent_parser",
        "decision": "local_poc_passed_with_advanced_modules" if not has_fail else "local_validation_failed",
        "checks": checks,
        "result_summary": result.get("summary", {}),
        "dashboard": result.get("dashboard", {}),
        "report": result.get("report", {}),
        "codex_completed": [
            "offline event file loader with generated sample flows",
            "schema validation and DLQ result preservation",
            "privacy-sensitive field removal and pattern masking",
            "rule-based detection R001-R008",
            "advanced detection R009-R011 for L7 URL, application action, and malware hash",
            "MITRE ATT&CK attack-chain mapping",
            "PCAP TCP flow analyzer and decrypted L7 proxy-log ingestion",
            "dry-run response plan generation",
            "AI-style host risk prediction",
            "gzip telemetry pipeline bundle",
            "static SIEM dashboard fed by latest CLI result",
            "Markdown and HTML report artifacts generated from latest result",
        ],
        "next_user_required": [
            "Run the macOS agent on an actual Mac if packet-capture validation is required.",
            "Use an approved local proxy/CA setup before collecting decrypted HTTPS metadata in a real environment.",
            "Review false-positive tolerance with security scenario owners.",
        ],
    }


def _write_report(report: dict[str, Any]) -> dict[str, str]:
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    run_dir = VERIFICATION_DIR / "runs" / timestamp
    latest_path = VERIFICATION_DIR / "latest_verification.json"
    run_path = run_dir / "verification.json"
    run_dir.mkdir(parents=True, exist_ok=True)
    VERIFICATION_DIR.mkdir(parents=True, exist_ok=True)

    payload = json.dumps(report, ensure_ascii=False, indent=2)
    run_path.write_text(payload + "\n", encoding="utf-8")
    latest_path.write_text(payload + "\n", encoding="utf-8")
    return {"latest": str(latest_path), "run": str(run_path)}


def _print_summary(report: dict[str, Any], paths: dict[str, str]) -> None:
    summary = {
        "decision": report["decision"],
        "checks": {check["name"]: check["status"] for check in report["checks"]},
        "latest": paths["latest"],
        "run": paths["run"],
    }
    print(json.dumps(summary, ensure_ascii=False, indent=2))


if __name__ == "__main__":
    sys.exit(main())
