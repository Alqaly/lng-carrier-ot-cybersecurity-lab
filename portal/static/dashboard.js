(function (root) {
  'use strict';
  const numeric = (value, places = 2) => typeof value === 'number' && Number.isFinite(value) ? value.toFixed(places) : '—';
  const state = value => value?.ready === true ? value : {};
  const available = value => value === true ? 'AVAILABLE' : value === false ? 'UNAVAILABLE' : 'UNKNOWN';
  const feedback = (value, label) => label + (value === true ? '✓' : value === false ? '–' : '?');
  const records = value => Array.isArray(value) && value.every(item => item && typeof item === 'object' && !Array.isArray(item)) ? value : null;
  const metric = value => typeof value === 'number' && Number.isFinite(value) && value >= 0 ? String(value) : '—';
  function render(doc, snapshot) {
    const put = (id, value) => { doc.getElementById(id).textContent = value; };
    const el = (tag, text, cls) => {
      const node = doc.createElement(tag);
      if (text !== undefined) node.textContent = String(text);
      if (cls) node.className = cls;
      return node;
    };
    const c = state(snapshot?.cargo), p = state(snapshot?.pms), m = state(snapshot?.propulsion);
    const links = state(snapshot?.vessel).links || {};
    const fields = {
      c_ls: [c.levelSource, 'm'], c_ld: [c.levelDestination, 'm'],
      c_f: [typeof c.flowMeasured === 'number' ? c.flowMeasured * 3600 : undefined, 'm³/h', 0],
      c_kw: [c.pumpPowerKW, 'kW', 0], p_hz: [p.frequencyHz, 'Hz'],
      p_l: [p.totalLoadKW, 'kW', 0], p_r: [p.spinningReserveKW, 'kW', 0],
      m_rpm: [m.engineRPM, 'rpm', 1], m_lube: [m.lubeOilPressureBar, 'bar'],
      m_temp: [m.coolantTempC, '°C', 1], m_spd: [m.vesselSpeedKn, 'kn'],
      v_cargo_kw: [links.cargoElectricalLoadKW, 'kW', 0],
      iv_cargo: [links.cargoElectricalLoadKW, 'kW', 0], iv_aux: [links.propulsionAuxLoadKW, 'kW', 0]
    };
    for (const [id, [value, unit, places]] of Object.entries(fields)) put(id, numeric(value, places) + ' ' + unit);
    put('c_fb', feedback(c.valveFeedback, 'V') + ' / ' + feedback(c.pumpFeedback, 'P'));
    put('p_g', feedback(p.gen1BreakerFB, 'G1') + ' ' + feedback(p.gen2BreakerFB, 'G2'));
    put('v_bus', available(links.busAvailable));
    put('iv_bus', available(links.busAvailable));
    put('v_cargo_power', available(links.cargoPowerAvailable));
    put('iv_cp', available(links.cargoPowerAvailable));
    put('iv_pp', available(links.propulsionAuxPowerAvailable));
    const metrics = snapshot?.alarm_metrics || {};
    put('am_active', metric(metrics.active_total));
    put('am_unack', metric(metrics.unacknowledged_total));
    put('am_rate', metric(metrics.transitions_last_10m));
    put('am_flood', metrics.flood_warning === true ? 'YES' : metrics.flood_warning === false ? 'NO' : 'UNKNOWN');

    const history = records(snapshot?.history), alarms = records(snapshot?.alarms), catalog = records(snapshot?.catalog);
    const historyNode = doc.getElementById('alarm-history');
    historyNode.replaceChildren();
    if (history === null || history.length === 0) {
      const row = el('tr'), cell = el('td', history === null ? 'Alarm history unavailable.' : 'No transitions recorded.');
      cell.colSpan = 5; row.append(cell); historyNode.append(row);
    } else {
      for (const item of history.slice(0, 20)) {
        const row = el('tr');
        const date = typeof item.ts === 'number' && Number.isFinite(item.ts) ? new Date(item.ts * 1000) : null;
        const time = date && Number.isFinite(date.getTime()) ? date.toLocaleTimeString() : 'Unknown time';
        for (const text of [time, item.id, item.transition, item.priority, item.domain]) row.append(el('td', text ?? 'Unknown'));
        historyNode.append(row);
      }
    }
    const mini = doc.getElementById('alarm-mini');
    mini.replaceChildren();
    if (alarms === null) mini.append(el('p', 'Alarm state unavailable — do not infer no active alarms.'));
    else {
      const active = alarms.filter(item => item.active === true || item.active === 1);
      if (active.length === 0) mini.append(el('p', 'No active alarms reported by the chronicle.'));
      for (const item of active.slice(0, 5)) {
        const node = el('div', undefined, item.priority === 'MEDIUM' ? 'alarm medium' : 'alarm');
        node.append(el('strong', (item.priority ?? 'Unknown') + ' — ' + (item.message ?? 'Unknown alarm')));
        const ack = item.acked === true || item.acked === 1 ? 'ACK' : item.acked === false || item.acked === 0 ? 'UNACK' : 'ACK UNKNOWN';
        node.append(el('p', (item.domain ?? 'Unknown domain') + ' · ' + ack));
        if (item.rationalization?.operator_response) node.append(el('p', 'First response: ' + item.rationalization.operator_response));
        mini.append(node);
      }
    }
    const catalogue = doc.getElementById('alarm-catalog');
    catalogue.replaceChildren();
    if (catalog === null || catalog.length === 0) catalogue.append(el('p', catalog === null ? 'Alarm catalogue unavailable.' : 'No catalogue entries returned.'));
    else for (const item of catalog) {
      const node = el('div', undefined, item.priority === 'MEDIUM' ? 'alarm medium' : 'alarm');
      node.append(el('strong', (item.id ?? 'Unknown') + ' · ' + (item.priority ?? 'Unknown') + ' · ' + (item.title ?? 'Unknown')));
      node.append(el('p', 'Consequence: ' + (item.consequence ?? 'Unavailable')));
      node.append(el('p', 'Operator response: ' + (item.operator_response ?? 'Unavailable')));
      node.append(el('p', 'Timing: on ' + numeric(item.activation_delay_s) + 's / clear ' + numeric(item.clear_delay_s) + 's'));
      catalogue.append(node);
    }
    put('clock', snapshot ? 'Response received ' + new Date().toLocaleTimeString() + ' · see each source state' : 'Live data unavailable');
  }
  if (typeof module !== 'undefined') module.exports = {render, records, numeric};
  if (!root.document) return;
  const doc = root.document;
  doc.querySelectorAll('.tabs button').forEach(button => button.addEventListener('click', () => {
    doc.querySelectorAll('.tabs button, .page').forEach(node => node.classList.remove('active'));
    button.classList.add('active'); doc.getElementById(button.dataset.tab).classList.add('active');
  }));
  async function getJSON(url) {
    const controller = new AbortController(), timeout = setTimeout(() => controller.abort(), 5000);
    try {
      const response = await fetch(url, {signal: controller.signal});
      if (!response.ok) throw new Error('Unavailable');
      const value = await response.json();
      if (!value || typeof value !== 'object' || Array.isArray(value)) throw new Error('Invalid response');
      return value;
    } finally { clearTimeout(timeout); }
  }
  async function tick() {
    try { render(doc, await getJSON('/api/snapshot')); }
    catch (_) { render(doc, null); }
    setTimeout(tick, 2500);
  }
  async function contracts() {
    let values = {};
    try { values = await getJSON('/api/contracts'); } catch (_) {}
    for (const name of ['cargo', 'pms', 'propulsion']) {
      doc.getElementById('contract-' + name).textContent = JSON.stringify(values[name] || {ready: false, error: 'Contract unavailable'}, null, 2);
    }
    setTimeout(contracts, 10000);
  }
  tick(); contracts();
})(typeof window === 'undefined' ? {} : window);
