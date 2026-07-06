# Report 기능 설명

Report는 탐지 결과를 사람이 읽을 수 있게 정리하는 부분입니다.

## 담당 코드

```text
src/report_builder.py
```

## 생성되는 결과

CLI를 실행하면 다음 파일이 생성됩니다.

```text
outputs/reports/latest/security_report.html
outputs/reports/latest/security_report.md
```

`outputs/`는 실행 결과이므로 GitHub에는 올리지 않습니다.

## Dashboard에서 보는 방식

Dashboard의 `보고서 열기` 버튼을 누르면 report popup이 뜹니다.

`PDF 저장` 버튼은 브라우저 인쇄 창을 열고, 사용자가 `Save as PDF`를 선택하는 방식입니다.
정적 HTML PoC라서 서버 없이 동작합니다.

## Report에 들어가는 분석 내용

| 섹션 | 설명 |
|---|---|
| Executive Summary | 현재 EDR 상태, 최고 risk, alert 수 |
| Endpoint Risk | 사용자/기기별 risk score |
| Incident Summary | attack chain으로 묶인 사건 |
| Alert Evidence | rule별 근거 |
| MITRE ATT&CK Mapping | 공격 tactic 분류 |
| SIEM Analysis | 반복 가능한 query finding |
| Deep Inspection / L7 Visibility | URL/app action 기반 L7 metadata |
| AI Prediction / Response Plan | 예측 점수와 대응 계획 |
| Pipeline Delivery | gRPC/mTLS bundle, metadata, auth mode |
| Data Quality / DLQ | schema 오류와 수집 품질 |

## Agent와 분리되는 이유

Agent는 client telemetry를 수집하는 역할입니다.
Report는 이미 수집/분석된 결과를 사람이 이해할 수 있게 설명하는 역할입니다.

이 둘을 분리해야 나중에 다음 확장이 쉬워집니다.

- Agent 교체: Windows, macOS, Linux agent를 따로 발전
- Report 교체: HTML, PDF, Slack, Notion export 등으로 확장
- Pipeline 교체: primary gRPC + mTLS collector는 유지하면서 queue/storage/report consumer를 교체
