from __future__ import annotations

import argparse
import json
import math
import sys
import urllib.parse
from pathlib import Path
from typing import Any

from .condition_capability import apply_review_evidence, classify_condition_capability, matched_and_unmatched
from .config import get_settings
from .google_places_client import GooglePlacesClient, GooglePlacesError, dedupe_places
from .openai_poc_client import OpenAIPocClient, OpenAIPocError
from .result_writer import failure_result, write_result


PUBLIC_PLACE_KEYS = [
    "place_id",
    "name",
    "address",
    "x",
    "y",
    "types",
    "rating",
    "user_rating_count",
    "price_level",
    "business_status",
    "open_now",
    "opening_hours_available",
    "place_url",
    "source",
    "source_query",
    "role",
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

        if not settings.google_maps_api_key or not settings.openai_api_key:
            result = failure_result(
                input_payload={"query": query},
                modules_run=modules_run,
                code="MISSING_API_KEY",
                error_type="ConfigurationError",
                message="GOOGLE_MAPS_API_KEY와 OPENAI_API_KEY가 모두 필요합니다.",
                limitations=["실제 데이터 검증 PoC이므로 키 없이 샘플 성공처럼 처리하지 않습니다."],
            )
            _write_and_print(settings.base_dir, result)
            return 2

        openai_client = OpenAIPocClient(
            settings.openai_api_key,
            model=settings.openai_model,
            timeout_seconds=settings.openai_timeout_seconds,
        )
        google_client = GooglePlacesClient(
            settings.google_maps_api_key,
            timeout_seconds=settings.google_timeout_seconds,
        )

        parsed_conditions = openai_client.parse_conditions(query)
        modules_run.append("openai_condition_parser")
        partial_result["parsed_conditions"] = parsed_conditions

        initial_capability = classify_condition_capability(parsed_conditions)
        modules_run.append("condition_capability_classifier")
        partial_result["initial_condition_capability"] = initial_capability

        candidates, fallback_log = _collect_candidates(google_client, parsed_conditions, settings)
        modules_run.append("google_places_candidate_collector")
        partial_result["candidate_count"] = len(candidates)

        review_places, review_errors = _fetch_review_samples(google_client, candidates, settings.max_review_places)
        modules_run.append("google_places_review_fetcher")

        review_evidence = openai_client.extract_review_evidence(
            moods=parsed_conditions.get("moods") or [],
            place_reviews=review_places,
        )
        modules_run.append("openai_review_evidence_extractor")

        final_capability = apply_review_evidence(initial_capability, review_evidence)
        condition_match = matched_and_unmatched(final_capability)
        route = _build_simple_route(candidates, parsed_conditions)
        directions_url = _build_google_maps_directions_url(route, parsed_conditions.get("transport"))

        status = "success" if len(candidates) >= 1 else "failed"
        result = {
            "poc_name": "date_route_google_places_data_gap",
            "status": status,
            "input": {"query": query},
            "modules_run": modules_run,
            "summary": {
                "condition_count": len(final_capability["items"]),
                "condition_capability": final_capability["summary"],
                "candidate_count": len(candidates),
                "review_place_count": len(review_places),
                "review_evidence_count": sum(len(item.get("evidence") or []) for item in review_evidence),
                "fallback_applied": any(step.get("applied") for step in fallback_log),
                "route_stop_count": len(route),
            },
            "parsed_conditions": parsed_conditions,
            "condition_capability": final_capability,
            "matched_conditions": condition_match["matched_conditions"],
            "unmatched_conditions": condition_match["unmatched_conditions"],
            "data_gap_policy": {
                "rule": "검증 불가능한 조건은 필터에 쓰지 않고 unmatched_conditions에 이유와 함께 남깁니다.",
                "unsupported_conditions_used_as_filter": False,
                "mood_conditions_used_as_hard_filter": False,
            },
            "fallback_log": fallback_log,
            "candidate_places": _public_places(candidates),
            "review_evidence": review_evidence,
            "review_fetch_errors": review_errors,
            "route": route,
            "directions": [{"provider": "google_maps_url", "url": directions_url}] if directions_url else [],
            "api_usage": {
                "google_text_search_calls": google_client.search_calls,
                "google_place_details_calls": google_client.details_calls,
                "openai_calls": openai_client.calls,
                "openai_model": settings.openai_model,
            },
            "limitations": [
                "정확한 메뉴 가격, 실시간 웨이팅, 예약 가능 여부는 Google Places 기본 필드로 직접 검증하지 않습니다.",
                "무드 조건은 최종 후보 리뷰에서 근거 문장이 잡힌 경우에만 proxy_verified로 표시합니다.",
                "동선은 최적화가 아니라 PoC용 역할 순서 기반 단순 연결입니다.",
            ],
        }
        _write_and_print(settings.base_dir, result)
        return 0 if status == "success" else 3
    except (OpenAIPocError, GooglePlacesError) as exc:
        result = failure_result(
            input_payload={"query": args.query} if args.query else {},
            modules_run=modules_run,
            code="API_REQUEST_FAILED",
            error_type=type(exc).__name__,
            message=str(exc),
            partial_result=partial_result,
            limitations=["외부 API 호출 실패도 outputs/latest/result.json에 실패 산출물로 저장합니다."],
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
    parser = argparse.ArgumentParser(description="Date route Google Places data-gap PoC")
    parser.add_argument("--query", help="Natural-language date route request")
    return parser.parse_args(argv)


def _read_default_query(base_dir: Path) -> str | None:
    path = base_dir / "samples" / "default_query.txt"
    if not path.exists():
        return None
    query = path.read_text(encoding="utf-8").strip()
    return query or None


def _collect_candidates(
    client: GooglePlacesClient,
    conditions: dict[str, Any],
    settings: Any,
) -> tuple[list[dict[str, Any]], list[dict[str, Any]]]:
    min_required = settings.min_final_candidates
    categories = conditions.get("categories") or []
    region = conditions.get("region") or ""
    moods = conditions.get("moods") or []

    attempts = [
        {"name": "region_category_mood", "include_mood": True, "max_per_category": settings.max_places_per_category},
        {"name": "region_category_only", "include_mood": False, "max_per_category": settings.max_places_per_category},
        {"name": "expanded_result_count", "include_mood": False, "max_per_category": min(10, settings.max_places_per_category + 3)},
    ]
    fallback_log: list[dict[str, Any]] = []
    last_candidates: list[dict[str, Any]] = []

    for index, attempt in enumerate(attempts, start=1):
        places: list[dict[str, Any]] = []
        queries: list[str] = []
        for category in categories:
            query = _compose_query(region, category, moods if attempt["include_mood"] else [])
            queries.append(query)
            places.extend(
                client.search_text(
                    text_query=query,
                    role=str(category.get("role") or "extra"),
                    max_result_count=attempt["max_per_category"],
                )
            )
        candidates = _rank_places(dedupe_places(places))[: settings.max_total_places]
        fallback_log.append(
            {
                "step": index,
                "attempt": attempt["name"],
                "queries": queries,
                "candidate_count": len(candidates),
                "applied": index > 1,
                "reason": "candidate_count_below_minimum" if len(last_candidates) < min_required and index > 1 else "initial_attempt",
            }
        )
        last_candidates = candidates
        if len(candidates) >= min_required:
            return candidates, fallback_log

    return last_candidates, fallback_log


def _compose_query(region: str, category: dict[str, Any], moods: list[str]) -> str:
    parts = [region, str(category.get("search_query") or category.get("label") or ""), *moods]
    return " ".join(part for part in parts if part).strip()


def _rank_places(places: list[dict[str, Any]]) -> list[dict[str, Any]]:
    def score(place: dict[str, Any]) -> float:
        rating = float(place.get("rating") or 0)
        count = float(place.get("user_rating_count") or 0)
        open_bonus = 0.5 if place.get("open_now") is True else 0
        return rating * 10 + math.log10(count + 1) + open_bonus

    return sorted(places, key=score, reverse=True)


def _fetch_review_samples(
    client: GooglePlacesClient,
    candidates: list[dict[str, Any]],
    max_review_places: int,
) -> tuple[list[dict[str, Any]], list[dict[str, str]]]:
    review_places: list[dict[str, Any]] = []
    errors: list[dict[str, str]] = []
    for place in candidates[:max_review_places]:
        place_id = str(place.get("place_id") or "")
        if not place_id:
            continue
        try:
            reviews = client.fetch_reviews(place_id)
            review_places.append({"place_id": place_id, "name": place.get("name"), "reviews": reviews})
        except GooglePlacesError as exc:
            errors.append({"place_id": place_id, "name": str(place.get("name") or ""), "message": str(exc)})
    return review_places, errors


def _build_simple_route(candidates: list[dict[str, Any]], conditions: dict[str, Any]) -> list[dict[str, Any]]:
    target_count = max(2, min(3, int(conditions.get("route_stop_count") or 2)))
    selected: list[dict[str, Any]] = []
    used: set[str] = set()
    for role in ["meal", "cafe", "walk_photo", "extra"]:
        if len(selected) >= target_count:
            break
        for place in candidates:
            key = str(place.get("place_id") or "")
            if key in used or place.get("role") != role:
                continue
            selected.append(place)
            used.add(key)
            break
    for place in candidates:
        if len(selected) >= target_count:
            break
        key = str(place.get("place_id") or "")
        if key in used:
            continue
        selected.append(place)
        used.add(key)

    route: list[dict[str, Any]] = []
    for order, place in enumerate(selected, start=1):
        route.append(
            {
                "order": order,
                "place_id": place.get("place_id"),
                "name": place.get("name"),
                "role": place.get("role"),
                "selection_reason": _selection_reason(place),
            }
        )
    return route


def _selection_reason(place: dict[str, Any]) -> str:
    parts = []
    if place.get("rating"):
        parts.append(f"평점 {place['rating']}")
    if place.get("user_rating_count"):
        parts.append(f"리뷰 수 {place['user_rating_count']}")
    if place.get("open_now") is True:
        parts.append("현재 영업 중")
    if place.get("source_query"):
        parts.append(f"검색어 '{place['source_query']}' 결과")
    return ", ".join(parts) if parts else "역할별 후보 다양성을 기준으로 선택"


def _build_google_maps_directions_url(route: list[dict[str, Any]], transport: str | None) -> str | None:
    route_places = [stop for stop in route if stop.get("place_id")]
    if len(route_places) < 2:
        return None
    travel_mode = "walking" if transport == "walk" else "driving" if transport == "car" else "transit" if transport == "transit" else "walking"
    origin = route_places[0]["name"]
    destination = route_places[-1]["name"]
    waypoints = [place["name"] for place in route_places[1:-1]]
    params = {
        "api": "1",
        "travelmode": travel_mode,
        "origin": origin,
        "destination": destination,
    }
    if waypoints:
        params["waypoints"] = "|".join(waypoints)
    return f"https://www.google.com/maps/dir/?{urllib.parse.urlencode(params)}"


def _public_places(places: list[dict[str, Any]]) -> list[dict[str, Any]]:
    return [{key: place.get(key) for key in PUBLIC_PLACE_KEYS} for place in places]


def _write_and_print(base_dir: Path, result: dict[str, Any]) -> None:
    paths = write_result(base_dir, result)
    print(json.dumps({"status": result["status"], "latest": str(paths["latest"]), "run": str(paths["run"])}, ensure_ascii=False))


if __name__ == "__main__":
    sys.exit(main())
