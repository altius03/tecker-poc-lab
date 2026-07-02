# date_route_poc

데이트 동선 탐색 PoC용 Python CLI입니다. 전체 서비스가 아니라 아래 병목 흐름이 코드로 가능한지 검증합니다.

```text
자연어 조건 구조화 -> Kakao Local 장소 후보 조회 -> provider mode -> 장소 필터링 -> 코스 생성 -> 길찾기 후보 URL JSON 생성
```

웹 UI, DB, 로그인, 배포, Google Places/Routes 실제 호출은 구현하지 않았습니다.

## 1. 설치 방법

아래 명령을 실제 검증했습니다.

```bash
uv sync --python 3.11
```

검증 환경에서는 `.venv`가 생성되고 `requests`, `python-dotenv`, `pydantic`, `typer`, `rich`가 설치됐습니다.

## 2. .env 설정 방법

```bash
cp .env.example .env
```

`.env`에 Kakao Local REST API 키를 넣습니다.

```env
KAKAO_REST_API_KEY=발급받은_REST_API_KEY
```

키가 없고 `--use-sample`도 없으면 실제 조회처럼 꾸미지 않고 `MISSING_API_KEY` 실패 JSON을 저장합니다.

## 3. 기본 실행 명령

Kakao Local API 키가 설정된 뒤 실행하는 실제 API 경로입니다.

```bash
uv run python -m src.run --query "성수역 근처에서 저녁 데이트할 건데, 예산 12만 원 안쪽, 분위기 좋은 파스타집이랑 디저트 카페, 걸어서 이동 가능한 코스로 짜줘"
```

입력값을 생략하면 `samples/default_query.txt`를 사용합니다.

```bash
uv run python -m src.run
```

## 4. 샘플 실행 명령

아래 명령을 실제 검증했고, `status: success` 결과 JSON이 생성됐습니다.

```bash
uv run python -m src.run --query "성수역 근처 데이트 코스 짜줘" --use-sample
```

샘플 실행 결과에는 아래 값이 들어갑니다.

```json
{
  "fallback_used": true,
  "fallback_reason": "explicit_use_sample"
}
```

## 5. 결과 JSON 위치

모든 실행은 성공/실패와 관계없이 결과 JSON을 저장합니다.

```text
outputs/latest/result.json
outputs/runs/YYYYMMDD_HHMMSS/result.json
```

## 6. 실패 시 확인할 error.code

- `MISSING_API_KEY`: `.env`에 `KAKAO_REST_API_KEY`가 없고 `--use-sample`도 없음
- `MISSING_INPUT`: `--query`가 없고 `samples/default_query.txt`도 없음
- `API_REQUEST_FAILED`: Kakao Local API HTTP 오류, 네트워크 오류, 응답 파싱 실패
- `VALIDATION_ERROR`: 후보 장소나 코스 수가 PoC 성공 기준보다 부족함
- `UNEXPECTED_ERROR`: 그 외 예상하지 못한 예외

## 7. PoC 판정 검증

로컬에서 할 수 있는 검증은 아래 명령으로 한 번에 실행합니다.

```bash
uv run python scripts/validate_poc.py
```

현재 검증 결과는 아래 위치에 저장됩니다.

```text
outputs/verification/latest_verification.json
outputs/verification/runs/YYYYMMDD_HHMMSS/verification.json
```

이 검증은 다음 항목을 확인합니다.

- Python 모듈 compile
- `unittest` 기반 핵심 모듈 테스트
- 샘플 모드 대표 질의 벤치마크
- 성공 JSON/실패 JSON 스키마 형태
- API 키 누락 시 `MISSING_API_KEY` 실패 JSON 생성
- Google Places/Routes 실제 API 호스트 미사용 여부

실제 Kakao Local API까지 포함하려면 `.env`에 키를 넣고 아래 명령을 실행합니다.

```bash
uv run python scripts/validate_poc.py --real-api
```

실제 Kakao API 키를 넣고 검증한 최종 기술 판정은 `technical_poc_passed_pending_human_quality_review`입니다. 즉, 샘플/구조/실패 처리/실제 Kakao API smoke 검증은 통과했고, 사람이 보는 결과물 품질 평가는 별도로 필요합니다.

`--real-api` 실행 시 아래 메시지가 나오면 키는 읽혔지만 Kakao Developers 앱에서 카카오맵/로컬 서비스가 활성화되지 않은 상태입니다.

```text
App(VOC) disabled OPEN_MAP_AND_LOCAL service
```

이 경우 Kakao Developers 콘솔에서 해당 앱의 카카오맵/로컬 또는 Open Map and Local 관련 서비스/권한을 활성화한 뒤 다시 실행합니다.

## 검증한 명령

```bash
uv sync --python 3.11
uv run python -m src.run --query "성수역 근처 데이트 코스 짜줘" --use-sample
uv run python -m src.run --query "성수역 근처 데이트 코스 짜줘"
python -m compileall src
uv run python -m unittest discover -s tests
uv run python scripts/validate_poc.py
uv run python scripts/validate_poc.py --real-api
```

실제 Kakao API smoke 검증에서는 대표 성수역 질의 3개가 모두 통과했고, 실패 경로 검증에서는 API 키가 없을 때 `MISSING_API_KEY`가 저장되는 것을 확인했습니다.
