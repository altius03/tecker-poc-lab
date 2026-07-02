from src.voc_classifier import classify_items


def test_classifier_detects_issue_types_and_sarcasm() -> None:
    items = [
        {
            "item_id": "cafe-0001",
            "title": "진짜 빠르네요 ㅋㅋ",
            "snippet": "배송 지연 때문에 2주 만에 받았습니다.",
            "ad_suspected": False,
        },
        {
            "item_id": "blog-0002",
            "title": "사용 후 따가움",
            "snippet": "자극이 있고 트러블이 올라왔습니다.",
            "ad_suspected": False,
        },
        {
            "item_id": "blog-0003",
            "title": "환불 문의",
            "snippet": "가격이 비싸다 싶고 교환 정책도 불편합니다.",
            "ad_suspected": False,
        },
    ]

    classified = classify_items(items, product_seed="브랜드A 블루 수딩 앰플")

    by_id = {item["item_id"]: item for item in classified}
    assert by_id["cafe-0001"]["issue_type"] == "shipping"
    assert by_id["cafe-0001"]["sarcasm_suspected"] is True
    assert by_id["blog-0002"]["issue_type"] == "skin_irritation"
    assert by_id["blog-0003"]["issue_type"] == "price_refund"

