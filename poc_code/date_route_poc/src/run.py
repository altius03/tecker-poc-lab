from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path
from typing import Any

from .condition_parser import parse_conditions
from .config import get_settings
from .directions_url_builder import build_directions
from .kakao_local_client import KakaoLocalClient, KakaoLocalError
from .place_filter import filter_places
from .provider_router import select_provider_mode
from .region_resolver import resolve_region_center
from .result_writer import failure_result, write_result
from .route_builder import build_route


CATEGORY_GROUPS = {
    "meal": "FD6",
    "cafe": "CE7",
    "walk_photo": "AT4",
}
PUBLIC_PLACE_KEYS = [
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
]


def main(argv: list[str] | None = None) -> int:
    args = _parse_args(argv)
    settings = get_settings()
    modules_run: list[str] = []
    partial_result: dict[str, Any] = {}

    try:
        query = args.query or _read_default_query(settings.base_dir)
        if not query:
            result = failure_result(
                input_payload={},
                modules_run=modules_run,
                code="MISSING_INPUT",
                error_type="InputError",
                message="--query가 없고 samples/default_query.txt도 비어 있거나 없습니다.",
                limitations=["입력 자연어가 없으면 조건 구조화와 장소 조회를 시작할 수 없습니다."],
            )
            _write_and_print(settings.base_dir, result)
            return 2

        conditions = parse_conditions(query)
        modules_run.append("condition_parser")
        partial_result["parsed_conditions"] = conditions

        provider_info = select_provider_mode("kakao")
        modules_run.append("provider_router")
        partial_result["provider_mode"] = provider_info["provider_mode"]

        if not args.use_sample and not settings.kakao_rest_api_key:
            result = failure_result(
                input_payload={"query": query},
                modules_run=modules_run,
                code="MISSING_API_KEY",
                error_type="ConfigurationError",
                message="KAKAO_REST_API_KEY가 없습니다. 실제 Kakao Local 후보 조회를 하려면 .env에 REST API 키를 설정하거나 --use-sample을 명시하세요.",
                partial_result=partial_result,
                limitations=["사용자 승인 없이 샘플을 자동 대체하지 않습니다.", "실제 장소 후보 조회 성공처럼 보이는 결과를 만들지 않았습니다."],
            )
            _write_and_print(settings.base_dir, result)
            return 2

        client = None if args.use_sample else KakaoLocalClient(settings.kakao_rest_api_key or "", settings.kakao_timeout_seconds)

        region_center = resolve_region_center(conditions, client=client, use_sample=args.use_sample)
        modules_run.append("region_resolver")
        partial_result["region_center"] = region_center

        candidate_places = _load_sample_places(settings.base_dir) if args.use_sample else _collect_kakao_candidates(client, conditions, region_center, settings)
        modules_run.append("kakao_local_client" if not args.use_sample else "sample_places_loader")
        partial_result["candidate_place_count"] = len(candidate_places)

        filter_result = filter_places(candidate_places, conditions, region_center)
        modules_run.append("place_filter")
        filtered_places = filter_result["filtered_places"]
        partial_result["filtered_place_count"] = len(filtered_places)

        route, route_explanations = build_route(filtered_places, conditions)
        modules_run.append("route_builder")
        partial_result["route_stop_count"] = len(route)

        directions = build_directions(route, filtered_places, conditions.get("transport"))
        modules_run.append("directions_url_builder")
        partial_result["directions_url_count"] = len(directions)

        if len(candidate_places) < 5 or len(route) < 2:
            result = failure_result(
                input_payload={"query": query},
                modules_run=modules_run,
                code="VALIDATION_ERROR",
                error_type="ValidationError",
                message="PoC 성공 기준을 만족할 만큼 후보 장소나 코스가 생성되지 않았습니다.",
                partial_result={
                    **partial_result,
                    "candidate_places": _public_places(candidate_places),
                    "filtered_places": _public_places(filtered_places, include_role=True),
                    "route": route,
                },
                limitations=["후보 수집 결과가 부족하면 category/keyword 검색어를 조정해야 합니다."],
            )
            _write_and_print(settings.base_dir, result)
            return 3

        result = {
            "poc_name": "date_route",
            "status": "success",
            "input": {"query": query},
            "modules_run": modules_run,
            "summary": {
                "parsed_condition_count": conditions.get("parsed_condition_count", 0),
                "candidate_place_count": len(candidate_places),
                "filtered_place_count": len(filtered_places),
                "route_stop_count": len(route),
                "directions_url_count": len(directions),
            },
            "parsed_conditions": conditions,
            "region_center": region_center,
            "distance_filter_skipped": filter_result["distance_filter_skipped"],
            "provider_mode": provider_info["provider_mode"],
            "candidate_places": _public_places(candidate_places),
            "filtered_places": _public_places(filtered_places, include_role=True),
            "route": route,
            "explanations": filter_result["explanations"] + route_explanations,
            "directions": directions,
            "risks_verified": [
                "Google Places API and Google Routes API actual calls are not present in this code path.",
                "Missing API key path writes outputs/latest/result.json instead of raising an uncaught exception.",
            ],
            "limitations": filter_result["limitations"]
            + [
                "영업시간, 혼잡도, 가격, 예약 가능 여부는 Kakao Local 응답만으로 완전 검증하지 않습니다.",
                "길찾기는 API 최적화 결과가 아니라 후보 URL 생성까지만 수행합니다.",
            ],
            "fallback_used": bool(args.use_sample),
            "fallback_reason": "explicit_use_sample" if args.use_sample else None,
        }
        _write_and_print(settings.base_dir, result)
        return 0
    except KakaoLocalError as exc:
        result = failure_result(
            input_payload={"query": args.query} if args.query else {},
            modules_run=modules_run,
            code="API_REQUEST_FAILED",
            error_type=type(exc).__name__,
            message=str(exc),
            partial_result=partial_result,
            limitations=["Kakao Local API 호출 실패 시에도 실패 JSON을 저장합니다."],
        )
        _write_and_print(settings.base_dir, result)
        return 4
    except Exception as exc:
        result = failure_result(
            input_payload={"query": args.query} if args.query else {},
            modules_run=modules_run,
            code="UNEXPECTED_ERROR",
            error_type=type(exc).__name__,
            message=str(exc),
            partial_result=partial_result,
            limitations=["예상하지 못한 예외도 실패 JSON으로 저장합니다."],
        )
        _write_and_print(settings.base_dir, result)
        return 5


def _parse_args(argv: list[str] | None) -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Date route planning PoC")
    parser.add_argument("--query", help="Natural-language date route request")
    parser.add_argument("--use-sample", action="store_true", help="Use samples/sample_places.json instead of Kakao Local API")
    return parser.parse_args(argv)


def _read_default_query(base_dir: Path) -> str | None:
    path = base_dir / "samples" / "default_query.txt"
    if not path.exists():
        return None
    query = path.read_text(encoding="utf-8").strip()
    return query or None


def _load_sample_places(base_dir: Path) -> list[dict[str, Any]]:
    path = base_dir / "samples" / "sample_places.json"
    with path.open("r", encoding="utf-8") as file:
        data = json.load(file)
    return [dict(place, source="sample_places") for place in data][:20]


def _collect_kakao_candidates(
    client: KakaoLocalClient | None,
    conditions: dict[str, Any],
    region_center: dict[str, Any] | None,
    settings: Any,
) -> list[dict[str, Any]]:
    if client is None:
        return []

    region = conditions.get("region") or ""
    desired_roles = conditions.get("desired_roles") or ["meal", "cafe", "walk_photo"]
    category_keywords = conditions.get("categories") or []
    role_buckets: list[list[dict[str, Any]]] = []

    for role in desired_roles:
        category_group = CATEGORY_GROUPS.get(role)
        keyword = _keyword_for_role(role, category_keywords)
        query = " ".join(part for part in [region, keyword] if part).strip()
        role_candidates: list[dict[str, Any]] = []
        if query:
            role_candidates.extend(
                client.search_keyword(
                    query,
                    x=region_center.get("x") if region_center else None,
                    y=region_center.get("y") if region_center else None,
                    radius=2500 if region_center else None,
                    category_group_code=category_group,
                    size=settings.max_places_per_category,
                )
            )
        if category_group and region_center:
            role_candidates.extend(
                client.search_category(
                    category_group,
                    x=region_center.get("x"),
                    y=region_center.get("y"),
                    radius=2500,
                    size=settings.max_places_per_category,
                )
            )
        role_buckets.append(role_candidates)

    return _round_robin_dedupe(role_buckets)[: settings.max_total_places]


def _keyword_for_role(role: str, category_keywords: list[str]) -> str:
    if role == "meal":
        for keyword in category_keywords:
            if keyword in {"파스타", "일식", "고기", "한식", "양식", "레스토랑", "맛집", "음식점"}:
                return keyword
        return "맛집"
    if role == "cafe":
        return "디저트 카페" if "디저트" in category_keywords else "카페"
    if role == "walk_photo":
        return "사진 명소" if any(keyword in category_keywords for keyword in ["사진", "포토"]) else "산책"
    return "데이트"


def _dedupe(places: list[dict[str, Any]]) -> list[dict[str, Any]]:
    seen: set[tuple[str, str]] = set()
    result: list[dict[str, Any]] = []
    for place in places:
        key = (str(place.get("place_id") or ""), f"{place.get('name')}|{place.get('address')}")
        if key in seen:
            continue
        seen.add(key)
        result.append(place)
    return result


def _round_robin_dedupe(role_buckets: list[list[dict[str, Any]]]) -> list[dict[str, Any]]:
    seen: set[tuple[str, str]] = set()
    result: list[dict[str, Any]] = []
    max_length = max((len(bucket) for bucket in role_buckets), default=0)
    for index in range(max_length):
        for bucket in role_buckets:
            if index >= len(bucket):
                continue
            place = bucket[index]
            key = (str(place.get("place_id") or ""), f"{place.get('name')}|{place.get('address')}")
            if key in seen:
                continue
            seen.add(key)
            result.append(place)
    return result


def _public_places(places: list[dict[str, Any]], *, include_role: bool = False) -> list[dict[str, Any]]:
    public_places: list[dict[str, Any]] = []
    for place in places:
        public = {key: place.get(key) for key in PUBLIC_PLACE_KEYS}
        public["matched_keywords"] = list(public.get("matched_keywords") or [])
        if include_role and place.get("role"):
            public["role"] = place.get("role")
        public_places.append(public)
    return public_places


def _write_and_print(base_dir: Path, result: dict[str, Any]) -> None:
    paths = write_result(base_dir, result)
    print(json.dumps({"status": result["status"], "latest": str(paths["latest"]), "run": str(paths["run"])}, ensure_ascii=False))


if __name__ == "__main__":
    sys.exit(main())
