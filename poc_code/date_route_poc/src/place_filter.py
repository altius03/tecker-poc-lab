from __future__ import annotations

import math
from typing import Any


ROLE_KEYWORDS = {
    "meal": ["음식점", "파스타", "일식", "고기", "한식", "양식", "레스토랑", "맛집", "FD6"],
    "cafe": ["카페", "디저트", "커피", "베이커리", "CE7"],
    "walk_photo": ["관광", "명소", "공원", "산책", "전시", "거리", "전망", "포토", "여행", "도보여행", "숲", "한강", "AT4"],
}


def filter_places(
    places: list[dict[str, Any]],
    conditions: dict[str, Any],
    region_center: dict[str, Any] | None,
) -> dict[str, Any]:
    deduped = _dedupe_places(places)
    distance_filter_skipped = region_center is None
    max_distance_m = _max_distance_for_transport(conditions.get("transport"))
    filtered: list[dict[str, Any]] = []
    explanations: list[str] = []
    limitations: list[str] = []

    if distance_filter_skipped:
        explanations.append("중심 좌표가 없어 거리 기반 필터링을 건너뛰고 키워드/카테고리 기준으로 후보를 유지했습니다.")
    else:
        explanations.append(f"이동수단 '{conditions.get('transport') or 'unspecified'}' 기준 최대 {max_distance_m}m 안쪽 후보를 우선했습니다.")

    for place in deduped:
        enriched = dict(place)
        enriched["role"] = classify_role(enriched)
        enriched["matched_keywords"] = _merge_matched_keywords(enriched, conditions)

        if not distance_filter_skipped:
            enriched["distance_m"] = _resolve_distance_m(enriched, region_center)
            if enriched["distance_m"] is not None and enriched["distance_m"] > max_distance_m:
                continue

        if _matches_desired_roles(enriched, conditions) or len(filtered) < 5:
            filtered.append(enriched)

    if len(filtered) < min(5, len(deduped)):
        existing_ids = {place.get("place_id") for place in filtered}
        for place in deduped:
            if place.get("place_id") in existing_ids:
                continue
            enriched = dict(place)
            enriched["role"] = classify_role(enriched)
            enriched["matched_keywords"] = _merge_matched_keywords(enriched, conditions)
            enriched["distance_m"] = _resolve_distance_m(enriched, region_center) if region_center else enriched.get("distance_m")
            filtered.append(enriched)
            if len(filtered) >= min(5, len(deduped)):
                break

    if conditions.get("budget_krw"):
        limitations.append("Kakao Local 후보에는 가격 정보가 없어 예산 조건은 설명 근거에만 반영했고 가격 검증 필터로 사용하지 않았습니다.")

    return {
        "filtered_places": filtered,
        "distance_filter_skipped": distance_filter_skipped,
        "explanations": explanations,
        "limitations": limitations,
    }


def classify_role(place: dict[str, Any]) -> str:
    role_hint = place.get("role_hint")
    if role_hint in {"meal", "cafe", "walk_photo", "extra"}:
        return role_hint

    haystack = " ".join(str(place.get(key, "")) for key in ["name", "category", "address"])
    if any(keyword in haystack for keyword in ROLE_KEYWORDS["walk_photo"]):
        return "walk_photo"
    if any(keyword in haystack for keyword in ROLE_KEYWORDS["cafe"]):
        return "cafe"
    if any(keyword in haystack for keyword in ROLE_KEYWORDS["meal"]):
        return "meal"
    return "extra"


def _dedupe_places(places: list[dict[str, Any]]) -> list[dict[str, Any]]:
    seen: set[tuple[str, str]] = set()
    result: list[dict[str, Any]] = []
    for place in places:
        key = (str(place.get("place_id") or ""), f"{place.get('name')}|{place.get('address')}")
        if key in seen:
            continue
        seen.add(key)
        result.append(place)
    return result


def _merge_matched_keywords(place: dict[str, Any], conditions: dict[str, Any]) -> list[str]:
    matched = list(place.get("matched_keywords") or [])
    haystack = " ".join(str(place.get(key, "")) for key in ["name", "category", "address"])
    for keyword in list(conditions.get("categories") or []) + list(conditions.get("moods") or []):
        if keyword in haystack or keyword in matched:
            if keyword not in matched:
                matched.append(keyword)

    role = classify_role(place)
    if role == "meal" and "식사" not in matched:
        matched.append("식사")
    if role == "cafe" and "카페" not in matched:
        matched.append("카페")
    if role == "walk_photo" and "산책/포토" not in matched:
        matched.append("산책/포토")
    return matched


def _matches_desired_roles(place: dict[str, Any], conditions: dict[str, Any]) -> bool:
    desired_roles = set(conditions.get("desired_roles") or [])
    return not desired_roles or place.get("role") in desired_roles


def _max_distance_for_transport(transport: str | None) -> int:
    if transport == "walk":
        return 1800
    if transport == "car":
        return 6000
    if transport == "transit":
        return 3500
    return 2500


def _resolve_distance_m(place: dict[str, Any], region_center: dict[str, Any] | None) -> int | None:
    if place.get("distance_m") is not None:
        try:
            return int(place["distance_m"])
        except (TypeError, ValueError):
            pass

    if not region_center:
        return None

    try:
        place_x = float(place["x"])
        place_y = float(place["y"])
        center_x = float(region_center["x"])
        center_y = float(region_center["y"])
    except (KeyError, TypeError, ValueError):
        return None

    return int(_haversine_m(center_y, center_x, place_y, place_x))


def _haversine_m(lat1: float, lon1: float, lat2: float, lon2: float) -> float:
    radius_m = 6371000
    phi1 = math.radians(lat1)
    phi2 = math.radians(lat2)
    delta_phi = math.radians(lat2 - lat1)
    delta_lambda = math.radians(lon2 - lon1)
    a = math.sin(delta_phi / 2) ** 2 + math.cos(phi1) * math.cos(phi2) * math.sin(delta_lambda / 2) ** 2
    return radius_m * (2 * math.atan2(math.sqrt(a), math.sqrt(1 - a)))
