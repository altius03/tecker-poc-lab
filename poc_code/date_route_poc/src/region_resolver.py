from __future__ import annotations

from typing import Any

from .kakao_local_client import KakaoLocalClient


STATIC_REGION_CENTERS = {
    "성수역": {"name": "성수역", "x": "127.055983", "y": "37.544581", "address": "서울 성동구 아차산로"},
    "성수": {"name": "성수역", "x": "127.055983", "y": "37.544581", "address": "서울 성동구 아차산로"},
    "홍대": {"name": "홍대입구역", "x": "126.923708", "y": "37.557527", "address": "서울 마포구 양화로"},
    "강남역": {"name": "강남역", "x": "127.027610", "y": "37.497952", "address": "서울 강남구 강남대로"},
    "잠실": {"name": "잠실역", "x": "127.100159", "y": "37.513261", "address": "서울 송파구 올림픽로"},
}


def resolve_region_center(
    conditions: dict[str, Any],
    *,
    client: KakaoLocalClient | None,
    use_sample: bool,
) -> dict[str, Any] | None:
    region = conditions.get("region")
    if not region:
        return None

    if client:
        docs = client.search_keyword(str(region), size=3)
        if docs:
            first = docs[0]
            return {
                "name": first["name"],
                "address": first["address"],
                "x": first["x"],
                "y": first["y"],
                "source": "kakao_local_api",
            }

    if use_sample:
        static = STATIC_REGION_CENTERS.get(str(region))
        if static:
            return {**static, "source": "sample_static_region"}

    return None
