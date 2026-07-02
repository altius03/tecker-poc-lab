from typing import Any


def build_schedules(medicines: list[dict[str, Any]]) -> list[dict[str, Any]]:
    schedules: list[dict[str, Any]] = []

    for index, medicine in enumerate(medicines, start=1):
        instruction = medicine.get("_instruction", {})
        frequency = instruction.get("frequency", "")
        timing = instruction.get("timing", "")
        duration = instruction.get("duration", "")

        schedules.append(
            {
                "schedule_id": f"schedule-{index:03d}",
                "medicine_id": medicine["medicine_id"],
                "frequency": frequency,
                "timing": timing,
                "duration": duration,
                "start_date": None,
                "needs_user_confirmation": bool(
                    medicine.get("needs_user_confirmation")
                    or not frequency
                    or not timing
                    or not duration
                ),
            }
        )

    return schedules


def build_appointment_actions(appointments: list[dict[str, str]]) -> list[str]:
    actions: list[str] = []
    for appointment in appointments:
        date = appointment.get("date", "")
        time = appointment.get("time", "")
        keyword = appointment.get("keyword") or "일정"
        when = " ".join(part for part in (date, time) if part)
        if when:
            actions.append(f"{when} {keyword} 일정 확인")
        else:
            actions.append(f"{appointment.get('raw_text', '')} 일정 확인")
    return actions

