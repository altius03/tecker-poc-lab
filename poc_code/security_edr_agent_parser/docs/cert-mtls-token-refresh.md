# 인증서, mTLS, Token Refresh 설계

## 왜 인증서가 필요한가

이 서비스는 사용자 계정이 아니라 기기 단위로 telemetry를 보냅니다.
따라서 매 요청마다 ID/PW를 넣는 방식보다, 기기 인증서로 device identity를 증명하는 mTLS가 더 적합합니다.

## PoC에서 구현한 범위

`src/pipeline.py`는 gzip bundle을 전송할 때 다음 header를 붙입니다.

| Header | 의미 |
|---|---|
| X-EDR-Agent-Version | agent/parser version |
| X-EDR-Customer-Id | 고객사 또는 tenant 구분 |
| X-EDR-Device-Id | client device 구분 |
| X-EDR-Envelope-Version | telemetry schema version |
| Content-Encoding | gzip |

실행 예시:

```powershell
python -m src.run --ship-url https://collector.example.local/v1/telemetry:ingest --customer-id acme-demo --device-id kim-minjun-finance-laptop --agent-version 0.1.0 --client-cert certs\device.crt --client-key certs\device.key
```

## Local cert 생성

테스트 인증서는 Windows에서는 PowerShell script로 생성합니다.

```powershell
.\scripts\create_local_cert.ps1 -CustomerId acme-demo -DeviceId kim-minjun-finance-laptop
```

생성 위치:

```text
certs/device.cer
certs/device.pfx
```

OpenSSL이 있는 환경에서는 PEM cert/key도 생성할 수 있습니다.

```powershell
python scripts\create_local_cert.py --customer-id acme-demo --device-id kim-minjun-finance-laptop
```

생성 위치:

```text
certs/device.crt
certs/device.key
```

주의:

- `--client-cert`, `--client-key` 옵션은 Python `ssl.load_cert_chain()` 기준이라 PEM `.crt/.key`를 기대합니다.
- Windows PowerShell script가 만드는 `.pfx`는 collector 등록, 인증서 저장소 적용, 운영 설계 검증용입니다.
- Windows에서 Python mTLS 전송까지 바로 테스트하려면 PFX를 PEM으로 변환하거나 OpenSSL을 설치해야 합니다.

`certs/`는 `.gitignore`에 포함되어 있으며, private key/PFX는 절대 GitHub에 올리지 않습니다.

## Cert apply

운영 설계에서는 collector가 고객사 CA 또는 등록된 device certificate fingerprint를 신뢰해야 합니다.

PoC 적용 순서:

1. 고객사별 root/intermediate CA 준비
2. device별 client certificate 발급
3. collector에 허용된 customer_id, device_id, cert fingerprint 등록
4. agent가 mTLS로 telemetry bundle 전송
5. collector가 header와 cert subject/fingerprint를 함께 검증

## Token refresh

Token은 사용자 세션용이라기보다 운영 보조 수단으로 둡니다.
기본 신뢰는 mTLS certificate가 담당하고, token은 짧은 만료 시간의 보조 권한으로 사용합니다.

OpenAPI에는 다음 endpoint를 문서화했습니다.

```text
POST /v1/agents/{deviceId}/token:refresh
```

gRPC 설계에서는 다음 RPC가 같은 역할입니다.

```text
RefreshDeviceToken(DeviceTokenRefreshRequest) returns (DeviceTokenRefreshResponse)
```

## REST vs gRPC

PoC는 지금 Python 표준 라이브러리만 쓰기 때문에 REST/gzip shipping까지만 실행됩니다.
운영형 collector로 가면 gRPC + mTLS가 더 자연스럽습니다.

이유:

- device identity를 mTLS로 검증하기 좋음
- streaming telemetry로 확장 가능
- protobuf schema로 event contract를 강제하기 쉬움
- customer/device/version metadata를 metadata header로 관리 가능
