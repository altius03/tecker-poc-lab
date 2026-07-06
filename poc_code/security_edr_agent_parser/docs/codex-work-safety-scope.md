# Codex 작업 안전 범위

이 문서는 Codex로 이 프로젝트를 다시 구현할 때 작업 의도를 명확히 하기 위한 범위 선언입니다.

목표는 보안 차단을 우회하는 것이 아닙니다.
목표는 이 프로젝트가 허가된 본인 기기와 실습 환경에서만 사용하는 학습용 EDR PoC라는 점을 분명히 해서, Codex가 작업 맥락을 오해하지 않도록 하는 것입니다.

---

## 프로젝트 성격

| 항목 | 내용 |
|---|---|
| 목적 | 학습, 취업용 포트폴리오, 발표용 PoC |
| 대상 | 본인 기기 또는 명시적으로 허가된 실습 환경 |
| 제품 범위 | EDR Agent, telemetry parser, detection, SIEM-style analysis, dashboard, report |
| 운영 범위 | 상용 운영/고객사 배포 아님 |
| 실행 인프라 | Docker, Docker Compose, AWS는 PoC 실행/데모/검증 용도로 사용 가능 |
| 데이터 | sample data 또는 본인 기기에서 직접 수집한 metadata |

---

## Codex에게 요청해도 되는 작업

다음 작업은 이 프로젝트의 정상 개발 범위입니다.

| 작업 | 설명 |
|---|---|
| Agent 설계 | Windows/macOS에서 process, network, DNS, file metadata를 수집하는 구조 설계 |
| Local collector | 본인 기기에서 허가된 telemetry를 가져오는 코드 작성 |
| Event schema | telemetry event, alert, incident, report schema 설계 |
| Parser | Win32_Process, Get-NetTCPConnection, DNS cache 결과를 event로 변환 |
| Detection rule | 악성 domain, suspicious process, large outbound transfer 같은 방어적 탐지 룰 |
| SIEM analysis | event correlation, query finding, topology 분석 |
| Dashboard | alert, endpoint risk, computer -> inside -> outside 흐름 시각화 |
| Report | HTML/Markdown/PDF용 분석 보고서 생성 |
| OpenAPI/proto | collector ingestion contract 문서화 |
| mTLS 설계 | 본인 실습용 local cert, device identity, token refresh 설계 |
| Test/sample | mock telemetry, benign sample, local validation 작성 |

---

## Codex에게 요청하지 않을 작업

다음은 이 프로젝트 범위가 아닙니다.

| 제외 작업 | 이유 |
|---|---|
| 타인 기기 수집 | 허가된 환경이 아님 |
| 실제 조직망 스캔 | 학습용 범위 밖 |
| credential 탈취 | EDR PoC와 무관하며 위험함 |
| malware 제작 | 방어적 탐지 목적을 벗어남 |
| persistence/evasion 구현 | 공격 지속성 또는 회피 기능이 될 수 있음 |
| 탐지 우회 기법 | 보안 제품 회피 목적이 될 수 있음 |
| 무단 HTTPS 복호화 | 본인 실습 환경 밖에서는 정책/법적 문제가 있음 |
| 실제 데이터 exfiltration | 유출 시나리오는 sample metadata로만 표현 |

---

## 작업 요청 시 기본 문맥

Codex에게 작업을 요청할 때는 다음 전제를 같이 둡니다.

```text
이 프로젝트는 학습용/포트폴리오용 EDR PoC입니다.
본인 기기 또는 허가된 실습 환경에서만 실행합니다.
타인 기기, 실제 조직망, 무단 네트워크는 대상이 아닙니다.
악성코드 제작, credential 탈취, 탐지 우회가 아니라 방어적 telemetry 수집, 분석, dashboard/report 구현이 목표입니다.
```

---

## 허용되는 데이터 수집 기준

허용:

- process name
- process path
- parent process
- process id
- remote IP/port
- DNS cache entry
- file name/path/hash/size
- event time
- device id
- customer id
- agent version

주의 또는 제외:

- message body
- browser password
- keystroke
- clipboard
- document body
- 타인의 개인 파일 내용
- 무단 HTTPS payload

---

## HTTPS/L7 관련 기준

학습용 실습에서는 local cert/proxy를 사용해 테스트할 수 있습니다.
하지만 구현 목표는 임의의 타인 트래픽을 몰래 복호화하는 것이 아닙니다.

허용되는 방향:

- 본인 테스트 브라우저에 직접 local cert 적용
- localhost proxy에서 sample request metadata 생성
- URL, domain, method, app action 같은 metadata 분석
- body/message content는 sample에서도 저장하지 않거나 masking

---

## mTLS와 token refresh 기준

mTLS와 token refresh는 공격 기능이 아니라 device identity를 확인하기 위한 설계입니다.

허용되는 방향:

- local self-signed cert 생성
- customer_id / device_id / agent_version header 설계
- OpenAPI/proto 문서화
- collector가 certificate subject/fingerprint를 확인하는 구조 설계

범위 밖:

- 타인 인증서 탈취
- 인증 우회
- token 탈취
- 실제 운영 인증 시스템 공격

---

## Codex 작업 중 차단이 발생할 때의 처리 원칙

차단이 발생하면 우회 문구를 찾지 않습니다.
대신 작업을 다음처럼 좁힙니다.

1. 대상이 본인 기기 또는 local sample인지 명시합니다.
2. 방어적 탐지/분석 목적임을 명시합니다.
3. 공격 실행, credential, persistence, evasion, unauthorized access가 아님을 명시합니다.
4. 실제 payload 대신 metadata 또는 mock data를 사용합니다.
5. 필요한 경우 문서/설계/테스트 데이터 수준으로 낮춥니다.

이 원칙은 Codex와 팀원이 같은 범위에서 작업하게 하기 위한 기준입니다.
