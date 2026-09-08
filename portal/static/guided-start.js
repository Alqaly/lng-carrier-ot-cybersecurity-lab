(function (root) {
  'use strict';
  const KEY = 'lng-first-session-v1:notes';
  function number(value, scale = 1, places = 2) {
    return typeof value === 'number' && Number.isFinite(value) ? (value * scale).toFixed(places) : 'unavailable';
  }
  function flag(value) { return value === true ? 'AVAILABLE' : value === false ? 'UNAVAILABLE' : 'UNKNOWN'; }
  function cleanProgress(value, count) {
    if (!value || typeof value !== 'object') return {step: 0, notes: {}};
    const step = Number.isInteger(value.step) && value.step >= 0 && value.step < count ? value.step : 0;
    const notes = {};
    if (value.notes && typeof value.notes === 'object') {
      for (let i = 0; i < count; i++) if (typeof value.notes[i] === 'string') notes[i] = value.notes[i].slice(0, 8000);
    }
    return {step, notes};
  }
  function telemetry(snapshot) {
    const cargo = snapshot?.cargo?.ready === true ? snapshot.cargo : {};
    const pms = snapshot?.pms?.ready === true ? snapshot.pms : {};
    const vessel = snapshot?.vessel?.ready === true ? snapshot.vessel.links || {} : {};
    return [
      ['Bus supply', flag(vessel.busAvailable)], ['Cargo power', flag(vessel.cargoPowerAvailable)],
      ['Bus frequency (Hz)', number(pms.frequencyHz)], ['Spinning reserve (kW)', number(pms.spinningReserveKW, 1, 0)],
      ['Pump request', typeof cargo.pumpCmd === 'boolean' ? String(cargo.pumpCmd) : 'unknown'],
      ['Pump feedback', typeof cargo.pumpFeedback === 'boolean' ? String(cargo.pumpFeedback) : 'unknown'],
      ['Source level (m)', number(cargo.levelSource)], ['Destination level (m)', number(cargo.levelDestination)],
      ['Actual model flow (m³/s)', number(cargo.flow)], ['Measured model flow (m³/s)', number(cargo.flowMeasured)],
      ['Converted flow (m³/h)', number(cargo.flowMeasured, 3600, 0)]
    ];
  }
  const api = {number, flag, cleanProgress, telemetry};
  if (typeof module !== 'undefined' && module.exports) module.exports = api;
  if (!root.document) return;
  const doc = root.document;
  const target = doc.getElementById('guided-session');
  if (!target) return;
  function el(tag, text, cls) {
    const n = doc.createElement(tag); if (text !== undefined) n.textContent = text;
    if (cls) n.className = cls; return n;
  }
  async function start() {
    try {
      const response = await fetch('/static/first-session.json');
      if (!response.ok) throw new Error('Lesson unavailable');
      const course = await response.json();
      if (course.id !== 'lng-first-session-v1' || !Array.isArray(course.steps) || course.steps.length !== 7) throw new Error('Invalid lesson');
      let saved = null, persistent = true;
      try { saved = JSON.parse(localStorage.getItem(KEY)); } catch (_) { persistent = false; }
      let state = cleanProgress(saved, course.steps.length);
      function save() {
        try { localStorage.setItem(KEY, JSON.stringify(state)); } catch (_) { persistent = false; }
        storage.textContent = persistent ? 'Private practice notes stay in this browser. They are not verified evidence. Export before clearing browser data.' : 'Browser storage unavailable: notes last for this visit only. Export to keep them.';
      }
      const title = el('h1', course.title);
      const summary = el('p', course.outcome, 'guided-lead');
      const boundary = el('p', `${course.evidence_boundary} ${course.claim_boundary}`, 'guided-evidence-boundary');
      const nav = el('nav', undefined, 'guided-steps'); nav.setAttribute('aria-label', 'First session steps');
      const article = el('article', undefined, 'guided-card');
      const heading = el('h2'); heading.tabIndex = -1;
      const why = el('p'); const figure = el('img'); figure.src = '/static/diagrams/first-session.svg';
      figure.alt = 'Liquid moves from ship tank through pump and valve to shore. PMS supplies pump power. Commands and feedback cross Modbus; PLC publication through OPC UA to HMI/history is a separate commissioned path.';
      figure.className = 'guided-diagram';
      const layer = el('p', undefined, 'guided-layer');
      const action = el('p'); const command = el('pre', undefined, 'code');
      const expect = el('p'); const trouble = el('details'); trouble.append(el('summary', 'If the result is different')); const troubleText = el('p'); trouble.append(troubleText);
      const packet = el('div', undefined, 'guided-packet');
      packet.append(el('h3', 'Illustrative response — not your live capture'), el('pre', '00 01 | 00 00 | 00 05 | 01 | 04 | 02 | 07 08', 'code'), el('p', 'Transaction 1 · protocol 0 · length 5 · unit 1 · function 04 · 2 data bytes · value 1800. The requested address is in the request, not repeated in this response.'));
      const live = el('section', undefined, 'guided-live'); live.append(el('h3', 'Live model observation — separate from the illustration'));
      const freshness = el('p', 'Waiting for live model data. Lessons remain available.'); freshness.setAttribute('role', 'status');
      const values = el('dl', undefined, 'guided-values'); live.append(freshness, values);
      const question = el('label'); question.htmlFor = 'guided-notes';
      const notes = el('textarea'); notes.id = 'guided-notes'; notes.rows = 4; notes.maxLength = 8000;
      notes.placeholder = 'Your explanation, observation and uncertainty. Do not enter credentials.';
      const reference = el('a', 'Read the detailed lesson on GitHub');
      const controls = el('div', undefined, 'guided-controls');
      const previous = el('button', 'Previous'); const next = el('button', 'Next step');
      previous.type = next.type = 'button'; controls.append(previous, next);
      const storage = el('p', undefined, 'note');
      const exportButton = el('button', 'Export practice notes'); exportButton.type = 'button';
      exportButton.addEventListener('click', () => {
        const data = {journey: course.id, exported_at: new Date().toISOString(), ...state, boundary: 'Self-reported practice, not runtime acceptance evidence'};
        const url = URL.createObjectURL(new Blob([JSON.stringify(data, null, 2)], {type: 'application/json'}));
        const a = el('a'); a.href = url; a.download = 'lng-first-session-notes.json'; a.click(); setTimeout(() => URL.revokeObjectURL(url), 1000);
      });
      article.append(heading, why, figure, layer, el('h3', 'Do this'), action, command, el('h3', 'Expected observation'), expect, packet, trouble, live, el('h3', 'Explain it in your own words'), question, notes, reference, controls);
      target.replaceChildren(title, summary, boundary, nav, article, storage, exportButton);
      const buttons = course.steps.map((step, i) => {
        const b = el('button', `${i + 1}. ${step.title}`); b.type = 'button';
        b.addEventListener('click', () => move(i)); nav.append(b); return b;
      });
      function render(focus) {
        const step = course.steps[state.step];
        heading.textContent = `Step ${state.step + 1} of ${course.steps.length} — ${step.title}`;
        why.textContent = step.why; layer.textContent = `Focus in the diagram: ${step.layer}. Arrows describe relationships, not captured traffic.`;
        action.textContent = step.action; command.textContent = step.command; command.hidden = !step.command;
        expect.textContent = step.expect; troubleText.textContent = step.trouble; trouble.open = false;
        packet.hidden = step.id !== 'packet'; question.textContent = step.explain; notes.value = state.notes[state.step] || '';
        reference.href = 'https://github.com/Alqaly/lng-carrier-ot-cybersecurity-lab/blob/main/' + step.reference;
        previous.disabled = state.step === 0; next.disabled = state.step === course.steps.length - 1;
        next.textContent = next.disabled ? 'First-session path finished — review your explanation' : 'Next step';
        buttons.forEach((b, i) => { b.setAttribute('aria-current', i === state.step ? 'step' : 'false'); });
        save(); if (focus) heading.focus();
      }
      function move(i) { state.step = Math.max(0, Math.min(course.steps.length - 1, i)); render(true); }
      notes.addEventListener('input', () => { state.notes[state.step] = notes.value; save(); });
      previous.addEventListener('click', () => move(state.step - 1)); next.addEventListener('click', () => move(state.step + 1));
      render(false);
      async function poll() {
        try {
          const controller = new AbortController(); const timeout = setTimeout(() => controller.abort(), 10000);
          let response;
          try { response = await fetch('/api/snapshot', {signal: controller.signal}); } finally { clearTimeout(timeout); }
          if (!response.ok) throw new Error('Snapshot unavailable');
          const snapshot = await response.json();
          values.replaceChildren(); telemetry(snapshot).forEach(([label, value]) => { values.append(el('dt', label), el('dd', value)); });
          freshness.textContent = snapshot?.cargo?.ready === true ? `Model response received at ${new Date().toLocaleTimeString()}. This is not a PLC, PCAP or historian freshness check.` : 'Cargo model unavailable or not ready. Unknown values are not zero; the lesson remains readable.';
        } catch (_) {
          values.replaceChildren();
          freshness.textContent = 'Live observation unavailable. Previous readings cleared; no simulated sample has been substituted. You can continue reading.';
        }
        setTimeout(poll, 2500); // No overlapping requests, even with slow upstreams.
      }
      poll();
    } catch (_) {
      target.replaceChildren(el('p', 'The guided lesson could not load. Read the first Cargo investigation using the GitHub link below. No live evidence or progress has been inferred.'));
    }
  }
  start();
})(typeof window === 'undefined' ? {} : window);
