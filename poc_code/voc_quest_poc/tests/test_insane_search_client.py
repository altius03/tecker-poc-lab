from src.insane_search_client import (
    InsaneSearchClient,
    append_method,
    extract_visible_text,
    normalize_public_text,
    prepare_reader_url,
)


def test_append_method_adds_without_duplicates() -> None:
    assert append_method("naver_search_api", "insane_search") == "naver_search_api+insane_search"
    assert append_method("naver_search_api+insane_search", "insane_search") == "naver_search_api+insane_search"


def test_normalize_public_text_collapses_whitespace_and_limits() -> None:
    assert normalize_public_text("  공개\n\n후기\t텍스트  ", 20) == "공개 후기 텍스트"


def test_extract_visible_text_removes_script_and_tags() -> None:
    html = "<html><script>ignore()</script><body><h1>후기</h1><p>배송 지연</p></body></html>"
    assert extract_visible_text(html).strip() == "후기 배송 지연"


def test_prepare_reader_url_converts_naver_blog_to_mobile_postview() -> None:
    assert prepare_reader_url("https://blog.naver.com/yunautumn_/224221281499") == (
        "https://m.blog.naver.com/PostView.naver?blogId=yunautumn_&logNo=224221281499"
    )
    assert prepare_reader_url("https://example.com/post") == "https://example.com/post"


def test_enrich_items_marks_public_text_when_fetch_succeeds(monkeypatch) -> None:
    client = InsaneSearchClient()

    monkeypatch.setattr(type(client), "available", property(lambda self: True))
    monkeypatch.setattr(
        client,
        "fetch_url",
        lambda url: {
            "ok": True,
            "content": "SNS 공개 후기입니다. 배송 지연이 있었고 트러블도 언급됩니다.",
            "content_length": 36,
            "final_url": url,
            "verdict": "strong_ok",
            "summary": "test",
        },
    )

    items = [
        {
            "item_id": "blog-0001",
            "source_type": "blog",
            "source_url": "https://example.com/post",
            "collection_method": "naver_search_api",
            "text_scope": "snippet_only",
            "next_action": "analyze_snippet",
        },
        {
            "item_id": "shop-0002",
            "source_type": "shop",
            "source_url": "https://example.com/shop",
            "collection_method": "naver_search_api",
        },
    ]

    enriched = client.enrich_items(items, max_items=5)

    assert enriched[0]["text_scope"] == "public_page_text"
    assert enriched[0]["next_action"] == "analyze_public_text"
    assert enriched[0]["collection_method"] == "naver_search_api+insane_search"
    assert "배송 지연" in enriched[0]["public_text_excerpt"]
    assert enriched[1]["insane_search"]["attempted"] is False
