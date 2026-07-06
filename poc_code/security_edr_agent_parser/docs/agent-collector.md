# Agent Collector 설명

이 문서는 EDR Agent Parser에서 telemetry를 어디서 가져오는지 설명합니다.

## Telemetry란

Telemetry는 클라이언트 PC 안에서 발생한 보안 관찰 데이터입니다.
이 PoC는 파일 내용이나 메시지 본문이 아니라, 분석 가능한 metadata만 사용합니다.

## Windows 수집 흐름

명령:

```powershell
python -m src.run --collect-local
```

코드:

```text
src/local_collector.py
```

수집 흐름:

```text
Windows PC
-> PowerShell command
-> JSON rows
-> EDR event schema
-> detection/report/dashboard
```

## Win32_Process

Windows process 목록은 WMI/CIM의 `Win32_Process`에서 가져옵니다.

실행되는 PowerShell 개념:

```powershell
Get-CimInstance Win32_Process
```

가져오는 주요 field:

| Field | 의미 |
|---|---|
| ProcessId | process id |
| ParentProcessId | parent process id |
| Name | process name |
| ExecutablePath | 실행 파일 경로 |
| CommandLine | 실행 command line |

PoC에서는 이 값을 `process_start` event 형태로 바꿉니다.

## Network Connection

현재 연결된 TCP connection은 `Get-NetTCPConnection`으로 가져옵니다.

```powershell
Get-NetTCPConnection -State Established
```

가져오는 주요 field:

| Field | 의미 |
|---|---|
| LocalAddress / LocalPort | 내 PC의 local socket |
| RemoteAddress / RemotePort | 외부 또는 내부 destination |
| OwningProcess | 어떤 process가 만든 연결인지 |
| State | 연결 상태 |

PoC에서는 이 값을 `network_connection` event로 바꿉니다.

## DNS Cache

DNS는 기본 수집에서 제외되어 있습니다.
방문 흔적이 될 수 있어서 명시 옵션을 켠 경우에만 가져옵니다.

```powershell
python -m src.run --collect-local --include-dns-cache
```

내부적으로는 다음 Windows command를 사용합니다.

```powershell
Get-DnsClientCache
```

가져오는 주요 field:

| Field | 의미 |
|---|---|
| Entry | domain |
| Data | resolved IP 또는 DNS data |
| Type | DNS record type |

PoC에서는 이 값을 `dns_query` event로 바꿉니다.

## 수집하지 않는 것

| 제외 항목 | 수집하지 않는 이유 | 대신 수집할 수 있는 metadata |
|---|---|---|
| message body / chat content | 개인 대화 원문은 EDR 탐지보다 민감정보 노출 위험이 큼 | app name, process, destination domain, byte count, policy match |
| browser password | credential theft와 구분이 어렵고 방어적 PoC에 필요하지 않음 | browser process, suspicious extension/process, known credential-stealer IOC |
| keystroke | keylogging은 공격 행위와 동일하게 보일 수 있음 | process start, parent process, command line |
| clipboard | token/password/개인 대화가 섞일 수 있음 | 필요한 경우 synthetic event의 count/time만 사용 |
| document body | 문서 원문은 회사/개인 정보가 바로 포함될 수 있음 | file path category, extension, size, hash, created/modified time |
| 임의의 HTTPS payload / HTTPS body | 무작위 복호화 payload는 무단 감청처럼 보이고 로그인/결제/메시지가 섞일 수 있음 | SNI/domain, URL path, method, status, content-type, byte count, hash, rule match |

Agent의 기준은 원문 내용 수집이 아니라 보안 판단에 필요한 metadata 수집입니다.

## Agent와 Report 분리

Agent collector의 책임:

- client PC에서 telemetry metadata 수집
- event schema로 변환
- customer/device/version gRPC metadata와 함께 전송 준비

Report의 책임:

- 수집된 event를 분석한 결과를 사람이 읽는 문서로 변환
- alert, incident, SIEM finding, MITRE mapping, response action 표시

Agent는 데이터를 만들고, Report는 분석 결과를 설명합니다.
