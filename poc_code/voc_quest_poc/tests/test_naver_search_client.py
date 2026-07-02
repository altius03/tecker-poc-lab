from pathlib import Path

import pytest
import requests

from src.naver_search_client import ApiRequestError, NaverSearchClient


class FakeResponse:
    def __init__(self, payload=None, error: Exception | None = None):
        self.payload = payload
        self.error = error

    def raise_for_status(self) -> None:
        if self.error:
            raise self.error

    def json(self):
        if isinstance(self.payload, Exception):
            raise self.payload
        return self.payload


def test_collect_from_sample_normalizes_blog_cafe_shop() -> None:
    client = NaverSearchClient(client_id=None, client_secret=None)

    items = client.collect_from_sample(Path("samples/sample_naver_response.json"))

    assert len(items) >= 10
    assert {item["source_type"] for item in items} == {"blog", "cafe", "shop"}
    assert all(item["collection_method"] == "naver_search_api" for item in items)
    assert all(item["item_id"] for item in items)


def test_collect_maps_http_failure_to_api_error(monkeypatch: pytest.MonkeyPatch) -> None:
    def fake_get(*args, **kwargs):
        return FakeResponse(error=requests.HTTPError("403 forbidden"))

    monkeypatch.setattr(requests, "get", fake_get)
    client = NaverSearchClient(client_id="id", client_secret="secret")

    with pytest.raises(ApiRequestError, match="Naver API request failed"):
        client.collect(queries=["브랜드A"], display_per_query=1, max_items=1)


def test_collect_maps_non_json_response_to_api_error(monkeypatch: pytest.MonkeyPatch) -> None:
    def fake_get(*args, **kwargs):
        return FakeResponse(payload=ValueError("not json"))

    monkeypatch.setattr(requests, "get", fake_get)
    client = NaverSearchClient(client_id="id", client_secret="secret")

    with pytest.raises(ApiRequestError, match="non-JSON"):
        client.collect(queries=["브랜드A"], display_per_query=1, max_items=1)

