from __future__ import annotations

import re


DEFAULT_SUFFIXES = [
    "후기",
    "리뷰",
    "단점",
    "불만",
    "배송 지연",
    "배송 늦음",
    "트러블",
    "따가움",
    "자극",
    "환불",
    "교환",
    "비싸다",
    "냄새",
    "펌프 불량",
    "파손",
    "내돈내산",
    "협찬",
]

COMMUNITY_SUFFIXES = [
    "맘카페",
    "맘스홀릭",
    "파우더룸",
    "여우야",
    "성분",
    "내돈내산 단점",
]

SNS_DISCOVERY_SUFFIXES = [
    "인스타 후기",
    "쓰레드 후기",
    "트위터 후기",
    "X 후기",
]


def normalize_seed(seed: str | None) -> str:
    return re.sub(r"\s+", " ", seed or "").strip()


def expand_queries(seed: str, max_queries: int = 20) -> list[str]:
    normalized = normalize_seed(seed)
    if not normalized:
        return []

    tokens = normalized.split()
    brand = tokens[0] if tokens else normalized
    product = " ".join(tokens[1:]) if len(tokens) > 1 else normalized
    product_no_space = product.replace(" ", "")

    candidates: list[str] = [
        normalized,
        f"{normalized} 공식",
        f"{normalized} 최저가",
        f"{brand} {product_no_space}",
    ]

    priority_suffixes = [
        "후기",
        "리뷰",
        "단점",
        "불만",
        "맘카페",
        "맘스홀릭",
        "파우더룸",
        "여우야",
        "인스타 후기",
        "쓰레드 후기",
        "트러블",
        "따가움",
        "자극",
        "환불",
        "냄새",
        "배송 지연",
    ]

    for suffix in priority_suffixes:
        candidates.append(f"{normalized} {suffix}")

    if product and product != normalized:
        candidates.extend(
            [
                f"{product} 후기",
                f"{product} 단점",
                f"{brand} 앰플 리뷰",
            ]
        )

    deduped = list(dict.fromkeys(q for q in candidates if q.strip()))
    return deduped[:max_queries]
