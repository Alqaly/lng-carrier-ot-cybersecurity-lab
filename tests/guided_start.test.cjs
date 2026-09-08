const assert = require('node:assert/strict');
const fs = require('node:fs');
const path = require('node:path');
const test = require('node:test');
const vm = require('node:vm');

const ROOT = path.resolve(__dirname, '..');
const lesson = JSON.parse(
  fs.readFileSync(path.join(ROOT, 'portal/static/first-session.json'), 'utf8'),
);
const script = fs.readFileSync(
  path.join(ROOT, 'portal/static/guided-start.js'),
  'utf8',
);
const portal = fs.readFileSync(path.join(ROOT, 'portal/static/index.html'), 'utf8');

class Element {
  constructor(tag = 'div') {
    this.tagName = tag.toUpperCase();
    this.children = [];
    this.listeners = {};
    this.dataset = {};
    this.className = '';
    this._textContent = '';
    this.innerHTML = '';
    this.value = '';
    this.disabled = false;
    this.hidden = false;
  }

  get textContent() {
    return this._textContent + this.children.map((child) => child.textContent || '').join('');
  }

  set textContent(value) {
    this._textContent = String(value ?? '');
    this.children = [];
  }

  append(...nodes) {
    this.children.push(...nodes);
  }

  appendChild(node) {
    this.children.push(node);
    return node;
  }

  replaceChildren(...nodes) {
    this._textContent = '';
    this.children = [...nodes];
  }

  setAttribute(name, value) {
    this[name] = String(value);
  }

  addEventListener(type, callback) {
    this.listeners[type] = callback;
  }

  focus() {}
}

function all(root) {
  return [root, ...root.children.flatMap(all)];
}

async function mount({ snapshot = null, fetchError = null } = {}) {
  const mountNode = new Element('div');
  const document = {
    createElement: (tag) => new Element(tag),
    getElementById: (id) => (id === 'guided-session' ? mountNode : null),
  };
  const storage = new Map();
  const fetch = async (url) => {
    if (url === '/static/first-session.json') {
      return { ok: true, json: async () => lesson };
    }
    if (url === '/api/snapshot') {
      if (fetchError) throw fetchError;
      return { ok: true, json: async () => snapshot || {} };
    }
    throw new Error(`unexpected URL: ${url}`);
  };
  const context = {
    AbortController,
    clearTimeout,
    console,
    document,
    fetch,
    localStorage: {
      getItem: (key) => storage.get(key) || null,
      setItem: (key, value) => storage.set(key, value),
    },
    module: { exports: {} },
    setTimeout: () => 0,
    window: { document },
  };
  vm.runInNewContext(script, context);
  await new Promise(setImmediate);
  return { mountNode, storage };
}

test('the first session is a seven-step causal path', () => {
  assert.equal(lesson.steps.length, 7);
  assert.deepEqual(
    lesson.steps.map((step) => step.id),
    ['process', 'power', 'transfer', 'packet', 'bias', 'supervision', 'explain'],
  );
  for (const step of lesson.steps) {
    for (const field of ['why', 'action', 'expect', 'trouble', 'explain', 'reference']) {
      assert.ok(step[field], `${step.id} is missing ${field}`);
    }
  }
});

test('the portal opens on the guide and does not coerce missing live data to zero', () => {
  assert.match(portal, /data-tab="learn" class="active">Guided start/);
  assert.match(portal, /<section id="learn" class="page active">/);
  assert.match(portal, /<summary>Explore reference panels<\/summary>/);
  assert.doesNotMatch(portal, /Number\(n\?\?0\)/);
  assert.doesNotMatch(portal, /flowMeasured\|\|0/);
});

test('commands are constrained to learning demos and capture', () => {
  const commands = lesson.steps.map((step) => step.command || '').filter(Boolean);
  assert.ok(commands.includes('./labctl demo pms'));
  assert.ok(commands.includes('./labctl demo cargo'));
  assert.ok(commands.includes('./labctl demo cargo-fault'));
  assert.ok(commands.some((command) => command.includes('./labctl capture cargo modbus')));
  assert.equal(commands.some((command) => /down\s+-v|git clean|reset --hard/.test(command)), false);
});

test('the lesson names evidence and publication boundaries', () => {
  assert.match(lesson.evidence_boundary, /not acceptance evidence/i);
  assert.match(lesson.claim_boundary, /FINAL: PASS/);
  assert.match(lesson.claim_boundary, /not commissioned/i);
});

test('formatters do not turn unavailable telemetry into zero or false', () => {
  const { number, flag } = require('../portal/static/guided-start.js');
  assert.equal(number(undefined), 'unavailable');
  assert.equal(number(Number.NaN), 'unavailable');
  assert.equal(number(0, 1, 1), '0.0');
  assert.equal(flag(undefined), 'UNKNOWN');
  assert.equal(flag(false), 'UNAVAILABLE');
  assert.equal(flag(true), 'AVAILABLE');
});

test('saved notes are restored only for known steps', () => {
  const { cleanProgress } = require('../portal/static/guided-start.js');
  const cleaned = cleanProgress(
    { step: 2, notes: { 0: 'pressure creates flow', 2: 42, 8: 'ignore me' } },
    lesson.steps.length,
  );
  assert.deepEqual(cleaned, { step: 2, notes: { 0: 'pressure creates flow' } });
});

test('telemetry distinguishes live, unavailable and constructed values', () => {
  const { telemetry } = require('../portal/static/guided-start.js');
  const live = Object.fromEntries(telemetry({
    cargo: { ready: true, flowMeasured: 0.5, valveFeedback: true, pumpFeedback: false },
    pms: { ready: true, frequencyHz: 60.0, spinningReserveKW: 850 },
    vessel: { ready: true, links: { busAvailable: true, cargoPowerAvailable: false } },
  }));
  assert.equal(live['Converted flow (m³/h)'], '1800');
  assert.equal(live['Bus frequency (Hz)'], '60.00');
  assert.equal(live['Bus supply'], 'AVAILABLE');

  const unavailable = Object.fromEntries(telemetry({}));
  assert.equal(unavailable['Converted flow (m³/h)'], 'unavailable');
  assert.equal(unavailable['Bus frequency (Hz)'], 'unavailable');
  assert.equal(unavailable['Bus supply'], 'UNKNOWN');
});

test('the mounted guide starts at step one and supports next-step navigation', async () => {
  const { mountNode } = await mount({ snapshot: { ready: true } });
  assert.match(mountNode.textContent, /First, follow the liquid/);
  const next = all(mountNode).find((node) => node.textContent === 'Next step');
  assert.ok(next, 'next-step button was not rendered');
  next.listeners.click();
  assert.match(mountNode.textContent, /Give the pump electrical power/);
});

test('the guide remains usable when the live snapshot is offline', async () => {
  const { mountNode } = await mount({ fetchError: new Error('offline') });
  assert.match(mountNode.textContent, /First, follow the liquid/);
  assert.match(mountNode.textContent, /Live observation unavailable/);
});
