import argparse
import sys
from pathlib import Path

from .config import DEFAULT_SAMPLE_PATH
from .pipeline import PipelineError, build_failure_result, process_ocr_text
from .result_writer import write_result


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="Be:Careful OCR-to-handoff-card PoC")
    parser.add_argument("--ocr-file", help="Path to a dummy OCR text file.")
    parser.add_argument("--ocr-text", help="Dummy OCR text. Takes priority over --ocr-file.")
    args = parser.parse_args(argv)

    try:
        ocr_text, input_meta = _load_input(args)
        result = process_ocr_text(ocr_text, input_meta=input_meta, initial_modules=["input_loader"])
        paths = write_result(result)
        _print_result(paths, result["status"])
        return 0 if result["status"] == "success" else 1

    except PipelineError as error:
        result = build_failure_result(
            input_meta={},
            modules_run=[],
            code=error.code,
            error_type=type(error).__name__,
            message=str(error),
            partial_result=error.partial_result,
        )
        paths = write_result(result)
        _print_result(paths, result["status"])
        return 1

    except Exception as error:
        result = build_failure_result(
            input_meta={},
            modules_run=[],
            code="UNEXPECTED_ERROR",
            error_type=type(error).__name__,
            message=str(error),
            partial_result={},
        )
        paths = write_result(result)
        _print_result(paths, result["status"])
        return 1


def _load_input(args: argparse.Namespace) -> tuple[str, dict[str, Any]]:
    if args.ocr_text is not None:
        text = args.ocr_text.strip()
        if not text:
            raise PipelineError("MISSING_INPUT", "--ocr-text 값이 비어 있습니다.")
        return text, {"source": "ocr_text"}

    if args.ocr_file:
        requested_path = Path(args.ocr_file)
        path = requested_path if requested_path.is_absolute() else Path.cwd() / requested_path
        if not path.exists():
            raise PipelineError(
                "MISSING_INPUT",
                f"OCR 파일을 찾을 수 없습니다: {path}",
                {"requested_path": str(path)},
            )
        return path.read_text(encoding="utf-8"), {
            "source": "ocr_file",
            "path": str(path),
        }

    if DEFAULT_SAMPLE_PATH.exists():
        return DEFAULT_SAMPLE_PATH.read_text(encoding="utf-8"), {
            "source": "default_sample",
            "path": str(DEFAULT_SAMPLE_PATH),
        }

    raise PipelineError(
        "MISSING_INPUT",
        "입력값이 없고 samples/default_rx.txt 파일도 없습니다.",
        {"default_sample_path": str(DEFAULT_SAMPLE_PATH)},
    )

def _print_result(paths: dict[str, Path], status: str) -> None:
    print(f"status={status}")
    print(f"latest={paths['latest_path']}")
    print(f"run={paths['run_path']}")


if __name__ == "__main__":
    sys.exit(main())
