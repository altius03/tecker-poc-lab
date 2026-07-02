from typing import Any

KNOWN_MEDICINES = {
    "아모잘탄정": "아모잘탄정",
    "리피토정": "리피토정",
    "타이레놀정": "타이레놀정",
}


def normalize_medicines(observations: list[dict[str, Any]]) -> list[dict[str, Any]]:
    normalized: list[dict[str, Any]] = []

    for index, observation in enumerate(observations, start=1):
        raw_name = observation["raw_name"]
        normalized_name, confidence = _normalize_name(raw_name, bool(observation.get("dose")))
        normalized.append(
            {
                "medicine_id": f"med-{index:03d}",
                "raw_name": raw_name,
                "normalized_name": normalized_name,
                "dose": observation.get("dose", ""),
                "line_no": observation.get("line_no", 0),
                "confidence": confidence,
                "needs_user_confirmation": True,
                "_instruction": observation.get("instruction", {}),
                "_raw_instruction": observation.get("raw_instruction", ""),
            }
        )

    return normalized


def public_medicine_candidates(medicines: list[dict[str, Any]]) -> list[dict[str, Any]]:
    public_keys = [
        "medicine_id",
        "raw_name",
        "normalized_name",
        "dose",
        "line_no",
        "confidence",
        "needs_user_confirmation",
    ]
    return [{key: medicine[key] for key in public_keys} for medicine in medicines]


def _normalize_name(raw_name: str, has_dose: bool) -> tuple[str, float]:
    compact = "".join(raw_name.split()).strip(".,;:：")

    for known_raw, normalized_name in KNOWN_MEDICINES.items():
        if known_raw in compact:
            return normalized_name, 0.92 if has_dose else 0.86

    for suffix in ("캡슐제", "정제", "캡슐", "정"):
        if suffix in compact:
            candidate = compact[: compact.find(suffix) + len(suffix)]
            return candidate, 0.72 if has_dose else 0.64

    return compact or raw_name, 0.55
