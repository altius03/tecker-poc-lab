from typing import Any

from .schedule_builder import build_appointment_actions


def build_handoff_cards(
    medicines: list[dict[str, Any]],
    schedules: list[dict[str, Any]],
    dur_checks: list[dict[str, Any]],
    appointments: list[dict[str, str]],
) -> list[dict[str, Any]]:
    needs_confirmation = _build_needs_confirmation(medicines, schedules, dur_checks)
    questions = _build_questions(medicines, dur_checks)
    next_actions = [
        "원본 약봉투와 약명/용량/복용 일정 후보를 대조하세요.",
        "의료진 확인 전 임의로 복용을 중단하지 마세요.",
    ]
    next_actions.extend(build_appointment_actions(appointments))

    needs_check_count = sum(1 for check in dur_checks if check["status"] != "no_known_issue")
    summary = (
        f"OCR 텍스트에서 약명 후보 {len(medicines)}개와 복약 일정 {len(schedules)}개를 추출했습니다. "
        f"mock DUR 확인 필요 항목은 {needs_check_count}개입니다."
    )

    return [
        {
            "card_id": "handoff-001",
            "title": "보호자 인수인계 카드",
            "summary": summary,
            "needs_confirmation": needs_confirmation,
            "questions_for_professional": questions,
            "next_actions": next_actions,
        }
    ]


def _build_needs_confirmation(
    medicines: list[dict[str, Any]],
    schedules: list[dict[str, Any]],
    dur_checks: list[dict[str, Any]],
) -> list[str]:
    items = [
        f"{medicine['normalized_name']} {medicine.get('dose', '')}".strip() + " 약명/용량 원문 대조"
        for medicine in medicines
    ]

    for schedule in schedules:
        if schedule["needs_user_confirmation"]:
            items.append(f"{schedule['medicine_id']} 복용 횟수/시간/기간 확인")

    for check in dur_checks:
        if check["status"] != "no_known_issue":
            items.append(check["safe_phrase"])

    return _dedupe(items)


def _build_questions(medicines: list[dict[str, Any]], dur_checks: list[dict[str, Any]]) -> list[str]:
    medicine_names = ", ".join(medicine["normalized_name"] for medicine in medicines)
    questions = [
        f"{medicine_names} 후보가 처방전/약봉투 원문과 일치하나요?",
        "복용 횟수, 복용 시간, 복용 기간이 처방 의도와 일치하나요?",
    ]

    if any(check["status"] != "no_known_issue" for check in dur_checks):
        questions.append("함께 복용 시 추가 확인이 필요한 항목이 있나요?")

    return questions


def _dedupe(values: list[str]) -> list[str]:
    seen: set[str] = set()
    result: list[str] = []
    for value in values:
        if value and value not in seen:
            seen.add(value)
            result.append(value)
    return result

