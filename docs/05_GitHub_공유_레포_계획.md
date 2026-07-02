# GitHub 공유 레포 계획

## 0. 목적

PoC 구현이 끝난 뒤, 코드와 결과 JSON을 팀원/멘토에게 공유하기 위한 임시 GitHub 레포 구성 계획이다.
현재 코드 구현 중인 폴더에는 영향을 주지 않고, 나중에 결과물을 한 번에 모아 올리는 기준만 정한다.

---

## 1. 권장 레포 이름

아래 중 하나를 사용한다.

| 후보 | 설명 |
| --- | --- |
| `tecker-poc-lab` | 가장 무난한 임시 PoC 레포명 |
| `tecker-idea-poc` | 아이디어 검증용 코드라는 의미가 명확함 |
| `tecker-bootcamp-poc` | 부트캠프 제출/공유 맥락이 드러남 |

추천: `tecker-poc-lab`

---

## 2. 공개 범위

| 선택지 | 장점 | 단점 | 추천 |
| --- | --- | --- | --- |
| Private | API 키/미완성 코드 노출 위험이 낮음 | 멘토/팀원 초대 필요 | 추천 |
| Public | 공유가 쉬움 | 실수로 키/민감 정보 노출 위험 | 비추천 |

추천: **Private 레포로 생성 후 팀원/멘토만 초대**

---

## 3. 최종 레포 구조

```text
tecker-poc-lab/
  README.md
  .gitignore

  docs/
    00_아이디어_정리_인덱스.md
    01_VOC_Quest.md
    02_BeCareful.md
    03_데이트_동선.md

  instructions/
    01_VOC_Quest_Codex_PoC_작업지시서.md
    02_BeCareful_Codex_PoC_작업지시서.md
    03_데이트_동선_Codex_PoC_작업지시서.md

  voc_quest_poc/
    README.md
    .env.example
    pyproject.toml 또는 requirements.txt
    src/
    samples/
    outputs/latest/result.json

  becareful_poc/
    README.md
    .env.example
    pyproject.toml 또는 requirements.txt
    src/
    samples/
    outputs/latest/result.json

  date_route_poc/
    README.md
    .env.example
    pyproject.toml 또는 requirements.txt
    src/
    samples/
    outputs/latest/result.json
```

---

## 4. `.gitignore` 기준

```gitignore
.env
.venv/
venv/
__pycache__/
*.pyc
.pytest_cache/
.ruff_cache/
.DS_Store
outputs/runs/
```

`outputs/latest/result.json`은 발표 근거이므로 커밋해도 된다.
`outputs/runs/`는 누적 실행 로그라 커밋하지 않는다.

---

## 5. 레포 README에 들어갈 내용

```md
# Tecker PoC Lab

## 목적
3개 아이디어의 핵심 챌린징 포인트를 Python CLI PoC로 검증한다.
전체 서비스 구현이 아니라, 구현 가능성을 보여주는 미니 파이프라인이다.

## 프로젝트
| 프로젝트 | 검증 포인트 |
| --- | --- |
| VOC Quest | 제품 seed 기반 공개 VOC 수집/분류/퀘스트화 |
| Be:Careful | OCR 텍스트 기반 복약 정보 구조화/안전 문구/인수인계 |
| 데이트 동선 | 자연어 조건 구조화/Kakao 장소 후보/코스 생성 |

## 실행 결과
각 프로젝트의 `outputs/latest/result.json` 확인.

## 보안
실제 API 키는 `.env`에만 저장하고 커밋하지 않는다.
```

---

## 6. 코드 취합 순서

1. 각 Codex 스레드가 자기 프로젝트 폴더만 구현한다.
2. 각 프로젝트에서 `outputs/latest/result.json` 생성까지 확인한다.
3. `poc_code` 아래 3개 프로젝트를 임시 레포 루트로 복사한다.
4. `docs/`에 상단 4개 문서를 복사한다.
5. `instructions/`에 작업지시서 3개를 복사한다.
6. `.env`가 없는지 확인한다.
7. `outputs/runs/`는 제외한다.
8. GitHub private 레포에 push한다.

---

## 7. 레포 생성 전 사용자 결정 필요

- 레포 이름: 기본 추천 `tecker-poc-lab`
- 공개 여부: 기본 추천 `private`
- 소유자: 개인 계정 또는 팀 조직
- 팀원 초대 여부
- 구현 결과를 한 번에 올릴지, 주제별로 순차 push할지

---

## 8. 원격 레포 생성 명령 예시

GitHub CLI를 사용할 경우:

```bash
gh repo create tecker-poc-lab --private --description "Tecker bootcamp idea PoC lab" --add-readme=false
```

원격 연결 예시:

```bash
git init
git add .
git commit -m "Initial PoC lab structure"
git branch -M main
git remote add origin https://github.com/<owner>/tecker-poc-lab.git
git push -u origin main
```

실제 생성은 레포명/공개 여부/소유자 확인 후 진행한다.
