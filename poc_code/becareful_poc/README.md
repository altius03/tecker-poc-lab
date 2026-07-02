# Be:Careful Python CLI PoC

Be:Careful의 핵심 병목인 `OCR 텍스트 -> 약명/복용 일정 후보 추출 -> mock DUR -> 안전 문구 변환 -> 인수인계 카드 JSON 생성` 흐름만 검증하는 Python CLI PoC입니다.

실제 OCR API, DUR API, 웹 UI, DB, 로그인, 배포는 포함하지 않습니다.

## 1. 설치 방법

외부 패키지 의존성은 없습니다. Python 3.11 이상에서 실행합니다.

```powershell
cd "C:\Users\geonh\Desktop\테커 아이디어회의\poc_code\becareful_poc"
python --version
```

검증 환경:

```text
Python 3.11.15
```

## 2. .env 설정 방법

API 키가 필요하지 않습니다. `.env.example`은 비워 둡니다.

## 3. 기본 실행 명령

입력값을 주지 않으면 `samples/default_rx.txt`를 사용합니다.

```powershell
python -m src.run
```

## 4. 샘플 실행 명령

아래 명령을 실제로 검증했습니다.

```powershell
python -m src.run --ocr-file samples/default_rx.txt
python -m src.run --ocr-text "아모잘탄정 5/50mg 1일 1회 아침 식후 30일"
```

실패 JSON 생성 검증:

```powershell
python -m src.run --ocr-text "환자명: 홍길동"
```

자동 테스트:

```powershell
python -m unittest discover -s tests
```

골든 샘플 평가:

```powershell
python -m src.evaluate
```

## 5. 결과 JSON 위치

```text
outputs/latest/result.json
outputs/runs/YYYYMMDD_HHMMSS/result.json
outputs/evaluation/latest_report.json
```

성공/실패 모두 위 경로에 JSON을 남깁니다.

## 6. 실패 시 확인할 error.code 목록

```text
MISSING_INPUT
PARSING_FAILED
VALIDATION_ERROR
UNEXPECTED_ERROR
```

## 구현 범위

- 더미 OCR 텍스트 입력
- 개인정보 이름/전화번호/주민번호 형태 마스킹
- rule-based 약명, 용량, 복용 횟수, 복용 시간, 기간, 병원 일정 후보 추출
- mock DUR 상태 생성
- 위험한 의료 판단 문구를 안전 문구로 변환
- 복약 일정 JSON 생성
- 보호자 인수인계 카드 JSON 생성
- 실패 시에도 `outputs/latest/result.json` 저장

`ocr_parser.py`와 `handoff_builder.py`의 rule-based 파서는 실제 서비스 단계에서 LLM parser/summarizer로 교체할 수 있습니다.

## 현재 검증 해석

`python -m src.evaluate`는 더미 OCR 텍스트 기준의 골든 샘플만 평가합니다. 이 평가가 통과해도 실제 서비스 가능성이 확정되는 것은 아닙니다.

남은 핵심 검증:

- 실제 OCR API가 약봉투/처방전 사진에서 약명, 용량, 복용법을 충분히 추출하는지 확인
- mock DUR 대신 실제 의약품/DUR 데이터 소스를 연결할 수 있는지 확인
- 약사 또는 의료 도메인 검수자로 인수인계 카드 문구 안전성 확인
