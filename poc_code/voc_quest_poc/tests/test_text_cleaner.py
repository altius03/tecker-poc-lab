from src.text_cleaner import clean_items


def test_clean_items_masks_pii_flags_ads_and_counts_duplicates() -> None:
    items = [
        {
            "item_id": "blog-0001",
            "title": "배송 지연",
            "snippet": "전화 010-1234-5678, 주문번호 AB-2026-0702 남겼습니다.",
        },
        {
            "item_id": "blog-0002",
            "title": "배송 지연",
            "snippet": "전화 010-1234-5678, 주문번호 AB-2026-0702 남겼습니다.",
        },
        {
            "item_id": "blog-0003",
            "title": "체험단 리뷰",
            "snippet": "제품을 제공받아 작성한 광고 후기입니다.",
            "public_text_excerpt": "문의는 test@example.com 으로 주세요.",
        },
    ]

    cleaned, stats = clean_items(items)

    assert "[PHONE_MASKED]" in cleaned[0]["snippet"]
    assert "[ORDER_MASKED]" in cleaned[0]["snippet"]
    assert cleaned[0]["pii_masked"] is True
    assert cleaned[2]["ad_suspected"] is True
    assert "[EMAIL_MASKED]" in cleaned[2]["public_text_excerpt"]
    assert stats["pii_masked_count"] == 3
    assert stats["ad_suspected_count"] == 1
    assert stats["duplicate_count"] == 1
