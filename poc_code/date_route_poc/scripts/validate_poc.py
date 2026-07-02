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
BENCHMARK_PATH = BASE_DIR / "samples" / "benchmark_queries.json"
LATEST_RESULT_PATH = BASE_DIR / "outputs" / "latest" / "result.json"
VERIFICATION_DIR = BASE_DIR / "outputs" / "verification"

REQUIRED_SUCCESS_KEYS = {
    "poc_name",
    "status",
    "input",
    "modules_run",
    "summary",
    "parsed_conditions",
    "region_center",
    "distance_filter_skipped",
    "provider_mode",
    "candidate_places",
    "filtered_places",
    "route",
    "explanations",
    "directions",
    "risks_verified",
    "limitations",
    "fallback_used",
    "fallback_reason",
}
REQUIRED_FAILURE_KEYS = {"poc_name", "status", "input", "modules_run", "error", "partial_result", "limitations"}
REQUIRED_PLACE_KEYS = {
    "place_id",
    "name",
    "category",
    "address",
    "x",
    "y",
    "phone",
    "place_url",
    "distance_m",
    "source",
    "matched_keywords",
}
REQUIRED_ROUTE_KEYS = {"order", "place_id", "name", "role", "estimated_stay_minutes", "selection_reason"}
REQUIRED_DIRECTION_KEYS = {"provider", "url", "verification_status", "note"}
FORBIDDEN_STATIC_PATTERNS = [
    "maps.googleapis.com",
    "places.googleapis.com",
    "routes.googleapis.com",
    "googleapis.com/maps",
]


def main(argv: list[str] | None = None) -> int:
    args = _parse_args(argv)
    checks: list[dict[str, Any]] = []
    benchmark_results: list[dict[str, Any]] = []
    benchmark_cases = _load_benchmark_cases()

    checks.append(_check_compile())
    checks.append(_check_unit_tests())
    checks.append(_check_forbidden_static_patterns())

    for case in benchmark_cases:
        result = _run_cli(case["query"], use_sample=True, force_missing_key=False)
        assessment = _assess_success_result(result.get("result"), case)
        benchmark_results.append({"id": case["id"], "query": case["query"], **assessment})

    checks.append(_summarize_benchmark(benchmark_results))
    checks.append(_check_missing_api_key_failure())

    real_api_results: list[dict[str, Any]] = []
    if args.real_api:
        real_api_results = _run_real_api_smoke(benchmark_cases[: args.real_api_limit])
        real_api_summary = _summarize_real_api(real_api_results)
        checks.append(real_api_summary)
        if real_api_summary["status"] == "blocked":
            checks.append(_restore_sample_latest_result(benchmark_cases[0]))
    else:
        checks.append(
            {
                "name": "real_kakao_api_smoke",
                "status": "blocked",
                "details": "Not run. Pass --real-api after adding KAKAO_REST_API_KEY to .env.",
            }
        )
        checks.append(_restore_sample_latest_result(benchmark_cases[0]))

    report = _build_report(checks, benchmark_results, real_api_results)
    paths = _write_report(report)
    _print_summary(report, paths)

    hard_fail = any(check["status"] == "fail" for check in checks)
    return 1 if hard_fail else 0


def _parse_args(argv: list[str] | None) -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Validate local PoC readiness gates.")
    parser.add_argument("--real-api", action="store_true", help="Run smoke tests against real Kakao Local API.")
    parser.add_argument("--real-api-limit", type=int, default=3, help="Number of benchmark queries to run with real Kakao API.")
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


def _check_forbidden_static_patterns() -> dict[str, Any]:
    hits: list[str] = []
    for path in (BASE_DIR / "src").glob("*.py"):
        text = path.read_text(encoding="utf-8")
        for pattern in FORBIDDEN_STATIC_PATTERNS:
            if pattern in text:
                hits.append(f"{path.name}: {pattern}")

    return {
        "name": "no_google_places_routes_actual_call",
        "status": "pass" if not hits else "fail",
        "details": "No Google Places/Routes API hostnames found in src." if not hits else hits,
    }


def _load_benchmark_cases() -> list[dict[str, Any]]:
    return json.loads(BENCHMARK_PATH.read_text(encoding="utf-8"))


def _run_cli(query: str, *, use_sample: bool, force_missing_key: bool) -> dict[str, Any]:
    env = os.environ.copy()
    if force_missing_key:
        env["KAKAO_REST_API_KEY"] = ""

    command = [sys.executable, "-m", "src.run", "--query", query]
    if use_sample:
        command.append("--use-sample")

    completed = subprocess.run(
        command,
        cwd=BASE_DIR,
        text=True,
        capture_output=True,
        timeout=45,
        env=env,
    )
    result = _read_latest_result()
    return {
        "returncode": completed.returncode,
        "stdout": completed.stdout.strip(),
        "stderr": completed.stderr.strip(),
        "result": result,
    }


def _read_latest_result() -> dict[str, Any]:
    if not LATEST_RESULT_PATH.exists():
        return {}
    return json.loads(LATEST_RESULT_PATH.read_text(encoding="utf-8"))


def _assess_success_result(cli_result: dict[str, Any] | None, case: dict[str, Any]) -> dict[str, Any]:
    result = cli_result or {}
    failures: list[str] = []

    if result.get("status") != "success":
        failures.append(f"status is {result.get('status')!r}, expected 'success'")
        return {"status": "fail", "failures": failures, "summary": result.get("summary", {})}

    missing_keys = sorted(REQUIRED_SUCCESS_KEYS - set(result.keys()))
    if missing_keys:
        failures.append(f"missing success keys: {missing_keys}")

    summary = result.get("summary", {})
    if summary.get("parsed_condition_count", 0) < 5:
        failures.append("parsed_condition_count below 5")
    if summary.get("candidate_place_count", 0) < 5:
        failures.append("candidate_place_count below 5")
    if summary.get("filtered_place_count", 0) < 5:
        failures.append("filtered_place_count below 5")
    if not 2 <= summary.get("route_stop_count", 0) <= 4:
        failures.append("route_stop_count outside 2..4")
    if summary.get("directions_url_count", 0) < summary.get("route_stop_count", 0):
        failures.append("directions_url_count below route_stop_count")

    parsed = result.get("parsed_conditions", {})
    if case.get("expected_region") and parsed.get("region") != case["expected_region"]:
        failures.append(f"expected region {case['expected_region']!r}, got {parsed.get('region')!r}")

    candidate_places = result.get("candidate_places", [])
    for index, place in enumerate(candidate_places):
        missing_place_keys = sorted(REQUIRED_PLACE_KEYS - set(place.keys()))
        if missing_place_keys:
            failures.append(f"candidate_places[{index}] missing keys: {missing_place_keys}")
            break

    route = result.get("route", [])
    if len(route) < case.get("expected_min_stops", 2):
        failures.append(f"route has {len(route)} stops, expected at least {case.get('expected_min_stops', 2)}")
    for index, stop in enumerate(route):
        missing_route_keys = sorted(REQUIRED_ROUTE_KEYS - set(stop.keys()))
        if missing_route_keys:
            failures.append(f"route[{index}] missing keys: {missing_route_keys}")
            break

    route_roles = [stop.get("role") for stop in route]
    role_rank = {"meal": 0, "cafe": 1, "walk_photo": 2, "extra": 3}
    ranked = [role_rank.get(role, 99) for role in route_roles]
    if ranked != sorted(ranked):
        failures.append(f"route role order is not stable: {route_roles}")

    directions = result.get("directions", [])
    for index, direction in enumerate(directions):
        missing_direction_keys = sorted(REQUIRED_DIRECTION_KEYS - set(direction.keys()))
        if missing_direction_keys:
            failures.append(f"directions[{index}] missing keys: {missing_direction_keys}")
            break
        if direction.get("provider") == "google_maps_url" and direction.get("verification_status") != "not_verified":
            failures.append("google_maps_url direction must remain not_verified")

    if result.get("fallback_used") is not True or result.get("fallback_reason") != "explicit_use_sample":
        failures.append("sample run fallback flags are not explicit")

    return {
        "status": "pass" if not failures else "fail",
        "failures": failures,
        "summary": summary,
        "route_roles": route_roles,
    }


def _summarize_benchmark(benchmark_results: list[dict[str, Any]]) -> dict[str, Any]:
    failed = [item for item in benchmark_results if item["status"] != "pass"]
    return {
        "name": "sample_benchmark",
        "status": "pass" if not failed else "fail",
        "details": {
            "total": len(benchmark_results),
            "passed": len(benchmark_results) - len(failed),
            "failed_ids": [item["id"] for item in failed],
        },
    }


def _check_missing_api_key_failure() -> dict[str, Any]:
    cli_result = _run_cli("성수역 근처 데이트 코스 짜줘", use_sample=False, force_missing_key=True)
    result = cli_result["result"]
    failures: list[str] = []

    if cli_result["returncode"] == 0:
        failures.append("CLI returned success when API key was forced missing")
    if result.get("status") != "failed":
        failures.append(f"status is {result.get('status')!r}, expected 'failed'")
    missing_failure_keys = sorted(REQUIRED_FAILURE_KEYS - set(result.keys()))
    if missing_failure_keys:
        failures.append(f"missing failure keys: {missing_failure_keys}")
    if result.get("error", {}).get("code") != "MISSING_API_KEY":
        failures.append(f"error.code is {result.get('error', {}).get('code')!r}, expected MISSING_API_KEY")

    return {
        "name": "missing_api_key_failure_json",
        "status": "pass" if not failures else "fail",
        "details": "MISSING_API_KEY failure JSON is written." if not failures else failures,
    }


def _run_real_api_smoke(cases: list[dict[str, Any]]) -> list[dict[str, Any]]:
    results: list[dict[str, Any]] = []
    for case in cases:
        cli_result = _run_cli(case["query"], use_sample=False, force_missing_key=False)
        result = cli_result["result"]
        if result.get("status") == "failed" and result.get("error", {}).get("code") == "MISSING_API_KEY":
            results.append({"id": case["id"], "status": "blocked", "reason": "MISSING_API_KEY"})
            continue
        if _is_kakao_permission_blocked(result):
            results.append(
                {
                    "id": case["id"],
                    "status": "blocked",
                    "reason": "KAKAO_LOCAL_SERVICE_DISABLED",
                    "error": result.get("error", {}),
                }
            )
            continue
        assessment = _assess_real_api_result(result, case)
        results.append({"id": case["id"], "query": case["query"], **assessment})
    return results


def _is_kakao_permission_blocked(result: dict[str, Any]) -> bool:
    if result.get("status") != "failed":
        return False
    error = result.get("error", {})
    if error.get("code") != "API_REQUEST_FAILED":
        return False
    message = str(error.get("message") or "")
    return "NotAuthorizedError" in message or "disabled OPEN_MAP_AND_LOCAL service" in message


def _assess_real_api_result(result: dict[str, Any], case: dict[str, Any]) -> dict[str, Any]:
    if result.get("status") != "success":
        return {
            "status": "fail",
            "failures": [f"real API result status is {result.get('status')!r}"],
            "error": result.get("error", {}),
            "summary": result.get("summary", {}),
            "route_roles": [],
        }
    fake_sample_flags = {**result, "fallback_used": True, "fallback_reason": "explicit_use_sample"}
    base = _assess_success_result(fake_sample_flags, case)
    failures = [failure for failure in base["failures"] if "sample run fallback flags" not in failure]
    if result.get("fallback_used") is not False:
        failures.append("real API run must not use fallback")
    if any(place.get("source") != "kakao_local_api" for place in result.get("candidate_places", [])):
        failures.append("real API run includes non-kakao source candidates")
    return {
        "status": "pass" if not failures else "fail",
        "failures": failures,
        "summary": result.get("summary", {}),
        "route_roles": [stop.get("role") for stop in result.get("route", [])],
    }


def _summarize_real_api(real_api_results: list[dict[str, Any]]) -> dict[str, Any]:
    if any(item["status"] == "blocked" for item in real_api_results):
        return {
            "name": "real_kakao_api_smoke",
            "status": "blocked",
            "details": real_api_results,
        }
    failed = [item for item in real_api_results if item["status"] != "pass"]
    return {
        "name": "real_kakao_api_smoke",
        "status": "pass" if not failed else "fail",
        "details": real_api_results,
    }


def _restore_sample_latest_result(case: dict[str, Any]) -> dict[str, Any]:
    cli_result = _run_cli(case["query"], use_sample=True, force_missing_key=False)
    result = cli_result["result"]
    ok = cli_result["returncode"] == 0 and result.get("status") == "success" and result.get("fallback_used") is True
    return {
        "name": "latest_result_restored_to_sample_success",
        "status": "pass" if ok else "fail",
        "details": "outputs/latest/result.json restored to a sample success result." if ok else result,
    }


def _build_report(
    checks: list[dict[str, Any]],
    benchmark_results: list[dict[str, Any]],
    real_api_results: list[dict[str, Any]],
) -> dict[str, Any]:
    has_fail = any(check["status"] == "fail" for check in checks)
    real_api_check = next((check for check in checks if check["name"] == "real_kakao_api_smoke"), None)
    if has_fail:
        decision = "local_validation_failed"
    elif real_api_check and real_api_check["status"] == "pass":
        decision = "technical_poc_passed_pending_human_quality_review"
    else:
        decision = "local_poc_passed_blocked_by_real_api_and_human_quality_review"

    return {
        "generated_at": datetime.now().isoformat(timespec="seconds"),
        "poc_name": "date_route",
        "decision": decision,
        "checks": checks,
        "sample_benchmark_results": benchmark_results,
        "real_api_results": real_api_results,
        "codex_completed": [
            "sample-mode end-to-end benchmark",
            "success JSON schema shape checks",
            "failure JSON check for missing API key",
            "unit tests for parser/filter/route/directions/failure schema",
            "static scan confirming no Google Places/Routes API hostnames in src",
        ],
        "user_required": [
            "Add a real Kakao Local REST API key to .env.",
            "Run: uv run python scripts/validate_poc.py --real-api",
            "Open outputs/verification/latest_verification.json and outputs/latest/result.json.",
            "Manually judge whether the real Kakao places and route order are acceptable for a date-course product.",
            "Click generated Kakao/Google Maps candidate URLs and confirm they are usable enough for the intended demo.",
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
