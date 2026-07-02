from __future__ import annotations

import hashlib
import html
import re
from typing import Any


AD_KEYWORDS = ["협찬", "제공받아", "체험단", "파트너스", "광고"]
TAG_RE = re.compile(r"<[^>]+>")
PHONE_RE = re.compile(r"(?<!\d)(?:01[016789])[-.\s]?\d{3,4}[-.\s]?\d{4}(?!\d)")
EMAIL_RE = re.compile(r"[\w.+-]+@[\w-]+(?:\.[\w-]+)+")
ORDER_RE = re.compile(r"(주문\s*번호|order\s*no\.?)\s*[:#-]?\s*[A-Z0-9-]{6,}", re.IGNORECASE)
ADDRESS_RE = re.compile(r"([가-힣]+(?:시|도)\s+[가-힣]+(?:구|군|시)\s+[가-힣0-9-]+(?:로|길)\s*\d+)")


def clean_items(items: list[dict[str, Any]]) -> tuple[list[dict[str, Any]], dict[str, int]]:
    cleaned: list[dict[str, Any]] = []
    hash_counts: dict[str, int] = {}
    pii_count = 0
    ad_count = 0

    for item in items:
        title, title_pii = clean_text(item.get("title", ""))
        snippet, snippet_pii = clean_text(item.get("snippet", ""))
        public_text_excerpt, public_text_pii = clean_text(item.get("public_text_excerpt", ""))
        post_text, post_text_pii = clean_text(item.get("post_text", ""))
        content_hash = make_content_hash(title, snippet, public_text_excerpt, post_text)
        hash_counts[content_hash] = hash_counts.get(content_hash, 0) + 1
        ad_suspected = contains_ad_signal(title, snippet, public_text_excerpt, post_text)
        pii_masked = title_pii or snippet_pii or public_text_pii or post_text_pii

        if pii_masked:
            pii_count += 1
        if ad_suspected:
            ad_count += 1

        next_item = dict(item)
        next_item.update(
            {
                "title": title,
                "snippet": snippet,
                "public_text_excerpt": public_text_excerpt,
                "post_text": post_text,
                "content_hash": content_hash,
                "ad_suspected": ad_suspected,
                "pii_masked": pii_masked,
            }
        )
        cleaned.append(next_item)

    duplicate_count = sum(count - 1 for count in hash_counts.values() if count > 1)
    return cleaned, {
        "pii_masked_count": pii_count,
        "ad_suspected_count": ad_count,
        "duplicate_count": duplicate_count,
    }


def clean_text(value: str) -> tuple[str, bool]:
    text = html.unescape(TAG_RE.sub("", value or ""))
    text = re.sub(r"\s+", " ", text).strip()
    original = text
    text = PHONE_RE.sub("[PHONE_MASKED]", text)
    text = EMAIL_RE.sub("[EMAIL_MASKED]", text)
    text = ORDER_RE.sub("[ORDER_MASKED]", text)
    text = ADDRESS_RE.sub("[ADDRESS_MASKED]", text)
    return text, text != original


def contains_ad_signal(title: str, snippet: str, public_text_excerpt: str = "", post_text: str = "") -> bool:
    merged = f"{title} {snippet} {public_text_excerpt} {post_text}"
    return any(keyword in merged for keyword in AD_KEYWORDS)


def make_content_hash(title: str, snippet: str, public_text_excerpt: str = "", post_text: str = "") -> str:
    normalized = re.sub(r"\s+", " ", f"{title} {snippet} {public_text_excerpt} {post_text}".lower()).strip()
    return hashlib.sha256(normalized.encode("utf-8")).hexdigest()[:16]
