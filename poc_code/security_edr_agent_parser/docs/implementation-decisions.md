# 신규 구현 결정 기록

이 문서는 EDR Agent Parser를 0부터 다시 구현할 때 흔들리지 않을 기준을 정리합니다.

---

## 1. 수집 원칙

Agent는 보안 판단에 필요한 metadata만 수집합니다.
원문 내용, 비밀번호, 키 입력, 클립보드, 문서 본문, 임의의 HTTPS payload는 수집하지 않습니다.

이유는 다음과 같습니다.

| 제외 항목 | 수집하지 않는 이유 | 대신 사용할 데이터 |
|---|---|---|
| message body | 메신저/메일/채팅 본문은 spyware처럼 보이고 탐지에 필요한 신호보다 민감 원문이 많음 | app name, process, destination, time, byte count |
| browser password | credential theft와 구분이 어렵고 방어적 PoC에 필요하지 않음 | browser process, suspicious process, credential-stealer IOC |
| keystroke | keylogging은 공격 기능으로 해석될 수 있음 | process tree, command line, network connection |
| clipboard | token/password/개인 대화가 섞일 수 있음 | 필요한 경우 synthetic event count/time |
| document body | 문서 원문은 회사/개인 정보가 바로 포함될 수 있음 | file extension, size, hash, timestamp |
| 임의의 HTTPS payload | 무단 감청/복호화로 보일 수 있고 로그인/결제/메시지가 섞일 수 있음 | SNI/domain, URL path, method, status, content-type, byte count, hash |

판단 기준은 단순합니다.

```text
탐지에 필요한 신호는 남긴다.
사람이 작성한 원문 내용은 저장하지 않는다.
```

---

## 2. Transport

결정: `gRPC + mTLS`를 1차 구현의 primary transport로 사용합니다.

REST ingestion은 기본 경로로 두지 않습니다.
REST/OpenAPI는 health check, admin/debug, report download, Swagger 설명 같은 보조 API로만 사용합니다.

| 항목 | 결정 |
|---|---|
| Primary ingest | gRPC `TelemetryIngestService/IngestTelemetry` |
| Streaming 확장 | gRPC `StreamTelemetry` 후보 |
| Device identity | mTLS client certificate |
| Short-lived authorization | device token refresh |
| Tenant 분리 | `customer_id` |
| Device 분리 | `device_id` |
| Version 분리 | `agent_version`, `schema_version` |

gRPC metadata 예시는 다음과 같습니다.

```text
edr-customer-id: acme-demo
edr-device-id: kim-minjun-finance-laptop
edr-agent-version: 0.1.0
edr-schema-version: telemetry.v1
```

---

## 3. Backend

결정: Python 3.11 기반 collector로 갑니다.

| 영역 | 결정 |
|---|---|
| Collector runtime | Python 3.11 |
| Primary server | gRPC server |
| 보조 HTTP API | FastAPI |
| HTTP API 용도 | health, admin/debug, report download, Swagger |
| Node/NestJS | 사용하지 않음 |

이유:

- Agent, parser, detection, report 쪽이 Python과 잘 맞음
- 팀이 빠르게 PoC를 구현하기 쉬움
- gRPC Python으로 proto contract를 강제할 수 있음
- FastAPI는 Swagger와 보조 API에만 쓰면 역할이 명확함

---

## 4. Storage

결정: PostgreSQL을 기본 저장소로 사용합니다.

| 용도 | 결정 |
|---|---|
| 기본 DB | PostgreSQL |
| Local fallback | SQLite |
| Queue/DLQ | PostgreSQL table로 시작 |
| Object/file artifact | local volume 또는 S3-compatible storage |

SQLite는 unit test나 Docker가 없는 local fallback에만 사용합니다.
PoC 데모는 Docker Compose의 PostgreSQL을 기준으로 잡습니다.

---

## 5. Certificate

결정: PoC 구현은 PEM file 기준으로 시작합니다.

| 항목 | 결정 |
|---|---|
| Local cert format | PEM |
| Agent identity | certificate subject + fingerprint |
| Token refresh | mTLS 연결 위에서 short-lived token 발급 |
| Windows PFX/cert store | 패키징 단계에서 확장 |

PEM을 먼저 쓰는 이유는 local dev, Docker, CI에서 검증하기 쉽기 때문입니다.
Windows cert store/PFX는 실제 설치형 agent를 만들 때 추가합니다.

---

## 6. Dashboard

결정: React + Vite + TypeScript SPA로 신규 구현합니다.

정적 HTML dashboard는 reference artifact로만 유지합니다.
신규 dashboard는 Falcon/Palo Alto처럼 operational dashboard 느낌으로 갑니다.

필수 화면:

- 첫 화면 topology: 컴퓨터 -> 우리 내부 -> 나가는 destination
- time range: last 10 minutes, 1 hour, 24 hours
- severity quick filter
- alert inspector: 클릭한 alert를 우상단에서 즉시 식별
- endpoint status: success/failure가 아니라 EDR status와 risk state로 표시
- report popup
- PDF download

---

## 7. Sample Identity

결정: 실제 사람처럼 구분 가능한 한국어 가명을 사용합니다.

실제 팀원, 지인, 회사 사람의 개인정보는 넣지 않습니다.

예시:

| device_id | 표시 이름 | 역할 |
|---|---|---|
| kim-minjun-finance-laptop | 김민준 | 재무팀 laptop |
| park-soyeon-hr-desktop | 박소연 | 인사팀 desktop |
| lee-hyunwoo-dev-workstation | 이현우 | 개발팀 workstation |

---

## 8. HTTPS/L7 분석

결정: 허가된 local proxy, test app, sample record만 사용합니다.

저장하는 것:

- domain
- SNI
- URL path
- method
- status
- content-type
- byte count
- file hash
- rule match
- app action label

저장하지 않는 것:

- raw HTTP body
- message body
- password/token 원문
- document body
- 임의의 HTTPS payload

---

## 9. 구현 우선순위

1. contracts: protobuf, OpenAPI 보조 API, event schema
2. collector: gRPC + mTLS ingest, PostgreSQL 저장
3. agent: Windows process/network/DNS/file metadata 수집
4. analysis: detection, SIEM correlation, MITRE mapping
5. dashboard: React/Vite topology와 alert workflow
6. report: popup, HTML, PDF export
7. packaging: Docker Compose, local cert, demo seed data

---

## 10. 남은 미결정

현재 기준 문서에서는 미결정 항목을 남기지 않습니다.
구현 중 바뀌는 내용은 이 문서에 decision 변경으로 기록합니다.
