from typing import Any

from .config import DEFAULT_LIMITATIONS, POC_NAME
from .handoff_builder import build_handoff_cards
from .medicine_normalizer import normalize_medicines, public_medicine_candidates
from .mock_dur_checker import check_mock_dur
from .ocr_parser import parse_ocr_text
from .safety_phrase_guard import guard_dur_checks
from .schedule_builder import build_schedules


class PipelineError(Exception):
    def __init__(
        self,
        code: str,
        message: str,
        partial_result: dict[str, Any] | None = None,
    ) -> None:
        super().__init__(message)
        self.code = code
        self.partial_result = partial_result or {}


def process_ocr_text(
    ocr_text: str,
    input_meta: dict[str, Any] | None = None,
    initial_modules: list[str] | None = None,
) -> dict[str, Any]:
    modules_run = list(initial_modules or [])
    partial_result: dict[str, Any] = {}
    input_meta = input_meta or {"source": "ocr_text"}

    try:
        if not ocr_text or not ocr_text.strip():
            raise PipelineError("MISSING_INPUT", "OCR 텍스트가 비어 있습니다.")

        parsed = parse_ocr_text(ocr_text)
        modules_run.append("ocr_parser")
        partial_result["masked_text"] = parsed["masked_text"]
        partial_result["medicine_observation_count"] = len(parsed["medicine_observations"])

        if not parsed["medicine_observations"]:
            raise PipelineError(
                "PARSING_FAILED",
                "약명 후보를 추출하지 못했습니다.",
                partial_result,
            )

        medicines = normalize_medicines(parsed["medicine_observations"])
        modules_run.append("medicine_normalizer")

        dur_checks = check_mock_dur(medicines)
        modules_run.append("mock_dur_checker")

        guarded_dur_checks, safe_phrases = guard_dur_checks(dur_checks)
        modules_run.append("safety_phrase_guard")

        schedules = build_schedules(medicines)
        modules_run.append("schedule_builder")

        handoff_cards = build_handoff_cards(
            medicines,
            schedules,
            guarded_dur_checks,
            parsed["appointments"],
        )
        modules_run.append("handoff_builder")

        return build_success_result(
            input_meta=input_meta,
            modules_run=modules_run,
            masked_text=parsed["masked_text"],
            medicines=public_medicine_candidates(medicines),
            schedules=schedules,
            dur_checks=guarded_dur_checks,
            safe_phrases=safe_phrases,
            handoff_cards=handoff_cards,
        )

    except PipelineError as error:
        return build_failure_result(
            input_meta=input_meta,
            modules_run=modules_run,
            code=error.code,
            error_type=type(error).__name__,
            message=str(error),
            partial_result={**partial_result, **error.partial_result},
        )

    except Exception as error:
        return build_failure_result(
            input_meta=input_meta,
            modules_run=modules_run,
            code="UNEXPECTED_ERROR",
            error_type=type(error).__name__,
            message=str(error),
            partial_result=partial_result,
        )


def build_success_result(
    input_meta: dict[str, Any],
    modules_run: list[str],
    masked_text: str,
    medicines: list[dict[str, Any]],
    schedules: list[dict[str, Any]],
    dur_checks: list[dict[str, Any]],
    safe_phrases: list[dict[str, str]],
    handoff_cards: list[dict[str, Any]],
) -> dict[str, Any]:
    needs_confirmation_count = (
        sum(1 for medicine in medicines if medicine["needs_user_confirmation"])
        + sum(1 for schedule in schedules if schedule["needs_user_confirmation"])
        + sum(1 for check in dur_checks if check["status"] != "no_known_issue")
    )

    return {
        "poc_name": POC_NAME,
        "schema_version": "0.2.0",
        "status": "success",
        "input": input_meta,
        "modules_run": modules_run,
        "summary": {
            "medicine_candidate_count": len(medicines),
            "schedule_count": len(schedules),
            "dur_check_count": len(dur_checks),
            "needs_confirmation_count": needs_confirmation_count,
            "handoff_card_count": len(handoff_cards),
        },
        "masked_text": masked_text,
        "medicine_candidates": medicines,
        "schedules": schedules,
        "dur_checks": dur_checks,
        "safe_phrases": safe_phrases,
        "handoff_cards": handoff_cards,
        "risks_verified": [
            "개인정보 이름/전화번호/주민번호 형태 마스킹",
            "mock DUR 결과를 안전 문구로 변환",
            "보호자 확인용 인수인계 카드 JSON 생성",
        ],
        "limitations": DEFAULT_LIMITATIONS,
    }


def build_failure_result(
    input_meta: dict[str, Any],
    modules_run: list[str],
    code: str,
    error_type: str,
    message: str,
    partial_result: dict[str, Any],
) -> dict[str, Any]:
    return {
        "poc_name": POC_NAME,
        "schema_version": "0.2.0",
        "status": "failed",
        "input": input_meta,
        "modules_run": modules_run,
        "error": {
            "code": code,
            "type": error_type,
            "message": message,
        },
        "partial_result": partial_result,
        "limitations": DEFAULT_LIMITATIONS,
    }

