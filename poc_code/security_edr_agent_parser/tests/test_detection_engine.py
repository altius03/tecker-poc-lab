import json
import sys
import unittest
from pathlib import Path

PROJECT_DIR = Path(__file__).resolve().parents[1]
if str(PROJECT_DIR) not in sys.path:
    sys.path.insert(0, str(PROJECT_DIR))

from src.config import DEFAULT_EVENTS_PATH
from src.detection_engine import analyze_events
from src.sample_loader import load_events


class DetectionEngineTests(unittest.TestCase):
    def test_default_sample_generates_required_security_outputs(self) -> None:
        events, meta = load_events(DEFAULT_EVENTS_PATH)
        result = analyze_events(events, input_meta=meta)

        self.assertEqual(result["status"], "success")
        self.assertGreaterEqual(result["summary"]["input_event_count"], 50)
        self.assertGreaterEqual(result["summary"]["valid_event_count"], 50)
        self.assertGreaterEqual(result["summary"]["dlq_event_count"], 1)
        self.assertGreaterEqual(result["summary"]["alert_count"], 8)
        self.assertEqual(result["decision"], "needs_security_review")

    def test_core_rules_are_detected(self) -> None:
        events, meta = load_events(DEFAULT_EVENTS_PATH)
        result = analyze_events(events, input_meta=meta)
        rules = {alert["rule_id"] for alert in result["alerts"]}

        for rule_id in {"R001", "R002", "R003", "R004", "R005", "R006", "R007", "R008"}:
            self.assertIn(rule_id, rules)

    def test_attack_chain_and_mitre_mapping_are_created(self) -> None:
        events, meta = load_events(DEFAULT_EVENTS_PATH)
        result = analyze_events(events, input_meta=meta)

        self.assertGreaterEqual(len(result["incidents"]), 1)
        incident = result["incidents"][0]
        tactics = {item["tactic"] for item in incident["mitre_mapping"]}

        self.assertEqual(incident["primary_category"], "suspicious_download_to_c2_sequence")
        self.assertIn("Initial Access", tactics)
        self.assertIn("Execution", tactics)
        self.assertIn("Command and Control", tactics)
        self.assertIn("Exfiltration", tactics)

    def test_privacy_sensitive_values_are_removed_or_masked(self) -> None:
        events, meta = load_events(DEFAULT_EVENTS_PATH)
        result = analyze_events(events, input_meta=meta)
        serialized = json.dumps(result, ensure_ascii=False)

        self.assertNotIn("김테커", serialized)
        self.assertNotIn("private message body should never be retained", serialized)
        self.assertGreaterEqual(result["summary"]["privacy_mask_action_count"], 1)


if __name__ == "__main__":
    unittest.main()

