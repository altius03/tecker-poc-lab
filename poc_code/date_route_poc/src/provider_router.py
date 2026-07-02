from __future__ import annotations

from typing import Any


def select_provider_mode(requested_provider: str | None = None) -> dict[str, Any]:
    provider = (requested_provider or "kakao").lower()
    if provider in {"google", "google_places", "google_routes"}:
        return {
            "provider_mode": "google_mode_stub",
            "actual_place_provider": None,
            "actual_route_provider": None,
            "actual_call_enabled": False,
            "note": "Google Places/Routes actual calls are intentionally out of scope for this PoC.",
        }

    return {
        "provider_mode": "kakao_mode",
        "actual_place_provider": "kakao_local_api",
        "actual_route_provider": None,
        "actual_call_enabled": True,
        "note": "Kakao Local is used for place candidate retrieval; route URLs are generated as candidates only.",
    }
