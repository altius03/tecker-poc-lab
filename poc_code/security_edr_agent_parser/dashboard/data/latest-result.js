window.SIEM_RESULT = {
  "status": "success",
  "poc_name": "security_edr_agent_parser",
  "project": "lightweight_edr_siem",
  "generated_at": "2026-07-06T11:59:19",
  "input": {
    "source": "event_file",
    "path": "samples/default_events.json",
    "raw_event_count": 60,
    "generated_event_count": 38
  },
  "summary": {
    "input_event_count": 60,
    "valid_event_count": 58,
    "dlq_event_count": 2,
    "privacy_mask_action_count": 4,
    "alert_count": 29,
    "incident_count": 1,
    "critical_endpoint_count": 2,
    "highest_risk_score": 100,
    "flow_event_count": 1,
    "l7_event_count": 2,
    "decryption_event_count": 1,
    "response_action_count": 29,
    "ai_prediction_count": 3,
    "predicted_high_or_critical_count": 2
  },
  "signature_db": {
    "version": "2026.07.poc"
  },
  "rules_run": [
    {
      "rule_id": "R001",
      "name": "known malicious domain access",
      "mitre": [
        "Initial Access"
      ],
      "base_score": 34
    },
    {
      "rule_id": "R002",
      "name": "suspicious executable downloaded from browser",
      "mitre": [
        "Initial Access"
      ],
      "base_score": 28
    },
    {
      "rule_id": "R003",
      "name": "unsigned executable started from Downloads",
      "mitre": [
        "Execution"
      ],
      "base_score": 30
    },
    {
      "rule_id": "R004",
      "name": "periodic external connection",
      "mitre": [
        "Command and Control"
      ],
      "base_score": 36
    },
    {
      "rule_id": "R005",
      "name": "large outbound transfer",
      "mitre": [
        "Exfiltration"
      ],
      "base_score": 35
    },
    {
      "rule_id": "R006",
      "name": "rare ASN connection outside work hours",
      "mitre": [
        "Command and Control"
      ],
      "base_score": 22
    },
    {
      "rule_id": "R007",
      "name": "shell process creates network connection",
      "mitre": [
        "Execution",
        "Command and Control"
      ],
      "base_score": 26
    },
    {
      "rule_id": "R008",
      "name": "VPN tunnel plus abnormal transfer",
      "mitre": [
        "Exfiltration"
      ],
      "base_score": 32
    },
    {
      "rule_id": "R009",
      "name": "decrypted L7 malicious URL access",
      "mitre": [
        "Initial Access",
        "Command and Control"
      ],
      "base_score": 38
    },
    {
      "rule_id": "R010",
      "name": "risky application action with malicious URL",
      "mitre": [
        "Collection",
        "Exfiltration"
      ],
      "base_score": 34
    },
    {
      "rule_id": "R011",
      "name": "known malware hash signature match",
      "mitre": [
        "Execution",
        "Defense Evasion"
      ],
      "base_score": 42
    },
    {
      "rule_id": "R012",
      "name": "response action generated for high-risk detection",
      "mitre": [
        "Impact"
      ],
      "base_score": 20
    },
    {
      "rule_id": "R013",
      "name": "AI predicted high-risk host trajectory",
      "mitre": [
        "Command and Control",
        "Exfiltration"
      ],
      "base_score": 33
    }
  ],
  "events": [
    {
      "event_id": "benign-choi-haeun-001",
      "event_time": "2026-07-05T09:00:00+09:00",
      "host_id": "최하은-개발팀-Workstation",
      "event_type": "network_connection",
      "process_name": "chrome.exe",
      "domain": "docs.company.test",
      "dst_ip": "10.20.0.10",
      "dst_port": 443,
      "bytes_out": 22000
    },
    {
      "event_id": "benign-choi-haeun-002",
      "event_time": "2026-07-05T09:01:00+09:00",
      "host_id": "최하은-개발팀-Workstation",
      "event_type": "network_connection",
      "process_name": "chrome.exe",
      "domain": "mail.company.test",
      "dst_ip": "10.20.0.11",
      "dst_port": 443,
      "bytes_out": 22000
    },
    {
      "event_id": "benign-choi-haeun-003",
      "event_time": "2026-07-05T09:02:00+09:00",
      "host_id": "최하은-개발팀-Workstation",
      "event_type": "network_connection",
      "process_name": "chrome.exe",
      "domain": "calendar.company.test",
      "dst_ip": "10.20.0.12",
      "dst_port": 443,
      "bytes_out": 22000
    },
    {
      "event_id": "benign-choi-haeun-004",
      "event_time": "2026-07-05T09:03:00+09:00",
      "host_id": "최하은-개발팀-Workstation",
      "event_type": "network_connection",
      "process_name": "chrome.exe",
      "domain": "repo.company.test",
      "dst_ip": "10.20.0.13",
      "dst_port": 443,
      "bytes_out": 22000
    },
    {
      "event_id": "benign-choi-haeun-005",
      "event_time": "2026-07-05T09:04:00+09:00",
      "host_id": "최하은-개발팀-Workstation",
      "event_type": "network_connection",
      "process_name": "chrome.exe",
      "domain": "docs.company.test",
      "dst_ip": "10.20.0.10",
      "dst_port": 443,
      "bytes_out": 22000
    },
    {
      "event_id": "benign-choi-haeun-006",
      "event_time": "2026-07-05T09:05:00+09:00",
      "host_id": "최하은-개발팀-Workstation",
      "event_type": "network_connection",
      "process_name": "chrome.exe",
      "domain": "mail.company.test",
      "dst_ip": "10.20.0.11",
      "dst_port": 443,
      "bytes_out": 22000
    },
    {
      "event_id": "benign-choi-haeun-007",
      "event_time": "2026-07-05T09:06:00+09:00",
      "host_id": "최하은-개발팀-Workstation",
      "event_type": "network_connection",
      "process_name": "chrome.exe",
      "domain": "calendar.company.test",
      "dst_ip": "10.20.0.12",
      "dst_port": 443,
      "bytes_out": 22000
    },
    {
      "event_id": "benign-choi-haeun-008",
      "event_time": "2026-07-05T09:07:00+09:00",
      "host_id": "최하은-개발팀-Workstation",
      "event_type": "network_connection",
      "process_name": "chrome.exe",
      "domain": "repo.company.test",
      "dst_ip": "10.20.0.13",
      "dst_port": 443,
      "bytes_out": 22000
    },
    {
      "event_id": "benign-choi-haeun-009",
      "event_time": "2026-07-05T09:08:00+09:00",
      "host_id": "최하은-개발팀-Workstation",
      "event_type": "network_connection",
      "process_name": "chrome.exe",
      "domain": "docs.company.test",
      "dst_ip": "10.20.0.10",
      "dst_port": 443,
      "bytes_out": 22000
    },
    {
      "event_id": "benign-choi-haeun-010",
      "event_time": "2026-07-05T09:09:00+09:00",
      "host_id": "최하은-개발팀-Workstation",
      "event_type": "network_connection",
      "process_name": "chrome.exe",
      "domain": "mail.company.test",
      "dst_ip": "10.20.0.11",
      "dst_port": 443,
      "bytes_out": 22000
    },
    {
      "event_id": "benign-choi-haeun-011",
      "event_time": "2026-07-05T09:10:00+09:00",
      "host_id": "최하은-개발팀-Workstation",
      "event_type": "network_connection",
      "process_name": "chrome.exe",
      "domain": "calendar.company.test",
      "dst_ip": "10.20.0.12",
      "dst_port": 443,
      "bytes_out": 22000
    },
    {
      "event_id": "benign-choi-haeun-012",
      "event_time": "2026-07-05T09:11:00+09:00",
      "host_id": "최하은-개발팀-Workstation",
      "event_type": "network_connection",
      "process_name": "chrome.exe",
      "domain": "repo.company.test",
      "dst_ip": "10.20.0.13",
      "dst_port": 443,
      "bytes_out": 22000
    },
    {
      "event_id": "benign-choi-haeun-013",
      "event_time": "2026-07-05T09:12:00+09:00",
      "host_id": "최하은-개발팀-Workstation",
      "event_type": "network_connection",
      "process_name": "chrome.exe",
      "domain": "docs.company.test",
      "dst_ip": "10.20.0.10",
      "dst_port": 443,
      "bytes_out": 22000
    },
    {
      "event_id": "benign-choi-haeun-014",
      "event_time": "2026-07-05T09:13:00+09:00",
      "host_id": "최하은-개발팀-Workstation",
      "event_type": "network_connection",
      "process_name": "chrome.exe",
      "domain": "mail.company.test",
      "dst_ip": "10.20.0.11",
      "dst_port": 443,
      "bytes_out": 22000
    },
    {
      "event_id": "benign-choi-haeun-015",
      "event_time": "2026-07-05T09:14:00+09:00",
      "host_id": "최하은-개발팀-Workstation",
      "event_type": "network_connection",
      "process_name": "chrome.exe",
      "domain": "calendar.company.test",
      "dst_ip": "10.20.0.12",
      "dst_port": 443,
      "bytes_out": 22000
    },
    {
      "event_id": "benign-choi-haeun-016",
      "event_time": "2026-07-05T09:15:00+09:00",
      "host_id": "최하은-개발팀-Workstation",
      "event_type": "network_connection",
      "process_name": "chrome.exe",
      "domain": "repo.company.test",
      "dst_ip": "10.20.0.13",
      "dst_port": 443,
      "bytes_out": 22000
    },
    {
      "event_id": "benign-choi-haeun-017",
      "event_time": "2026-07-05T09:16:00+09:00",
      "host_id": "최하은-개발팀-Workstation",
      "event_type": "network_connection",
      "process_name": "chrome.exe",
      "domain": "docs.company.test",
      "dst_ip": "10.20.0.10",
      "dst_port": 443,
      "bytes_out": 22000
    },
    {
      "event_id": "benign-choi-haeun-018",
      "event_time": "2026-07-05T09:17:00+09:00",
      "host_id": "최하은-개발팀-Workstation",
      "event_type": "network_connection",
      "process_name": "chrome.exe",
      "domain": "mail.company.test",
      "dst_ip": "10.20.0.11",
      "dst_port": 443,
      "bytes_out": 22000
    },
    {
      "event_id": "benign-choi-haeun-019",
      "event_time": "2026-07-05T09:18:00+09:00",
      "host_id": "최하은-개발팀-Workstation",
      "event_type": "network_connection",
      "process_name": "chrome.exe",
      "domain": "calendar.company.test",
      "dst_ip": "10.20.0.12",
      "dst_port": 443,
      "bytes_out": 22000
    },
    {
      "event_id": "benign-choi-haeun-020",
      "event_time": "2026-07-05T09:19:00+09:00",
      "host_id": "최하은-개발팀-Workstation",
      "event_type": "network_connection",
      "process_name": "chrome.exe",
      "domain": "repo.company.test",
      "dst_ip": "10.20.0.13",
      "dst_port": 443,
      "bytes_out": 22000
    },
    {
      "event_id": "benign-choi-haeun-021",
      "event_time": "2026-07-05T09:20:00+09:00",
      "host_id": "최하은-개발팀-Workstation",
      "event_type": "network_connection",
      "process_name": "chrome.exe",
      "domain": "docs.company.test",
      "dst_ip": "10.20.0.10",
      "dst_port": 443,
      "bytes_out": 22000
    },
    {
      "event_id": "benign-choi-haeun-022",
      "event_time": "2026-07-05T09:21:00+09:00",
      "host_id": "최하은-개발팀-Workstation",
      "event_type": "network_connection",
      "process_name": "chrome.exe",
      "domain": "mail.company.test",
      "dst_ip": "10.20.0.11",
      "dst_port": 443,
      "bytes_out": 22000
    },
    {
      "event_id": "benign-choi-haeun-023",
      "event_time": "2026-07-05T09:22:00+09:00",
      "host_id": "최하은-개발팀-Workstation",
      "event_type": "network_connection",
      "process_name": "chrome.exe",
      "domain": "calendar.company.test",
      "dst_ip": "10.20.0.12",
      "dst_port": 443,
      "bytes_out": 22000
    },
    {
      "event_id": "benign-choi-haeun-024",
      "event_time": "2026-07-05T09:23:00+09:00",
      "host_id": "최하은-개발팀-Workstation",
      "event_type": "network_connection",
      "process_name": "chrome.exe",
      "domain": "repo.company.test",
      "dst_ip": "10.20.0.13",
      "dst_port": 443,
      "bytes_out": 22000
    },
    {
      "event_id": "benign-choi-haeun-025",
      "event_time": "2026-07-05T09:24:00+09:00",
      "host_id": "최하은-개발팀-Workstation",
      "event_type": "network_connection",
      "process_name": "chrome.exe",
      "domain": "docs.company.test",
      "dst_ip": "10.20.0.10",
      "dst_port": 443,
      "bytes_out": 22000
    },
    {
      "event_id": "benign-choi-haeun-026",
      "event_time": "2026-07-05T09:25:00+09:00",
      "host_id": "최하은-개발팀-Workstation",
      "event_type": "network_connection",
      "process_name": "chrome.exe",
      "domain": "mail.company.test",
      "dst_ip": "10.20.0.11",
      "dst_port": 443,
      "bytes_out": 22000
    },
    {
      "event_id": "benign-choi-haeun-027",
      "event_time": "2026-07-05T09:26:00+09:00",
      "host_id": "최하은-개발팀-Workstation",
      "event_type": "network_connection",
      "process_name": "chrome.exe",
      "domain": "calendar.company.test",
      "dst_ip": "10.20.0.12",
      "dst_port": 443,
      "bytes_out": 22000
    },
    {
      "event_id": "benign-choi-haeun-028",
      "event_time": "2026-07-05T09:27:00+09:00",
      "host_id": "최하은-개발팀-Workstation",
      "event_type": "network_connection",
      "process_name": "chrome.exe",
      "domain": "repo.company.test",
      "dst_ip": "10.20.0.13",
      "dst_port": 443,
      "bytes_out": 22000
    },
    {
      "event_id": "benign-choi-haeun-029",
      "event_time": "2026-07-05T09:28:00+09:00",
      "host_id": "최하은-개발팀-Workstation",
      "event_type": "network_connection",
      "process_name": "chrome.exe",
      "domain": "docs.company.test",
      "dst_ip": "10.20.0.10",
      "dst_port": 443,
      "bytes_out": 22000
    },
    {
      "event_id": "benign-choi-haeun-030",
      "event_time": "2026-07-05T09:29:00+09:00",
      "host_id": "최하은-개발팀-Workstation",
      "event_type": "network_connection",
      "process_name": "chrome.exe",
      "domain": "mail.company.test",
      "dst_ip": "10.20.0.11",
      "dst_port": 443,
      "bytes_out": 22000
    },
    {
      "event_id": "benign-choi-haeun-031",
      "event_time": "2026-07-05T09:30:00+09:00",
      "host_id": "최하은-개발팀-Workstation",
      "event_type": "network_connection",
      "process_name": "chrome.exe",
      "domain": "calendar.company.test",
      "dst_ip": "10.20.0.12",
      "dst_port": 443,
      "bytes_out": 22000
    },
    {
      "event_id": "benign-choi-haeun-032",
      "event_time": "2026-07-05T09:31:00+09:00",
      "host_id": "최하은-개발팀-Workstation",
      "event_type": "network_connection",
      "process_name": "chrome.exe",
      "domain": "repo.company.test",
      "dst_ip": "10.20.0.13",
      "dst_port": 443,
      "bytes_out": 22000
    },
    {
      "event_id": "benign-choi-haeun-033",
      "event_time": "2026-07-05T09:32:00+09:00",
      "host_id": "최하은-개발팀-Workstation",
      "event_type": "network_connection",
      "process_name": "chrome.exe",
      "domain": "docs.company.test",
      "dst_ip": "10.20.0.10",
      "dst_port": 443,
      "bytes_out": 22000
    },
    {
      "event_id": "benign-choi-haeun-034",
      "event_time": "2026-07-05T09:33:00+09:00",
      "host_id": "최하은-개발팀-Workstation",
      "event_type": "network_connection",
      "process_name": "chrome.exe",
      "domain": "mail.company.test",
      "dst_ip": "10.20.0.11",
      "dst_port": 443,
      "bytes_out": 22000
    },
    {
      "event_id": "benign-choi-haeun-035",
      "event_time": "2026-07-05T09:34:00+09:00",
      "host_id": "최하은-개발팀-Workstation",
      "event_type": "network_connection",
      "process_name": "chrome.exe",
      "domain": "calendar.company.test",
      "dst_ip": "10.20.0.12",
      "dst_port": 443,
      "bytes_out": 22000
    },
    {
      "event_id": "benign-choi-haeun-036",
      "event_time": "2026-07-05T09:35:00+09:00",
      "host_id": "최하은-개발팀-Workstation",
      "event_type": "network_connection",
      "process_name": "chrome.exe",
      "domain": "repo.company.test",
      "dst_ip": "10.20.0.13",
      "dst_port": 443,
      "bytes_out": 22000
    },
    {
      "event_id": "benign-choi-haeun-037",
      "event_time": "2026-07-05T09:36:00+09:00",
      "host_id": "최하은-개발팀-Workstation",
      "event_type": "network_connection",
      "process_name": "chrome.exe",
      "domain": "docs.company.test",
      "dst_ip": "10.20.0.10",
      "dst_port": 443,
      "bytes_out": 22000
    },
    {
      "event_id": "benign-choi-haeun-038",
      "event_time": "2026-07-05T09:37:00+09:00",
      "host_id": "최하은-개발팀-Workstation",
      "event_type": "network_connection",
      "process_name": "chrome.exe",
      "domain": "mail.company.test",
      "dst_ip": "10.20.0.11",
      "dst_port": 443,
      "bytes_out": 22000
    },
    {
      "event_id": "evt-001",
      "event_time": "2026-07-05T10:00:00+09:00",
      "host_id": "김민준-재무팀-Laptop",
      "event_type": "process_start",
      "process_name": "chrome.exe",
      "domain": "",
      "privacy_masked_fields": [
        "user_name"
      ]
    },
    {
      "event_id": "evt-002",
      "event_time": "2026-07-05T10:00:10+09:00",
      "host_id": "김민준-재무팀-Laptop",
      "event_type": "dns_query",
      "process_name": "chrome.exe",
      "domain": "malware-drop.example"
    },
    {
      "event_id": "evt-018",
      "event_time": "2026-07-05T10:00:11+09:00",
      "host_id": "김민준-재무팀-Laptop",
      "event_type": "decryption_event",
      "process_name": "chrome.exe",
      "domain": "malware-drop.example",
      "dst_port": 443
    },
    {
      "event_id": "evt-003",
      "event_time": "2026-07-05T10:00:12+09:00",
      "host_id": "김민준-재무팀-Laptop",
      "event_type": "network_connection",
      "process_name": "chrome.exe",
      "domain": "malware-drop.example",
      "dst_ip": "203.0.113.77",
      "dst_port": 443,
      "bytes_out": 42000
    },
    {
      "event_id": "evt-019",
      "event_time": "2026-07-05T10:00:13+09:00",
      "host_id": "김민준-재무팀-Laptop",
      "event_type": "http_request",
      "process_name": "chrome.exe",
      "domain": "malware-drop.example",
      "dst_ip": "203.0.113.77",
      "dst_port": 443,
      "method": "GET",
      "url": "https://malware-drop.example/payload/invoice.exe",
      "app_name": "browser",
      "decrypted": true,
      "privacy_masked_fields": [
        "http_body"
      ]
    },
    {
      "event_id": "evt-004",
      "event_time": "2026-07-05T10:00:20+09:00",
      "host_id": "김민준-재무팀-Laptop",
      "event_type": "file_download",
      "process_name": "chrome.exe",
      "domain": "malware-drop.example"
    },
    {
      "event_id": "evt-005",
      "event_time": "2026-07-05T10:01:10+09:00",
      "host_id": "김민준-재무팀-Laptop",
      "event_type": "process_start",
      "process_name": "invoice.exe",
      "domain": ""
    },
    {
      "event_id": "evt-006",
      "event_time": "2026-07-05T10:01:40+09:00",
      "host_id": "김민준-재무팀-Laptop",
      "event_type": "dns_query",
      "process_name": "invoice.exe",
      "domain": "c2.badbeacon.example"
    },
    {
      "event_id": "evt-007",
      "event_time": "2026-07-05T10:02:00+09:00",
      "host_id": "김민준-재무팀-Laptop",
      "event_type": "network_connection",
      "process_name": "invoice.exe",
      "domain": "c2.badbeacon.example",
      "dst_ip": "203.0.113.77",
      "dst_port": 443,
      "bytes_out": 3200
    },
    {
      "event_id": "evt-008",
      "event_time": "2026-07-05T10:02:30+09:00",
      "host_id": "김민준-재무팀-Laptop",
      "event_type": "network_connection",
      "process_name": "invoice.exe",
      "domain": "c2.badbeacon.example",
      "dst_ip": "203.0.113.77",
      "dst_port": 443,
      "bytes_out": 3400
    },
    {
      "event_id": "evt-009",
      "event_time": "2026-07-05T10:03:00+09:00",
      "host_id": "김민준-재무팀-Laptop",
      "event_type": "network_connection",
      "process_name": "invoice.exe",
      "domain": "c2.badbeacon.example",
      "dst_ip": "203.0.113.77",
      "dst_port": 443,
      "bytes_out": 3300
    },
    {
      "event_id": "evt-010",
      "event_time": "2026-07-05T10:03:30+09:00",
      "host_id": "김민준-재무팀-Laptop",
      "event_type": "network_connection",
      "process_name": "invoice.exe",
      "domain": "c2.badbeacon.example",
      "dst_ip": "203.0.113.77",
      "dst_port": 443,
      "bytes_out": 3500
    },
    {
      "event_id": "evt-011",
      "event_time": "2026-07-05T10:04:00+09:00",
      "host_id": "김민준-재무팀-Laptop",
      "event_type": "network_connection",
      "process_name": "invoice.exe",
      "domain": "c2.badbeacon.example",
      "dst_ip": "203.0.113.77",
      "dst_port": 443,
      "bytes_out": 118000000
    },
    {
      "event_id": "evt-012",
      "event_time": "2026-07-05T10:04:08+09:00",
      "host_id": "김민준-재무팀-Laptop",
      "event_type": "autorun_entry",
      "process_name": "invoice.exe",
      "domain": ""
    },
    {
      "event_id": "evt-020",
      "event_time": "2026-07-05T10:05:00+09:00",
      "host_id": "김민준-재무팀-Laptop",
      "event_type": "application_action",
      "process_name": "KakaoTalk",
      "domain": "evil-kakao-link.example",
      "url": "https://evil-kakao-link.example/collect",
      "app_name": "KakaoTalk",
      "app_action": "message_send",
      "decrypted": true,
      "privacy_masked_fields": [
        "message_content"
      ]
    },
    {
      "event_id": "evt-016",
      "event_time": "2026-07-05T13:45:00+09:00",
      "host_id": "이도윤-IT관리자-PC",
      "event_type": "process_start",
      "process_name": "powershell.exe",
      "domain": ""
    },
    {
      "event_id": "evt-017",
      "event_time": "2026-07-05T13:46:00+09:00",
      "host_id": "이도윤-IT관리자-PC",
      "event_type": "network_connection",
      "process_name": "powershell.exe",
      "domain": "admin-tools.example",
      "dst_ip": "198.51.100.9",
      "dst_port": 443,
      "bytes_out": 56000
    },
    {
      "event_id": "evt-013",
      "event_time": "2026-07-05T22:10:00+09:00",
      "host_id": "박서연-영업팀-VPN",
      "event_type": "vpn_tunnel",
      "process_name": "vpnclient.exe",
      "domain": "",
      "dst_ip": "198.51.100.10",
      "dst_port": 443
    },
    {
      "event_id": "evt-014",
      "event_time": "2026-07-05T22:24:00+09:00",
      "host_id": "박서연-영업팀-VPN",
      "event_type": "network_connection",
      "process_name": "syncclient.exe",
      "domain": "rare-storage.example",
      "dst_ip": "198.51.100.66",
      "dst_port": 443,
      "bytes_out": 92000000
    },
    {
      "event_id": "evt-015",
      "event_time": "2026-07-05T22:26:00+09:00",
      "host_id": "박서연-영업팀-VPN",
      "event_type": "flow_summary",
      "process_name": "syncclient.exe",
      "domain": "rare-storage.example",
      "dst_ip": "198.51.100.66",
      "dst_port": 443,
      "bytes_out": 74000000
    }
  ],
  "alerts": [
    {
      "rule_id": "R001",
      "rule_name": "known malicious domain access",
      "host_id": "김민준-재무팀-Laptop",
      "event_ids": [
        "evt-002"
      ],
      "event_time": "2026-07-05T10:00:10+09:00",
      "title": "Known malicious destination observed: malware-drop.example",
      "risk_score": 34,
      "mitre_mapping": [
        "Initial Access"
      ],
      "evidence": [
        "destination matched signature set: malware-drop.example",
        "source event type: dns_query"
      ],
      "decision": "needs_security_review",
      "alert_id": "alert-001",
      "severity": "suspicious"
    },
    {
      "rule_id": "R001",
      "rule_name": "known malicious domain access",
      "host_id": "김민준-재무팀-Laptop",
      "event_ids": [
        "evt-018"
      ],
      "event_time": "2026-07-05T10:00:11+09:00",
      "title": "Known malicious destination observed: malware-drop.example",
      "risk_score": 34,
      "mitre_mapping": [
        "Initial Access"
      ],
      "evidence": [
        "destination matched signature set: malware-drop.example",
        "source event type: decryption_event"
      ],
      "decision": "needs_security_review",
      "alert_id": "alert-002",
      "severity": "suspicious"
    },
    {
      "rule_id": "R001",
      "rule_name": "known malicious domain access",
      "host_id": "김민준-재무팀-Laptop",
      "event_ids": [
        "evt-003"
      ],
      "event_time": "2026-07-05T10:00:12+09:00",
      "title": "Known malicious destination observed: malware-drop.example",
      "risk_score": 34,
      "mitre_mapping": [
        "Initial Access"
      ],
      "evidence": [
        "destination matched signature set: malware-drop.example",
        "source event type: network_connection"
      ],
      "decision": "needs_security_review",
      "alert_id": "alert-003",
      "severity": "suspicious"
    },
    {
      "rule_id": "R001",
      "rule_name": "known malicious domain access",
      "host_id": "김민준-재무팀-Laptop",
      "event_ids": [
        "evt-019"
      ],
      "event_time": "2026-07-05T10:00:13+09:00",
      "title": "Known malicious destination observed: malware-drop.example",
      "risk_score": 34,
      "mitre_mapping": [
        "Initial Access"
      ],
      "evidence": [
        "destination matched signature set: malware-drop.example",
        "source event type: http_request"
      ],
      "decision": "needs_security_review",
      "alert_id": "alert-004",
      "severity": "suspicious"
    },
    {
      "rule_id": "R009",
      "rule_name": "decrypted L7 malicious URL access",
      "host_id": "김민준-재무팀-Laptop",
      "event_ids": [
        "evt-019"
      ],
      "event_time": "2026-07-05T10:00:13+09:00",
      "title": "Decrypted L7 request matched policy: https://malware-drop.example/payload/invoice.exe",
      "risk_score": 38,
      "mitre_mapping": [
        "Initial Access",
        "Command and Control"
      ],
      "evidence": [
        "url=https://malware-drop.example/payload/invoice.exe",
        "domain=malware-drop.example",
        "url_category=malware",
        "decrypted=True"
      ],
      "decision": "needs_security_review",
      "alert_id": "alert-005",
      "severity": "suspicious"
    },
    {
      "rule_id": "R001",
      "rule_name": "known malicious domain access",
      "host_id": "김민준-재무팀-Laptop",
      "event_ids": [
        "evt-004"
      ],
      "event_time": "2026-07-05T10:00:20+09:00",
      "title": "Known malicious destination observed: malware-drop.example",
      "risk_score": 34,
      "mitre_mapping": [
        "Initial Access"
      ],
      "evidence": [
        "destination matched signature set: malware-drop.example",
        "source event type: file_download"
      ],
      "decision": "needs_security_review",
      "alert_id": "alert-006",
      "severity": "suspicious"
    },
    {
      "rule_id": "R002",
      "rule_name": "suspicious executable downloaded from browser",
      "host_id": "김민준-재무팀-Laptop",
      "event_ids": [
        "evt-004"
      ],
      "event_time": "2026-07-05T10:00:20+09:00",
      "title": "Executable download needs review: invoice.exe",
      "risk_score": 28,
      "mitre_mapping": [
        "Initial Access"
      ],
      "evidence": [
        "downloaded file has executable extension",
        "source_domain=malware-drop.example",
        "browser initiated the download"
      ],
      "decision": "needs_review",
      "alert_id": "alert-007",
      "severity": "info"
    },
    {
      "rule_id": "R011",
      "rule_name": "known malware hash signature match",
      "host_id": "김민준-재무팀-Laptop",
      "event_ids": [
        "evt-004"
      ],
      "event_time": "2026-07-05T10:00:20+09:00",
      "title": "Known malware hash observed: badbeef00000...",
      "risk_score": 42,
      "mitre_mapping": [
        "Execution",
        "Defense Evasion"
      ],
      "evidence": [
        "hash_sha256=badbeef0000000000000000000000000000000000000000000000000000000001",
        "event_type=file_download",
        "process_name=chrome.exe"
      ],
      "decision": "needs_security_review",
      "alert_id": "alert-008",
      "severity": "suspicious"
    },
    {
      "rule_id": "R003",
      "rule_name": "unsigned executable started from Downloads",
      "host_id": "김민준-재무팀-Laptop",
      "event_ids": [
        "evt-005"
      ],
      "event_time": "2026-07-05T10:01:10+09:00",
      "title": "Unsigned executable started: invoice.exe",
      "risk_score": 30,
      "mitre_mapping": [
        "Execution"
      ],
      "evidence": [
        "process is unsigned",
        "process path is under Downloads",
        "parent_process=chrome.exe"
      ],
      "decision": "needs_security_review",
      "alert_id": "alert-009",
      "severity": "suspicious"
    },
    {
      "rule_id": "R011",
      "rule_name": "known malware hash signature match",
      "host_id": "김민준-재무팀-Laptop",
      "event_ids": [
        "evt-005"
      ],
      "event_time": "2026-07-05T10:01:10+09:00",
      "title": "Known malware hash observed: badbeef00000...",
      "risk_score": 42,
      "mitre_mapping": [
        "Execution",
        "Defense Evasion"
      ],
      "evidence": [
        "hash_sha256=badbeef0000000000000000000000000000000000000000000000000000000001",
        "event_type=process_start",
        "process_name=invoice.exe"
      ],
      "decision": "needs_security_review",
      "alert_id": "alert-010",
      "severity": "suspicious"
    },
    {
      "rule_id": "R001",
      "rule_name": "known malicious domain access",
      "host_id": "김민준-재무팀-Laptop",
      "event_ids": [
        "evt-006"
      ],
      "event_time": "2026-07-05T10:01:40+09:00",
      "title": "Known malicious destination observed: c2.badbeacon.example",
      "risk_score": 34,
      "mitre_mapping": [
        "Initial Access"
      ],
      "evidence": [
        "destination matched signature set: c2.badbeacon.example",
        "source event type: dns_query"
      ],
      "decision": "needs_security_review",
      "alert_id": "alert-011",
      "severity": "suspicious"
    },
    {
      "rule_id": "R001",
      "rule_name": "known malicious domain access",
      "host_id": "김민준-재무팀-Laptop",
      "event_ids": [
        "evt-007"
      ],
      "event_time": "2026-07-05T10:02:00+09:00",
      "title": "Known malicious destination observed: c2.badbeacon.example",
      "risk_score": 34,
      "mitre_mapping": [
        "Initial Access"
      ],
      "evidence": [
        "destination matched signature set: c2.badbeacon.example",
        "source event type: network_connection"
      ],
      "decision": "needs_security_review",
      "alert_id": "alert-012",
      "severity": "suspicious"
    },
    {
      "rule_id": "R001",
      "rule_name": "known malicious domain access",
      "host_id": "김민준-재무팀-Laptop",
      "event_ids": [
        "evt-008"
      ],
      "event_time": "2026-07-05T10:02:30+09:00",
      "title": "Known malicious destination observed: c2.badbeacon.example",
      "risk_score": 34,
      "mitre_mapping": [
        "Initial Access"
      ],
      "evidence": [
        "destination matched signature set: c2.badbeacon.example",
        "source event type: network_connection"
      ],
      "decision": "needs_security_review",
      "alert_id": "alert-013",
      "severity": "suspicious"
    },
    {
      "rule_id": "R001",
      "rule_name": "known malicious domain access",
      "host_id": "김민준-재무팀-Laptop",
      "event_ids": [
        "evt-009"
      ],
      "event_time": "2026-07-05T10:03:00+09:00",
      "title": "Known malicious destination observed: c2.badbeacon.example",
      "risk_score": 34,
      "mitre_mapping": [
        "Initial Access"
      ],
      "evidence": [
        "destination matched signature set: c2.badbeacon.example",
        "source event type: network_connection"
      ],
      "decision": "needs_security_review",
      "alert_id": "alert-014",
      "severity": "suspicious"
    },
    {
      "rule_id": "R001",
      "rule_name": "known malicious domain access",
      "host_id": "김민준-재무팀-Laptop",
      "event_ids": [
        "evt-010"
      ],
      "event_time": "2026-07-05T10:03:30+09:00",
      "title": "Known malicious destination observed: c2.badbeacon.example",
      "risk_score": 34,
      "mitre_mapping": [
        "Initial Access"
      ],
      "evidence": [
        "destination matched signature set: c2.badbeacon.example",
        "source event type: network_connection"
      ],
      "decision": "needs_security_review",
      "alert_id": "alert-015",
      "severity": "suspicious"
    },
    {
      "rule_id": "R001",
      "rule_name": "known malicious domain access",
      "host_id": "김민준-재무팀-Laptop",
      "event_ids": [
        "evt-011"
      ],
      "event_time": "2026-07-05T10:04:00+09:00",
      "title": "Known malicious destination observed: c2.badbeacon.example",
      "risk_score": 34,
      "mitre_mapping": [
        "Initial Access"
      ],
      "evidence": [
        "destination matched signature set: c2.badbeacon.example",
        "source event type: network_connection"
      ],
      "decision": "needs_security_review",
      "alert_id": "alert-016",
      "severity": "suspicious"
    },
    {
      "rule_id": "R005",
      "rule_name": "large outbound transfer",
      "host_id": "김민준-재무팀-Laptop",
      "event_ids": [
        "evt-011"
      ],
      "event_time": "2026-07-05T10:04:00+09:00",
      "title": "Large outbound transfer: 118,000,000 bytes",
      "risk_score": 35,
      "mitre_mapping": [
        "Exfiltration"
      ],
      "evidence": [
        "bytes_out=118000000",
        "process_name=invoice.exe",
        "destination=c2.badbeacon.example"
      ],
      "decision": "needs_security_review",
      "alert_id": "alert-017",
      "severity": "suspicious"
    },
    {
      "rule_id": "R001",
      "rule_name": "known malicious domain access",
      "host_id": "김민준-재무팀-Laptop",
      "event_ids": [
        "evt-020"
      ],
      "event_time": "2026-07-05T10:05:00+09:00",
      "title": "Known malicious destination observed: evil-kakao-link.example",
      "risk_score": 34,
      "mitre_mapping": [
        "Initial Access"
      ],
      "evidence": [
        "destination matched signature set: evil-kakao-link.example",
        "source event type: application_action"
      ],
      "decision": "needs_security_review",
      "alert_id": "alert-018",
      "severity": "suspicious"
    },
    {
      "rule_id": "R010",
      "rule_name": "risky application action with malicious URL",
      "host_id": "김민준-재무팀-Laptop",
      "event_ids": [
        "evt-020"
      ],
      "event_time": "2026-07-05T10:05:00+09:00",
      "title": "Risky application action observed: KakaoTalk message_send",
      "risk_score": 34,
      "mitre_mapping": [
        "Collection",
        "Exfiltration"
      ],
      "evidence": [
        "app=KakaoTalk",
        "action=message_send",
        "object_url=https://evil-kakao-link.example/collect",
        "message body was not retained"
      ],
      "decision": "needs_security_review",
      "alert_id": "alert-019",
      "severity": "suspicious"
    },
    {
      "rule_id": "R011",
      "rule_name": "known malware hash signature match",
      "host_id": "김민준-재무팀-Laptop",
      "event_ids": [
        "evt-020"
      ],
      "event_time": "2026-07-05T10:05:00+09:00",
      "title": "Known malware hash observed: badbeef00000...",
      "risk_score": 42,
      "mitre_mapping": [
        "Execution",
        "Defense Evasion"
      ],
      "evidence": [
        "hash_sha256=badbeef0000000000000000000000000000000000000000000000000000000001",
        "event_type=application_action",
        "process_name=KakaoTalk"
      ],
      "decision": "needs_security_review",
      "alert_id": "alert-020",
      "severity": "suspicious"
    },
    {
      "rule_id": "R007",
      "rule_name": "shell process creates network connection",
      "host_id": "이도윤-IT관리자-PC",
      "event_ids": [
        "evt-017"
      ],
      "event_time": "2026-07-05T13:46:00+09:00",
      "title": "Shell process made outbound connection: powershell.exe",
      "risk_score": 26,
      "mitre_mapping": [
        "Execution",
        "Command and Control"
      ],
      "evidence": [
        "process_name=powershell.exe",
        "destination=admin-tools.example",
        "shell network activity often needs analyst review"
      ],
      "decision": "needs_review",
      "alert_id": "alert-021",
      "severity": "info"
    },
    {
      "rule_id": "R001",
      "rule_name": "known malicious domain access",
      "host_id": "박서연-영업팀-VPN",
      "event_ids": [
        "evt-014"
      ],
      "event_time": "2026-07-05T22:24:00+09:00",
      "title": "Known malicious destination observed: rare-storage.example",
      "risk_score": 34,
      "mitre_mapping": [
        "Initial Access"
      ],
      "evidence": [
        "destination matched signature set: rare-storage.example",
        "source event type: network_connection"
      ],
      "decision": "needs_security_review",
      "alert_id": "alert-022",
      "severity": "suspicious"
    },
    {
      "rule_id": "R005",
      "rule_name": "large outbound transfer",
      "host_id": "박서연-영업팀-VPN",
      "event_ids": [
        "evt-014"
      ],
      "event_time": "2026-07-05T22:24:00+09:00",
      "title": "Large outbound transfer: 92,000,000 bytes",
      "risk_score": 35,
      "mitre_mapping": [
        "Exfiltration"
      ],
      "evidence": [
        "bytes_out=92000000",
        "process_name=syncclient.exe",
        "destination=rare-storage.example"
      ],
      "decision": "needs_security_review",
      "alert_id": "alert-023",
      "severity": "suspicious"
    },
    {
      "rule_id": "R006",
      "rule_name": "rare ASN connection outside work hours",
      "host_id": "박서연-영업팀-VPN",
      "event_ids": [
        "evt-014"
      ],
      "event_time": "2026-07-05T22:24:00+09:00",
      "title": "Rare ASN connection outside work hours: AS64590",
      "risk_score": 22,
      "mitre_mapping": [
        "Command and Control"
      ],
      "evidence": [
        "destination_asn=AS64590",
        "event_time is outside 07:00-20:00",
        "destination=rare-storage.example"
      ],
      "decision": "needs_review",
      "alert_id": "alert-024",
      "severity": "info"
    },
    {
      "rule_id": "R008",
      "rule_name": "VPN tunnel plus abnormal transfer",
      "host_id": "박서연-영업팀-VPN",
      "event_ids": [
        "evt-014"
      ],
      "event_time": "2026-07-05T22:24:00+09:00",
      "title": "VPN session with abnormal external transfer",
      "risk_score": 32,
      "mitre_mapping": [
        "Exfiltration"
      ],
      "evidence": [
        "vpn_active=true",
        "bytes_out=92000000",
        "destination_asn=AS64590"
      ],
      "decision": "needs_security_review",
      "alert_id": "alert-025",
      "severity": "suspicious"
    },
    {
      "rule_id": "R005",
      "rule_name": "large outbound transfer",
      "host_id": "박서연-영업팀-VPN",
      "event_ids": [
        "evt-015"
      ],
      "event_time": "2026-07-05T22:26:00+09:00",
      "title": "Large outbound transfer: 74,000,000 bytes",
      "risk_score": 35,
      "mitre_mapping": [
        "Exfiltration"
      ],
      "evidence": [
        "bytes_out=74000000",
        "process_name=syncclient.exe",
        "destination=rare-storage.example"
      ],
      "decision": "needs_security_review",
      "alert_id": "alert-026",
      "severity": "suspicious"
    },
    {
      "rule_id": "R006",
      "rule_name": "rare ASN connection outside work hours",
      "host_id": "박서연-영업팀-VPN",
      "event_ids": [
        "evt-015"
      ],
      "event_time": "2026-07-05T22:26:00+09:00",
      "title": "Rare ASN connection outside work hours: AS64590",
      "risk_score": 22,
      "mitre_mapping": [
        "Command and Control"
      ],
      "evidence": [
        "destination_asn=AS64590",
        "event_time is outside 07:00-20:00",
        "destination=rare-storage.example"
      ],
      "decision": "needs_review",
      "alert_id": "alert-027",
      "severity": "info"
    },
    {
      "rule_id": "R008",
      "rule_name": "VPN tunnel plus abnormal transfer",
      "host_id": "박서연-영업팀-VPN",
      "event_ids": [
        "evt-015"
      ],
      "event_time": "2026-07-05T22:26:00+09:00",
      "title": "VPN session with abnormal external transfer",
      "risk_score": 32,
      "mitre_mapping": [
        "Exfiltration"
      ],
      "evidence": [
        "vpn_active=true",
        "bytes_out=74000000",
        "destination_asn=AS64590"
      ],
      "decision": "needs_security_review",
      "alert_id": "alert-028",
      "severity": "suspicious"
    },
    {
      "rule_id": "R004",
      "rule_name": "periodic external connection",
      "host_id": "김민준-재무팀-Laptop",
      "event_ids": [
        "evt-007",
        "evt-008",
        "evt-009",
        "evt-010",
        "evt-011"
      ],
      "event_time": "2026-07-05T10:02:00+09:00",
      "title": "Periodic outbound connection every ~30s",
      "risk_score": 36,
      "mitre_mapping": [
        "Command and Control"
      ],
      "evidence": [
        "process_name=invoice.exe",
        "destination=c2.badbeacon.example",
        "regular_interval_count=4"
      ],
      "decision": "needs_security_review",
      "interval_seconds": 30,
      "event_count": 5,
      "alert_id": "alert-029",
      "severity": "suspicious"
    }
  ],
  "incidents": [
    {
      "incident_id": "incident-001",
      "host_id": "김민준-재무팀-Laptop",
      "risk_score": 100,
      "severity": "critical",
      "primary_category": "suspicious_download_to_c2_sequence",
      "detected_sequence": [
        {
          "stage": "unknown_file_download",
          "event_id": "evt-004",
          "summary": "invoice.exe downloaded from malware-drop.example"
        },
        {
          "stage": "unsigned_process_execution",
          "event_id": "evt-005",
          "summary": "invoice.exe started by chrome.exe"
        },
        {
          "stage": "periodic_external_connection",
          "event_ids": [
            "evt-007",
            "evt-008",
            "evt-009",
            "evt-010",
            "evt-011"
          ],
          "summary": "Periodic outbound connection every ~30s"
        },
        {
          "stage": "large_outbound_transfer",
          "event_ids": [
            "evt-011"
          ],
          "summary": "Large outbound transfer: 118,000,000 bytes"
        }
      ],
      "mitre_mapping": [
        {
          "tactic": "Initial Access",
          "reason": "unknown executable was downloaded from a rare or malicious domain"
        },
        {
          "tactic": "Execution",
          "reason": "downloaded unsigned executable was started from Downloads"
        },
        {
          "tactic": "Command and Control",
          "reason": "process made repeated outbound connections at a regular interval"
        },
        {
          "tactic": "Exfiltration",
          "reason": "large outbound transfer followed the suspicious process activity"
        }
      ],
      "evidence": [
        "downloaded file was not trusted",
        "parent process was browser",
        "destination matched suspicious domain or IP evidence",
        "connection interval was regular",
        "large outbound transfer occurred after execution"
      ],
      "decision": "needs_security_review"
    }
  ],
  "endpoint_risk": [
    {
      "host_id": "김민준-재무팀-Laptop",
      "risk_score": 100,
      "severity": "critical",
      "alert_count": 21,
      "incident_count": 1,
      "top_rules": [
        "R001",
        "R011",
        "R009",
        "R002"
      ],
      "last_event_time": "2026-07-05T10:05:00+09:00"
    },
    {
      "host_id": "박서연-영업팀-VPN",
      "risk_score": 100,
      "severity": "critical",
      "alert_count": 7,
      "incident_count": 0,
      "top_rules": [
        "R005",
        "R006",
        "R008",
        "R001"
      ],
      "last_event_time": "2026-07-05T22:26:00+09:00"
    },
    {
      "host_id": "이도윤-IT관리자-PC",
      "risk_score": 26,
      "severity": "info",
      "alert_count": 1,
      "incident_count": 0,
      "top_rules": [
        "R007"
      ],
      "last_event_time": "2026-07-05T13:46:00+09:00"
    },
    {
      "host_id": "최하은-개발팀-Workstation",
      "risk_score": 0,
      "severity": "info",
      "alert_count": 0,
      "incident_count": 0,
      "top_rules": [],
      "last_event_time": "2026-07-05T09:37:00+09:00"
    }
  ],
  "mitre_distribution": [
    {
      "tactic": "Initial Access",
      "count": 16
    },
    {
      "tactic": "Execution",
      "count": 6
    },
    {
      "tactic": "Defense Evasion",
      "count": 3
    },
    {
      "tactic": "Collection",
      "count": 1
    },
    {
      "tactic": "Command and Control",
      "count": 6
    },
    {
      "tactic": "Exfiltration",
      "count": 7
    }
  ],
  "top_suspicious_domains": [
    {
      "domain": "c2.badbeacon.example",
      "count": 6
    },
    {
      "domain": "malware-drop.example",
      "count": 5
    },
    {
      "domain": "rare-storage.example",
      "count": 2
    },
    {
      "domain": "evil-kakao-link.example",
      "count": 1
    },
    {
      "domain": "admin-tools.example",
      "count": 1
    }
  ],
  "top_suspicious_ips": [
    {
      "ip": "203.0.113.77",
      "count": 7
    },
    {
      "ip": "198.51.100.66",
      "count": 2
    },
    {
      "ip": "198.51.100.9",
      "count": 1
    }
  ],
  "process_trees": [
    {
      "host_id": "김민준-재무팀-Laptop",
      "parent_process": "explorer.exe",
      "process_name": "chrome.exe",
      "process_path": "C:\\Program Files\\Google\\Chrome\\Application\\chrome.exe",
      "signed": true,
      "event_id": "evt-001",
      "event_time": "2026-07-05T10:00:00+09:00"
    },
    {
      "host_id": "김민준-재무팀-Laptop",
      "parent_process": "chrome.exe",
      "process_name": "invoice.exe",
      "process_path": "C:\\Users\\analyst\\Downloads\\invoice.exe",
      "signed": false,
      "event_id": "evt-005",
      "event_time": "2026-07-05T10:01:10+09:00"
    },
    {
      "host_id": "이도윤-IT관리자-PC",
      "parent_process": "explorer.exe",
      "process_name": "powershell.exe",
      "process_path": "C:\\Windows\\System32\\WindowsPowerShell\\v1.0\\powershell.exe",
      "signed": true,
      "event_id": "evt-016",
      "event_time": "2026-07-05T13:45:00+09:00"
    }
  ],
  "dlq_events": [
    {
      "index": 58,
      "event_id": "evt-invalid-001",
      "code": "INVALID_EVENT_SCHEMA",
      "errors": [
        "missing required fields: ['received_time']"
      ],
      "sanitized_event": {
        "event_id": "evt-invalid-001",
        "event_time": "2026-07-05T11:00:00+09:00",
        "host_id": "정우진-미등록-PC",
        "event_type": "network_connection",
        "source": "agent",
        "payload_version": "v1",
        "dst_ip": "203.0.113.200",
        "privacy_masked_fields": [
          "raw_payload"
        ]
      }
    },
    {
      "index": 59,
      "event_id": "evt-invalid-002",
      "code": "INVALID_EVENT_SCHEMA",
      "errors": [
        "unsupported event_type: unknown_event_type",
        "invalid datetime field: event_time"
      ],
      "sanitized_event": {
        "event_id": "evt-invalid-002",
        "event_time": "not-a-date",
        "received_time": "2026-07-05T11:05:03+09:00",
        "host_id": "정우진-미등록-PC",
        "event_type": "unknown_event_type",
        "source": "agent",
        "payload_version": "v1"
      }
    }
  ],
  "privacy_actions": [
    {
      "event_id": "evt-001",
      "masked_fields": [
        "user_name"
      ],
      "actions": [
        "removed_sensitive_field"
      ]
    },
    {
      "event_id": "evt-019",
      "masked_fields": [
        "http_body"
      ],
      "actions": [
        "removed_sensitive_field"
      ]
    },
    {
      "event_id": "evt-020",
      "masked_fields": [
        "message_content"
      ],
      "actions": [
        "removed_sensitive_field"
      ]
    },
    {
      "event_id": "evt-invalid-001",
      "masked_fields": [
        "raw_payload"
      ],
      "actions": [
        "removed_sensitive_field"
      ]
    }
  ],
  "decision": "needs_security_review",
  "limitations": [
    "PoC는 endpoint metadata, PCAP flow summary, L7 proxy log를 분석하며 OS kernel driver 수준의 EDR은 아닙니다.",
    "HTTPS deep inspection은 로컬 프록시/복호화 로그를 전제로 한 PoC입니다. 임의의 HTTPS를 몰래 복호화하지 않습니다.",
    "threat intelligence는 rules/threat_signatures.json의 small signature set입니다.",
    "AI prediction은 학습된 상용 모델이 아니라 feature 기반 risk scoring PoC입니다.",
    "response action은 기본 dry-run입니다. 실제 차단/격리 적용 전에는 운영 정책 검토가 필요합니다."
  ],
  "response_plan": {
    "mode": "dry-run",
    "action_count": 29,
    "by_action_type": [
      {
        "action_type": "block_destination",
        "count": 13
      },
      {
        "action_type": "quarantine_hash",
        "count": 3
      },
      {
        "action_type": "rate_limit_or_block_transfer",
        "count": 3
      },
      {
        "action_type": "review_rare_asn",
        "count": 2
      },
      {
        "action_type": "review_vpn_exfiltration",
        "count": 2
      },
      {
        "action_type": "block_url",
        "count": 1
      },
      {
        "action_type": "quarantine_download",
        "count": 1
      },
      {
        "action_type": "kill_and_quarantine_process",
        "count": 1
      },
      {
        "action_type": "block_app_url_and_notify",
        "count": 1
      },
      {
        "action_type": "review_shell_network",
        "count": 1
      },
      {
        "action_type": "contain_host_for_c2_review",
        "count": 1
      }
    ],
    "actions": [
      {
        "action_id": "response-001",
        "mode": "dry-run",
        "status": "planned",
        "host_id": "김민준-재무팀-Laptop",
        "rule_id": "R001",
        "alert_id": "alert-001",
        "action_type": "block_destination",
        "description": "Block known malicious domain/IP at DNS or proxy policy.",
        "created_at": "2026-07-06T11:59:19",
        "evidence": [
          "destination matched signature set: malware-drop.example",
          "source event type: dns_query"
        ]
      },
      {
        "action_id": "response-002",
        "mode": "dry-run",
        "status": "planned",
        "host_id": "김민준-재무팀-Laptop",
        "rule_id": "R001",
        "alert_id": "alert-002",
        "action_type": "block_destination",
        "description": "Block known malicious domain/IP at DNS or proxy policy.",
        "created_at": "2026-07-06T11:59:19",
        "evidence": [
          "destination matched signature set: malware-drop.example",
          "source event type: decryption_event"
        ]
      },
      {
        "action_id": "response-003",
        "mode": "dry-run",
        "status": "planned",
        "host_id": "김민준-재무팀-Laptop",
        "rule_id": "R001",
        "alert_id": "alert-003",
        "action_type": "block_destination",
        "description": "Block known malicious domain/IP at DNS or proxy policy.",
        "created_at": "2026-07-06T11:59:19",
        "evidence": [
          "destination matched signature set: malware-drop.example",
          "source event type: network_connection"
        ]
      },
      {
        "action_id": "response-004",
        "mode": "dry-run",
        "status": "planned",
        "host_id": "김민준-재무팀-Laptop",
        "rule_id": "R001",
        "alert_id": "alert-004",
        "action_type": "block_destination",
        "description": "Block known malicious domain/IP at DNS or proxy policy.",
        "created_at": "2026-07-06T11:59:19",
        "evidence": [
          "destination matched signature set: malware-drop.example",
          "source event type: http_request"
        ]
      },
      {
        "action_id": "response-005",
        "mode": "dry-run",
        "status": "planned",
        "host_id": "김민준-재무팀-Laptop",
        "rule_id": "R009",
        "alert_id": "alert-005",
        "action_type": "block_url",
        "description": "Block malicious or phishing URL at proxy.",
        "created_at": "2026-07-06T11:59:19",
        "evidence": [
          "url=https://malware-drop.example/payload/invoice.exe",
          "domain=malware-drop.example",
          "url_category=malware"
        ]
      },
      {
        "action_id": "response-006",
        "mode": "dry-run",
        "status": "planned",
        "host_id": "김민준-재무팀-Laptop",
        "rule_id": "R001",
        "alert_id": "alert-006",
        "action_type": "block_destination",
        "description": "Block known malicious domain/IP at DNS or proxy policy.",
        "created_at": "2026-07-06T11:59:19",
        "evidence": [
          "destination matched signature set: malware-drop.example",
          "source event type: file_download"
        ]
      },
      {
        "action_id": "response-007",
        "mode": "dry-run",
        "status": "planned",
        "host_id": "김민준-재무팀-Laptop",
        "rule_id": "R002",
        "alert_id": "alert-007",
        "action_type": "quarantine_download",
        "description": "Quarantine executable downloaded from suspicious source.",
        "created_at": "2026-07-06T11:59:19",
        "evidence": [
          "downloaded file has executable extension",
          "source_domain=malware-drop.example",
          "browser initiated the download"
        ]
      },
      {
        "action_id": "response-008",
        "mode": "dry-run",
        "status": "planned",
        "host_id": "김민준-재무팀-Laptop",
        "rule_id": "R011",
        "alert_id": "alert-008",
        "action_type": "quarantine_hash",
        "description": "Quarantine known malware hash.",
        "created_at": "2026-07-06T11:59:19",
        "evidence": [
          "hash_sha256=badbeef0000000000000000000000000000000000000000000000000000000001",
          "event_type=file_download",
          "process_name=chrome.exe"
        ]
      },
      {
        "action_id": "response-009",
        "mode": "dry-run",
        "status": "planned",
        "host_id": "김민준-재무팀-Laptop",
        "rule_id": "R003",
        "alert_id": "alert-009",
        "action_type": "kill_and_quarantine_process",
        "description": "Stop unsigned executable and quarantine file.",
        "created_at": "2026-07-06T11:59:19",
        "evidence": [
          "process is unsigned",
          "process path is under Downloads",
          "parent_process=chrome.exe"
        ]
      },
      {
        "action_id": "response-010",
        "mode": "dry-run",
        "status": "planned",
        "host_id": "김민준-재무팀-Laptop",
        "rule_id": "R011",
        "alert_id": "alert-010",
        "action_type": "quarantine_hash",
        "description": "Quarantine known malware hash.",
        "created_at": "2026-07-06T11:59:19",
        "evidence": [
          "hash_sha256=badbeef0000000000000000000000000000000000000000000000000000000001",
          "event_type=process_start",
          "process_name=invoice.exe"
        ]
      },
      {
        "action_id": "response-011",
        "mode": "dry-run",
        "status": "planned",
        "host_id": "김민준-재무팀-Laptop",
        "rule_id": "R001",
        "alert_id": "alert-011",
        "action_type": "block_destination",
        "description": "Block known malicious domain/IP at DNS or proxy policy.",
        "created_at": "2026-07-06T11:59:19",
        "evidence": [
          "destination matched signature set: c2.badbeacon.example",
          "source event type: dns_query"
        ]
      },
      {
        "action_id": "response-012",
        "mode": "dry-run",
        "status": "planned",
        "host_id": "김민준-재무팀-Laptop",
        "rule_id": "R001",
        "alert_id": "alert-012",
        "action_type": "block_destination",
        "description": "Block known malicious domain/IP at DNS or proxy policy.",
        "created_at": "2026-07-06T11:59:19",
        "evidence": [
          "destination matched signature set: c2.badbeacon.example",
          "source event type: network_connection"
        ]
      },
      {
        "action_id": "response-013",
        "mode": "dry-run",
        "status": "planned",
        "host_id": "김민준-재무팀-Laptop",
        "rule_id": "R001",
        "alert_id": "alert-013",
        "action_type": "block_destination",
        "description": "Block known malicious domain/IP at DNS or proxy policy.",
        "created_at": "2026-07-06T11:59:19",
        "evidence": [
          "destination matched signature set: c2.badbeacon.example",
          "source event type: network_connection"
        ]
      },
      {
        "action_id": "response-014",
        "mode": "dry-run",
        "status": "planned",
        "host_id": "김민준-재무팀-Laptop",
        "rule_id": "R001",
        "alert_id": "alert-014",
        "action_type": "block_destination",
        "description": "Block known malicious domain/IP at DNS or proxy policy.",
        "created_at": "2026-07-06T11:59:19",
        "evidence": [
          "destination matched signature set: c2.badbeacon.example",
          "source event type: network_connection"
        ]
      },
      {
        "action_id": "response-015",
        "mode": "dry-run",
        "status": "planned",
        "host_id": "김민준-재무팀-Laptop",
        "rule_id": "R001",
        "alert_id": "alert-015",
        "action_type": "block_destination",
        "description": "Block known malicious domain/IP at DNS or proxy policy.",
        "created_at": "2026-07-06T11:59:19",
        "evidence": [
          "destination matched signature set: c2.badbeacon.example",
          "source event type: network_connection"
        ]
      },
      {
        "action_id": "response-016",
        "mode": "dry-run",
        "status": "planned",
        "host_id": "김민준-재무팀-Laptop",
        "rule_id": "R001",
        "alert_id": "alert-016",
        "action_type": "block_destination",
        "description": "Block known malicious domain/IP at DNS or proxy policy.",
        "created_at": "2026-07-06T11:59:19",
        "evidence": [
          "destination matched signature set: c2.badbeacon.example",
          "source event type: network_connection"
        ]
      },
      {
        "action_id": "response-017",
        "mode": "dry-run",
        "status": "planned",
        "host_id": "김민준-재무팀-Laptop",
        "rule_id": "R005",
        "alert_id": "alert-017",
        "action_type": "rate_limit_or_block_transfer",
        "description": "Review and block abnormal outbound transfer.",
        "created_at": "2026-07-06T11:59:19",
        "evidence": [
          "bytes_out=118000000",
          "process_name=invoice.exe",
          "destination=c2.badbeacon.example"
        ]
      },
      {
        "action_id": "response-018",
        "mode": "dry-run",
        "status": "planned",
        "host_id": "김민준-재무팀-Laptop",
        "rule_id": "R001",
        "alert_id": "alert-018",
        "action_type": "block_destination",
        "description": "Block known malicious domain/IP at DNS or proxy policy.",
        "created_at": "2026-07-06T11:59:19",
        "evidence": [
          "destination matched signature set: evil-kakao-link.example",
          "source event type: application_action"
        ]
      },
      {
        "action_id": "response-019",
        "mode": "dry-run",
        "status": "planned",
        "host_id": "김민준-재무팀-Laptop",
        "rule_id": "R010",
        "alert_id": "alert-019",
        "action_type": "block_app_url_and_notify",
        "description": "Block application-level URL and notify analyst.",
        "created_at": "2026-07-06T11:59:19",
        "evidence": [
          "app=KakaoTalk",
          "action=message_send",
          "object_url=https://evil-kakao-link.example/collect"
        ]
      },
      {
        "action_id": "response-020",
        "mode": "dry-run",
        "status": "planned",
        "host_id": "김민준-재무팀-Laptop",
        "rule_id": "R011",
        "alert_id": "alert-020",
        "action_type": "quarantine_hash",
        "description": "Quarantine known malware hash.",
        "created_at": "2026-07-06T11:59:19",
        "evidence": [
          "hash_sha256=badbeef0000000000000000000000000000000000000000000000000000000001",
          "event_type=application_action",
          "process_name=KakaoTalk"
        ]
      },
      {
        "action_id": "response-021",
        "mode": "dry-run",
        "status": "planned",
        "host_id": "이도윤-IT관리자-PC",
        "rule_id": "R007",
        "alert_id": "alert-021",
        "action_type": "review_shell_network",
        "description": "Inspect shell process command line and destination.",
        "created_at": "2026-07-06T11:59:19",
        "evidence": [
          "process_name=powershell.exe",
          "destination=admin-tools.example",
          "shell network activity often needs analyst review"
        ]
      },
      {
        "action_id": "response-022",
        "mode": "dry-run",
        "status": "planned",
        "host_id": "박서연-영업팀-VPN",
        "rule_id": "R001",
        "alert_id": "alert-022",
        "action_type": "block_destination",
        "description": "Block known malicious domain/IP at DNS or proxy policy.",
        "created_at": "2026-07-06T11:59:19",
        "evidence": [
          "destination matched signature set: rare-storage.example",
          "source event type: network_connection"
        ]
      },
      {
        "action_id": "response-023",
        "mode": "dry-run",
        "status": "planned",
        "host_id": "박서연-영업팀-VPN",
        "rule_id": "R005",
        "alert_id": "alert-023",
        "action_type": "rate_limit_or_block_transfer",
        "description": "Review and block abnormal outbound transfer.",
        "created_at": "2026-07-06T11:59:19",
        "evidence": [
          "bytes_out=92000000",
          "process_name=syncclient.exe",
          "destination=rare-storage.example"
        ]
      },
      {
        "action_id": "response-024",
        "mode": "dry-run",
        "status": "planned",
        "host_id": "박서연-영업팀-VPN",
        "rule_id": "R006",
        "alert_id": "alert-024",
        "action_type": "review_rare_asn",
        "description": "Review off-hours rare ASN connection.",
        "created_at": "2026-07-06T11:59:19",
        "evidence": [
          "destination_asn=AS64590",
          "event_time is outside 07:00-20:00",
          "destination=rare-storage.example"
        ]
      },
      {
        "action_id": "response-025",
        "mode": "dry-run",
        "status": "planned",
        "host_id": "박서연-영업팀-VPN",
        "rule_id": "R008",
        "alert_id": "alert-025",
        "action_type": "review_vpn_exfiltration",
        "description": "Review VPN transfer and destination ASN.",
        "created_at": "2026-07-06T11:59:19",
        "evidence": [
          "vpn_active=true",
          "bytes_out=92000000",
          "destination_asn=AS64590"
        ]
      },
      {
        "action_id": "response-026",
        "mode": "dry-run",
        "status": "planned",
        "host_id": "박서연-영업팀-VPN",
        "rule_id": "R005",
        "alert_id": "alert-026",
        "action_type": "rate_limit_or_block_transfer",
        "description": "Review and block abnormal outbound transfer.",
        "created_at": "2026-07-06T11:59:19",
        "evidence": [
          "bytes_out=74000000",
          "process_name=syncclient.exe",
          "destination=rare-storage.example"
        ]
      },
      {
        "action_id": "response-027",
        "mode": "dry-run",
        "status": "planned",
        "host_id": "박서연-영업팀-VPN",
        "rule_id": "R006",
        "alert_id": "alert-027",
        "action_type": "review_rare_asn",
        "description": "Review off-hours rare ASN connection.",
        "created_at": "2026-07-06T11:59:19",
        "evidence": [
          "destination_asn=AS64590",
          "event_time is outside 07:00-20:00",
          "destination=rare-storage.example"
        ]
      },
      {
        "action_id": "response-028",
        "mode": "dry-run",
        "status": "planned",
        "host_id": "박서연-영업팀-VPN",
        "rule_id": "R008",
        "alert_id": "alert-028",
        "action_type": "review_vpn_exfiltration",
        "description": "Review VPN transfer and destination ASN.",
        "created_at": "2026-07-06T11:59:19",
        "evidence": [
          "vpn_active=true",
          "bytes_out=74000000",
          "destination_asn=AS64590"
        ]
      },
      {
        "action_id": "response-029",
        "mode": "dry-run",
        "status": "planned",
        "host_id": "김민준-재무팀-Laptop",
        "rule_id": "R004",
        "alert_id": "alert-029",
        "action_type": "contain_host_for_c2_review",
        "description": "Open C2 beaconing review and consider host containment.",
        "created_at": "2026-07-06T11:59:19",
        "evidence": [
          "process_name=invoice.exe",
          "destination=c2.badbeacon.example",
          "regular_interval_count=4"
        ]
      }
    ],
    "note": "PoC response engine does not change firewall/process state unless integrated with an approved actuator."
  },
  "ai_predictions": {
    "model": "poc_feature_risk_model_v1",
    "prediction_count": 3,
    "high_or_critical_count": 2,
    "predictions": [
      {
        "prediction_id": "prediction-001",
        "host_id": "김민준-재무팀-Laptop",
        "model": "poc_feature_risk_model_v1",
        "prediction": "critical",
        "score": 100,
        "confidence": 0.95,
        "horizon": "next_24h",
        "features": {
          "alert_count": 21,
          "incident_count": 1,
          "rules": [
            "R001",
            "R002",
            "R003",
            "R004",
            "R005",
            "R009",
            "R010",
            "R011"
          ],
          "has_c2_and_exfil": true,
          "has_l7_malicious_url": true
        },
        "reason": "Beaconing and outbound transfer appeared together.",
        "created_at": "2026-07-06T11:59:19"
      },
      {
        "prediction_id": "prediction-002",
        "host_id": "박서연-영업팀-VPN",
        "model": "poc_feature_risk_model_v1",
        "prediction": "critical",
        "score": 87,
        "confidence": 0.85,
        "horizon": "next_24h",
        "features": {
          "alert_count": 7,
          "incident_count": 0,
          "rules": [
            "R001",
            "R005",
            "R006",
            "R008"
          ],
          "has_c2_and_exfil": false,
          "has_l7_malicious_url": false
        },
        "reason": "Multiple weak signals were combined into a host-level risk estimate.",
        "created_at": "2026-07-06T11:59:19"
      },
      {
        "prediction_id": "prediction-003",
        "host_id": "이도윤-IT관리자-PC",
        "model": "poc_feature_risk_model_v1",
        "prediction": "low",
        "score": 19,
        "confidence": 0.52,
        "horizon": "next_24h",
        "features": {
          "alert_count": 1,
          "incident_count": 0,
          "rules": [
            "R007"
          ],
          "has_c2_and_exfil": false,
          "has_l7_malicious_url": false
        },
        "reason": "Multiple weak signals were combined into a host-level risk estimate.",
        "created_at": "2026-07-06T11:59:19"
      }
    ],
    "note": "This is a deterministic PoC risk model, not a trained production ML model."
  },
  "telemetry_context": {
    "customer_id": "demo-customer",
    "device_id": "multi-endpoint-sample",
    "agent_version": "0.1.0",
    "transport": "local-file",
    "auth_mode": "none"
  },
  "siem_analysis": {
    "edr_state": {
      "level": "RED",
      "reason": "critical endpoint risk 또는 incident가 존재합니다.",
      "highest_risk_score": 100,
      "critical_alert_count": 0,
      "warning_alert_count": 0,
      "dlq_event_count": 2
    },
    "time_window": {
      "first_event_at": "2026-07-05T09:00:00+09:00",
      "last_event_at": "2026-07-05T22:26:00+09:00",
      "duration_minutes": 806
    },
    "event_type_distribution": [
      {
        "name": "network_connection",
        "count": 46
      },
      {
        "name": "process_start",
        "count": 3
      },
      {
        "name": "dns_query",
        "count": 2
      },
      {
        "name": "decryption_event",
        "count": 1
      },
      {
        "name": "http_request",
        "count": 1
      },
      {
        "name": "file_download",
        "count": 1
      },
      {
        "name": "autorun_entry",
        "count": 1
      },
      {
        "name": "application_action",
        "count": 1
      },
      {
        "name": "vpn_tunnel",
        "count": 1
      },
      {
        "name": "flow_summary",
        "count": 1
      }
    ],
    "source_distribution": [
      {
        "name": "unknown",
        "count": 58
      }
    ],
    "query_findings": [
      {
        "query_id": "Q001",
        "title": "악성 destination 접속",
        "severity": "critical",
        "count": 13,
        "logic": "DNS, network, L7 event의 domain/IP를 threat signature와 비교합니다."
      },
      {
        "query_id": "Q002",
        "title": "다운로드 -> 실행 -> C2 -> 유출 chain",
        "severity": "critical",
        "count": 1,
        "logic": "file_download, process_start, beaconing, large outbound transfer를 host별 시간순으로 연결합니다."
      },
      {
        "query_id": "Q003",
        "title": "대용량 outbound transfer",
        "severity": "warning",
        "count": 5,
        "logic": "bytes_out, VPN 상태, destination ASN을 함께 확인합니다."
      },
      {
        "query_id": "Q004",
        "title": "L7 decrypted metadata policy hit",
        "severity": "suspicious",
        "count": 2,
        "logic": "복호화된 URL, app action, URL category를 policy/signature와 비교합니다."
      },
      {
        "query_id": "Q005",
        "title": "수집 품질 DLQ",
        "severity": "warning",
        "count": 2,
        "logic": "필수 field 누락, 지원하지 않는 event_type, datetime 오류를 추적합니다."
      }
    ],
    "topology": {
      "nodes": [
        {
          "id": "최하은-개발팀-Workstation",
          "label": "최하은-개발팀-Workstation",
          "group": "computer",
          "status": "not_detected",
          "risk_score": 0
        },
        {
          "id": "우리 내부 서비스",
          "label": "우리 내부 서비스",
          "group": "inside",
          "status": "not_detected",
          "risk_score": 0
        },
        {
          "id": "김민준-재무팀-Laptop",
          "label": "김민준-재무팀-Laptop",
          "group": "computer",
          "status": "alert",
          "risk_score": 100
        },
        {
          "id": "malware-drop.example",
          "label": "malware-drop.example",
          "group": "outside",
          "status": "alert",
          "risk_score": 0
        },
        {
          "id": "c2.badbeacon.example",
          "label": "c2.badbeacon.example",
          "group": "outside",
          "status": "alert",
          "risk_score": 0
        },
        {
          "id": "evil-kakao-link.example",
          "label": "evil-kakao-link.example",
          "group": "outside",
          "status": "alert",
          "risk_score": 0
        },
        {
          "id": "이도윤-IT관리자-PC",
          "label": "이도윤-IT관리자-PC",
          "group": "computer",
          "status": "not_detected",
          "risk_score": 26
        },
        {
          "id": "admin-tools.example",
          "label": "admin-tools.example",
          "group": "outside",
          "status": "alert",
          "risk_score": 0
        },
        {
          "id": "박서연-영업팀-VPN",
          "label": "박서연-영업팀-VPN",
          "group": "computer",
          "status": "alert",
          "risk_score": 100
        },
        {
          "id": "rare-storage.example",
          "label": "rare-storage.example",
          "group": "outside",
          "status": "alert",
          "risk_score": 0
        }
      ],
      "edges": [
        {
          "source": "김민준-재무팀-Laptop",
          "target": "c2.badbeacon.example",
          "event_count": 6,
          "bytes_out": 118013400,
          "status": "alert"
        },
        {
          "source": "김민준-재무팀-Laptop",
          "target": "evil-kakao-link.example",
          "event_count": 1,
          "bytes_out": 0,
          "status": "alert"
        },
        {
          "source": "김민준-재무팀-Laptop",
          "target": "malware-drop.example",
          "event_count": 5,
          "bytes_out": 42000,
          "status": "alert"
        },
        {
          "source": "박서연-영업팀-VPN",
          "target": "rare-storage.example",
          "event_count": 2,
          "bytes_out": 166000000,
          "status": "alert"
        },
        {
          "source": "박서연-영업팀-VPN",
          "target": "우리 내부 서비스",
          "event_count": 1,
          "bytes_out": 0,
          "status": "not_detected"
        },
        {
          "source": "이도윤-IT관리자-PC",
          "target": "admin-tools.example",
          "event_count": 1,
          "bytes_out": 56000,
          "status": "alert"
        },
        {
          "source": "최하은-개발팀-Workstation",
          "target": "우리 내부 서비스",
          "event_count": 38,
          "bytes_out": 836000,
          "status": "not_detected"
        }
      ]
    },
    "analyst_notes": [
      "다운로드, 실행, C2, 유출로 이어지는 attack chain 후보가 있습니다.",
      "L7 metadata에서 URL 또는 application action 기반 policy hit가 발생했습니다.",
      "DLQ event가 있어 agent producer 또는 parser schema mapping 검토가 필요합니다."
    ]
  },
  "pipeline_delivery": {
    "compression": "gzip",
    "raw_bytes": 36350,
    "compressed_bytes": 4943,
    "compression_ratio": 0.136,
    "sha256": "1a3cd15011b9419cc58682340760fd0fb8da8dda977b2c8e6de78f48c9bb855d",
    "latest_bundle_path": "outputs/pipeline/latest/telemetry_bundle.json.gz",
    "run_bundle_path": "outputs/pipeline/runs/20260706_115919/telemetry_bundle.json.gz",
    "headers": {
      "Content-Type": "application/json",
      "Content-Encoding": "gzip",
      "X-EDR-PoC": "security_edr_agent_parser",
      "X-EDR-Agent-Version": "0.1.0",
      "X-EDR-Customer-Id": "demo-customer",
      "X-EDR-Device-Id": "multi-endpoint-sample",
      "X-EDR-Envelope-Version": "2026-07-telemetry-v1"
    },
    "ship_url": "",
    "ship_status": "not_requested",
    "auth_mode": "none"
  },
  "dashboard": {
    "index_path": "dashboard/index.html",
    "data_script_path": "dashboard/data/latest-result.js",
    "open_note": "브라우저에서 dashboard/index.html을 열면 최신 CLI 결과를 볼 수 있습니다."
  },
  "report": {
    "latest_markdown_path": "outputs/reports/latest/security_report.md",
    "latest_html_path": "outputs/reports/latest/security_report.html",
    "run_markdown_path": "outputs/reports/runs/20260706_115919/security_report.md",
    "run_html_path": "outputs/reports/runs/20260706_115919/security_report.html",
    "open_note": "HTML 보고서는 outputs/reports/latest/security_report.html에서 볼 수 있습니다."
  }
};
