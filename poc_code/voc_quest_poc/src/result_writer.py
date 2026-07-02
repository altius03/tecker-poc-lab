from __future__ import annotations

import json
from datetime import datetime
from pathlib import Path
from typing import Any

from pydantic import BaseModel

from .config import OUTPUTS_DIR


class ResultEnvelope(BaseModel):
    poc_name: str
    status: str


class ResultWriter:
    def __init__(self, outputs_dir: Path = OUTPUTS_DIR):
        self.outputs_dir = outputs_dir
        self.latest_dir = outputs_dir / "latest"
        self.runs_dir = outputs_dir / "runs"

    def write(self, result: dict[str, Any]) -> dict[str, str]:
        ResultEnvelope(**result)
        self.latest_dir.mkdir(parents=True, exist_ok=True)
        self.runs_dir.mkdir(parents=True, exist_ok=True)

        run_dir = self.runs_dir / datetime.now().strftime("%Y%m%d_%H%M%S")
        run_dir.mkdir(parents=True, exist_ok=True)

        latest_path = self.latest_dir / "result.json"
        run_path = run_dir / "result.json"
        payload = json.dumps(result, ensure_ascii=False, indent=2)
        latest_path.write_text(payload + "\n", encoding="utf-8")
        run_path.write_text(payload + "\n", encoding="utf-8")
        return {"latest": str(latest_path), "run": str(run_path)}


def build_failure_result(
    *,
    code: str,
    error_type: str,
    message: str,
    input_payload: dict[str, Any] | None = None,
    modules_run: list[str] | None = None,
    partial_result: dict[str, Any] | None = None,
    limitations: list[str] | None = None,
) -> dict[str, Any]:
    return {
        "poc_name": "voc_quest",
        "status": "failed",
        "input": input_payload or {},
        "modules_run": modules_run or [],
        "error": {
            "code": code,
            "type": error_type,
            "message": message,
        },
        "partial_result": partial_result or {},
        "limitations": limitations or [],
    }

