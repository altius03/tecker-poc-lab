import json
import sys
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

import windows_agent


class WindowsAgentMockTest(unittest.TestCase):
    def test_mock_payload_contract(self):
        raw = json.loads((ROOT / "samples" / "mock_windows_powershell.json").read_text(encoding="utf-8"))
        command = {
            "ok": True,
            "args": ["mock-file"],
            "returncode": 0,
            "stderr": "",
            "duration_ms": 1,
            "input_mode": "mock",
        }
        payload = windows_agent.build_payload(raw, command, "mock", render=False)
        self.assertFalse(payload["source_real"])
        self.assertTrue(payload["test_mode"])
        self.assertEqual(payload["schema_version"], "windows-edr-dashboard-v1")
        self.assertGreaterEqual(payload["summary"]["process_count"], 10)
        self.assertGreaterEqual(payload["summary"]["connection_count"], 10)
        self.assertGreaterEqual(payload["summary"]["alert_count"], 4)
        self.assertTrue(any(alert["rule_id"] == "WIN-PROC-001" for alert in payload["alerts"]))
        self.assertTrue(all("command-line arguments" in payload["privacy"]["excluded"] for _ in [0]))


if __name__ == "__main__":
    unittest.main()
