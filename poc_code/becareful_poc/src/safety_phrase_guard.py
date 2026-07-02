from typing import Any

RISK_PHRASE_MAP = {
    "이 약은 같이 먹으면 안 됩니다": "함께 복용 시 확인이 필요한 항목이 있습니다. 의사 또는 약사에게 확인하세요.",
    "복용하지 마세요": "의료진 확인 전 임의로 복용을 중단하지 마세요.",
    "위험합니다": "확인 필요",
    "이 영양제를 추천합니다": "관심 케어 카테고리에 맞는 상품입니다. 복용 중인 약과의 관계는 전문가에게 확인하세요.",
}


def guard_dur_checks(dur_checks: list[dict[str, Any]]) -> tuple[list[dict[str, Any]], list[dict[str, str]]]:
    guarded_checks: list[dict[str, Any]] = []
    safe_phrases: list[dict[str, str]] = []

    for check in dur_checks:
        guarded = dict(check)
        safe_phrase, replacements = to_safe_phrase(check["message"])
        guarded["message"] = safe_phrase
        guarded["safe_phrase"] = safe_phrase
        guarded_checks.append(guarded)
        safe_phrases.extend(replacements)

    return guarded_checks, safe_phrases


def to_safe_phrase(message: str) -> tuple[str, list[dict[str, str]]]:
    safe_message = message
    replacements: list[dict[str, str]] = []

    for risky_phrase, safe_phrase in RISK_PHRASE_MAP.items():
        if risky_phrase in safe_message:
            safe_message = safe_message.replace(risky_phrase, safe_phrase)
            replacements.append(
                {
                    "rewrite_reason": "risky_medical_phrase_rewritten",
                    "safe_phrase": safe_phrase,
                }
            )

    return safe_message, replacements
