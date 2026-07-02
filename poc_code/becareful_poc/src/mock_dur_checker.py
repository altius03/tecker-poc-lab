from itertools import combinations
from typing import Any

MOCK_PAIR_WARNINGS = {
    frozenset({"아모잘탄정", "리피토정"}): "이 약은 같이 먹으면 안 됩니다",
}


def check_mock_dur(medicines: list[dict[str, Any]]) -> list[dict[str, Any]]:
    checks: list[dict[str, Any]] = []

    if len(medicines) < 2:
        for medicine in medicines:
            status = "lookup_needed" if medicine["confidence"] < 0.7 else "no_known_issue"
            message = "DUR 조회가 필요한 약명 후보입니다." if status == "lookup_needed" else "주의 없음"
            checks.append(_build_check(len(checks) + 1, [medicine["medicine_id"]], status, message))
        return checks

    for left, right in combinations(medicines, 2):
        pair_key = frozenset({left["normalized_name"], right["normalized_name"]})
        if pair_key in MOCK_PAIR_WARNINGS:
            status = "needs_check"
            message = MOCK_PAIR_WARNINGS[pair_key]
        elif left["confidence"] < 0.7 or right["confidence"] < 0.7:
            status = "lookup_needed"
            message = "DUR 조회가 필요한 약명 후보가 포함되어 있습니다."
        else:
            status = "no_known_issue"
            message = "주의 없음"

        checks.append(
            _build_check(
                len(checks) + 1,
                [left["medicine_id"], right["medicine_id"]],
                status,
                message,
            )
        )

    return checks


def _build_check(index: int, medicine_ids: list[str], status: str, message: str) -> dict[str, Any]:
    return {
        "check_id": f"dur-{index:03d}",
        "medicine_ids": medicine_ids,
        "status": status,
        "message": message,
        "safe_phrase": "",
    }

