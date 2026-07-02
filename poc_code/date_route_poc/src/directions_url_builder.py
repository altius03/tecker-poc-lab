from __future__ import annotations

import urllib.parse
from typing import Any


def build_directions(route: list[dict[str, Any]], places: list[dict[str, Any]], transport: str | None) -> list[dict[str, str]]:
    places_by_id = {str(place.get("place_id")): place for place in places}
    route_places = [places_by_id.get(str(stop.get("place_id"))) for stop in route]
    route_places = [place for place in route_places if place]

    directions: list[dict[str, str]] = []
    for place in route_places:
        place_url = place.get("place_url") or _kakao_search_url(place.get("name", ""))
        directions.append(
            {
                "provider": "kakao",
                "url": place_url,
                "verification_status": "verified" if place.get("place_url") else "not_verified",
                "note": "Kakao Local place_url from candidate data." if place.get("place_url") else "Kakao Map search URL template.",
            }
        )

    if len(route_places) >= 2:
        directions.append(_google_maps_url(route_places, transport))
        directions.append(_kakao_route_candidate_url(route_places))

    return directions


def _kakao_search_url(name: str) -> str:
    return f"https://map.kakao.com/link/search/{urllib.parse.quote(name)}"


def _google_maps_url(route_places: list[dict[str, Any]], transport: str | None) -> dict[str, str]:
    travel_mode = "walking" if transport == "walk" else "driving" if transport == "car" else "transit" if transport == "transit" else "walking"
    origin = _lat_lng(route_places[0])
    destination = _lat_lng(route_places[-1])
    waypoints = [_lat_lng(place) for place in route_places[1:-1]]
    params = {
        "api": "1",
        "travelmode": travel_mode,
        "origin": origin,
        "destination": destination,
    }
    if waypoints:
        params["waypoints"] = "|".join(waypoints)
    return {
        "provider": "google_maps_url",
        "url": f"https://www.google.com/maps/dir/?{urllib.parse.urlencode(params)}",
        "verification_status": "not_verified",
        "note": "Google Maps URL template only; Google Places/Routes APIs were not called.",
    }


def _kakao_route_candidate_url(route_places: list[dict[str, Any]]) -> dict[str, str]:
    start = route_places[0]
    end = route_places[-1]
    url = (
        "https://map.kakao.com/link/from/"
        f"{urllib.parse.quote(start.get('name', 'start'))},{start.get('y')},{start.get('x')}"
        "/to/"
        f"{urllib.parse.quote(end.get('name', 'end'))},{end.get('y')},{end.get('x')}"
    )
    return {
        "provider": "not_verified",
        "url": url,
        "verification_status": "not_verified",
        "note": "Kakao route link candidate assembled from coordinates; not verified by a routing API.",
    }


def _lat_lng(place: dict[str, Any]) -> str:
    return f"{place.get('y')},{place.get('x')}"
