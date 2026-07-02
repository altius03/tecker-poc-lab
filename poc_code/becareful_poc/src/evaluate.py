import argparse
import json
import sys
from datetime import datetime
from pathlib import Path
from typing import Any

from .config import BASE_DIR
from .pipeline import process_ocr_text

FORBIDDEN_OUTPUT_PHRASES = [
    "같이 먹으면 안 됩니다",
    "복용하지 마세요",
    "위험합니다",
    "추천합니다",
]


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="Evaluate Be:Careful PoC golden cases.")
    parser.add_argument(
        "--cases-file",
        default=str(BASE_DIR / "golden_cases" / "cases.json"),
        help="Path to golden cases JSON.",
    )
    parser.add_argument(
        "--output-file",
        default=str(BASE_DIR / "outputs" / "evaluation" / "latest_report.json"),
        help="Path to write evaluation report JSON.",
    )
    args = parser.parse_args(argv)

    report = evaluate_cases(Path(args.cases_file))
    output_path = Path(args.output_file)
    output_path.parent.mkdir(parents=True, exist_ok=True)
    output_path.write_text(json.dumps(report, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")

    print(f"status={report['status']}")
    print(f"passed={report['summary']['passed_cases']}/{report['summary']['total_cases']}")
    print(f"output={output_path}")
    return 0 if report["status"] == "pass" else 1


def evaluate_cases(cases_path: Path) -> dict[str, Any]:
    cases = json.loads(cases_path.read_text(encoding="utf-8"))
    case_reports = []

    for case in cases:
        result = process_ocr_text(
            case["text"],
            input_meta={"source": "golden_case", "case_id": case["id"]},
        )
        checks = _evaluate_case(case, result)
        case_reports.append(
            {
                "case_id": case["id"],
                "description": case.get("description", ""),
                "status": "pass" if all(check["passed"] for check in checks) else "fail",
                "checks": checks,
                "actual_summary": result.get("summary", {}),
                "actual_error": result.get("error", {}),
            }
        )

    passed_cases = sum(1 for case_report in case_reports if case_report["status"] == "pass")
    total_cases = len(case_reports)

    return {
        "poc_name": "becareful",
        "evaluation_name": "rule_based_pipeline_golden_cases",
        "generated_at": datetime.now().isoformat(timespec="seconds"),
        "status": "pass" if passed_cases == total_cases else "fail",
        "summary": {
            "total_cases": total_cases,
            "passed_cases": passed_cases,
            "failed_cases": total_cases - passed_cases,
        },
        "go_no_go": _build_go_no_go(case_reports),
        "case_reports": case_reports,
    }


def _evaluate_case(case: dict[str, Any], result: dict[str, Any]) -> list[dict[str, Any]]:
    expected = case.get("expected", {})
    checks: list[dict[str, Any]] = []

    _add_check(checks, "status", result.get("status") == expected.get("status", "success"), result.get("status"))

    if result.get("status") == "success":
        names = [item["normalized_name"] for item in result["medicine_candidates"]]
        doses = [item["dose"] for item in result["medicine_candidates"]]
        durations = [item["duration"] for item in result["schedules"]]
        timings = [item["timing"] for item in result["schedules"]]
        dur_statuses = [item["status"] for item in result["dur_checks"]]

        for name in expected.get("normalized_names", []):
            _add_check(checks, f"normalized_name:{name}", name in names, names)
        for dose in expected.get("doses", []):
            _add_check(checks, f"dose:{dose}", dose in doses, doses)
        for duration in expected.get("durations", []):
            _add_check(checks, f"duration:{duration}", duration in durations, durations)
        for timing in expected.get("timing_contains", []):
            _add_check(checks, f"timing_contains:{timing}", any(timing in item for item in timings), timings)
        for status in expected.get("dur_statuses", []):
            _add_check(checks, f"dur_status:{status}", status in dur_statuses, dur_statuses)

        min_cards = expected.get("min_handoff_cards")
        if min_cards is not None:
            _add_check(
                checks,
                "min_handoff_cards",
                len(result["handoff_cards"]) >= min_cards,
                len(result["handoff_cards"]),
            )

    else:
        error_code = result.get("error", {}).get("code")
        expected_code = expected.get("error_code")
        if expected_code:
            _add_check(checks, f"error_code:{expected_code}", error_code == expected_code, error_code)

    masked_text = result.get("masked_text") or result.get("partial_result", {}).get("masked_text", "")
    for value in expected.get("masked_not_contains", []):
        _add_check(checks, f"masked_not_contains:{value}", value not in masked_text, masked_text)
    for value in expected.get("masked_contains", []):
        _add_check(checks, f"masked_contains:{value}", value in masked_text, masked_text)

    serialized_result = json.dumps(result, ensure_ascii=False)
    for phrase in FORBIDDEN_OUTPUT_PHRASES:
        _add_check(
            checks,
            f"forbidden_output_phrase_absent:{phrase}",
            phrase not in serialized_result,
            "present" if phrase in serialized_result else "absent",
        )

    return checks


def _add_check(checks: list[dict[str, Any]], name: str, passed: bool, actual: Any) -> None:
    checks.append({"name": name, "passed": passed, "actual": actual})


def _build_go_no_go(case_reports: list[dict[str, Any]]) -> dict[str, Any]:
    failed_cases = [case for case in case_reports if case["status"] == "fail"]
    if failed_cases:
        return {
            "decision": "no_go",
            "reason": "골든 케이스 자동 평가에서 실패 케이스가 있습니다.",
        }
    return {
        "decision": "conditional_go_for_next_validation",
        "reason": "더미 OCR/mock DUR 기반 골든 케이스는 통과했지만 실제 OCR/DUR API 검증은 아직 필요합니다.",
    }


if __name__ == "__main__":
    sys.exit(main())

