from __future__ import annotations

from typing import Any

import requests


class GooglePlacesError(RuntimeError):
    pass


class GooglePlacesClient:
    TEXT_SEARCH_URL = "https://places.googleapis.com/v1/places:searchText"
    DETAILS_URL = "https://places.googleapis.com/v1/{place_name}"

    SEARCH_FIELD_MASK = ",".join(
        [
            "places.id",
            "places.displayName",
            "places.formattedAddress",
            "places.location",
            "places.types",
            "places.rating",
            "places.userRatingCount",
            "places.priceLevel",
            "places.businessStatus",
            "places.currentOpeningHours",
            "places.regularOpeningHours",
            "places.googleMapsUri",
        ]
    )
    DETAILS_FIELD_MASK = ",".join(
        [
            "id",
            "displayName",
            "reviews",
            "editorialSummary",
            "rating",
            "userRatingCount",
            "priceLevel",
            "googleMapsUri",
        ]
    )

    def __init__(self, api_key: str, timeout_seconds: int = 15):
        self.api_key = api_key
        self.timeout_seconds = timeout_seconds
        self.search_calls = 0
        self.details_calls = 0

    def search_text(self, *, text_query: str, role: str, max_result_count: int = 5) -> list[dict[str, Any]]:
        self.search_calls += 1
        response = requests.post(
            self.TEXT_SEARCH_URL,
            headers={
                "Content-Type": "application/json",
                "X-Goog-Api-Key": self.api_key,
                "X-Goog-FieldMask": self.SEARCH_FIELD_MASK,
            },
            json={
                "textQuery": text_query,
                "languageCode": "ko",
                "regionCode": "KR",
                "maxResultCount": max(1, min(10, max_result_count)),
            },
            timeout=self.timeout_seconds,
        )
        if response.status_code >= 400:
            raise GooglePlacesError(f"Google Places Text Search failed: {response.status_code} {response.text[:300]}")
        places = response.json().get("places") or []
        return [self._normalize_place(place, role=role, source_query=text_query) for place in places]

    def fetch_reviews(self, place_name: str) -> list[dict[str, Any]]:
        self.details_calls += 1
        resource = place_name if place_name.startswith("places/") else f"places/{place_name}"
        response = requests.get(
            self.DETAILS_URL.format(place_name=resource),
            headers={
                "X-Goog-Api-Key": self.api_key,
                "X-Goog-FieldMask": self.DETAILS_FIELD_MASK,
            },
            timeout=self.timeout_seconds,
        )
        if response.status_code >= 400:
            raise GooglePlacesError(f"Google Places Details failed: {response.status_code} {response.text[:300]}")
        payload = response.json()
        return [self._normalize_review(review) for review in payload.get("reviews") or [] if self._review_text(review)]

    def _normalize_place(self, place: dict[str, Any], *, role: str, source_query: str) -> dict[str, Any]:
        location = place.get("location") or {}
        current_hours = place.get("currentOpeningHours") or {}
        regular_hours = place.get("regularOpeningHours") or {}
        return {
            "place_id": place.get("id"),
            "name": _localized_text(place.get("displayName")),
            "address": place.get("formattedAddress"),
            "x": location.get("longitude"),
            "y": location.get("latitude"),
            "types": place.get("types") or [],
            "rating": place.get("rating"),
            "user_rating_count": place.get("userRatingCount"),
            "price_level": place.get("priceLevel"),
            "business_status": place.get("businessStatus"),
            "open_now": current_hours.get("openNow"),
            "opening_hours_available": bool(current_hours or regular_hours),
            "place_url": place.get("googleMapsUri"),
            "source": "google_places_text_search",
            "source_query": source_query,
            "role": role,
            "matched_keywords": [source_query],
        }

    def _normalize_review(self, review: dict[str, Any]) -> dict[str, Any]:
        return {
            "rating": review.get("rating"),
            "relative_time": review.get("relativePublishTimeDescription"),
            "text": self._review_text(review),
        }

    def _review_text(self, review: dict[str, Any]) -> str:
        return _localized_text(review.get("text")) or _localized_text(review.get("originalText")) or ""


def dedupe_places(places: list[dict[str, Any]]) -> list[dict[str, Any]]:
    seen: set[str] = set()
    result: list[dict[str, Any]] = []
    for place in places:
        key = str(place.get("place_id") or f"{place.get('name')}|{place.get('address')}")
        if key in seen:
            continue
        seen.add(key)
        result.append(place)
    return result


def _localized_text(value: Any) -> str:
    if isinstance(value, dict):
        text = value.get("text")
        return str(text).strip() if text else ""
    if value is None:
        return ""
    return str(value).strip()
