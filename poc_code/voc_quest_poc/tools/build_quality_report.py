from __future__ import annotations

import argparse
import csv
import json
import re
from pathlib import Path
from typing import Any


PROJECT_ROOT = Path(__file__).resolve().parents[1]
EVALUATIONS_DIR = PROJECT_ROOT / "outputs" / "evaluations"


def main() -> int:
    parser = argparse.ArgumentParser(description="Build a quality report from a VOC Quest batch_results.json file.")
    parser.add_argument("--evaluation-dir", type=Path, default=None)
    args = parser.parse_args()

    evaluation_dir = args.evaluation_dir or find_latest_evaluation_dir()
    batch_path = evaluation_dir / "batch_results.json"
    if not batch_path.exists():
        raise SystemExit(f"Missing {batch_path}")

    batch = json.loads(batch_path.read_text(encoding="utf-8"))
    rows = [score_run(run) for run in batch]
    write_csv(evaluation_dir / "quality_summary.csv", rows)
    write_markdown(evaluation_dir / "quality_report.md", rows)
    print(f"Wrote {evaluation_dir / 'quality_summary.csv'}")
    print(f"Wrote {evaluation_dir / 'quality_report.md'}")
    return 0


def find_latest_evaluation_dir() -> Path:
    dirs = [path for path in EVALUATIONS_DIR.iterdir() if path.is_dir()]
    if not dirs:
        raise SystemExit(f"No evaluation directories found under {EVALUATIONS_DIR}")
    return sorted(dirs, key=lambda path: path.name)[-1]


def score_run(run: dict[str, Any]) -> dict[str, Any]:
    seed = run["seed"]
    result = run["result"]
    summary = result.get("summary", {})
    collected = result.get("collected_items", [])
    quests = result.get("quests", [])
    classified = result.get("classified_items", [])
    seed_tokens = tokenize_seed(seed)
    brand_token = seed_tokens[0] if seed_tokens else ""
    product_tokens = seed_tokens[1:] if len(seed_tokens) > 1 else seed_tokens

    brand_hits = 0
    product_2plus_hits = 0
    any_seed_hits = 0
    source_counts: dict[str, int] = {}
    for item in collected:
        text = f"{item.get('title', '')} {item.get('snippet', '')}".lower()
        source_type = item.get("source_type", "unknown")
        source_counts[source_type] = source_counts.get(source_type, 0) + 1
        if brand_token and brand_token.lower() in text:
            brand_hits += 1
        product_hit_count = sum(1 for token in product_tokens if token.lower() in text)
        if product_hit_count >= min(2, len(product_tokens)):
            product_2plus_hits += 1
        if any(token.lower() in text for token in seed_tokens):
            any_seed_hits += 1

    collected_count = len(collected)
    duplicate_count = int(summary.get("duplicate_count", 0))
    ad_count = int(summary.get("ad_suspected_count", 0))
    shop_evidence_count = count_shop_evidence(quests)
    unknown_count = sum(1 for item in classified if item.get("issue_type") == "unknown")
    issue_count = max(1, len(classified))

    flags = build_flags(
        seed=seed,
        status=result.get("status"),
        collected_count=collected_count,
        quest_count=int(summary.get("quest_count", 0)),
        duplicate_rate=safe_rate(duplicate_count, collected_count),
        ad_rate=safe_rate(ad_count, collected_count),
        brand_hit_rate=safe_rate(brand_hits, collected_count),
        product_2plus_hit_rate=safe_rate(product_2plus_hits, collected_count),
        shop_evidence_count=shop_evidence_count,
    )
    verdict = decide_verdict(flags)

    return {
        "seed": seed,
        "status": result.get("status"),
        "collected_count": collected_count,
        "quest_count": summary.get("quest_count", 0),
        "public_text_enriched_count": summary.get("public_text_enriched_count", 0),
        "insane_search_attempted_count": summary.get("insane_search_attempted_count", 0),
        "duplicate_rate": round(safe_rate(duplicate_count, collected_count), 3),
        "ad_rate": round(safe_rate(ad_count, collected_count), 3),
        "brand_hit_rate": round(safe_rate(brand_hits, collected_count), 3),
        "product_2plus_hit_rate": round(safe_rate(product_2plus_hits, collected_count), 3),
        "any_seed_hit_rate": round(safe_rate(any_seed_hits, collected_count), 3),
        "unknown_issue_rate": round(safe_rate(unknown_count, issue_count), 3),
        "shop_evidence_count": shop_evidence_count,
        "source_blog": source_counts.get("blog", 0),
        "source_cafe": source_counts.get("cafe", 0),
        "source_web": source_counts.get("web", 0),
        "source_shop": source_counts.get("shop", 0),
        "verdict": verdict,
        "flags": "; ".join(flags),
    }


def tokenize_seed(seed: str) -> list[str]:
    return [token for token in re.split(r"\s+", seed.strip()) if len(token) >= 2]


def count_shop_evidence(quests: list[dict[str, Any]]) -> int:
    count = 0
    for quest in quests:
        count += sum(1 for item_id in quest.get("evidence_item_ids", []) if str(item_id).startswith("shop-"))
    return count


def build_flags(
    *,
    seed: str,
    status: str | None,
    collected_count: int,
    quest_count: int,
    duplicate_rate: float,
    ad_rate: float,
    brand_hit_rate: float,
    product_2plus_hit_rate: float,
    shop_evidence_count: int,
) -> list[str]:
    flags: list[str] = []
    if status != "success":
        flags.append("api_or_pipeline_failed")
    if re.search(r"브랜드[A-Z]$", seed.split()[0]):
        flags.append("placeholder_brand_seed")
    if collected_count >= 80:
        flags.append("collection_cap_hit")
    if duplicate_rate >= 0.30:
        flags.append("high_duplicate_rate")
    if ad_rate >= 0.10:
        flags.append("high_ad_rate")
    if brand_hit_rate < 0.20:
        flags.append("low_brand_match")
    if product_2plus_hit_rate < 0.50:
        flags.append("low_product_match")
    if shop_evidence_count > 0:
        flags.append("shop_used_as_voc_evidence")
    if quest_count < 2:
        flags.append("low_quest_count")
    return flags


def decide_verdict(flags: list[str]) -> str:
    if "api_or_pipeline_failed" in flags:
        return "fail_api"
    if "placeholder_brand_seed" in flags or "low_brand_match" in flags or "low_product_match" in flags:
        return "needs_real_seed_quality_check"
    if "shop_used_as_voc_evidence" in flags or "high_duplicate_rate" in flags:
        return "watch_needs_tuning"
    return "pass_candidate"


def safe_rate(numerator: int, denominator: int) -> float:
    if denominator <= 0:
        return 0.0
    return numerator / denominator


def write_csv(path: Path, rows: list[dict[str, Any]]) -> None:
    if not rows:
        return
    with path.open("w", encoding="utf-8-sig", newline="") as f:
        writer = csv.DictWriter(f, fieldnames=list(rows[0].keys()))
        writer.writeheader()
        writer.writerows(rows)


def write_markdown(path: Path, rows: list[dict[str, Any]]) -> None:
    verdict_counts: dict[str, int] = {}
    for row in rows:
        verdict = str(row["verdict"])
        verdict_counts[verdict] = verdict_counts.get(verdict, 0) + 1

    lines = [
        "# VOC Quest PoC Quality Report",
        "",
        "## Verdict Summary",
        "",
    ]
    for verdict, count in sorted(verdict_counts.items()):
        lines.append(f"- `{verdict}`: {count}")

    lines.extend(
        [
            "",
            "## Seed Metrics",
            "",
            "| seed | verdict | collected | public_text | quests | duplicate_rate | ad_rate | brand_hit_rate | product_2plus_hit_rate | shop_evidence_count | flags |",
            "| --- | --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | --- |",
        ]
    )
    for row in rows:
        lines.append(
            "| {seed} | `{verdict}` | {collected_count} | {public_text_enriched_count} | {quest_count} | {duplicate_rate} | {ad_rate} | {brand_hit_rate} | {product_2plus_hit_rate} | {shop_evidence_count} | {flags} |".format(
                **row
            )
        )

    lines.extend(
        [
            "",
            "## Interpretation",
            "",
            "- `collection_cap_hit` means the PoC reached the configured max of 80 candidates, so the API path can collect enough volume.",
            "- `placeholder_brand_seed` or `low_brand_match` means this run is not enough to judge real product relevance.",
            "- `high_duplicate_rate` means query expansion is overlapping and deduped items should be excluded before clustering.",
            "- `shop_used_as_voc_evidence` means shopping metadata is being used as VOC evidence and should be downweighted or excluded from quest evidence.",
        ]
    )
    path.write_text("\n".join(lines) + "\n", encoding="utf-8")


if __name__ == "__main__":
    raise SystemExit(main())
