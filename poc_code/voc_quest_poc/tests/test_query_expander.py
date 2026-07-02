from src.query_expander import expand_queries, normalize_seed


def test_expand_queries_generates_enough_deduped_queries() -> None:
    queries = expand_queries(" 브랜드A   블루 수딩 앰플 ", max_queries=20)

    assert len(queries) >= 15
    assert len(queries) == len(set(queries))
    assert queries[0] == "브랜드A 블루 수딩 앰플"
    assert "브랜드A 블루 수딩 앰플 배송 지연" in queries
    assert "브랜드A 블루 수딩 앰플 트러블" in queries
    assert "브랜드A 블루 수딩 앰플 맘카페" in queries
    assert "브랜드A 블루 수딩 앰플 파우더룸" in queries


def test_normalize_seed_handles_empty_input() -> None:
    assert normalize_seed(None) == ""
    assert normalize_seed("   ") == ""
