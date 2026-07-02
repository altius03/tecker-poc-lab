from src.quest_generator import generate_issue_clusters, generate_quests


def test_quest_generation_clusters_negative_issues() -> None:
    classified = [
        {
            "item_id": "blog-0001",
            "sentiment": "negative",
            "issue_type": "shipping",
            "evidence": "배송 지연",
            "confidence": 0.8,
        },
        {
            "item_id": "cafe-0002",
            "sentiment": "mixed",
            "issue_type": "shipping",
            "evidence": "2주 지연",
            "confidence": 0.7,
        },
        {
            "item_id": "shop-0003",
            "sentiment": "neutral",
            "issue_type": "unknown",
            "evidence": "상품 정보",
            "confidence": 0.3,
        },
    ]

    clusters = generate_issue_clusters(classified)
    quests = generate_quests(clusters)

    assert len(clusters) == 1
    assert clusters[0]["issue_type"] == "shipping"
    assert clusters[0]["count"] == 2
    assert quests[0]["owner_candidate"] == "logistics"
    assert quests[0]["priority"] == "medium"

