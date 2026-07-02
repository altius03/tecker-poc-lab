from __future__ import annotations

from typing import Any


ROLE_ORDER = ["meal", "cafe", "walk_photo", "extra"]
ROLE_RANK = {role: index for index, role in enumerate(ROLE_ORDER)}
STAY_MINUTES = {
    "meal": 75,
    "cafe": 45,
    "walk_photo": 40,
    "extra": 35,
}


def build_route(filtered_places: list[dict[str, Any]], conditions: dict[str, Any]) -> tuple[list[dict[str, Any]], list[str]]:
    target_count = max(2, min(4, int(conditions.get("route_stop_count") or 3)))
    ordered_places = _pick_ordered_places(filtered_places, target_count)
    route: list[dict[str, Any]] = []
    explanations: list[str] = []

    for index, place in enumerate(ordered_places, start=1):
        role = place.get("role") or "extra"
        reason_parts = []
        matched = place.get("matched_keywords") or []
        if matched:
            reason_parts.append(f"조건 키워드({', '.join(matched[:4])})와 맞음")
        if place.get("distance_m") is not None:
            reason_parts.append(f"중심지에서 약 {place['distance_m']}m")
        if conditions.get("budget_krw"):
            reason_parts.append(f"전체 예산 {conditions['budget_krw']:,}원 조건을 코스 설명에 반영")
        if not reason_parts:
            reason_parts.append("카테고리 순서와 후보 다양성을 기준으로 선택")

        route.append(
            {
                "order": index,
                "place_id": place.get("place_id", ""),
                "name": place.get("name", ""),
                "role": role,
                "estimated_stay_minutes": STAY_MINUTES.get(role, 35),
                "selection_reason": "; ".join(reason_parts),
            }
        )
        explanations.append(f"{index}. {place.get('name')}은/는 {role} 단계 후보로 선택했습니다.")

    return route, explanations


def _pick_ordered_places(places: list[dict[str, Any]], target_count: int) -> list[dict[str, Any]]:
    selected: list[dict[str, Any]] = []
    used_ids: set[str] = set()

    for role in ROLE_ORDER:
        if len(selected) >= target_count:
            break
        for place in places:
            place_id = str(place.get("place_id") or f"{place.get('name')}|{place.get('address')}")
            if place_id in used_ids or place.get("role") != role:
                continue
            selected.append(place)
            used_ids.add(place_id)
            break

    min_fill_rank = ROLE_RANK.get(str(selected[-1].get("role")), 0) if selected else 0
    for place in places:
        if len(selected) >= target_count:
            break
        place_id = str(place.get("place_id") or f"{place.get('name')}|{place.get('address')}")
        if place_id in used_ids:
            continue
        if ROLE_RANK.get(str(place.get("role")), 99) < min_fill_rank:
            continue
        selected.append(place)
        used_ids.add(place_id)

    for place in places:
        if len(selected) >= target_count:
            break
        place_id = str(place.get("place_id") or f"{place.get('name')}|{place.get('address')}")
        if place_id in used_ids:
            continue
        selected.append(place)
        used_ids.add(place_id)

    return selected
