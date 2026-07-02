from __future__ import annotations

import os
from dataclasses import dataclass
from pathlib import Path


BASE_DIR = Path(__file__).resolve().parents[1]


@dataclass(frozen=True)
class Settings:
    base_dir: Path
    kakao_rest_api_key: str | None
    google_maps_api_key: str | None
    openai_api_key: str | None
    openai_model: str = "gpt-4o-mini"
    kakao_timeout_seconds: int = 10
    google_timeout_seconds: int = 15
    openai_timeout_seconds: int = 30
    max_places_per_category: int = 5
    max_total_places: int = 20
    min_final_candidates: int = 3
    max_review_places: int = 2


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
    kakao_api_key = os.getenv("KAKAO_REST_API_KEY")
    google_api_key = os.getenv("GOOGLE_MAPS_API_KEY")
    openai_api_key = os.getenv("OPENAI_API_KEY")
    openai_model = os.getenv("OPENAI_MODEL")
    return Settings(
        base_dir=BASE_DIR,
        kakao_rest_api_key=kakao_api_key.strip() if kakao_api_key and kakao_api_key.strip() else None,
        google_maps_api_key=google_api_key.strip() if google_api_key and google_api_key.strip() else None,
        openai_api_key=openai_api_key.strip() if openai_api_key and openai_api_key.strip() else None,
        openai_model=openai_model.strip() if openai_model and openai_model.strip() else "gpt-4o-mini",
    )
