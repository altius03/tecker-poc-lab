from __future__ import annotations

from statistics import mean
from typing import Any


ISSUE_META = {
    "shipping": {
        "title": "배송 지연/파손 VOC 확인",
        "owner": "logistics",
        "action": "배송 지연·파손 언급 후보를 CS 처리 이력과 대조하고 배송 안내 문구를 보강한다.",
    },
    "skin_irritation": {
        "title": "피부 자극 반응 원인 점검",
        "owner": "product",
        "action": "자극·트러블 언급 후보를 성분/사용법/피부 타입 안내와 연결해 개선 가설을 만든다.",
    },
    "price_refund": {
        "title": "가격/환불 불만 흐름 점검",
        "owner": "cs",
        "action": "환불·교환·가격 불만 후보를 정책 안내와 구매 전환 문구 개선 항목으로 분리한다.",
    },
    "packaging": {
        "title": "용기/포장 품질 이슈 확인",
        "owner": "product",
        "action": "펌프·포장·파손 언급 후보를 패키징 QA 체크리스트에 반영한다.",
    },
    "smell_texture": {
        "title": "향/제형 불만 표현 정리",
        "owner": "content",
        "action": "냄새·향·제형 언급 후보를 상세페이지 기대치 조정 문구로 전환한다.",
    },
}


def generate_issue_clusters(classified_items: list[dict[str, Any]]) -> list[dict[str, Any]]:
    grouped: dict[str, list[dict[str, Any]]] = {}
    for item in classified_items:
        issue_type = item.get("issue_type", "unknown")
        sentiment = item.get("sentiment", "neutral")
        if issue_type == "unknown" or sentiment not in {"negative", "mixed"}:
            continue
        grouped.setdefault(issue_type, []).append(item)

    clusters: list[dict[str, Any]] = []
    for issue_type, items in sorted(grouped.items(), key=lambda pair: len(pair[1]), reverse=True):
        clusters.append(
            {
                "issue_type": issue_type,
                "count": len(items),
                "evidence_item_ids": [item["item_id"] for item in items],
                "representative_evidence": items[0].get("evidence", ""),
                "average_confidence": round(mean(item.get("confidence", 0.0) for item in items), 2),
            }
        )
    return clusters


def generate_quests(issue_clusters: list[dict[str, Any]]) -> list[dict[str, Any]]:
    quests: list[dict[str, Any]] = []
    for index, cluster in enumerate(issue_clusters, start=1):
        issue_type = cluster["issue_type"]
        meta = ISSUE_META.get(
            issue_type,
            {
                "title": "미분류 VOC 확인",
                "owner": "unknown",
                "action": "미분류 후보를 사람이 검토해 후속 분류 기준을 추가한다.",
            },
        )
        count = cluster.get("count", 0)
        priority = "high" if count >= 3 else "medium" if count == 2 else "low"
        quests.append(
            {
                "quest_id": f"QST-{index:03d}",
                "title": meta["title"],
                "issue_type": issue_type,
                "priority": priority,
                "owner_candidate": meta["owner"],
                "action": meta["action"],
                "evidence_item_ids": cluster.get("evidence_item_ids", []),
            }
        )
    return quests

