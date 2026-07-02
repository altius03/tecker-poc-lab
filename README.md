# Tecker PoC Lab

테커 부트캠프 아이디어 회의용 PoC 코드와 정리 문서 공유 레포입니다.

## 구조

- `docs/`: 아이디어 정리, PoC 판단 근거, Codex 작업지시서
- `poc_code/`: 각 주제별 독립 Python CLI PoC

## 실행 원칙

실제 API 키는 GitHub에 올리지 않습니다. 각 프로젝트의 `.env.example`을 `.env`로 복사한 뒤 로컬에서만 값을 채워 실행합니다.

키 없이 구조만 확인하려면 각 PoC README의 sample/mock 실행 방식을 사용합니다.

## 현재 포함된 PoC

- `poc_code/voc_quest_poc`: VOC Quest 시장조사 파이프라인 PoC

Be:Careful, 데이트 동선 탐색 PoC는 구현 결과가 준비되는 대로 같은 구조로 추가합니다.
