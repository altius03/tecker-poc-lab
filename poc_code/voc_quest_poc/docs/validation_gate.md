# VOC Quest PoC 검증 게이트

이 문서는 `voc_quest_poc`가 "서비스 가능할 것 같다"는 판단을 줄 만큼 챌린징 포인트를 통과했는지 확인하기 위한 기준이다.

## 현재 자동 검증 대상

```powershell
python -m pytest
python -m src.run --seed "브랜드A 블루 수딩 앰플" --use-sample
python tools\run_seed_batch.py --use-sample
python tools\run_seed_batch.py --seeds-file samples\evaluation_seeds.txt --use-insane-search --insane-search-max-items 5
```

자동 검증이 확인하는 것:

- seed에서 15개 이상 검색어 생성
- 샘플 네이버 응답을 blog/cafe/shop 후보로 정규화
- HTTP 실패와 비JSON 응답을 `ApiRequestError`로 변환
- 권한/출처 라우팅 이후 개인정보 마스킹, 광고 플래그, 중복 hash 동작
- rule-based 이슈 분류와 비꼼 후보 탐지
- 이슈 클러스터와 개선 퀘스트 생성
- CLI 성공 실행이 `outputs/latest/result.json`을 생성
- `--use-insane-search` 사용 시 공개 URL 원문 보강 수를 `public_text_enriched_count`로 기록

## 실제 API 검증 기준

실제 네이버 API 키를 `.env`에 설정한 뒤 실행한다.

```powershell
python tools\run_seed_batch.py --seeds-file samples\evaluation_seeds.txt
```

판단 기준:

| 항목 | Pass 기준 | Fail/수정 신호 |
| --- | --- | --- |
| API 실행 | seed 대부분이 success | 인증 오류, 429, timeout 반복 |
| 후보 수집 | seed당 관련 후보 5건 이상 | 쇼핑 메타만 나오거나 빈 결과 |
| 검색 노이즈 | 사람이 보기에 관련 후보 60~70% 이상 | 무관 브랜드/동명이품 과다 |
| 개인정보 | 마스킹 누락 0건 | 전화번호/이메일/주소/주문번호 노출 |
| 광고 플래그 | 명백한 협찬/체험단 대부분 탐지 | 광고성 후기 다수 미탐 |
| 분류 | 주요 불만 유형 3개 이상 구분 가능 | 대부분 unknown 또는 오분류 |
| 퀘스트 | seed당 유용한 퀘스트 1~2개 이상 | 액션이 추상적이거나 근거 부족 |
| 공개 원문 보강 | seed당 공개 원문 3건 이상 확보 | 대부분 snippet_only로 남음 |

## 의사결정

- `pass`: 실제 API에서도 수집과 퀘스트 생성이 반복적으로 의미 있다. 다음 단계는 내부 검수용 서비스화.
- `watch`: 수집은 되지만 노이즈/오분류가 높다. query 확장, source별 가중치, 분류 룰 보강 필요.
- `fail`: 실제 API 결과가 부족하거나 개인정보/품질 리스크가 크다. 아이디어 방향 또는 데이터 소스 재검토.

## 사람이 직접 채점할 파일

배치 실행 후 아래 파일을 채운다.

```text
outputs/evaluations/YYYYMMDD_HHMMSS/manual_review_sheet.csv
```

주요 수동 입력 컬럼:

- `manual_related_items_0_to_collected`
- `manual_useful_quests_0_to_quest_count`
- `manual_pii_leak_found_y_n`
- `manual_ad_flag_reasonable_y_n`
- `manual_decision_pass_watch_fail`
- `manual_notes`
