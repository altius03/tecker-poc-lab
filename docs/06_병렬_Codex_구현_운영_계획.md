# 병렬 Codex 구현 운영 계획

## 0. 목적

3개 PoC를 새 Codex 스레드에서 병렬 구현할 때 서로 충돌하지 않도록 작업 범위와 완료 기준을 정리한다.
현재 구현 중인 코드에는 영향을 주지 않고, 병렬 작업 관리 기준만 제공한다.

---

## 1. 병렬 스레드 구성

| 스레드 | 작업지시서 | 작업 폴더 |
| --- | --- | --- |
| VOC Quest | `04_Codex_PoC_작업지시서/01_VOC_Quest_Codex_PoC_작업지시서.md` | `poc_code/voc_quest_poc` |
| Be:Careful | `04_Codex_PoC_작업지시서/02_BeCareful_Codex_PoC_작업지시서.md` | `poc_code/becareful_poc` |
| 데이트 동선 | `04_Codex_PoC_작업지시서/03_데이트_동선_Codex_PoC_작업지시서.md` | `poc_code/date_route_poc` |

각 스레드는 자기 작업 폴더 밖을 수정하지 않는다.

---

## 2. 각 스레드에 공통으로 붙일 지시문

```text
작업지시서에 명시된 범위만 구현해줘.
전체 서비스가 아니라 핵심 PoC 모듈 구현이 목표다.
웹 UI, DB, 로그인, 배포는 만들지 마.
작업 폴더 밖의 파일은 수정하지 마.
실패해도 outputs/latest/result.json에 실패 JSON을 남겨.
README.md에는 실제 검증한 설치/실행 명령을 남겨.
.env는 만들 수 있지만 커밋/공유 대상에 포함하지 말고, .env.example만 제공해.
```

---

## 3. 완료 기준

각 스레드는 아래를 완료해야 한다.

| 항목 | 기준 |
| --- | --- |
| 코드 | 작업지시서의 모듈 파일 생성 |
| 실행 | README의 실행 명령으로 CLI 실행 가능 |
| 결과 | `outputs/latest/result.json` 생성 |
| 실패 처리 | 실패 케이스도 JSON으로 저장 |
| 의존성 | `pyproject.toml` 또는 `requirements.txt` 제공 |
| 문서 | README에 설치/실행/.env/결과 위치/error code 포함 |

---

## 4. API 키 처리

| 프로젝트 | 키 없을 때 구현 중 처리 | 런타임 처리 |
| --- | --- | --- |
| VOC Quest | 사용자에게 네이버 API 키 발급/제공 여부 질문 | `MISSING_API_KEY` 실패 JSON |
| Be:Careful | 키 필요 없음 | mock 기반 실행 |
| 데이트 동선 | 사용자에게 Kakao REST API 키 발급/제공 여부 질문 | `MISSING_API_KEY` 실패 JSON |

샘플 실행은 `--use-sample` 명시 옵션이 있을 때만 허용한다.

---

## 5. 병합 전 체크리스트

- [ ] `.env` 파일이 공유 대상에 없음
- [ ] `outputs/latest/result.json` 존재
- [ ] `outputs/runs/`는 공유 대상에서 제외
- [ ] README 실행 명령이 실제로 동작함
- [ ] 실패 JSON 생성 경로가 동작함
- [ ] 작업 폴더 밖 파일 수정 없음
- [ ] 각 프로젝트의 목적이 README 상단에 적혀 있음

---

## 6. 통합 레포로 옮길 때

1. 각 프로젝트 폴더를 `tecker-poc-lab/` 루트로 복사한다.
2. 문서 4개는 `docs/`에 복사한다.
3. 작업지시서 3개는 `instructions/`에 복사한다.
4. 루트 README와 `.gitignore`를 추가한다.
5. `.env` 및 개인 키가 없는지 최종 확인한다.
6. private GitHub 레포에 push한다.
