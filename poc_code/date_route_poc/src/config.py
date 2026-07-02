from __future__ import annotations

import os
from dataclasses import dataclass
from pathlib import Path


BASE_DIR = Path(__file__).resolve().parents[1]


@dataclass(frozen=True)
class Settings:
    base_dir: Path
    kakao_rest_api_key: str | None
    kakao_timeout_seconds: int = 10
    max_places_per_category: int = 5
    max_total_places: int = 20


def _load_dotenv_file(path: Path) -> None:
    if not path.exists():
        return
    for raw_line in path.read_text(encoding="utf-8-sig").splitlines():
        line = raw_line.strip()
        if not line or line.startswith("#") or "=" not in line:
            continue
        key, value = line.split("=", 1)
        os.environ.setdefault(key.strip().lstrip("\ufeff"), value.strip().strip('"').strip("'"))


def load_environment(base_dir: Path = BASE_DIR) -> None:
    env_path = base_dir / ".env"
    try:
        from dotenv import load_dotenv

        load_dotenv(env_path)
    except Exception:
        pass
    _load_dotenv_file(env_path)


def get_settings() -> Settings:
    load_environment(BASE_DIR)
    api_key = os.getenv("KAKAO_REST_API_KEY")
    return Settings(
        base_dir=BASE_DIR,
        kakao_rest_api_key=api_key.strip() if api_key and api_key.strip() else None,
    )
