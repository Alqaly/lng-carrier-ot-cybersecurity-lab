const test = require('node:test');
const assert = require('node:assert/strict');
const {render} = require('../portal/static/dashboard.js');

class Element {
  constructor(tag) { this.tag = tag; this.children = []; this._text = ''; }
  set textContent(value) { this._text = String(value); this.children = []; }
  get textContent() { return this._text + this.children.map(x => x.textContent).join(''); }
  set innerHTML(_) { throw new Error('Untrusted content must not be parsed as HTML'); }
  append(...nodes) { this.children.push(...nodes); }
  replaceChildren(...nodes) { this._text = ''; this.children = nodes; }
}
function document() {
  const nodes = new Map();
  return {
    createElement: tag => new Element(tag),
    getElementById: id => {
      if (!nodes.has(id)) nodes.set(id, new Element('div'));
      return nodes.get(id);
    }
  };
}
const text = (doc, id) => doc.getElementById(id).textContent;

test('populated alarm responses show active alarms, history and catalogue as text', () => {
  const doc = document(), markup = '<img src=x onerror=alert(1)>';
  render(doc, {
    alarms: [{active: 1, acked: 0, message: markup, priority: 'HIGH', domain: 'cargo'}],
    history: [{id: markup, ts: 1, transition: 'ACTIVE_UNACK'}],
    catalog: [{id: 'CARGO_NO_FLOW', title: markup, operator_response: markup}]
  });
  assert.match(text(doc, 'alarm-mini'), /UNACK/);
  for (const id of ['alarm-mini', 'alarm-history', 'alarm-catalog']) assert.ok(text(doc, id).includes(markup));
});

test('unavailable alarm sources are not presented as empty healthy lists', () => {
  const doc = document();
  render(doc, {alarms: {ready: false}, history: {ready: false}, catalog: {ready: false}});
  assert.match(text(doc, 'alarm-mini'), /Alarm state unavailable/);
  assert.match(text(doc, 'alarm-history'), /unavailable/);
  assert.match(text(doc, 'alarm-catalog'), /unavailable/);
  render(doc, {alarms: [], history: [], catalog: []});
  assert.match(text(doc, 'alarm-mini'), /No active alarms reported/);
  assert.match(text(doc, 'alarm-history'), /No transitions recorded/);
});

test('a lost response clears earlier readings, alarm metrics and history', () => {
  const doc = document();
  render(doc, {cargo: {ready: true, flowMeasured: 0.5}, alarm_metrics: {active_total: 7}, history: [{id: 'OLD', ts: 1}]});
  assert.equal(text(doc, 'c_f'), '1800 m³/h');
  render(doc, null);
  assert.equal(text(doc, 'c_f'), '— m³/h');
  assert.equal(text(doc, 'am_active'), '—');
  assert.equal(text(doc, 'am_flood'), 'UNKNOWN');
  assert.doesNotMatch(text(doc, 'alarm-history'), /OLD/);
  assert.equal(text(doc, 'clock'), 'Live data unavailable');
});

test('not-ready models and null flow never look like live zeros', () => {
  const doc = document();
  render(doc, {cargo: {ready: false, flowMeasured: 0.5}, vessel: {ready: false, links: {busAvailable: true}}});
  assert.equal(text(doc, 'c_f'), '— m³/h');
  assert.equal(text(doc, 'v_bus'), 'UNKNOWN');
  render(doc, {cargo: {ready: true, flowMeasured: null}});
  assert.equal(text(doc, 'c_f'), '— m³/h');
  render(doc, {cargo: {ready: true, flowMeasured: 0}});
  assert.equal(text(doc, 'c_f'), '0 m³/h');
});

test('malformed lists and missing timestamps retain an explicit uncertainty', () => {
  const doc = document();
  render(doc, {alarms: [null], catalog: [[]], history: [{id: 'event'}]});
  assert.match(text(doc, 'alarm-mini'), /unavailable/);
  assert.match(text(doc, 'alarm-catalog'), /unavailable/);
  assert.match(text(doc, 'alarm-history'), /Unknown time/);
});
