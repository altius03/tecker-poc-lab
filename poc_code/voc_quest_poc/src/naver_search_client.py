from __future__ import annotations

import json
from pathlib import Path
from typing import Any

import requests


class ApiRequestError(RuntimeError):
    pass


SEARCH_SOURCES = {
    "blog": "/v1/search/blog.json",
    "cafe": "/v1/search/cafearticle.json",
    "web": "/v1/search/webkr.json",
    "shop": "/v1/search/shop.json",
}


class NaverSearchClient:
    def __init__(
        self,
        *,
        client_id: str | None,
        client_secret: str | None,
        timeout_seconds: int = 10,
    ):
        self.client_id = client_id
        self.client_secret = client_secret
        self.timeout_seconds = timeout_seconds
        self.base_url = "https://openapi.naver.com"

    def collect(
        self,
        *,
        queries: list[str],
        display_per_query: int = 5,
        max_items: int = 80,
    ) -> list[dict[str, Any]]:
        if not self.client_id or not self.client_secret:
            raise ApiRequestError("Missing NAVER_CLIENT_ID or NAVER_CLIENT_SECRET.")

        headers = {
            "X-Naver-Client-Id": self.client_id,
            "X-Naver-Client-Secret": self.client_secret,
        }
        collected: list[dict[str, Any]] = []

        for query in queries:
            for source_type, endpoint in SEARCH_SOURCES.items():
                params = {
                    "query": query,
                    "display": display_per_query,
                    "start": 1,
                    "sort": "sim",
                }
                try:
                    response = requests.get(
                        self.base_url + endpoint,
                        headers=headers,
                        params=params,
                        timeout=self.timeout_seconds,
                    )
                    response.raise_for_status()
                except requests.RequestException as exc:
                    raise ApiRequestError(
                        f"Naver API request failed for source={source_type}, query={query}: {exc}"
                    ) from exc

                payload = self._read_json(response, source_type=source_type, query=query)
                collected.extend(
                    self._normalize_response_items(
                        source_type=source_type,
                        payload=payload,
                        query=query,
                        start_index=len(collected),
                    )
                )
                if len(collected) >= max_items:
                    return collected[:max_items]

        return collected[:max_items]

    def _read_json(self, response: requests.Response, *, source_type: str, query: str) -> dict[str, Any]:
        try:
            payload = response.json()
        except ValueError as exc:
            raise ApiRequestError(
                f"Naver API returned non-JSON response for source={source_type}, query={query}."
            ) from exc
        if not isinstance(payload, dict):
            raise ApiRequestError(
                f"Naver API returned unexpected JSON shape for source={source_type}, query={query}."
            )
        return payload

    def collect_from_sample(self, sample_path: Path, max_items: int = 80) -> list[dict[str, Any]]:
        payload = json.loads(sample_path.read_text(encoding="utf-8"))
        collected: list[dict[str, Any]] = []
        for source_type in ["blog", "cafe", "shop"]:
            source_payload = payload.get(source_type, {})
            collected.extend(
                self._normalize_response_items(
                    source_type=source_type,
                    payload=source_payload,
                    query=source_payload.get("query", "sample"),
                    start_index=len(collected),
                )
            )
        return collected[:max_items]

    def _normalize_response_items(
        self,
        *,
        source_type: str,
        payload: dict[str, Any],
        query: str,
        start_index: int,
    ) -> list[dict[str, Any]]:
        normalized: list[dict[str, Any]] = []
        for offset, item in enumerate(payload.get("items", []), start=1):
            title = item.get("title") or ""
            link = item.get("link") or item.get("url") or ""
            snippet = item.get("description") or item.get("snippet") or ""
            if source_type == "shop":
                snippet_parts = [
                    item.get("mallName"),
                    item.get("brand"),
                    item.get("maker"),
                    item.get("category1"),
                    item.get("category2"),
                    item.get("category3"),
                    item.get("lprice"),
                ]
                snippet = " ".join(str(part) for part in snippet_parts if part)

            normalized.append(
                {
                    "item_id": f"{source_type}-{start_index + offset:04d}",
                    "source_type": source_type,
                    "source_url": link,
                    "title": title,
                    "snippet": snippet,
                    "collection_method": "naver_search_api",
                    "search_query": query,
                }
            )
        return normalized
