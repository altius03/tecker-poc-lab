# Techeer PoC Lab

Techeer 부트캠프 아이디어 회의용 PoC 코드와 정리 문서 공유 레포입니다.

## 구조

```text
techeer-poc-lab/
├─ README.md
├─ docs/
│  ├─ 00_아이디어_정리_인덱스.md
│  ├─ 01_VOC_Quest.md
│  ├─ 02_BeCareful.md
│  ├─ 03_데이트_동선.md
│  └─ codex_poc_instructions/
│     └─ 각 주제별 Codex 구현 작업지시서
└─ poc_code/
   ├─ voc_quest_poc/
   │  ├─ src/
   │  ├─ tests/
   │  └─ VOC Quest 시장조사 파이프라인 PoC
   ├─ becareful_poc/
   │  ├─ src/
   │  ├─ tests/
   │  └─ Be:Careful 복약 안내 PoC
   └─ date_route_poc/
      ├─ src/
      ├─ tests/
      └─ 데이트 동선 탐색 PoC
```

## 실행 원칙

실제 API 키는 GitHub에 올리지 않습니다. 각 프로젝트의 `.env.example`을 `.env`로 복사한 뒤 로컬에서만 값을 채워 실행합니다.

키 없이 구조만 확인하려면 각 PoC README의 sample/mock 실행 방식을 사용합니다.

## 제품별 상태

- `poc_code/voc_quest_poc`: VOC Quest 시장조사 파이프라인 PoC 코드 포함
- `poc_code/becareful_poc`: Be:Careful 더미 OCR + mock DUR PoC 코드 포함
- `poc_code/date_route_poc`: 데이트 동선 탐색 Kakao Local 기반 PoC 코드 포함
