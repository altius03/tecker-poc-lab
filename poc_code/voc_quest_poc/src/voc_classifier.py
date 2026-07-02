from __future__ import annotations

import re
from typing import Any


ISSUE_KEYWORDS = {
    "shipping": ["배송", "지연", "늦다", "늦음", "안 옴", "안옴", "2주", "파손"],
    "skin_irritation": ["자극", "따갑다", "따가움", "트러블", "뒤집어짐"],
    "price_refund": ["비싸다", "비싼", "환불", "교환", "돈 아깝다", "돈아깝"],
    "packaging": ["펌프", "불량", "새다", "샘", "포장", "파손", "용기"],
    "smell_texture": ["냄새", "향", "끈적", "제형", "묽다"],
}

NEGATIVE_KEYWORDS = ["별로", "실망", "최악", "불편", "불만", "아깝다", "짜증", "문제"]
POSITIVE_KEYWORDS = ["좋다", "좋네요", "만족", "추천", "촉촉", "빠르네요"]


def classify_items(items: list[dict[str, Any]], product_seed: str) -> list[dict[str, Any]]:
    # TODO: replace with LLM classifier after PoC validates the data path.
    classified: list[dict[str, Any]] = []
    for item in items:
        text = " ".join(
            [
                item.get("title", ""),
                item.get("snippet", ""),
                item.get("public_text_excerpt", ""),
                item.get("post_text", ""),
            ]
        )
        issue_type, issue_hits = detect_issue_type(text)
        negative_hits = find_hits(text, NEGATIVE_KEYWORDS)
        positive_hits = find_hits(text, POSITIVE_KEYWORDS)
        sarcasm_suspected = detect_sarcasm(text)
        sentiment = detect_sentiment(issue_type, negative_hits, positive_hits, sarcasm_suspected)
        evidence = build_evidence(text, issue_hits + negative_hits + positive_hits)
        confidence = score_confidence(issue_type, negative_hits, sarcasm_suspected, item.get("ad_suspected", False))

        classified.append(
            {
                "item_id": item["item_id"],
                "product_candidate": product_seed,
                "sentiment": sentiment,
                "sarcasm_suspected": sarcasm_suspected,
                "issue_type": issue_type,
                "evidence": evidence,
                "confidence": confidence,
            }
        )
    return classified


def detect_issue_type(text: str) -> tuple[str, list[str]]:
    best_issue = "unknown"
    best_hits: list[str] = []
    for issue_type, keywords in ISSUE_KEYWORDS.items():
        hits = find_hits(text, keywords)
        if len(hits) > len(best_hits):
            best_issue = issue_type
            best_hits = hits
    return best_issue, best_hits


def detect_sentiment(
    issue_type: str,
    negative_hits: list[str],
    positive_hits: list[str],
    sarcasm_suspected: bool,
) -> str:
    has_negative = issue_type != "unknown" or bool(negative_hits) or sarcasm_suspected
    has_positive = bool(positive_hits)
    if has_negative and has_positive:
        return "mixed"
    if has_negative:
        return "negative"
    if has_positive:
        return "positive"
    return "neutral"


def detect_sarcasm(text: str) -> bool:
    delay_signal = any(keyword in text for keyword in ["지연", "늦", "2주", "안 옴", "안옴"])
    negative_signal = any(keyword in text for keyword in NEGATIVE_KEYWORDS)
    laugh_signal = "ㅋㅋ" in text or "ㅋ" in text
    praise_with_problem = ("진짜 빠르네요" in text and delay_signal) or ("좋네요" in text and negative_signal)
    return laugh_signal and (delay_signal or negative_signal) or praise_with_problem


def score_confidence(
    issue_type: str,
    negative_hits: list[str],
    sarcasm_suspected: bool,
    ad_suspected: bool,
) -> float:
    score = 0.35
    if issue_type != "unknown":
        score += 0.3
    if negative_hits:
        score += 0.15
    if sarcasm_suspected:
        score += 0.1
    if ad_suspected:
        score -= 0.15
    return round(max(0.1, min(score, 0.95)), 2)


def find_hits(text: str, keywords: list[str]) -> list[str]:
    return [keyword for keyword in keywords if keyword in text]


def build_evidence(text: str, hits: list[str]) -> str:
    cleaned = re.sub(r"\s+", " ", text).strip()
    if not hits:
        return cleaned[:120]
    first_hit = hits[0]
    index = cleaned.find(first_hit)
    if index < 0:
        return cleaned[:120]
    start = max(0, index - 35)
    end = min(len(cleaned), index + 85)
    return cleaned[start:end]
