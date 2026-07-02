from __future__ import annotations

import json
import os
import re
import subprocess
import sys
from pathlib import Path
from typing import Any
from urllib.parse import urlparse

from .config import PROJECT_ROOT


ENGINE_ROOT = PROJECT_ROOT / "external" / "insane-search" / "skills" / "insane-search"


class InsaneSearchUnavailable(RuntimeError):
    pass


class InsaneSearchClient:
    def __init__(
        self,
        *,
        engine_root: Path = ENGINE_ROOT,
        timeout_seconds: int = 15,
        content_limit: int = 2500,
        max_attempts: int = 3,
        enable_playwright: bool = False,
    ):
        self.engine_root = engine_root
        self.timeout_seconds = timeout_seconds
        self.content_limit = content_limit
        self.max_attempts = max_attempts
        self.enable_playwright = enable_playwright

    @property
    def available(self) -> bool:
        return (self.engine_root / "engine" / "__main__.py").exists()

    def enrich_items(self, items: list[dict[str, Any]], max_items: int = 10) -> list[dict[str, Any]]:
        if not self.available:
            raise InsaneSearchUnavailable(f"insane-search engine not found at {self.engine_root}")

        enriched: list[dict[str, Any]] = []
        attempted = 0
        for item in items:
            next_item = dict(item)
            source_url = str(item.get("source_url") or "")
            source_type = item.get("source_type")
            if attempted < max_items and source_url.startswith("http") and source_type != "shop":
                attempted += 1
                reader_url = prepare_reader_url(source_url)
                fetched = self.fetch_url(reader_url)
                next_item["insane_search"] = {
                    "attempted": True,
                    "reader_url": reader_url,
                    "ok": fetched.get("ok", False),
                    "verdict": fetched.get("verdict", ""),
                    "final_url": fetched.get("final_url", ""),
                    "summary": fetched.get("summary", ""),
                    "error": fetched.get("error", ""),
                    "content_length": fetched.get("content_length", 0),
                }
                content = fetched.get("content", "")
                if fetched.get("ok") and content:
                    next_item["public_text_excerpt"] = normalize_public_text(content, self.content_limit)
                    next_item["public_text_length"] = len(content)
                    next_item["collection_method"] = append_method(
                        str(next_item.get("collection_method", "")),
                        "insane_search",
                    )
                    next_item["text_scope"] = "public_page_text"
                    next_item["next_action"] = "analyze_public_text"
            else:
                next_item["insane_search"] = {"attempted": False}
            enriched.append(next_item)
        return enriched

    def fetch_url(self, url: str) -> dict[str, Any]:
        script = (
            "import json, sys; "
            "sys.path.insert(0, sys.argv[1]); "
            "from engine import fetch; "
            "url=sys.argv[2]; timeout=int(sys.argv[3]); max_attempts=int(sys.argv[4]); "
            "enable_playwright=(sys.argv[5]=='1'); "
            "result=fetch(url, timeout=timeout, max_attempts=max_attempts, enable_playwright=enable_playwright); "
            "print(json.dumps({"
            "'ok': result.ok, "
            "'content': result.content, "
            "'content_length': len(result.content), "
            "'final_url': result.final_url, "
            "'verdict': result.verdict, "
            "'profile_used': result.profile_used, "
            "'summary': result.summary, "
            "'stop_reason': result.stop_reason"
            "}, ensure_ascii=False))"
        )
        try:
            completed = subprocess.run(
                [
                    sys.executable,
                    "-c",
                    script,
                    str(self.engine_root),
                    url,
                    str(self.timeout_seconds),
                    str(self.max_attempts),
                    "1" if self.enable_playwright else "0",
                ],
                cwd=PROJECT_ROOT,
                text=True,
                encoding="utf-8",
                errors="replace",
                capture_output=True,
                timeout=self.timeout_seconds + 20,
                env={**os.environ, "PYTHONIOENCODING": "utf-8"},
            )
        except subprocess.TimeoutExpired as exc:
            return {
                "ok": False,
                "error": f"timeout: {exc}",
                "content": "",
                "content_length": 0,
            }

        if completed.returncode not in {0, 1}:
            return {
                "ok": False,
                "error": (completed.stderr or completed.stdout).strip()[:2000],
                "content": "",
                "content_length": 0,
            }

        try:
            return json.loads(completed.stdout)
        except json.JSONDecodeError:
            return {
                "ok": False,
                "error": f"invalid engine json: {(completed.stderr or completed.stdout).strip()[:2000]}",
                "content": "",
                "content_length": 0,
            }


def append_method(existing: str, new_method: str) -> str:
    methods = [part for part in existing.split("+") if part]
    if new_method not in methods:
        methods.append(new_method)
    return "+".join(methods)


def normalize_public_text(text: str, limit: int) -> str:
    text = extract_visible_text(text)
    cleaned = re.sub(r"\s+", " ", text or "").strip()
    return cleaned[:limit]


def extract_visible_text(text: str) -> str:
    if not text:
        return ""
    if "<" not in text or ">" not in text:
        return text
    try:
        from bs4 import BeautifulSoup

        soup = BeautifulSoup(text, "html.parser")
        for tag in soup(["script", "style", "noscript"]):
            tag.decompose()
        return soup.get_text(" ")
    except Exception:
        return re.sub(r"<[^>]+>", " ", text)


def prepare_reader_url(url: str) -> str:
    parsed = urlparse(url)
    host = parsed.netloc.lower()
    if host == "blog.naver.com":
        parts = [part for part in parsed.path.split("/") if part]
        if len(parts) >= 2 and parts[1].isdigit():
            return f"https://m.blog.naver.com/PostView.naver?blogId={parts[0]}&logNo={parts[1]}"
    return url
