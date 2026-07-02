from pathlib import Path

POC_NAME = "becareful"
BASE_DIR = Path(__file__).resolve().parents[1]
DEFAULT_SAMPLE_PATH = BASE_DIR / "samples" / "default_rx.txt"
OUTPUTS_DIR = BASE_DIR / "outputs"
LATEST_OUTPUT_DIR = OUTPUTS_DIR / "latest"
RUNS_OUTPUT_DIR = OUTPUTS_DIR / "runs"

DEFAULT_LIMITATIONS = [
    "실제 OCR API를 호출하지 않고 입력 텍스트를 더미 OCR 결과로 사용합니다.",
    "실제 DUR API를 호출하지 않고 mock DUR 룰만 사용합니다.",
    "의료 진단, 처방 판단, 복용 중단 또는 복용 권고를 하지 않습니다.",
    "Rule-based 추출이므로 실제 서비스에서는 전문가 검수와 API/LLM 검증이 필요합니다.",
]

