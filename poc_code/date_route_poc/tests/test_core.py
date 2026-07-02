from __future__ import annotations

import json
import unittest
from pathlib import Path

from src.condition_parser import parse_conditions
from src.directions_url_builder import build_directions
from src.place_filter import classify_role, filter_places
from src.region_resolver import STATIC_REGION_CENTERS
from src.result_writer import failure_result
from src.route_builder import build_route


BASE_DIR = Path(__file__).resolve().parents[1]


class CorePipelineTests(unittest.TestCase):
    def test_condition_parser_extracts_core_conditions(self) -> None:
        query = "성수역 근처에서 저녁 데이트할 건데, 예산 12만 원 안쪽, 분위기 좋은 파스타집이랑 디저트 카페, 걸어서 이동 가능한 코스로 짜줘"

        parsed = parse_conditions(query)

        self.assertEqual(parsed["region"], "성수역")
        self.assertEqual(parsed["budget_krw"], 120000)
        self.assertEqual(parsed["transport"], "walk")
        self.assertIn("파스타", parsed["categories"])
        self.assertIn("카페", parsed["categories"])
        self.assertIn("분위기 좋은", parsed["moods"])
        self.assertGreaterEqual(parsed["parsed_condition_count"], 5)

    def test_sample_places_build_route_and_directions(self) -> None:
        sample_places = json.loads((BASE_DIR / "samples" / "sample_places.json").read_text(encoding="utf-8"))
        conditions = parse_conditions("성수역 근처 데이트 코스 짜줘")
        region_center = {**STATIC_REGION_CENTERS["성수역"], "source": "sample_static_region"}

        filter_result = filter_places(sample_places, conditions, region_center)
        route, _ = build_route(filter_result["filtered_places"], conditions)
        directions = build_directions(route, filter_result["filtered_places"], conditions["transport"])

        self.assertGreaterEqual(len(filter_result["filtered_places"]), 5)
        self.assertGreaterEqual(len(route), 2)
        self.assertLessEqual(len(route), 4)
        self.assertEqual([stop["role"] for stop in route[:3]], ["meal", "cafe", "walk_photo"])
        self.assertTrue(any(item["provider"] == "google_maps_url" and item["verification_status"] == "not_verified" for item in directions))

    def test_failure_result_schema_contains_required_error_fields(self) -> None:
        result = failure_result(
            input_payload={"query": "성수역 근처 데이트 코스 짜줘"},
            modules_run=["condition_parser"],
            code="MISSING_API_KEY",
            error_type="ConfigurationError",
            message="missing key",
            partial_result={"parsed_conditions": {}},
            limitations=["no key"],
        )

        self.assertEqual(result["status"], "failed")
        self.assertEqual(result["error"]["code"], "MISSING_API_KEY")
        self.assertIn("message", result["error"])
        self.assertIn("partial_result", result)

    def test_kakao_cafe_subcategory_is_not_classified_as_meal(self) -> None:
        place = {
            "name": "어니언 성수",
            "category": "음식점 > 카페",
            "address": "서울 성동구 성수동",
        }

        self.assertEqual(classify_role(place), "cafe")

    def test_route_builder_does_not_move_backwards_when_filling_extra_stop(self) -> None:
        places = [
            {"place_id": "c1", "name": "카페 1", "role": "cafe", "matched_keywords": []},
            {"place_id": "w1", "name": "산책 1", "role": "walk_photo", "matched_keywords": []},
            {"place_id": "c2", "name": "카페 2", "role": "cafe", "matched_keywords": []},
            {"place_id": "w2", "name": "산책 2", "role": "walk_photo", "matched_keywords": []},
        ]

        route, _ = build_route(places, {"route_stop_count": 3})

        self.assertEqual([stop["role"] for stop in route], ["cafe", "walk_photo", "walk_photo"])


if __name__ == "__main__":
    unittest.main()
