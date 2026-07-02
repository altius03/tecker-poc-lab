import json
import subprocess
import sys
from pathlib import Path


PROJECT_ROOT = Path(__file__).resolve().parents[1]


def test_cli_sample_run_writes_success_result() -> None:
    completed = subprocess.run(
        [
            sys.executable,
            "-m",
            "src.run",
            "--seed",
            "브랜드A 블루 수딩 앰플",
            "--use-sample",
        ],
        cwd=PROJECT_ROOT,
        text=True,
        capture_output=True,
        timeout=30,
    )

    assert completed.returncode == 0, completed.stderr + completed.stdout

    result_path = PROJECT_ROOT / "outputs" / "latest" / "result.json"
    result = json.loads(result_path.read_text(encoding="utf-8"))

    assert result["status"] == "success"
    assert result["fallback_used"] is True
    assert result["summary"]["query_count"] >= 15
    assert result["summary"]["collected_count"] >= 10
    assert result["summary"]["quest_count"] >= 2
    assert result["summary"]["duplicate_count"] >= 1

