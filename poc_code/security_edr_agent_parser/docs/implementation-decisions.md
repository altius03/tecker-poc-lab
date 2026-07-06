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

## 4. Storage와 Queue

결정: PostgreSQL은 source of truth DB로 사용하고, Redpanda를 Kafka-compatible event broker로 사용합니다.
Kafka는 DB가 아니라 event stream/message broker입니다.

| 용도 | 결정 |
|---|---|
| 기본 DB | PostgreSQL |
| Local fallback | SQLite |
| Transactional outbox | PostgreSQL `event_outbox` table |
| Message broker | Redpanda, Kafka API compatible |
| DLQ | broker DLQ topic + PostgreSQL `dead_letter_events` table |
| Object/file artifact | local volume 또는 S3-compatible storage |

SQLite는 unit test나 Docker가 없는 local fallback에만 사용합니다.
PoC 데모는 Docker Compose의 PostgreSQL + Redpanda를 기준으로 잡습니다.

왜 Kafka 자체가 아니라 Redpanda인가:

- Kafka protocol과 client 생태계를 그대로 쓸 수 있음
- Docker Compose에서 띄우기 쉽고 Zookeeper가 필요 없음
- 포트폴리오에서는 "Kafka-compatible event streaming" 구조를 보여주기에 충분함
- 나중에 AWS로 가면 MSK 또는 Apache Kafka로 교체 가능함

---

## 5. Event-Driven Pipeline

결정: 전체 backend는 event-driven 구조로 설계합니다.

Collector가 gRPC 요청 안에서 모든 분석을 끝내지 않습니다.
Collector는 검증 가능한 최소 작업만 수행하고, event를 PostgreSQL과 outbox에 안전하게 기록한 뒤 broker로 넘깁니다.
Detection, SIEM, report, dashboard projection은 consumer가 비동기로 처리합니다.

기본 흐름:

```text
Agent
-> gRPC + mTLS Collector
-> schema validation
-> PostgreSQL events + event_outbox transaction
-> outbox publisher
-> Redpanda/Kafka topic
-> detection / SIEM / report / dashboard projection consumers
-> alerts / incidents / reports / dashboard read model
```

기본 topic:

| Topic | 생산자 | 소비자 |
|---|---|---|
| `telemetry.raw.v1` | Collector outbox publisher | normalizer, data quality worker |
| `telemetry.validated.v1` | normalizer | detection worker, SIEM correlator |
| `alerts.created.v1` | detection worker | incident builder, dashboard projector, report worker |
| `incidents.created.v1` | incident builder | dashboard projector, report worker |
| `reports.requested.v1` | dashboard/API | report worker |
| `events.dlq.v1` | any worker | data quality dashboard, retry worker |

병목 대비 원칙:

- Collector는 ingest path를 짧게 유지합니다.
- 분석 worker는 consumer group으로 수평 확장합니다.
- broker가 느리거나 죽으면 PostgreSQL outbox에 backlog가 남습니다.
- 처리 실패 event는 DLQ topic과 `dead_letter_events` table에 남깁니다.
- dashboard는 raw broker를 직접 보지 않고 PostgreSQL/read model을 조회합니다.

---

## 6. Certificate

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

## 7. Dashboard

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

## 8. Sample Identity

결정: 실제 사람처럼 구분 가능한 한국어 가명을 사용합니다.

실제 팀원, 지인, 회사 사람의 개인정보는 넣지 않습니다.

예시:

| device_id | 표시 이름 | 역할 |
|---|---|---|
| kim-minjun-finance-laptop | 김민준 | 재무팀 laptop |
| park-soyeon-hr-desktop | 박소연 | 인사팀 desktop |
| lee-hyunwoo-dev-workstation | 이현우 | 개발팀 workstation |

---

## 9. HTTPS/L7 분석

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

## 10. 구현 우선순위

1. contracts: protobuf, OpenAPI 보조 API, event schema
2. infrastructure: Docker Compose PostgreSQL + Redpanda
3. collector: gRPC + mTLS ingest, PostgreSQL 저장, outbox 발행
4. agent: Windows process/network/DNS/file metadata 수집
5. analysis consumers: detection, SIEM correlation, MITRE mapping
6. dashboard: React/Vite topology와 alert workflow
7. report: popup, HTML, PDF export
8. packaging: local cert, demo seed data

---

## 11. 남은 미결정

현재 기준 문서에서는 미결정 항목을 남기지 않습니다.
구현 중 바뀌는 내용은 이 문서에 decision 변경으로 기록합니다.
