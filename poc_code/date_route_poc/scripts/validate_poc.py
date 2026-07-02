from __future__ import annotations

import argparse
import compileall
import json
import os
import subprocess
import sys
from datetime import datetime
from pathlib import Path
from typing import Any


BASE_DIR = Path(__file__).resolve().parents[1]
LATEST_RESULT_PATH = BASE_DIR / "outputs" / "latest" / "result.json"
VERIFICATION_DIR = BASE_DIR / "outputs" / "verification"


def main(argv: list[str] | None = None) -> int:
    args = _parse_args(argv)
    checks: list[dict[str, Any]] = []

    checks.append(_check_compile())
    checks.append(_check_unit_tests())

    if args.real_api:
        checks.append(_check_real_api(args.query))
    else:
        checks.append(
            {
                "name": "real_google_openai_smoke",
                "status": "blocked",
                "details": "Not run. Pass --real-api after setting GOOGLE_MAPS_API_KEY and OPENAI_API_KEY in .env.",
            }
        )

    report = {
        "generated_at": datetime.now().isoformat(timespec="seconds"),
        "poc_name": "date_route_google_places_data_gap",
        "decision": _decision(checks),
        "checks": checks,
    }
    paths = _write_report(report)
    print(json.dumps({"decision": report["decision"], "checks": {c["name"]: c["status"] for c in checks}, **paths}, ensure_ascii=False, indent=2))
    return 1 if any(check["status"] == "fail" for check in checks) else 0


def _parse_args(argv: list[str] | None) -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Validate date-route Google Places/OpenAI PoC.")
    parser.add_argument("--real-api", action="store_true", help="Run one real Google Places + OpenAI smoke test.")
    parser.add_argument(
        "--query",
        default="성수역 근처에서 조용한 파스타집이랑 디저트 카페, 예산 12만 원 안쪽, 도보 이동 가능한 코스로 짜줘",
        help="Natural-language query for real API smoke test.",
    )
    return parser.parse_args(argv)


def _check_compile() -> dict[str, Any]:
    ok = compileall.compile_dir(str(BASE_DIR / "src"), quiet=1, force=True)
    return {
        "name": "python_compile",
        "status": "pass" if ok else "fail",
        "details": "src modules compile successfully." if ok else "At least one src module failed to compile.",
    }


def _check_unit_tests() -> dict[str, Any]:
    completed = subprocess.run(
        [sys.executable, "-m", "unittest", "-q"],
        cwd=BASE_DIR,
        text=True,
        capture_output=True,
        timeout=60,
    )
    return {
        "name": "unit_tests",
        "status": "pass" if completed.returncode == 0 else "fail",
        "details": (completed.stdout + completed.stderr).strip(),
    }


def _check_real_api(query: str) -> dict[str, Any]:
    if not _has_env_key("GOOGLE_MAPS_API_KEY") or not _has_env_key("OPENAI_API_KEY"):
        return {
            "name": "real_google_openai_smoke",
            "status": "blocked",
            "details": "GOOGLE_MAPS_API_KEY and OPENAI_API_KEY are required in .env.",
        }

    completed = subprocess.run(
        [sys.executable, "-m", "src.run", "--query", query],
        cwd=BASE_DIR,
        text=True,
        capture_output=True,
        timeout=120,
    )
    result = _read_latest_result()
    failures = _assess_result(result)
    if completed.returncode != 0:
        failures.append(f"CLI returned {completed.returncode}: {(completed.stdout + completed.stderr).strip()}")
    return {
        "name": "real_google_openai_smoke",
        "status": "pass" if not failures else "fail",
        "details": {
            "failures": failures,
            "summary": result.get("summary", {}),
            "api_usage": result.get("api_usage", {}),
            "latest_result": str(LATEST_RESULT_PATH),
        },
    }


def _assess_result(result: dict[str, Any]) -> list[str]:
    failures: list[str] = []
    if result.get("status") != "success":
        failures.append(f"status is {result.get('status')!r}, expected success")
    required = {
        "parsed_conditions",
        "condition_capability",
        "matched_conditions",
        "unmatched_conditions",
        "fallback_log",
        "candidate_places",
        "api_usage",
    }
    missing = sorted(required - set(result.keys()))
    if missing:
        failures.append(f"missing required result keys: {missing}")
    summary = result.get("summary", {})
    if summary.get("candidate_count", 0) < 1:
        failures.append("candidate_count below 1")
    if "unsupported" not in summary.get("condition_capability", {}):
        failures.append("condition_capability should include unsupported conditions")
    return failures


def _has_env_key(name: str) -> bool:
    env_path = BASE_DIR / ".env"
    if env_path.exists():
        for raw_line in env_path.read_text(encoding="utf-8-sig").splitlines():
            line = raw_line.strip()
            if not line or line.startswith("#") or "=" not in line:
                continue
            key, value = line.split("=", 1)
            if key.strip().lstrip("\ufeff") == name and value.strip():
                return True
    return bool(os.getenv(name))


def _read_latest_result() -> dict[str, Any]:
    if not LATEST_RESULT_PATH.exists():
        return {}
    return json.loads(LATEST_RESULT_PATH.read_text(encoding="utf-8"))


def _decision(checks: list[dict[str, Any]]) -> str:
    if any(check["status"] == "fail" for check in checks):
        return "validation_failed"
    if any(check["status"] == "blocked" for check in checks):
        return "local_checks_passed_real_api_not_run"
    return "technical_poc_passed_pending_human_quality_review"


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


if __name__ == "__main__":
    sys.exit(main())
