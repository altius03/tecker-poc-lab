from __future__ import annotations

from typing import Any


UNSUPPORTED_REASON = {
    "exact_budget": "Google Places 기본 응답에는 메뉴 단위 가격 데이터가 없어 정확한 예산 조건을 검증하지 못합니다.",
    "waiting_time": "Google Places 기본 응답에는 실시간 웨이팅 정보가 없습니다.",
    "reservation": "예약 가능 여부는 장소별 외부 예약 채널 의존 정보라 안정적으로 검증하지 못합니다.",
}


def classify_condition_capability(parsed: dict[str, Any]) -> dict[str, Any]:
    items: list[dict[str, Any]] = []

    if parsed.get("region"):
        items.append(
            {
                "condition": "region",
                "value": parsed["region"],
                "status": "verifiable",
                "method": "google_places_text_search",
            }
        )

    categories = parsed.get("categories") or []
    if categories:
        items.append(
            {
                "condition": "category",
                "value": [category.get("label") for category in categories],
                "status": "verifiable",
                "method": "google_places_text_search",
            }
        )

    if parsed.get("transport"):
        items.append(
            {
                "condition": "transport",
                "value": parsed["transport"],
                "status": "verifiable",
                "method": "coordinate_distance_and_google_maps_url",
            }
        )

    items.append(
        {
            "condition": "rating",
            "value": parsed.get("rating_min"),
            "status": "verifiable",
            "method": "google_places_rating_field",
        }
    )
    items.append(
        {
            "condition": "review_count",
            "value": parsed.get("review_count_min"),
            "status": "verifiable",
            "method": "google_places_user_rating_count_field",
        }
    )
    items.append(
        {
            "condition": "opening_hours",
            "value": parsed.get("time_text") or parsed.get("open_now"),
            "status": "verifiable",
            "method": "google_places_opening_hours_fields",
        }
    )

    if parsed.get("budget_krw"):
        items.append(
            {
                "condition": "exact_budget",
                "value": parsed["budget_krw"],
                "status": "unsupported",
                "method": None,
                "reason": UNSUPPORTED_REASON["exact_budget"],
            }
        )

    for mood in parsed.get("moods") or []:
        items.append(
            {
                "condition": "mood",
                "value": mood,
                "status": "proxy_pending",
                "method": "review_evidence_extraction",
                "reason": "무드 조건은 공식 필드가 아니므로 리뷰 근거 문장으로만 간접 검증합니다.",
            }
        )

    for unsupported in parsed.get("unsupported_conditions") or []:
        key = str(unsupported)
        items.append(
            {
                "condition": key,
                "value": True,
                "status": "unsupported",
                "method": None,
                "reason": UNSUPPORTED_REASON.get(key, "현재 안정적으로 검증할 수 있는 필드가 없습니다."),
            }
        )

    return {
        "items": items,
        "summary": _summarize(items),
    }


def apply_review_evidence(capability: dict[str, Any], evidence: list[dict[str, Any]]) -> dict[str, Any]:
    evidence_by_mood: dict[str, list[dict[str, Any]]] = {}
    for item in evidence:
        mood = str(item.get("mood") or "")
        if not mood:
            continue
        evidence_by_mood.setdefault(mood, []).append(item)

    next_items: list[dict[str, Any]] = []
    for item in capability.get("items", []):
        if item.get("condition") != "mood":
            next_items.append(item)
            continue
        mood = str(item.get("value") or "")
        hits = evidence_by_mood.get(mood, [])
        found = [hit for hit in hits if hit.get("evidence")]
        next_item = dict(item)
        if found:
            next_item["status"] = "proxy_verified"
            next_item["evidence_count"] = sum(len(hit.get("evidence") or []) for hit in found)
        else:
            next_item["status"] = "proxy_not_found"
            next_item["reason"] = "최종 후보 리뷰에서 해당 무드 조건을 뒷받침하는 근거 문장을 찾지 못했습니다."
        next_items.append(next_item)

    return {
        "items": next_items,
        "summary": _summarize(next_items),
    }


def matched_and_unmatched(capability: dict[str, Any]) -> dict[str, list[dict[str, Any]]]:
    matched_statuses = {"verifiable", "proxy_verified"}
    unmatched_statuses = {"unsupported", "proxy_not_found"}
    matched = [item for item in capability.get("items", []) if item.get("status") in matched_statuses]
    unmatched = [item for item in capability.get("items", []) if item.get("status") in unmatched_statuses]
    return {"matched_conditions": matched, "unmatched_conditions": unmatched}


def _summarize(items: list[dict[str, Any]]) -> dict[str, int]:
    summary: dict[str, int] = {}
    for item in items:
        status = str(item.get("status") or "unknown")
        summary[status] = summary.get(status, 0) + 1
    return summary
