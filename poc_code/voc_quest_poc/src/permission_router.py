from __future__ import annotations

from typing import Any


def route_candidates(candidates: list[dict[str, Any]]) -> list[dict[str, Any]]:
    routed: list[dict[str, Any]] = []
    for item in candidates:
        source_type = item.get("source_type", "blog")
        source_url = item.get("source_url", "")

        if not source_url:
            permission_status = "customer_provided_needed"
            text_scope = "metadata_only"
            next_action = "use_customer_export"
        elif any(marker in source_url.lower() for marker in ["login", "auth", "paywall"]):
            permission_status = "auth_required"
            text_scope = "snippet_only"
            next_action = "request_permission"
        elif source_type == "shop":
            permission_status = "official_api"
            text_scope = "metadata_only"
            next_action = "analyze_snippet"
        else:
            permission_status = "snippet_only"
            text_scope = "snippet_only"
            next_action = "analyze_snippet"

        routed.append(
            {
                "item_id": item["item_id"],
                "source_type": source_type,
                "source_url": source_url,
                "title": item.get("title", ""),
                "snippet": item.get("snippet", ""),
                "collection_method": item.get("collection_method", "naver_search_api"),
                "permission_status": permission_status,
                "text_scope": text_scope,
                "next_action": next_action,
            }
        )
    return routed

