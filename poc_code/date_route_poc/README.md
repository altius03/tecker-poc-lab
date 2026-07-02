# date_route_poc

데이트 동선 탐색 PoC용 Python CLI입니다. Google Places API를 단순 호출하는 데모가 아니라, 아래 데이터 병목이 실제로 처리되는지 검증합니다.

```text
사용자 자연어
-> OpenAI로 조건 JSON 구조화
-> rule table로 조건 검증 가능성 분류
-> Google Places로 장소 후보 수집
-> 최종 후보 리뷰에서 OpenAI로 무드 근거 문장 추출
-> 검증 불가능한 조건은 unmatched_conditions에 명시
-> 후보 부족 시 rule 기반 fallback 로그 기록
-> 최종 후보/간단 코스/Google Maps URL JSON 생성
```

## 1. PoC 핵심

이번 PoC는 다음 3가지를 검증합니다.

```text
1. 조건별 데이터 검증 가능성 분리
2. 데이터 부족 조건 처리
3. 후보 0개 방지 fallback
```

조건 분류 기준:

```text
verifiable: Google Places 필드 또는 계산으로 직접 검증 가능
proxy_verified: 리뷰 근거 문장으로 간접 검증 가능
proxy_not_found: 리뷰를 봤지만 근거 문장을 찾지 못함
unsupported: 현재 데이터로 검증 불가
```

## 2. 설치 방법

```bash
uv sync --python 3.11
```

## 3. .env 설정 방법

```bash
cp .env.example .env
```

`.env`에는 실제 키를 로컬에만 저장합니다. GitHub에는 올리지 않습니다.

```env
GOOGLE_MAPS_API_KEY=발급받은_GOOGLE_MAPS_API_KEY
OPENAI_API_KEY=발급받은_OPENAI_API_KEY
OPENAI_MODEL=gpt-4o-mini
```

## 4. 실행 명령

```bash
uv run python -m src.run --query "성수역 근처에서 조용한 파스타집이랑 디저트 카페, 예산 12만 원 안쪽, 도보 이동 가능한 코스로 짜줘"
```

입력값을 생략하면 `samples/default_query.txt`를 사용합니다.

```bash
uv run python -m src.run
```

## 5. 결과 JSON 위치

성공/실패와 관계없이 결과 JSON을 저장합니다.

```text
outputs/latest/result.json
outputs/runs/YYYYMMDD_HHMMSS/result.json
```

주요 필드:

```text
parsed_conditions: OpenAI가 구조화한 조건
condition_capability: verifiable/proxy/unsupported 분류 결과
matched_conditions: 추천에 반영되거나 근거가 확인된 조건
unmatched_conditions: 못 맞춘 조건과 이유
fallback_log: 후보 부족 시 조건 완화 시도 로그
candidate_places: Google Places 후보 요약
review_evidence: 리뷰에서 추출한 무드 근거 문장
api_usage: Google/OpenAI 호출 수
```

## 6. 실제 소규모 검증 결과

2026-07-03에 실제 키로 두 번 실행했습니다.

대표 입력:

```text
성수역 근처에서 조용한 파스타집이랑 디저트 카페, 예산 12만 원 안쪽, 도보 이동 가능한 코스로 짜줘
```

결과 요약:

```text
status: success
candidate_count: 10
condition_capability: verifiable 6, unsupported 1, proxy_not_found 1
review_place_count: 2
review_evidence_count: 0
route_stop_count: 2
```

확인된 점:

- 정확한 예산은 메뉴 가격 데이터가 없어 `unsupported`로 분리됨
- 조용한 조건은 최종 후보 리뷰에서 근거 문장을 찾지 못해 `proxy_not_found`로 남음
- 후보는 충분히 나와 fallback은 발동하지 않음
- Google Text Search가 어려운 조건에도 넓게 후보를 반환하므로, 다음 병목은 후보 0개보다 검색 결과의 느슨한 매칭을 점수화하는 것

## 7. 검증 명령

```bash
uv run python -m unittest -q
uv run python -m compileall src
```

## 8. 실패 시 error.code

- `MISSING_API_KEY`: `GOOGLE_MAPS_API_KEY` 또는 `OPENAI_API_KEY`가 없음
- `MISSING_INPUT`: `--query`가 없고 `samples/default_query.txt`도 없음
- `API_REQUEST_FAILED`: Google Places 또는 OpenAI API 호출 실패
- `UNEXPECTED_ERROR`: 그 외 예상하지 못한 예외

## 9. 주의점

- Google Places 리뷰/상세 필드는 비용 리스크가 있으므로 최종 후보 일부에만 호출합니다.
- LLM은 장소를 지어내지 않고, 조건 구조화와 리뷰 근거 문장 추출에만 사용합니다.
- 동선은 최적화가 아니라 PoC용 역할 순서 기반 단순 연결입니다.
