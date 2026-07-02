from __future__ import annotations

import json
import shutil
from datetime import datetime
from pathlib import Path
from typing import Any


def write_result(base_dir: Path, result: dict[str, Any]) -> dict[str, Path]:
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    latest_dir = base_dir / "outputs" / "latest"
    run_dir = base_dir / "outputs" / "runs" / timestamp
    latest_dir.mkdir(parents=True, exist_ok=True)
    run_dir.mkdir(parents=True, exist_ok=True)

    run_path = run_dir / "result.json"
    latest_path = latest_dir / "result.json"
    payload = json.dumps(result, ensure_ascii=False, indent=2)
    run_path.write_text(payload + "\n", encoding="utf-8")
    shutil.copyfile(run_path, latest_path)
    return {"latest": latest_path, "run": run_path}


def failure_result(
    *,
    input_payload: dict[str, Any],
    modules_run: list[str],
    code: str,
    error_type: str,
    message: str,
    partial_result: dict[str, Any] | None = None,
    limitations: list[str] | None = None,
) -> dict[str, Any]:
    return {
        "poc_name": "date_route",
        "status": "failed",
        "input": input_payload,
        "modules_run": modules_run,
        "error": {
            "code": code,
            "type": error_type,
            "message": message,
        },
        "partial_result": partial_result or {},
        "limitations": limitations or [],
    }
