(function () {
  "use strict";
  const script = document.currentScript;
  if (!script) return;
  const assetRoot = new URL(".", script.src);
  const siteRoot = new URL("../", assetRoot);
  const target = document.getElementById("learning-journey");
  if (!target) return;

  function element(tag, text, className) {
    const node = document.createElement(tag);
    if (text !== undefined) node.textContent = text;
    if (className) node.className = className;
    return node;
  }

  fetch(new URL("learning-journey.json", assetRoot))
    .then(function (response) {
      if (!response.ok) throw new Error("Learning path unavailable");
      return response.json();
    })
    .then(function (data) {
      if (data.schema_version !== 1 || !Array.isArray(data.modules)) throw new Error("Unsupported learning path");
      const storageKey = data.id + ":practice";
      const validIds = new Set(data.modules.map(function (m) { return m.id; }));
      let completed = new Set();
      let persistent = true;
      let track = "reader";
      try {
        const saved = JSON.parse(localStorage.getItem(storageKey) || "[]");
        if (Array.isArray(saved)) completed = new Set(saved.filter(function (id) { return validIds.has(id); }));
      } catch (_) { persistent = false; }

      target.replaceChildren();
      const controls = element("div", undefined, "journey-controls");
      const label = element("label", "Choose your path");
      label.htmlFor = "journey-track";
      const select = element("select");
      select.id = "journey-track";
      Object.entries(data.tracks).forEach(function (entry) {
        const option = element("option", entry[1]); option.value = entry[0]; select.append(option);
      });
      controls.append(label, select);
      const summary = element("p"); summary.setAttribute("aria-live", "polite");
      const progress = element("progress"); progress.setAttribute("aria-label", "Self-reported practice progress");
      const next = element("p", undefined, "journey-next");
      const notice = element("p", undefined, "journey-notice"); notice.setAttribute("role", "status");
      const cards = element("div", undefined, "journey-cards");
      const exportButton = element("button", "Export my practice record"); exportButton.type = "button";
      exportButton.addEventListener("click", function () {
        const record = { journey: data.id, exported_at: new Date().toISOString(), completed: Array.from(completed).sort(), claim_boundary: data.claim_boundary };
        const url = URL.createObjectURL(new Blob([JSON.stringify(record, null, 2)], {type: "application/json"}));
        const link = element("a"); link.href = url; link.download = "lng-learning-practice.json"; link.click();
        setTimeout(function () { URL.revokeObjectURL(url); }, 1000);
      });
      target.append(controls, summary, progress, next, notice, cards, exportButton);

      function updateSummary() {
        const visible = data.modules.filter(function (m) { return m.tracks.includes(track); });
        const count = visible.filter(function (m) { return completed.has(m.id); }).length;
        summary.textContent = count + " of " + visible.length + " practice checkpoints self-reported on this path.";
        progress.max = visible.length; progress.value = count;
        const recommendation = visible.find(function (m) { return !completed.has(m.id) && m.prerequisites.every(function (id) { return completed.has(id); }); });
        next.textContent = recommendation ? "Next recommended: " + recommendation.id + " — " + recommendation.title : (count === visible.length ? "Revisit an explanation without notes, then try the next path." : "Review the listed prerequisites before the next checkpoint.");
        notice.textContent = persistent ? "Stored only in this browser. Export a copy before clearing browser data." : "Browser storage is unavailable. Progress lasts for this page visit; export a copy before leaving.";
      }

      function renderCards() {
        cards.replaceChildren();
        data.modules.filter(function (m) { return m.tracks.includes(track); }).forEach(function (module) {
          const card = element("article", undefined, "journey-card");
          card.append(element("p", module.phase + " · " + module.id, "journey-phase"));
          const heading = element("h3");
          const link = element("a", module.title);
          link.href = new URL(module.chapter.replace(/\.md$/, "/"), siteRoot).href;
          heading.append(link); card.append(heading, element("p", module.objective));
          card.append(element("p", "Before this: " + (module.prerequisites.join(", ") || "No prerequisite"), "journey-prerequisites"));
          const details = element("details"); details.append(element("summary", "Practice, evidence and explain-back"));
          [["Practice", module.practice], ["Retain", module.evidence], ["Explain", module.explain]].forEach(function (part) {
            const paragraph = element("p"); paragraph.append(element("strong", part[0] + ": "), document.createTextNode(part[1])); details.append(paragraph);
          });
          card.append(details);
          const checkLabel = element("label", undefined, "journey-check");
          const checkbox = element("input"); checkbox.type = "checkbox"; checkbox.checked = completed.has(module.id);
          checkbox.addEventListener("change", function () {
            if (checkbox.checked) completed.add(module.id); else completed.delete(module.id);
            try { localStorage.setItem(storageKey, JSON.stringify(Array.from(completed).sort())); } catch (_) { persistent = false; }
            updateSummary();
          });
          checkLabel.append(checkbox, document.createTextNode(module.checkpoint)); card.append(checkLabel); cards.append(card);
        });
        updateSummary();
      }
      select.addEventListener("change", function () { track = select.value; renderCards(); });
      renderCards();
    })
    .catch(function () { target.replaceChildren(element("p", "The interactive path could not load. All ten chapters and the study method remain available below.")); });
})();
