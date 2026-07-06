(function () {
  const result = window.SIEM_RESULT || {};
  const summary = result.summary || {};
  const state = {
    host: "all",
    severity: "all",
    timeRange: "all",
    search: "",
    selectedAlertId: null,
  };

  const ruleKorean = {
    R001: "악성 destination signature와 일치",
    R002: "브라우저에서 실행 파일 다운로드",
    R003: "Downloads 경로에서 unsigned executable 실행",
    R004: "주기적인 외부 연결 패턴",
    R005: "대용량 outbound transfer",
    R006: "업무 외 시간 rare ASN 연결",
    R007: "shell process의 network connection",
    R008: "VPN tunnel 상태의 비정상 전송",
    R009: "decrypted L7 malicious URL",
    R010: "risky application action",
    R011: "known malware hash",
    R012: "response action generated",
    R013: "AI predicted high-risk host",
  };

  const stageKorean = {
    unknown_file_download: "알 수 없는 실행 파일 다운로드",
    unsigned_process_execution: "unsigned executable 실행",
    periodic_external_connection: "주기적인 C2 의심 연결",
    large_outbound_transfer: "대용량 외부 전송",
  };

  initializeControls();
  render();

  function initializeControls() {
    setText("run-status", `상태: ${result.status || "unknown"}`);
    setText("run-time", `생성: ${formatTime(result.generated_at)}`);
    setText("run-source", `입력: ${sourceLabel(result.input)}`);

    const actionCount = (result.alerts || []).filter((alert) => ["critical", "warning"].includes(alert.severity)).length;
    setText("metric-risk", summary.highest_risk_score ?? 0);
    setText("metric-action", actionCount);
    setText("metric-events", summary.valid_event_count ?? 0);
    setText("metric-alerts", summary.alert_count ?? 0);
    setText("metric-incidents", summary.incident_count ?? 0);
    setText("metric-dlq", summary.dlq_event_count ?? 0);
    initializeReportLinks();

    const hostFilter = document.getElementById("host-filter");
    const severityFilter = document.getElementById("severity-filter");
    const timeRange = document.getElementById("time-range");
    const searchInput = document.getElementById("search-input");

    if (hostFilter) {
      const hosts = Array.from(
        new Set([...(result.events || []).map((event) => event.host_id), ...(result.endpoint_risk || []).map((row) => row.host_id)]),
      )
        .filter(Boolean)
        .sort();
      hostFilter.insertAdjacentHTML(
        "beforeend",
        hosts.map((host) => `<option value="${escapeAttr(host)}">${escapeHtml(host)}</option>`).join(""),
      );
      hostFilter.addEventListener("change", () => {
        state.host = hostFilter.value;
        state.selectedAlertId = null;
        render();
      });
    }

    if (severityFilter) {
      severityFilter.addEventListener("change", () => {
        state.severity = severityFilter.value;
        state.selectedAlertId = null;
        render();
      });
    }

    if (timeRange) {
      timeRange.addEventListener("change", () => {
        state.timeRange = timeRange.value;
        state.selectedAlertId = null;
        render();
      });
    }

    if (searchInput) {
      searchInput.addEventListener("input", () => {
        state.search = searchInput.value.trim().toLowerCase();
        state.selectedAlertId = null;
        render();
      });
    }
  }

  function render() {
    const filteredEvents = filterEvents(result.events || []);
    const filteredAlerts = filterAlerts(result.alerts || []);
    const filteredEndpoints = filterEndpoints(result.endpoint_risk || [], filteredAlerts, filteredEvents);

    renderSignals();
    renderIncidentQueue(result.incidents || [], filteredAlerts, filteredEndpoints);
    renderReportCenter();
    renderEventVolume(filteredEvents, filteredAlerts);
    renderEndpointRisk(filteredEndpoints);
    renderMitre(result.mitre_distribution || []);
    renderAttackTimeline(result.incidents || [], filteredAlerts);
    renderResponseActions(filteredAlerts, result.dlq_events || []);
    renderCompactList("domains", filterRankedRows(result.top_suspicious_domains || [], "domain"), "domain");
    renderCompactList("ips", filterRankedRows(result.top_suspicious_ips || [], "ip"), "ip");
    renderDlq(result.dlq_events || []);
    renderAlerts(filteredAlerts);
    renderProcessTree(filterProcessRows(result.process_trees || []));
    renderEventLog(filteredEvents);

    setText("visible-alert-count", `${filteredAlerts.length}건 표시`);
    setText("visible-event-count", `${filteredEvents.length}개 행`);
  }

  function initializeReportLinks() {
    const htmlPath = result.report?.latest_html_path;
    const markdownPath = result.report?.latest_markdown_path;
    const htmlHref = pathToFileUrl(htmlPath) || "../outputs/reports/latest/security_report.html";
    const markdownHref = pathToFileUrl(markdownPath) || "../outputs/reports/latest/security_report.md";
    setLink("top-report-link", htmlHref);
    setLink("report-html-link", htmlHref);
    setLink("report-md-link", markdownHref);
  }

  function renderSignals() {
    const processEvents = (result.events || []).filter((event) => event.event_type === "process_start").length;
    const networkEvents = (result.events || []).filter((event) => event.event_type === "network_connection").length;
    const l7Events = (result.events || []).filter((event) => ["http_request", "application_action", "decryption_event"].includes(event.event_type)).length;
    const incidents = result.incidents || [];
    const mitre = result.mitre_distribution || [];
    const dlqCount = summary.dlq_event_count || 0;
    const pipeline = result.pipeline_delivery || {};
    const ai = result.ai_predictions || {};

    setText("signal-agent", processEvents ? `활성 · process ${processEvents}` : "제한됨");
    setText("signal-correlation", l7Events ? `L7 ${l7Events} events` : incidents.length ? `상관분석 ${incidents.length}건` : networkEvents ? "telemetry 연결됨" : "대기 중");
    setText("signal-siem", pipeline.compressed_bytes ? `gzip ${formatBytes(pipeline.compressed_bytes)}` : dlqCount ? `DLQ ${dlqCount}건 확인 필요` : "정상 수집");
    setText("signal-mitre", ai.high_or_critical_count ? `AI high ${ai.high_or_critical_count}` : mitre.length ? `${mitre.length}개 tactic` : "매핑 없음");
  }

  function renderIncidentQueue(incidents, alerts, endpoints) {
    const root = document.getElementById("incident-queue");
    if (!root) return;
    const rows = incidents.length
      ? incidents.map((incident) => ({
          id: incident.incident_id,
          host: incident.host_id,
          severity: incident.severity,
          risk: incident.risk_score,
          title: incident.primary_category,
          decision: incident.decision,
          alertCount: alerts.filter((alert) => alert.host_id === incident.host_id).length,
          sequenceCount: (incident.detected_sequence || []).length,
          mitre: (incident.mitre_mapping || []).map((item) => item.tactic).join(" / "),
        }))
      : endpoints.slice(0, 4).map((endpoint, index) => ({
          id: `triage-${index + 1}`,
          host: endpoint.host_id,
          severity: endpoint.severity,
          risk: endpoint.risk_score,
          title: endpoint.risk_score > 0 ? "endpoint_triage_candidate" : "no_active_incident",
          decision: endpoint.risk_score > 0 ? "needs_review" : "monitor",
          alertCount: endpoint.alert_count,
          sequenceCount: endpoint.incident_count,
          mitre: (endpoint.top_rules || []).join(" / ") || "탐지 없음",
        }));

    setText("incident-count", `${rows.length}건 표시`);
    if (!rows.length) {
      root.innerHTML = empty("표시할 Incident 후보가 없습니다.");
      return;
    }
    root.innerHTML = rows
      .map(
        (row) => `
          <article class="incident-row ${escapeHtml(row.severity)}">
            <div class="incident-top">
              <span class="incident-title">${escapeHtml(row.id)} · ${escapeHtml(row.title)}</span>
              <span class="pill severity-${escapeHtml(row.severity)}">${escapeHtml(row.severity)}</span>
            </div>
            <div class="muted">Endpoint <strong>${escapeHtml(row.host)}</strong> · Decision ${escapeHtml(row.decision)}</div>
            <div class="incident-grid">
              <div class="mini-stat"><span>Risk</span><strong>${escapeHtml(row.risk)}</strong></div>
              <div class="mini-stat"><span>Alerts</span><strong>${escapeHtml(row.alertCount)}</strong></div>
              <div class="mini-stat"><span>Sequence</span><strong>${escapeHtml(row.sequenceCount)}</strong></div>
              <div class="mini-stat"><span>MITRE / Rules</span><strong>${escapeHtml(row.mitre)}</strong></div>
            </div>
          </article>
        `,
      )
      .join("");
  }

  function renderReportCenter() {
    const root = document.getElementById("report-summary");
    if (!root) return;
    const report = result.report || {};
    const pipeline = result.pipeline_delivery || {};
    const ai = result.ai_predictions || {};
    const htmlName = report.latest_html_path ? fileName(report.latest_html_path) : "security_report.html";
    const markdownName = report.latest_markdown_path ? fileName(report.latest_markdown_path) : "security_report.md";
    root.innerHTML = `
      <strong>분석 보고서 생성 완료</strong>
      <div class="muted">판정: ${escapeHtml(result.decision || "unknown")}</div>
      <div class="muted">포함: Executive Summary, Endpoint Risk, Incident, Alert Evidence, MITRE ATT&CK, DLQ, L7, AI, Pipeline</div>
      <div class="muted">AI predictions: ${escapeHtml(ai.prediction_count || 0)} · Pipeline: ${escapeHtml(pipeline.compression || "none")} ${escapeHtml(pipeline.compressed_bytes ? formatBytes(pipeline.compressed_bytes) : "")}</div>
      <div class="muted mono">${escapeHtml(htmlName)} · ${escapeHtml(markdownName)}</div>
    `;
  }

  function filterEvents(events) {
    return events.filter((event) => {
      if (state.host !== "all" && event.host_id !== state.host) return false;
      if (!matchesTimeRange(event.event_time)) return false;
      if (!matchesSearch([event.event_id, event.event_type, event.host_id, event.process_name, event.domain, event.dst_ip].join(" "))) {
        return false;
      }
      return true;
    });
  }

  function filterAlerts(alerts) {
    return alerts.filter((alert) => {
      if (state.host !== "all" && alert.host_id !== state.host) return false;
      if (state.severity !== "all" && alert.severity !== state.severity) return false;
      if (!matchesTimeRange(alert.event_time)) return false;
      const haystack = [
        alert.alert_id,
        alert.rule_id,
        alert.rule_name,
        alert.host_id,
        alert.title,
        ruleKorean[alert.rule_id],
        ...(alert.evidence || []),
        ...(alert.mitre_mapping || []),
      ].join(" ");
      return matchesSearch(haystack);
    });
  }

  function filterEndpoints(rows, alerts, events) {
    const activeHosts = new Set([...alerts.map((alert) => alert.host_id), ...events.map((event) => event.host_id)]);
    return rows.filter((row) => {
      if (state.host !== "all" && row.host_id !== state.host) return false;
      if (state.severity !== "all" && row.severity !== state.severity && !activeHosts.has(row.host_id)) return false;
      return state.host !== "all" || activeHosts.has(row.host_id) || !state.search;
    });
  }

  function filterRankedRows(rows, key) {
    if (!state.search) return rows;
    return rows.filter((row) => String(row[key] || "").toLowerCase().includes(state.search));
  }

  function filterProcessRows(rows) {
    return rows.filter((row) => {
      if (state.host !== "all" && row.host_id !== state.host) return false;
      return matchesSearch([row.host_id, row.parent_process, row.process_name, row.process_path].join(" "));
    });
  }

  function renderEventVolume(events, alerts) {
    const root = document.getElementById("event-volume");
    if (!root) return;
    if (!events.length) {
      root.innerHTML = empty("표시할 event가 없습니다.");
      setText("event-window", "sample window");
      return;
    }

    const bucketMap = new Map();
    for (const event of events) {
      const bucket = hourBucket(event.event_time);
      if (!bucketMap.has(bucket)) bucketMap.set(bucket, { bucket, events: 0, alerts: 0 });
      bucketMap.get(bucket).events += 1;
    }
    for (const alert of alerts) {
      const bucket = hourBucket(alert.event_time);
      if (!bucketMap.has(bucket)) bucketMap.set(bucket, { bucket, events: 0, alerts: 0 });
      bucketMap.get(bucket).alerts += 1;
    }

    const buckets = Array.from(bucketMap.values()).sort((a, b) => a.bucket.localeCompare(b.bucket));
    const maxEvents = Math.max(...buckets.map((item) => item.events), 1);
    const maxAlerts = Math.max(...buckets.map((item) => item.alerts), 1);
    setText("event-window", `${buckets[0].bucket} - ${buckets[buckets.length - 1].bucket}`);

    root.innerHTML = buckets
      .map((item) => {
        const eventHeight = Math.max(3, Math.round((item.events / maxEvents) * 128));
        const alertHeight = item.alerts ? Math.max(5, Math.round((item.alerts / maxAlerts) * 58)) : 0;
        return `
          <div class="volume-bar" title="${escapeAttr(item.bucket)} event ${item.events}, alert ${item.alerts}">
            <div class="bar-stack">
              <div class="alert-bar" style="height:${alertHeight}px"></div>
              <div class="event-bar" style="height:${eventHeight}px"></div>
            </div>
            <span class="bar-time">${escapeHtml(item.bucket.slice(11, 16))}</span>
          </div>
        `;
      })
      .join("");
  }

  function renderEndpointRisk(rows) {
    const root = document.getElementById("endpoint-risk");
    if (!root) return;
    if (!rows.length) {
      root.innerHTML = empty("조건에 맞는 Endpoint가 없습니다.");
      return;
    }
    root.innerHTML = rows
      .map((row) => {
        const severity = row.severity || "info";
        return `
          <div class="endpoint-row">
            <div class="row-top">
              <span class="host">${escapeHtml(row.host_id)}</span>
              <span class="pill severity-${escapeHtml(severity)}">${escapeHtml(severity)}</span>
            </div>
            <div class="score-track" aria-label="Risk score ${row.risk_score}">
              <div class="score-fill ${escapeHtml(severity)}" style="width:${clamp(row.risk_score)}%"></div>
            </div>
            <div class="meta">
              Risk <strong>${row.risk_score}</strong>/100 · Alert ${row.alert_count} · Incident ${row.incident_count}
            </div>
            <div class="muted">주요 Rule: ${escapeHtml((row.top_rules || []).join(", ") || "탐지 없음")}</div>
          </div>
        `;
      })
      .join("");
  }

  function renderMitre(rows) {
    const root = document.getElementById("mitre-bars");
    if (!root) return;
    if (!rows.length) {
      root.innerHTML = empty("MITRE ATT&CK 매핑이 없습니다.");
      return;
    }
    const max = Math.max(...rows.map((row) => row.count), 1);
    root.innerHTML = rows
      .map((row) => {
        const width = Math.max(8, Math.round((row.count / max) * 100));
        return `
          <div class="bar-row">
            <div class="bar-label">
              <strong>${escapeHtml(row.tactic)}</strong>
              <span class="count-badge">${row.count}</span>
            </div>
            <div class="bar-track">
              <div class="bar-fill suspicious" style="width:${width}%"></div>
            </div>
            <div class="muted">${escapeHtml(tacticHelp(row.tactic))}</div>
          </div>
        `;
      })
      .join("");
  }

  function renderResponseActions(alerts, dlqEvents) {
    const root = document.getElementById("response-actions");
    if (!root) return;
    const planned = result.response_plan?.actions || [];
    if (planned.length) {
      root.innerHTML = planned
        .slice(0, 8)
        .map(
          (action) => `
            <article class="action-item">
              <div class="action-top">
                <strong>${escapeHtml(action.action_type)}</strong>
                <span class="pill severity-${action.mode === "dry-run" ? "info" : "warning"}">${escapeHtml(action.mode)}</span>
              </div>
              <div class="muted">${escapeHtml(action.description)}</div>
              <div class="muted mono">${escapeHtml(action.host_id || "-")} · ${escapeHtml(action.rule_id || "-")} · ${escapeHtml(action.status || "-")}</div>
            </article>
          `,
        )
        .join("");
      return;
    }
    const rules = new Set(alerts.map((alert) => alert.rule_id));
    const actions = [];
    if (rules.has("R004")) {
      actions.push({
        title: "Beaconing 후보 검토",
        detail: "동일 process와 destination의 반복 주기가 정상 telemetry인지 allowlist와 비교합니다.",
        severity: "suspicious",
      });
    }
    if (rules.has("R005") || rules.has("R008")) {
      actions.push({
        title: "대용량 전송 경로 확인",
        detail: "bytes_out, 업무 시간대, VPN active 여부, destination ASN을 함께 확인합니다.",
        severity: "critical",
      });
    }
    if (rules.has("R001") || rules.has("R002") || rules.has("R003")) {
      actions.push({
        title: "파일 유입 및 실행 chain 확인",
        detail: "download source, file hash, parent process, 실행 시각을 incident sequence로 묶어 봅니다.",
        severity: "critical",
      });
    }
    if (rules.has("R007")) {
      actions.push({
        title: "Shell network activity 검토",
        detail: "PowerShell/cmd 계열 process의 command line과 destination을 운영 작업과 대조합니다.",
        severity: "suspicious",
      });
    }
    if (dlqEvents.length) {
      actions.push({
        title: "DLQ schema 수정",
        detail: "누락 field와 unsupported event_type을 collector mapping에 반영합니다.",
        severity: "warning",
      });
    }
    if (!actions.length) {
      actions.push({
        title: "현재 고위험 조치 없음",
        detail: "수집 범위를 늘리거나 DNS cache 옵션을 켜면 더 많은 correlation을 검증할 수 있습니다.",
        severity: "info",
      });
    }

    root.innerHTML = actions
      .map(
        (action) => `
          <article class="action-item">
            <div class="action-top">
              <strong>${escapeHtml(action.title)}</strong>
              <span class="pill severity-${escapeHtml(action.severity)}">${escapeHtml(action.severity)}</span>
            </div>
            <div class="muted">${escapeHtml(action.detail)}</div>
          </article>
        `,
      )
      .join("");
  }

  function renderAttackTimeline(incidents, fallbackAlerts) {
    const root = document.getElementById("attack-timeline");
    if (!root) return;
    const stages = incidents
      .filter((incident) => state.host === "all" || incident.host_id === state.host)
      .flatMap((incident) =>
        (incident.detected_sequence || []).map((stage) => ({
          host: incident.host_id,
          severity: incident.severity,
          stage: stage.stage,
          detail: stage.summary,
          risk: incident.risk_score,
        })),
      )
      .filter((stage) => matchesSearch([stage.host, stage.stage, stage.detail, stageKorean[stage.stage]].join(" ")));

    const rows = stages.length
      ? stages
      : fallbackAlerts.slice(0, 6).map((alert) => ({
          host: alert.host_id,
          severity: alert.severity,
          stage: alert.rule_id,
          detail: alert.title,
          risk: alert.risk_score,
        }));

    if (!rows.length) {
      root.innerHTML = empty("표시할 공격 흐름이 없습니다.");
      return;
    }

    root.innerHTML = rows
      .map(
        (row, index) => `
          <article class="timeline-card ${escapeHtml(row.severity)}">
            <div class="timeline-top">
              <span class="pill severity-${escapeHtml(row.severity)}">STEP ${index + 1}</span>
              <span class="muted">${escapeHtml(row.host)}</span>
            </div>
            <div class="timeline-stage">${escapeHtml(stageKorean[row.stage] || row.stage)}</div>
            <div class="muted mono">${escapeHtml(row.stage)}</div>
            <p class="meta">${escapeHtml(translateSentence(row.detail))}</p>
          </article>
        `,
      )
      .join("");
  }

  function renderCompactList(id, rows, key) {
    const root = document.getElementById(id);
    if (!root) return;
    if (!rows.length) {
      root.innerHTML = empty("표시할 항목이 없습니다.");
      return;
    }
    root.innerHTML = rows
      .map(
        (row) => `
          <div class="compact-row">
            <span class="title mono">${escapeHtml(row[key])}</span>
            <span class="count-badge">${row.count}</span>
          </div>
        `,
      )
      .join("");
  }

  function renderDlq(rows) {
    const root = document.getElementById("dlq-list");
    if (!root) return;
    if (!rows.length) {
      root.innerHTML = empty("DLQ로 이동한 event가 없습니다.");
      return;
    }
    root.innerHTML = rows
      .map(
        (row) => `
          <div class="compact-row">
            <span class="title mono">${escapeHtml(row.event_id || `index-${row.index}`)}</span>
            <span class="count-badge">${escapeHtml(row.code)}</span>
          </div>
          <div class="muted">${escapeHtml(translateSchemaErrors(row.errors || []))}</div>
        `,
      )
      .join("");
  }

  function renderAlerts(rows) {
    const root = document.getElementById("alerts-list");
    if (!root) return;
    if (!rows.length) {
      root.innerHTML = empty("조건에 맞는 Alert가 없습니다.");
      return;
    }
    if (!state.selectedAlertId && rows[0]) state.selectedAlertId = rows[0].alert_id;

    root.innerHTML = rows
      .map((alert) => {
        const selected = alert.alert_id === state.selectedAlertId ? "is-selected" : "";
        return `
          <article class="alert-row ${selected}" data-alert-id="${escapeAttr(alert.alert_id)}">
            <div class="alert-top">
              <span class="title">${escapeHtml(alert.rule_id)} · ${escapeHtml(ruleKorean[alert.rule_id] || alert.rule_name)}</span>
              <span class="pill severity-${escapeHtml(alert.severity)}">${escapeHtml(alert.severity)}</span>
            </div>
            <div class="meta">
              Endpoint <strong>${escapeHtml(alert.host_id)}</strong> · Risk <strong>${alert.risk_score}</strong> ·
              MITRE ATT&CK ${escapeHtml((alert.mitre_mapping || []).join(" / "))}
            </div>
            <div class="muted">${escapeHtml(translateSentence(alert.title))}</div>
            <ul class="evidence">
              ${(alert.evidence || []).slice(0, selected ? 6 : 2).map((item) => `<li>${escapeHtml(translateSentence(item))}</li>`).join("")}
            </ul>
          </article>
        `;
      })
      .join("");

    root.querySelectorAll("[data-alert-id]").forEach((node) => {
      node.addEventListener("click", () => {
        state.selectedAlertId = node.getAttribute("data-alert-id");
        renderAlerts(rows);
      });
    });
  }

  function renderProcessTree(rows) {
    const root = document.getElementById("process-tree");
    if (!root) return;
    if (!rows.length) {
      root.innerHTML = empty("표시할 process tree가 없습니다.");
      return;
    }
    root.innerHTML = rows
      .map(
        (row) => `
          <div class="process-row">
            <div class="process-main">
              <span class="process-name">${escapeHtml(row.parent_process)} -> ${escapeHtml(row.process_name)}</span>
              <span class="pill severity-${row.signed === false ? "suspicious" : "info"}">${row.signed === false ? "unsigned" : "signed"}</span>
            </div>
            <div class="muted">${escapeHtml(row.host_id)} · ${escapeHtml(formatTime(row.event_time))}</div>
            <div class="muted mono">${escapeHtml(row.process_path || "")}</div>
          </div>
        `,
      )
      .join("");
  }

  function renderEventLog(events) {
    const root = document.getElementById("event-log");
    if (!root) return;
    if (!events.length) {
      root.innerHTML = `<tr><td colspan="6">${empty("표시할 event가 없습니다.")}</td></tr>`;
      return;
    }
    root.innerHTML = events
      .slice(-80)
      .reverse()
      .map(
        (event) => `
          <tr>
            <td class="mono">${escapeHtml(formatTime(event.event_time))}</td>
            <td>${escapeHtml(event.host_id)}</td>
            <td>${escapeHtml(event.event_type)}</td>
            <td>${escapeHtml(event.process_name || "-")}</td>
            <td class="mono">${escapeHtml(event.domain || event.dst_ip || "-")}</td>
            <td>${escapeHtml(formatBytes(event.bytes_out))}</td>
          </tr>
        `,
      )
      .join("");
  }

  function matchesTimeRange(value) {
    if (state.timeRange === "all") return true;
    const hour = new Date(value).getHours();
    const isWork = hour >= 7 && hour < 20;
    return state.timeRange === "work" ? isWork : !isWork;
  }

  function matchesSearch(value) {
    if (!state.search) return true;
    return String(value || "").toLowerCase().includes(state.search);
  }

  function hourBucket(value) {
    const date = new Date(value);
    if (Number.isNaN(date.getTime())) return "unknown";
    const year = date.getFullYear();
    const month = String(date.getMonth() + 1).padStart(2, "0");
    const day = String(date.getDate()).padStart(2, "0");
    const hour = String(date.getHours()).padStart(2, "0");
    return `${year}-${month}-${day} ${hour}:00`;
  }

  function formatTime(value) {
    if (!value) return "-";
    const date = new Date(value);
    if (Number.isNaN(date.getTime())) return value;
    const month = String(date.getMonth() + 1).padStart(2, "0");
    const day = String(date.getDate()).padStart(2, "0");
    const hour = String(date.getHours()).padStart(2, "0");
    const minute = String(date.getMinutes()).padStart(2, "0");
    return `${month}-${day} ${hour}:${minute}`;
  }

  function formatBytes(value) {
    const bytes = Number(value || 0);
    if (!bytes) return "-";
    if (bytes >= 1_000_000) return `${(bytes / 1_000_000).toFixed(1)} MB`;
    if (bytes >= 1_000) return `${(bytes / 1_000).toFixed(1)} KB`;
    return `${bytes} B`;
  }

  function sourceLabel(input) {
    if (!input) return "unknown";
    if (input.source === "event_file") return `${input.raw_event_count || 0}개 events`;
    return input.source || "unknown";
  }

  function tacticHelp(tactic) {
    const help = {
      "Initial Access": "초기 유입 또는 악성 destination 접촉 후보",
      Execution: "실행 파일 또는 shell 실행 흐름",
      "Command and Control": "반복 연결, rare ASN, C2 의심 통신",
      Exfiltration: "대용량 outbound transfer 흐름",
    };
    return help[tactic] || "추가 분석이 필요한 tactic입니다.";
  }

  function translateSchemaErrors(errors) {
    return errors
      .map((error) =>
        String(error)
          .replace("missing required fields", "필수 field 누락")
          .replace("unsupported event_type", "지원하지 않는 event_type")
          .replace("invalid datetime field", "datetime field 형식 오류"),
      )
      .join("; ");
  }

  function translateSentence(value) {
    return String(value || "")
      .replace("Known malicious destination observed", "알려진 악성 destination 탐지")
      .replace("Executable download needs review", "검토가 필요한 executable download")
      .replace("Unsigned executable started", "unsigned executable 실행")
      .replace("Periodic outbound connection every", "주기적인 outbound connection")
      .replace("Large outbound transfer", "대용량 outbound transfer")
      .replace("Rare ASN connection outside work hours", "업무 외 시간 rare ASN 연결")
      .replace("Shell process made outbound connection", "shell process outbound connection")
      .replace("VPN session with abnormal external transfer", "VPN session 중 비정상 external transfer")
      .replace("destination matched signature set", "destination이 signature set과 일치")
      .replace("source event type", "source event type")
      .replace("downloaded file has executable extension", "다운로드 파일이 executable 확장자입니다")
      .replace("browser initiated the download", "browser가 download를 시작했습니다")
      .replace("signature context raised suspicion", "signature context상 의심이 필요합니다")
      .replace("process is unsigned", "process가 unsigned 상태입니다")
      .replace("process path is under Downloads", "process path가 Downloads 하위입니다")
      .replace("shell network activity often needs analyst review", "shell network activity는 analyst 검토가 필요합니다")
      .replace("event_time is outside 07:00-20:00", "event_time이 07:00-20:00 밖입니다")
      .replace("regular_interval_count", "regular interval count")
      .replace("unknown executable was downloaded from a rare or malicious domain", "rare 또는 malicious domain에서 unknown executable이 다운로드되었습니다")
      .replace("downloaded unsigned executable was started from Downloads", "Downloads의 unsigned executable이 실행되었습니다")
      .replace("process made repeated outbound connections at a regular interval", "process가 일정 간격으로 outbound connection을 반복했습니다")
      .replace("large outbound transfer followed the suspicious process activity", "의심 process activity 이후 대용량 outbound transfer가 발생했습니다")
      .replace("downloaded file was not trusted", "downloaded file이 trusted 상태가 아닙니다")
      .replace("parent process was browser", "parent process가 browser입니다")
      .replace("destination matched suspicious domain or IP evidence", "destination이 suspicious domain 또는 IP 근거와 일치합니다")
      .replace("connection interval was regular", "connection interval이 규칙적입니다")
      .replace("large outbound transfer occurred after execution", "execution 이후 대용량 outbound transfer가 발생했습니다")
      .replace("downloaded from", "에서 다운로드")
      .replace("started by", "실행 parent");
  }

  function setText(id, value) {
    const node = document.getElementById(id);
    if (node) node.textContent = String(value);
  }

  function setLink(id, href) {
    const node = document.getElementById(id);
    if (node && href) node.setAttribute("href", href);
  }

  function empty(message) {
    return `<div class="empty">${escapeHtml(message)}</div>`;
  }

  function clamp(value) {
    return Math.max(0, Math.min(100, Number(value) || 0));
  }

  function escapeAttr(value) {
    return escapeHtml(value).replace(/`/g, "&#096;");
  }

  function escapeHtml(value) {
    return String(value ?? "")
      .replace(/&/g, "&amp;")
      .replace(/</g, "&lt;")
      .replace(/>/g, "&gt;")
      .replace(/"/g, "&quot;")
      .replace(/'/g, "&#039;");
  }

  function pathToFileUrl(path) {
    if (!path) return "";
    if (String(path).startsWith("file:")) return path;
    const normalized = String(path).replace(/\\/g, "/");
    if (/^[A-Za-z]:\//.test(normalized)) return encodeURI(`file:///${normalized}`);
    return encodeURI(normalized);
  }

  function fileName(path) {
    return String(path || "").replace(/\\/g, "/").split("/").pop() || "";
  }
})();
