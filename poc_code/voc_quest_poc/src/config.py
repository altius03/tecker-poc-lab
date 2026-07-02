from __future__ import annotations

import os
from dataclasses import dataclass
from pathlib import Path

from dotenv import load_dotenv


PROJECT_ROOT = Path(__file__).resolve().parents[1]
SAMPLES_DIR = PROJECT_ROOT / "samples"
OUTPUTS_DIR = PROJECT_ROOT / "outputs"


@dataclass(frozen=True)
class AppConfig:
    project_root: Path
    samples_dir: Path
    outputs_dir: Path
    naver_client_id: str | None
    naver_client_secret: str | None
    query_limit: int = 20
    display_per_query: int = 5
    max_collected_items: int = 80
    timeout_seconds: int = 10
    insane_search_timeout_seconds: int = 15
    insane_search_max_items: int = 10
    insane_search_content_limit: int = 2500

    @property
    def has_naver_credentials(self) -> bool:
        return bool(self.naver_client_id and self.naver_client_secret)


def load_config() -> AppConfig:
    load_dotenv(PROJECT_ROOT / ".env")
    return AppConfig(
        project_root=PROJECT_ROOT,
        samples_dir=SAMPLES_DIR,
        outputs_dir=OUTPUTS_DIR,
        naver_client_id=os.getenv("NAVER_CLIENT_ID") or None,
        naver_client_secret=os.getenv("NAVER_CLIENT_SECRET") or None,
    )
