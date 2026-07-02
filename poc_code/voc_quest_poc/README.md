# VOC Quest PoC

VOC Quest의 핵심 병목인 `제품 seed -> 검색어 확장 -> 네이버 검색 API 후보 수집 -> 권한/출처 라우팅 -> rule-based 분류 -> 개선 퀘스트 JSON 생성`을 검증하는 Python CLI PoC입니다.

웹 UI, DB, 로그인, 배포, 본문 크롤링은 구현하지 않습니다.

## 1. 설치 방법

아래 명령을 이 폴더에서 실제 검증했습니다.

```powershell
cd C:\Users\geonh\GH_archive\아이디어\poc_code\voc_quest_poc
python -m pip install -e .
```

검증 도구까지 설치하려면 아래 명령을 사용합니다.

```powershell
python -m pip install -e ".[dev]"
```

insane-search 기반 공개 URL 원문 보강까지 검증하려면 아래 의존성도 설치합니다.

```powershell
python -m pip install -e ".[dev,public-web]"
```

검증 환경:

```powershell
python --version
# Python 3.14.3
```

## 2. .env 설정 방법

`.env.example`을 복사해 `.env`를 만들고 네이버 검색 API 키를 넣습니다.

```powershell
Copy-Item .env.example .env
```

`.env`:

```env
NAVER_CLIENT_ID=발급받은_CLIENT_ID
NAVER_CLIENT_SECRET=발급받은_CLIENT_SECRET
```

실제 키가 없으면 `--use-sample` 없이 실행했을 때 `MISSING_API_KEY` 실패 JSON을 저장합니다.

## 3. 기본 실행 명령

실제 네이버 검색 API를 호출합니다.

```powershell
python -m src.run --seed "브랜드A 블루 수딩 앰플"
```

검색 결과 URL을 `external/insane-search` engine으로 읽어 공개 원문 텍스트를 보강하려면:

```powershell
python -m src.run --seed "브랜드A 블루 수딩 앰플" --use-insane-search --insane-search-max-items 5
```

`--seed`가 없으면 `samples/default_seed.txt` 값을 사용합니다.

```powershell
python -m src.run
```

## 4. 샘플 실행 명령

명시적으로 샘플 네이버 응답을 사용합니다. 이 명령을 실제 검증했습니다.

```powershell
python -m src.run --seed "브랜드A 블루 수딩 앰플" --use-sample
python -m src.run --use-sample
```

샘플 실행 결과에는 아래 값이 기록됩니다.

```json
{
  "fallback_used": true,
  "fallback_reason": "explicit_use_sample"
}
```

## 5. 결과 JSON 위치

성공과 실패 모두 아래 두 위치에 `result.json`을 저장합니다.

```text
outputs/latest/result.json
outputs/runs/YYYYMMDD_HHMMSS/result.json
```

검증한 샘플 실행의 `outputs/latest/result.json` 요약:

```json
{
  "query_count": 20,
  "collected_count": 13,
  "ad_suspected_count": 1,
  "duplicate_count": 1,
  "issue_cluster_count": 5,
  "quest_count": 5
}
```

## 6. 실패 시 확인할 error.code 목록

```text
MISSING_INPUT
MISSING_API_KEY
API_REQUEST_FAILED
VALIDATION_ERROR
UNEXPECTED_ERROR
```

검증한 실패 실행:

```powershell
python -m src.run --seed "브랜드A 블루 수딩 앰플"
```

`.env`에 키가 없는 상태에서 위 명령은 예외로 종료하지 않고 `outputs/latest/result.json`에 `MISSING_API_KEY` 실패 JSON을 저장했습니다.

## 7. PoC 검증 명령

모듈 계약과 mock API 실패 처리를 자동 테스트합니다.

```powershell
python -m pytest
```

여러 seed를 돌려 배치 요약과 사람이 채점할 CSV를 만듭니다.

```powershell
python tools\run_seed_batch.py --use-sample
python tools\run_seed_batch.py --seeds-file samples\evaluation_seeds.txt
python tools\run_seed_batch.py --seeds-file samples\evaluation_seeds.txt --use-insane-search --insane-search-max-items 5
```

결과 위치:

```text
outputs/evaluations/YYYYMMDD_HHMMSS/batch_summary.csv
outputs/evaluations/YYYYMMDD_HHMMSS/manual_review_sheet.csv
outputs/evaluations/YYYYMMDD_HHMMSS/batch_results.json
```

검증 기준은 [docs/validation_gate.md](docs/validation_gate.md)에 정리했습니다.

## 구현 범위 메모

- 네이버 API 호출 범위: blog, cafearticle, webkr, shop
- 후보 분석 범위: 기본은 네이버 API가 제공하는 제목/링크/요약/쇼핑 메타데이터
- 공개 원문 보강: `--use-insane-search` 사용 시 공개 접근 가능한 URL에 한해 `public_text_excerpt`를 추가
- 권한 라우팅: `official_api`, `snippet_only`, `auth_required`, `customer_provided_needed`
- 정제: HTML 태그 제거, 전화번호/이메일/주문번호/주소 마스킹, 광고/협찬 플래그, content hash 생성
- 분류: rule-based 감성, 비꼼 후보, 이슈 유형 분류
- 퀘스트: 이슈 클러스터별 개선 퀘스트 JSON 생성

## 실행 지속성

이 PoC는 로컬 노트북에서 실행됩니다. 노트북 전원이 꺼지면 실행도 중단됩니다. 장시간 배치가 필요하면 절전/종료를 끄거나, 원격 서버/클라우드 VM/항상 켜진 PC에서 실행해야 합니다.
