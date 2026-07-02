from __future__ import annotations

import argparse
import csv
import json
import subprocess
import sys
from datetime import datetime
from pathlib import Path
from typing import Any


PROJECT_ROOT = Path(__file__).resolve().parents[1]
DEFAULT_SEEDS_FILE = PROJECT_ROOT / "samples" / "evaluation_seeds.txt"


def main() -> int:
    parser = argparse.ArgumentParser(description="Run VOC Quest PoC for multiple seeds and create review files.")
    parser.add_argument("--seeds-file", type=Path, default=DEFAULT_SEEDS_FILE)
    parser.add_argument("--use-sample", action="store_true", help="Use sample Naver response for every seed.")
    parser.add_argument("--use-insane-search", action="store_true", help="Enrich public URLs with insane-search.")
    parser.add_argument("--insane-search-max-items", type=int, default=None)
    args = parser.parse_args()

    seeds = read_seeds(args.seeds_file)
    if not seeds:
        print(f"No seeds found in {args.seeds_file}", file=sys.stderr)
        return 1

    evaluation_dir = PROJECT_ROOT / "outputs" / "evaluations" / datetime.now().strftime("%Y%m%d_%H%M%S")
    evaluation_dir.mkdir(parents=True, exist_ok=True)

    rows: list[dict[str, Any]] = []
    raw_results: list[dict[str, Any]] = []

    for seed in seeds:
        command = [sys.executable, "-m", "src.run", "--seed", seed]
        if args.use_sample:
            command.append("--use-sample")
        if args.use_insane_search:
            command.append("--use-insane-search")
        if args.insane_search_max_items is not None:
            command.extend(["--insane-search-max-items", str(args.insane_search_max_items)])

        completed = subprocess.run(
            command,
            cwd=PROJECT_ROOT,
            text=True,
            capture_output=True,
            timeout=120,
        )
        result_path = PROJECT_ROOT / "outputs" / "latest" / "result.json"
        result = json.loads(result_path.read_text(encoding="utf-8"))
        raw_results.append({"seed": seed, "returncode": completed.returncode, "result": result})
        rows.append(summarize_result(seed, completed.returncode, result))

    write_json(evaluation_dir / "batch_results.json", raw_results)
    write_csv(evaluation_dir / "batch_summary.csv", rows)
    write_review_csv(evaluation_dir / "manual_review_sheet.csv", rows)

    print(f"Wrote {evaluation_dir}")
    print(f"Seeds: {len(seeds)}")
    print(f"Success: {sum(1 for row in rows if row['status'] == 'success')}")
    print(f"Failed: {sum(1 for row in rows if row['status'] == 'failed')}")
    return 0


def read_seeds(path: Path) -> list[str]:
    return [
        line.strip()
        for line in path.read_text(encoding="utf-8").splitlines()
        if line.strip() and not line.strip().startswith("#")
    ]


def summarize_result(seed: str, returncode: int, result: dict[str, Any]) -> dict[str, Any]:
    summary = result.get("summary", {})
    error = result.get("error", {})
    partial_result = result.get("partial_result", {})
    quests = result.get("quests", [])
    issue_clusters = result.get("issue_clusters", [])
    query_count = summary.get("query_count")
    if query_count is None:
        query_count = len(partial_result.get("queries", []))
    return {
        "seed": seed,
        "returncode": returncode,
        "status": result.get("status"),
        "error_code": error.get("code", ""),
        "query_count": query_count,
        "collected_count": summary.get("collected_count", 0),
        "analyzable_count": summary.get("analyzable_count", 0),
        "public_text_enriched_count": summary.get("public_text_enriched_count", 0),
        "insane_search_attempted_count": summary.get("insane_search_attempted_count", 0),
        "ad_suspected_count": summary.get("ad_suspected_count", 0),
        "duplicate_count": summary.get("duplicate_count", 0),
        "issue_cluster_count": summary.get("issue_cluster_count", 0),
        "quest_count": summary.get("quest_count", 0),
        "fallback_used": result.get("fallback_used", ""),
        "top_issue_types": "; ".join(cluster.get("issue_type", "") for cluster in issue_clusters[:5]),
        "quest_titles": "; ".join(quest.get("title", "") for quest in quests[:5]),
    }


def write_json(path: Path, payload: Any) -> None:
    path.write_text(json.dumps(payload, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")


def write_csv(path: Path, rows: list[dict[str, Any]]) -> None:
    if not rows:
        return
    with path.open("w", encoding="utf-8-sig", newline="") as f:
        writer = csv.DictWriter(f, fieldnames=list(rows[0].keys()))
        writer.writeheader()
        writer.writerows(rows)


def write_review_csv(path: Path, rows: list[dict[str, Any]]) -> None:
    review_rows = []
    for row in rows:
        review_row = dict(row)
        review_row.update(
            {
                "manual_related_items_0_to_collected": "",
                "manual_useful_quests_0_to_quest_count": "",
                "manual_pii_leak_found_y_n": "",
                "manual_ad_flag_reasonable_y_n": "",
                "manual_decision_pass_watch_fail": "",
                "manual_notes": "",
            }
        )
        review_rows.append(review_row)
    write_csv(path, review_rows)


if __name__ == "__main__":
    raise SystemExit(main())
