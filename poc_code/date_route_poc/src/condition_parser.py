from __future__ import annotations

import re
from typing import Any


KNOWN_REGIONS = [
    "성수역",
    "성수",
    "홍대입구역",
    "홍대",
    "강남역",
    "강남",
    "잠실역",
    "잠실",
    "연남동",
    "건대입구",
    "건대",
    "이태원",
    "한남동",
    "을지로",
    "익선동",
    "혜화",
    "대학로",
    "여의도",
    "압구정",
    "신사",
    "망원",
    "합정",
    "삼청동",
]

TIME_KEYWORDS = ["점심", "저녁", "밤", "오후", "오전"]
MOOD_KEYWORDS = [
    "분위기 좋은",
    "조용한",
    "야경",
    "실내",
    "비 오는 날",
    "사진 찍기 좋은",
    "데이트",
    "감성",
    "뷰 좋은",
    "아늑한",
]
CATEGORY_KEYWORDS = {
    "meal": ["파스타", "음식점", "식사", "저녁", "점심", "일식", "고기", "한식", "양식", "레스토랑", "맛집"],
    "cafe": ["카페", "디저트", "커피", "베이커리"],
    "walk_photo": ["산책", "전시", "관광", "포토", "사진", "야경", "공원", "거리"],
}
TRANSPORT_KEYWORDS = {
    "walk": ["걸어서", "도보", "걷기", "걸어"],
    "car": ["차로", "자동차", "자차", "운전"],
    "transit": ["대중교통", "지하철", "버스"],
}


def parse_conditions(query: str) -> dict[str, Any]:
    # TODO: replace with LLM condition parser when structured extraction accuracy matters.
    normalized = " ".join(query.split())
    region = _extract_region(normalized)
    budget_krw = _extract_budget_krw(normalized)
    time_of_day = [keyword for keyword in TIME_KEYWORDS if keyword in normalized]
    categories = _extract_categories(normalized)
    desired_roles = _roles_from_categories(categories)
    moods = [keyword for keyword in MOOD_KEYWORDS if keyword in normalized]
    transport = _extract_transport(normalized)
    route_stop_count = _extract_route_stop_count(normalized, desired_roles)

    parsed = {
        "raw_query": query,
        "region": region,
        "budget_krw": budget_krw,
        "time_of_day": time_of_day,
        "categories": categories,
        "desired_roles": desired_roles,
        "moods": moods,
        "transport": transport,
        "route_stop_count": route_stop_count,
    }
    parsed["parsed_condition_count"] = count_parsed_conditions(parsed)
    return parsed


def count_parsed_conditions(parsed: dict[str, Any]) -> int:
    count = 0
    for key in ["region", "budget_krw", "time_of_day", "categories", "desired_roles", "moods", "transport", "route_stop_count"]:
        value = parsed.get(key)
        if value is not None and value != [] and value != "":
            count += 1
    return count


def _extract_region(query: str) -> str | None:
    for region in KNOWN_REGIONS:
        if region in query:
            return region

    match = re.search(r"([가-힣A-Za-z0-9]{2,12}(?:역|동|로|길|입구))\s*(?:근처|주변|에서|쪽|인근)?", query)
    if match:
        return match.group(1)
    return None


def _extract_budget_krw(query: str) -> int | None:
    match = re.search(r"(\d+(?:\.\d+)?)\s*(만\s*원|만원|천\s*원|원)", query)
    if not match:
        return None

    amount = float(match.group(1))
    unit = match.group(2).replace(" ", "")
    if unit == "만원":
        return int(amount * 10000)
    if unit == "천원":
        return int(amount * 1000)
    return int(amount)


def _extract_categories(query: str) -> list[str]:
    found: list[str] = []
    for keywords in CATEGORY_KEYWORDS.values():
        for keyword in keywords:
            if keyword in query and keyword not in found:
                found.append(keyword)
    return found


def _roles_from_categories(categories: list[str]) -> list[str]:
    roles: list[str] = []
    for role, keywords in CATEGORY_KEYWORDS.items():
        if any(keyword in categories for keyword in keywords):
            roles.append(role)

    if not roles:
        roles = ["meal", "cafe", "walk_photo"]
    elif "meal" in roles and "cafe" in roles and "walk_photo" not in roles:
        roles.append("walk_photo")
    elif "meal" in roles and "cafe" not in roles:
        roles.append("cafe")
    return roles[:4]


def _extract_transport(query: str) -> str | None:
    for transport, keywords in TRANSPORT_KEYWORDS.items():
        if any(keyword in query for keyword in keywords):
            return transport
    if any(keyword in query for keyword in ["근처", "주변", "인근"]):
        return "walk"
    return None


def _extract_route_stop_count(query: str, desired_roles: list[str]) -> int:
    match = re.search(r"([2-4])\s*(?:곳|개|장소|코스|스팟)", query)
    if match:
        return int(match.group(1))
    return min(3, max(2, len(desired_roles)))
