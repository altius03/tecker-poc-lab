from __future__ import annotations

import json
from typing import Any

import requests


class OpenAIPocError(RuntimeError):
    pass


class OpenAIPocClient:
    def __init__(self, api_key: str, model: str, timeout_seconds: int = 30):
        self.api_key = api_key
        self.model = model
        self.timeout_seconds = timeout_seconds
        self.calls = 0

    def parse_conditions(self, query: str) -> dict[str, Any]:
        system = (
            "You convert Korean date-route requests into strict JSON. "
            "Return only JSON. Do not invent places. "
            "Use role values meal, cafe, walk_photo, extra."
        )
        user = f"""
Parse this request into JSON.

Request: {query}

Required shape:
{{
  "region": "string or null",
  "categories": [
    {{"role": "meal|cafe|walk_photo|extra", "label": "Korean category", "search_query": "Korean Google Places text query"}}
  ],
  "moods": ["Korean mood words"],
  "budget_krw": 120000 or null,
  "transport": "walk|car|transit|null",
  "time_text": "string or null",
  "rating_min": number or null,
  "review_count_min": number or null,
  "radius_m": number or null,
  "route_stop_count": number,
  "unsupported_conditions": ["exact_budget", "waiting_time", "reservation"] if mentioned
}}
"""
        data = self._chat_json(system, user)
        return _normalize_parsed_conditions(data, query)

    def extract_review_evidence(
        self,
        *,
        moods: list[str],
        place_reviews: list[dict[str, Any]],
    ) -> list[dict[str, Any]]:
        if not moods or not place_reviews:
            return []
        compact_reviews = []
        for place in place_reviews:
            compact_reviews.append(
                {
                    "place_id": place.get("place_id"),
                    "name": place.get("name"),
                    "reviews": [review.get("text", "")[:500] for review in place.get("reviews", [])[:5]],
                }
            )

        system = (
            "You extract evidence sentences from reviews. Return only JSON. "
            "Do not infer mood without an explicit or near-synonym sentence."
        )
        user = f"""
Moods to verify: {json.dumps(moods, ensure_ascii=False)}
Place reviews: {json.dumps(compact_reviews, ensure_ascii=False)}

Return JSON:
{{
  "evidence": [
    {{
      "place_id": "string",
      "place_name": "string",
      "mood": "one of requested moods",
      "status": "proxy_verified|proxy_not_found",
      "evidence": ["short exact Korean review sentences"],
      "confidence": "low|medium|high"
    }}
  ]
}}
"""
        data = self._chat_json(system, user)
        evidence = data.get("evidence") if isinstance(data, dict) else None
        return evidence if isinstance(evidence, list) else []

    def _chat_json(self, system: str, user: str) -> dict[str, Any]:
        self.calls += 1
        response = requests.post(
            "https://api.openai.com/v1/chat/completions",
            headers={
                "Authorization": f"Bearer {self.api_key}",
                "Content-Type": "application/json",
            },
            json={
                "model": self.model,
                "messages": [
                    {"role": "system", "content": system},
                    {"role": "user", "content": user},
                ],
                "temperature": 0,
                "response_format": {"type": "json_object"},
            },
            timeout=self.timeout_seconds,
        )
        if response.status_code >= 400:
            raise OpenAIPocError(f"OpenAI API failed: {response.status_code} {response.text[:300]}")
        payload = response.json()
        content = payload["choices"][0]["message"]["content"]
        try:
            return json.loads(content)
        except json.JSONDecodeError as exc:
            raise OpenAIPocError(f"OpenAI returned non-JSON content: {content[:300]}") from exc


def _normalize_parsed_conditions(data: dict[str, Any], raw_query: str) -> dict[str, Any]:
    categories = data.get("categories") if isinstance(data.get("categories"), list) else []
    normalized_categories = []
    for category in categories:
        if not isinstance(category, dict):
            continue
        role = str(category.get("role") or "extra")
        if role not in {"meal", "cafe", "walk_photo", "extra"}:
            role = "extra"
        label = str(category.get("label") or category.get("search_query") or "").strip()
        search_query = str(category.get("search_query") or label).strip()
        if not search_query:
            continue
        normalized_categories.append({"role": role, "label": label or search_query, "search_query": search_query})

    if not normalized_categories:
        normalized_categories = [
            {"role": "meal", "label": "식사", "search_query": "맛집"},
            {"role": "cafe", "label": "카페", "search_query": "카페"},
        ]

    route_stop_count = data.get("route_stop_count")
    try:
        route_stop_count = max(2, min(4, int(route_stop_count)))
    except Exception:
        route_stop_count = min(3, len(normalized_categories))

    return {
        "raw_query": raw_query,
        "region": _clean_optional_str(data.get("region")),
        "categories": normalized_categories,
        "desired_roles": [category["role"] for category in normalized_categories],
        "moods": [str(item).strip() for item in data.get("moods", []) if str(item).strip()],
        "budget_krw": _optional_int(data.get("budget_krw")),
        "transport": _clean_optional_str(data.get("transport")),
        "time_text": _clean_optional_str(data.get("time_text")),
        "rating_min": _optional_float(data.get("rating_min")),
        "review_count_min": _optional_int(data.get("review_count_min")),
        "radius_m": _optional_int(data.get("radius_m")) or 1000,
        "route_stop_count": route_stop_count,
        "unsupported_conditions": [str(item).strip() for item in data.get("unsupported_conditions", []) if str(item).strip()],
    }


def _clean_optional_str(value: Any) -> str | None:
    if value is None:
        return None
    text = str(value).strip()
    if not text or text.lower() == "null":
        return None
    return text


def _optional_int(value: Any) -> int | None:
    if value is None or value == "":
        return None
    try:
        return int(float(value))
    except Exception:
        return None


def _optional_float(value: Any) -> float | None:
    if value is None or value == "":
        return None
    try:
        return float(value)
    except Exception:
        return None
