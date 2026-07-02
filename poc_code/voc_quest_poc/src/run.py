from __future__ import annotations

from pathlib import Path
from typing import Any

import typer
from rich.console import Console

from .config import load_config
from .insane_search_client import InsaneSearchClient, InsaneSearchUnavailable
from .naver_search_client import ApiRequestError, NaverSearchClient
from .permission_router import route_candidates
from .query_expander import expand_queries, normalize_seed
from .quest_generator import generate_issue_clusters, generate_quests
from .result_writer import ResultWriter, build_failure_result
from .text_cleaner import clean_items
from .voc_classifier import classify_items


app = typer.Typer(add_completion=False, no_args_is_help=False)
console = Console()

COMMON_LIMITATIONS = [
    "네이버 검색 API는 원문 본문 전체가 아니라 제목/링크/요약/메타데이터 중심 결과를 제공한다.",
    "비공개, 로그인 필요, 페이월 페이지는 우회하지 않는다.",
    "PoC 분류는 rule-based이며 맥락 이해와 반어 판정은 제한적이다.",
]


@app.command()
def main(
    seed: str | None = typer.Option(None, "--seed", help="제품/브랜드 seed"),
    use_sample: bool = typer.Option(False, "--use-sample", help="명시적으로 샘플 응답을 사용"),
    use_insane_search: bool = typer.Option(False, "--use-insane-search", help="공개 URL 원문 읽기를 insane-search로 시도"),
    insane_search_max_items: int | None = typer.Option(None, "--insane-search-max-items", help="insane-search 원문 읽기 최대 후보 수"),
) -> None:
    writer = ResultWriter()
    modules_run: list[str] = []
    partial_result: dict[str, Any] = {}
    input_payload: dict[str, Any] = {}

    try:
        config = load_config()
        resolved_seed = resolve_seed(seed, config.samples_dir / "default_seed.txt")
        input_payload = {"seed": resolved_seed} if resolved_seed else {}

        if not resolved_seed:
            result = build_failure_result(
                code="MISSING_INPUT",
                error_type="InputError",
                message="--seed가 없고 samples/default_seed.txt에서도 seed를 찾지 못했습니다.",
                input_payload=input_payload,
                modules_run=modules_run,
                limitations=COMMON_LIMITATIONS,
            )
            paths = writer.write(result)
            console.print(f"[red]failed[/red] MISSING_INPUT -> {paths['latest']}")
            raise typer.Exit(code=1)

        queries = expand_queries(resolved_seed, max_queries=config.query_limit)
        modules_run.append("query_expander")
        partial_result["queries"] = queries

        if not use_sample and not config.has_naver_credentials:
            result = build_failure_result(
                code="MISSING_API_KEY",
                error_type="ConfigError",
                message="NAVER_CLIENT_ID 또는 NAVER_CLIENT_SECRET이 없습니다. 실제 API 실행에는 .env 설정이 필요합니다.",
                input_payload=input_payload,
                modules_run=modules_run,
                partial_result=partial_result,
                limitations=COMMON_LIMITATIONS,
            )
            paths = writer.write(result)
            console.print(f"[red]failed[/red] MISSING_API_KEY -> {paths['latest']}")
            raise typer.Exit(code=1)

        client = NaverSearchClient(
            client_id=config.naver_client_id,
            client_secret=config.naver_client_secret,
            timeout_seconds=config.timeout_seconds,
        )

        if use_sample:
            candidates = client.collect_from_sample(
                config.samples_dir / "sample_naver_response.json",
                max_items=config.max_collected_items,
            )
            fallback_used = True
            fallback_reason = "explicit_use_sample"
        else:
            candidates = client.collect(
                queries=queries,
                display_per_query=config.display_per_query,
                max_items=config.max_collected_items,
            )
            fallback_used = False
            fallback_reason = None
        modules_run.append("naver_search_client")
        partial_result["collected_candidate_count"] = len(candidates)

        routed_items = route_candidates(candidates)
        modules_run.append("permission_router")

        if use_insane_search:
            insane_client = InsaneSearchClient(
                timeout_seconds=config.insane_search_timeout_seconds,
                content_limit=config.insane_search_content_limit,
            )
            routed_items = insane_client.enrich_items(
                routed_items,
                max_items=insane_search_max_items or config.insane_search_max_items,
            )
            modules_run.append("insane_search_client")

        cleaned_items, cleaning_stats = clean_items(routed_items)
        modules_run.append("text_cleaner")

        classified_items = classify_items(cleaned_items, product_seed=resolved_seed)
        modules_run.append("voc_classifier")

        issue_clusters = generate_issue_clusters(classified_items)
        quests = generate_quests(issue_clusters)
        modules_run.append("quest_generator")

        result = {
            "poc_name": "voc_quest",
            "status": "success",
            "input": {"seed": resolved_seed},
            "modules_run": modules_run,
            "summary": {
                "query_count": len(queries),
                "collected_count": len(cleaned_items),
                "analyzable_count": sum(
                    1 for item in cleaned_items if item["next_action"] in {"analyze_snippet", "analyze_public_text"}
                ),
                "public_text_enriched_count": sum(
                    1 for item in cleaned_items if item.get("text_scope") == "public_page_text"
                ),
                "insane_search_attempted_count": sum(
                    1 for item in cleaned_items if item.get("insane_search", {}).get("attempted") is True
                ),
                "permission_needed_count": sum(
                    1
                    for item in cleaned_items
                    if item["next_action"] in {"request_permission", "use_customer_export"}
                ),
                "ad_suspected_count": cleaning_stats["ad_suspected_count"],
                "duplicate_count": cleaning_stats["duplicate_count"],
                "issue_cluster_count": len(issue_clusters),
                "quest_count": len(quests),
            },
            "queries": queries,
            "collected_items": cleaned_items,
            "classified_items": classified_items,
            "issue_clusters": issue_clusters,
            "quests": quests,
            "risks_verified": [
                "API 키는 .env에서만 읽고 .env.example에는 빈 값만 둔다.",
                "검색 결과 링크의 본문을 크롤링하지 않고 네이버 API 요약 범위에서만 분석한다.",
                "insane-search 사용 시에도 공개 URL만 읽고 로그인/페이월 우회는 하지 않는다.",
                "개인정보 패턴은 결과 JSON 저장 전 마스킹한다.",
                "광고/협찬 후보는 키워드 기반으로 플래그 처리한다.",
            ],
            "limitations": COMMON_LIMITATIONS,
            "fallback_used": fallback_used,
            "fallback_reason": fallback_reason,
        }
        paths = writer.write(result)
        console.print(f"[green]success[/green] result -> {paths['latest']}")
    except ApiRequestError as exc:
        result = build_failure_result(
            code="API_REQUEST_FAILED",
            error_type=type(exc).__name__,
            message=str(exc),
            input_payload=input_payload,
            modules_run=modules_run,
            partial_result=partial_result,
            limitations=COMMON_LIMITATIONS,
        )
        paths = writer.write(result)
        console.print(f"[red]failed[/red] API_REQUEST_FAILED -> {paths['latest']}")
        raise typer.Exit(code=1)
    except InsaneSearchUnavailable as exc:
        result = build_failure_result(
            code="UNEXPECTED_ERROR",
            error_type=type(exc).__name__,
            message=str(exc),
            input_payload=input_payload,
            modules_run=modules_run,
            partial_result=partial_result,
            limitations=COMMON_LIMITATIONS,
        )
        paths = writer.write(result)
        console.print(f"[red]failed[/red] INSANE_SEARCH_UNAVAILABLE -> {paths['latest']}")
        raise typer.Exit(code=1)
    except typer.Exit:
        raise
    except Exception as exc:
        result = build_failure_result(
            code="UNEXPECTED_ERROR",
            error_type=type(exc).__name__,
            message=str(exc),
            input_payload=input_payload,
            modules_run=modules_run,
            partial_result=partial_result,
            limitations=COMMON_LIMITATIONS,
        )
        paths = writer.write(result)
        console.print(f"[red]failed[/red] UNEXPECTED_ERROR -> {paths['latest']}")
        raise typer.Exit(code=1)


def resolve_seed(seed: str | None, default_seed_path: Path) -> str:
    normalized = normalize_seed(seed)
    if normalized:
        return normalized
    if default_seed_path.exists():
        return normalize_seed(default_seed_path.read_text(encoding="utf-8"))
    return ""


if __name__ == "__main__":
    app()
