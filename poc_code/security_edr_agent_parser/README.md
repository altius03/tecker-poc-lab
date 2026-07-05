# Security EDR Agent Parser PoC

상태: PoC parser
작성일: 2026-07-06

## 목적

Mac/Windows endpoint의 process와 TCP socket metadata를 공통 dashboard payload로 정규화하고, 간단한 rule engine으로 alert를 생성한다.

이 코드는 Mini XDR/SIEM 프로젝트의 Local Agent 확장 PoC다. 실제 EDR 제품, packet capture, TLS 복호화, 차단/격리 기능이 아니다.

## 포함 항목

| 파일 | 역할 |
| --- | --- |
| `mac_agent.py` | macOS `ps`/`lsof` metadata parser와 dashboard renderer |
| `collect_mac_telemetry.sh` | macOS 실행 wrapper |
| `windows_agent.py` | Windows PowerShell collector, parser, rule engine, dashboard renderer |
| `run_windows_agent.ps1` | Windows 실행 wrapper |
| `dashboard_template.html` | 정적 Falcon-style dashboard template |
| `samples/mock_windows_powershell.json` | Windows parser 검증용 fixture |
| `tests/test_windows_agent.py` | Windows mock payload contract test |

## 수집 경계

수집하는 것:

- process name, PID, PPID
- CPU/memory metric이 가능한 경우의 process metric
- TCP `LISTEN`/`ESTABLISHED` socket
- local/remote IP, port, TCP state
- OS/build metadata

수집하지 않는 것:

- command-line arguments
- environment variables
- packet payload
- TLS contents
- browser history
- file contents
- registry dump
- 실제 사용자명
- 토큰, 비밀번호, API key

## macOS 실행

```bash
zsh poc_code/security_edr_agent_parser/collect_mac_telemetry.sh
```

생성 파일은 `.gitignore`로 제외된다.

- `poc_code/security_edr_agent_parser/data/latest_mac_telemetry.json`
- `poc_code/security_edr_agent_parser/dashboard.html`

## Windows 실제 실행

Windows PowerShell에서 실행한다.

```powershell
cd C:\path\to\tecker-poc-lab\poc_code\security_edr_agent_parser
powershell -ExecutionPolicy Bypass -File .\run_windows_agent.ps1 -RenderDashboard
```

실제 실행 결과는 `source_real=true`, `test_mode=false`로 생성된다.

## mock 검증

macOS/Linux에서도 Windows parser를 fixture로 검증할 수 있다.

```bash
python3 poc_code/security_edr_agent_parser/windows_agent.py --mock --render-dashboard
python3 poc_code/security_edr_agent_parser/tests/test_windows_agent.py
```

mock 실행 결과는 `source_real=false`, `test_mode=true`다.

## Rule Engine

| Rule | 설명 |
| --- | --- |
| `NET-001` / `WIN-NET-001` | loopback 외부 또는 wildcard `LISTEN` socket |
| `NET-002` / `WIN-NET-002` | common port가 아닌 external remote port |
| `NET-003` / `WIN-NET-003` | 단일 process remote fan-out |
| `WIN-PROC-001` | script interpreter의 external network activity |
| `PROC-001` / `WIN-PROC-002` | 높은 CPU 또는 memory 사용 후보 |
