import re
from typing import Any

DOSE_RE = re.compile(
    r"(?<!\d)(\d+(?:\.\d+)?(?:/\d+(?:\.\d+)?)?\s?(?:mg|ml|g|mcg|㎎|정|캡슐))(?![A-Za-z0-9])",
    re.IGNORECASE,
)
FREQUENCY_RE = re.compile(r"(1일\s*\d+\s*회|하루\s*\d+\s*(?:번|회))")
DURATION_RE = re.compile(r"(\d+\s*(?:일|주))")
DATE_RE = re.compile(r"(\d{4}[-./]\d{1,2}[-./]\d{1,2})")
TIME_RE = re.compile(r"((?:오전|오후)?\s*\d{1,2}:\d{2})")
NAME_FIELD_RE = re.compile(r"((?:환자명|성명|이름)\s*[:：]\s*)([^\s,;]+)")
PHONE_RE = re.compile(r"(?<!\d)(?:01[016789]|0[2-6][0-9])[-.\s]?\d{3,4}[-.\s]?\d{4}(?!\d)")
RRN_RE = re.compile(r"(?<!\d)\d{6}[-\s]?[1-4]\d{6}(?!\d)")

MEDICINE_MARKERS = ("정", "캡슐", "mg", "ml", "정제", "캡슐제")
APPOINTMENT_KEYWORDS = ("진료", "예약", "방문")
TIMING_TERMS = ("취침 전", "취침전", "아침", "점심", "저녁", "식전", "식후")


def mask_personal_info(text: str) -> str:
    masked = NAME_FIELD_RE.sub(r"\1***", text)
    masked = RRN_RE.sub("******-*******", masked)
    masked = PHONE_RE.sub("***-****-****", masked)
    return masked


def parse_ocr_text(text: str) -> dict[str, Any]:
    if not text or not text.strip():
        raise ValueError("OCR text is empty.")

    # TODO: replace with LLM parser/summarizer for noisy OCR layouts after PoC validation.
    masked_text = mask_personal_info(text)
    numbered_lines = [
        (line_no, line.strip())
        for line_no, line in enumerate(text.splitlines(), start=1)
        if line.strip()
    ]
    medicine_positions = [
        pos for pos, (_, line) in enumerate(numbered_lines) if _is_medicine_line(line)
    ]

    observations: list[dict[str, Any]] = []
    for pos in medicine_positions:
        line_no, line = numbered_lines[pos]
        instruction_parts = [line]

        for next_pos in range(pos + 1, len(numbered_lines)):
            _, next_line = numbered_lines[next_pos]
            if _is_medicine_line(next_line) or _is_appointment_line(next_line):
                break
            instruction_parts.append(next_line)

        instruction_text = " ".join(instruction_parts)
        raw_name, dose = _extract_name_and_dose(line)
        instruction = _extract_instruction(instruction_text)
        observations.append(
            {
                "raw_name": raw_name,
                "dose": dose,
                "line_no": line_no,
                "instruction": instruction,
                "raw_instruction": instruction_text,
            }
        )

    appointments = [
        _extract_appointment(line_no, line)
        for line_no, line in numbered_lines
        if _is_appointment_line(line)
    ]
    appointments = [appointment for appointment in appointments if appointment]

    return {
        "masked_text": masked_text,
        "medicine_observations": observations,
        "appointments": appointments,
    }


def _is_medicine_line(line: str) -> bool:
    lowered = line.lower()
    return any(marker in lowered for marker in MEDICINE_MARKERS) and not _is_appointment_line(line)


def _is_appointment_line(line: str) -> bool:
    return any(keyword in line for keyword in APPOINTMENT_KEYWORDS)


def _extract_name_and_dose(line: str) -> tuple[str, str]:
    dose_match = DOSE_RE.search(line)
    if dose_match:
        dose = dose_match.group(1).replace(" ", "")
        name_part = line[: dose_match.start()]
    else:
        dose = ""
        name_part = FREQUENCY_RE.split(line, maxsplit=1)[0]

    name_part = re.sub(r"^(?:약명|처방약)\s*[:：]\s*", "", name_part).strip(" -:：")
    if not name_part:
        name_part = line.strip()
    return name_part, dose


def _extract_instruction(text: str) -> dict[str, str]:
    frequency_match = FREQUENCY_RE.search(text)
    duration_matches = DURATION_RE.findall(text)
    timings = [term for term in TIMING_TERMS if term in text]

    return {
        "frequency": _normalize_space(frequency_match.group(1)) if frequency_match else "",
        "timing": " ".join(timings),
        "duration": duration_matches[-1].replace(" ", "") if duration_matches else "",
    }


def _extract_appointment(line_no: int, line: str) -> dict[str, str] | None:
    date_match = DATE_RE.search(line)
    time_match = TIME_RE.search(line)
    if not date_match and not time_match:
        return None

    keyword = next((item for item in APPOINTMENT_KEYWORDS if item in line), "")
    return {
        "line_no": str(line_no),
        "raw_text": line,
        "keyword": keyword,
        "date": date_match.group(1) if date_match else "",
        "time": _normalize_space(time_match.group(1)) if time_match else "",
    }


def _normalize_space(value: str) -> str:
    return re.sub(r"\s+", " ", value).strip()
