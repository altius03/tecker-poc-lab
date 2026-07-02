import json
import sys
import unittest
from pathlib import Path

PROJECT_DIR = Path(__file__).resolve().parents[1]
if str(PROJECT_DIR) not in sys.path:
    sys.path.insert(0, str(PROJECT_DIR))

from src.evaluate import FORBIDDEN_OUTPUT_PHRASES, evaluate_cases
from src.config import BASE_DIR
from src.pipeline import process_ocr_text


class PipelineTests(unittest.TestCase):
    def test_default_sample_core_flow(self) -> None:
        text = (BASE_DIR / "samples" / "default_rx.txt").read_text(encoding="utf-8")
        result = process_ocr_text(text)

        self.assertEqual(result["status"], "success")
        self.assertEqual(result["summary"]["medicine_candidate_count"], 2)
        self.assertEqual(result["summary"]["schedule_count"], 2)
        self.assertEqual(result["summary"]["handoff_card_count"], 1)
        self.assertEqual({item["duration"] for item in result["schedules"]}, {"30일"})

    def test_final_output_hides_risky_dur_phrases(self) -> None:
        result = process_ocr_text(
            "아모잘탄정 5/50mg\n1일 1회 아침 식후 30일\n리피토정 10mg\n1일 1회 저녁 식후 30일"
        )
        serialized = json.dumps(result, ensure_ascii=False)

        for phrase in FORBIDDEN_OUTPUT_PHRASES:
            self.assertNotIn(phrase, serialized)
        self.assertIn("의사 또는 약사에게 확인하세요", serialized)

    def test_personal_info_masking(self) -> None:
        result = process_ocr_text(
            "이름: 박민수\n전화 010-1234-5678\n주민 900101-1234567\n리피토정 10mg 하루 1번 저녁 식후 2주"
        )

        self.assertEqual(result["status"], "success")
        self.assertNotIn("박민수", result["masked_text"])
        self.assertNotIn("010-1234-5678", result["masked_text"])
        self.assertNotIn("900101-1234567", result["masked_text"])

    def test_failure_result_is_structured(self) -> None:
        result = process_ocr_text("환자명: 홍길동")

        self.assertEqual(result["status"], "failed")
        self.assertEqual(result["error"]["code"], "PARSING_FAILED")
        self.assertIn("masked_text", result["partial_result"])
        self.assertNotIn("홍길동", result["partial_result"]["masked_text"])

    def test_golden_cases_pass(self) -> None:
        report = evaluate_cases(BASE_DIR / "golden_cases" / "cases.json")

        self.assertEqual(report["status"], "pass", report)
        self.assertEqual(report["summary"]["failed_cases"], 0)


if __name__ == "__main__":
    unittest.main()
