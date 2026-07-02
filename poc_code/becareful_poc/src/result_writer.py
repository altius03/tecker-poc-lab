import json
from datetime import datetime
from pathlib import Path
from typing import Any

from .config import LATEST_OUTPUT_DIR, RUNS_OUTPUT_DIR


def _write_json(path: Path, payload: dict[str, Any]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(
        json.dumps(payload, ensure_ascii=False, indent=2) + "\n",
        encoding="utf-8",
    )


def _new_run_dir() -> Path:
    stamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    run_dir = RUNS_OUTPUT_DIR / stamp
    suffix = 1
    while run_dir.exists():
        run_dir = RUNS_OUTPUT_DIR / f"{stamp}_{suffix:02d}"
        suffix += 1
    return run_dir


def write_result(payload: dict[str, Any]) -> dict[str, Path]:
    latest_path = LATEST_OUTPUT_DIR / "result.json"
    run_path = _new_run_dir() / "result.json"

    _write_json(latest_path, payload)
    _write_json(run_path, payload)

    return {
        "latest_path": latest_path,
        "run_path": run_path,
    }

