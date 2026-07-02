from __future__ import annotations

import json
import urllib.error
import urllib.parse
import urllib.request
from typing import Any


class KakaoLocalError(RuntimeError):
    pass


class KakaoLocalClient:
    BASE_URL = "https://dapi.kakao.com"

    def __init__(self, api_key: str, timeout_seconds: int = 10) -> None:
        self.api_key = api_key
        self.timeout_seconds = timeout_seconds

    def search_keyword(
        self,
        query: str,
        *,
        x: str | None = None,
        y: str | None = None,
        radius: int | None = None,
        category_group_code: str | None = None,
        size: int = 5,
    ) -> list[dict[str, Any]]:
        params: dict[str, Any] = {"query": query, "size": size}
        if x and y:
            params.update({"x": x, "y": y})
        if radius:
            params["radius"] = radius
        if category_group_code:
            params["category_group_code"] = category_group_code
        data = self._get_json("/v2/local/search/keyword.json", params)
        return [normalize_kakao_place(doc) for doc in data.get("documents", [])]

    def search_category(
        self,
        category_group_code: str,
        *,
        x: str | None = None,
        y: str | None = None,
        radius: int | None = None,
        size: int = 5,
    ) -> list[dict[str, Any]]:
        params: dict[str, Any] = {"category_group_code": category_group_code, "size": size}
        if x and y:
            params.update({"x": x, "y": y})
        if radius:
            params["radius"] = radius
        data = self._get_json("/v2/local/search/category.json", params)
        return [normalize_kakao_place(doc) for doc in data.get("documents", [])]

    def _get_json(self, path: str, params: dict[str, Any]) -> dict[str, Any]:
        url = f"{self.BASE_URL}{path}?{urllib.parse.urlencode(params)}"
        headers = {"Authorization": f"KakaoAK {self.api_key}"}

        try:
            import requests

            response = requests.get(url, headers=headers, timeout=self.timeout_seconds)
            if response.status_code >= 400:
                raise KakaoLocalError(f"Kakao Local API returned HTTP {response.status_code}: {response.text[:300]}")
            return response.json()
        except ImportError:
            request = urllib.request.Request(url, headers=headers)
            try:
                with urllib.request.urlopen(request, timeout=self.timeout_seconds) as response:
                    return json.loads(response.read().decode("utf-8"))
            except urllib.error.HTTPError as exc:
                body = exc.read().decode("utf-8", errors="replace")
                raise KakaoLocalError(f"Kakao Local API returned HTTP {exc.code}: {body[:300]}") from exc
        except KakaoLocalError:
            raise
        except Exception as exc:
            raise KakaoLocalError(str(exc)) from exc


def normalize_kakao_place(doc: dict[str, Any]) -> dict[str, Any]:
    return {
        "place_id": str(doc.get("id") or ""),
        "name": doc.get("place_name") or doc.get("name") or "",
        "category": doc.get("category_name") or doc.get("category") or "",
        "address": doc.get("road_address_name") or doc.get("address_name") or doc.get("address") or "",
        "x": str(doc.get("x") or ""),
        "y": str(doc.get("y") or ""),
        "phone": doc.get("phone") or "",
        "place_url": doc.get("place_url") or "",
        "distance_m": _as_int_or_none(doc.get("distance")),
        "source": "kakao_local_api",
        "matched_keywords": [],
    }


def _as_int_or_none(value: Any) -> int | None:
    if value in (None, ""):
        return None
    try:
        return int(float(value))
    except (TypeError, ValueError):
        return None
