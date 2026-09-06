// DOM-adapter unit tests, not a substitute for real browser accessibility QA.
const {test} = require("node:test");
const assert = require("node:assert/strict");
const fs = require("node:fs");
const path = require("node:path");
const vm = require("node:vm");
const root = path.resolve(__dirname, "..");
const script = fs.readFileSync(path.join(root, "docs/assets/learning-journey.js"), "utf8");
const manifest = JSON.parse(fs.readFileSync(path.join(root, "docs/assets/learning-journey.json"), "utf8"));

class Element {
  constructor(tag) { this.tag = tag; this.children = []; this.events = {}; this.textContent = ""; }
  append(...nodes) { this.children.push(...nodes); }
  replaceChildren(...nodes) { this.children = nodes; }
  setAttribute(name, value) { this[name] = value; }
  addEventListener(name, handler) { this.events[name] = handler; }
  click() { this.clicked = true; }
  all() { return [this, ...this.children.flatMap(n => n.all ? n.all() : [])]; }
}
async function mount({saved = "[]", brokenStorage = false, brokenFetch = false} = {}) {
  const target = new Element("section"); const writes = []; const requested = [];
  const context = {
    URL, Blob, Set, Date, console, setTimeout,
    document: {
      currentScript: {src: "https://example.test/lng-course/assets/learning-journey.js"},
      getElementById: () => target,
      createElement: tag => new Element(tag),
      createTextNode: text => ({textContent: text}),
    },
    localStorage: {
      getItem: () => { if (brokenStorage) throw new Error("disabled"); return saved; },
      setItem: (key, value) => { if (brokenStorage) throw new Error("disabled"); writes.push([key, value]); },
    },
    fetch: async url => { requested.push(String(url)); return {ok: !brokenFetch, json: async () => manifest}; },
  };
  vm.runInNewContext(script, context);
  await new Promise(resolve => setImmediate(resolve));
  return {target, writes, requested};
}
test("course assets and chapter links respect a hosting subpath", async () => {
  const {target, requested} = await mount();
  assert.deepEqual(requested, ["https://example.test/lng-course/assets/learning-journey.json"]);
  const chapter = target.all().find(n => n.tag === "a");
  assert.equal(chapter.href, "https://example.test/lng-course/course/01-project-orientation/");
  assert.equal(target.all().filter(n => n.tag === "article").length, 8);
});
test("checkbox updates local practice and next recommendation", async () => {
  const {target, writes} = await mount();
  const check = target.all().find(n => n.type === "checkbox");
  check.checked = true; check.events.change();
  assert.equal(writes.length, 1); assert.equal(writes[0][1], '["01"]');
  assert.ok(target.all().some(n => n.textContent.startsWith("Next recommended: 02")));
});
test("investigator track renders all ten modules", async () => {
  const {target} = await mount();
  const select = target.all().find(n => n.tag === "select");
  select.value = "investigator"; select.events.change();
  assert.equal(target.all().filter(n => n.tag === "article").length, 10);
});
test("unavailable browser storage does not prevent learning", async () => {
  const {target} = await mount({brokenStorage: true});
  assert.equal(target.all().filter(n => n.tag === "article").length, 8);
  assert.ok(target.all().some(n => n.textContent.includes("storage is unavailable")));
});
test("malformed saved progress is ignored without crashing", async () => {
  const {target} = await mount({saved: '"invalid-state"'});
  assert.equal(target.all().find(n => n.tag === "progress").value, 0);
});
test("failed asset retrieval leaves an explicit chapter fallback", async () => {
  const {target} = await mount({brokenFetch: true});
  assert.ok(target.all().some(n => n.textContent.includes("available below")));
});
