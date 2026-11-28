// "Analyze your own critique": lazy-loads the Pyodide worker on first use (focus or submit).
// Owner: pyodide-engineer (+ frontend-engineer for markup). Text stays on the device.
import { el, clear, fmt, sentClass, sentWord, badge } from "./ui.js";

const form = document.getElementById("analyze-form");
const box = document.getElementById("critique");
const btn = document.getElementById("analyze-btn");
const status = document.getElementById("analyze-status");
const out = document.getElementById("analyze-result");
const ASPECT_LABEL = { visuals: "Visuals", story: "Story", characters: "Characters", soundtrack: "Soundtrack" };

let worker = null;
let readyInfo = null;
let nextId = 1;
const pending = new Map();

function startWorker() {
  if (worker) return;
  status.textContent = "Loading Python and NLTK in your browser… (first time only, about 14 MB)";
  worker = new Worker("/js/analyzer.worker.mjs", { type: "module" });
  worker.onmessage = (e) => {
    const m = e.data;
    if (m.type === "progress") status.textContent = m.detail;
    else if (m.type === "ready") {
      readyInfo = m.info;
      status.textContent = `Ready: NLTK ${m.info.nltk} on Python ${m.info.python} (Pyodide), loaded in ${(m.info.ms / 1000).toFixed(1)} s.`;
    } else if (m.type === "result" || m.type === "error") {
      const p = pending.get(m.id);
      if (p) { pending.delete(m.id); m.type === "result" ? p.resolve(m.result) : p.reject(new Error(m.error)); }
      else if (m.type === "error") { status.textContent = `The analyzer could not start: ${m.error}`; btn.disabled = false; }
    }
  };
  worker.onerror = (e) => { status.textContent = `The analyzer could not start: ${e.message || "worker error"}`; btn.disabled = false; };
}

function analyze(text) {
  startWorker();
  const id = nextId++;
  return new Promise((resolve, reject) => { pending.set(id, { resolve, reject }); worker.postMessage({ id, text }); });
}

function render(r) {
  clear(out);
  const aspectCards = Object.entries(r.aspects).map(([a, d]) => el("div", { class: "result-card" }, [
    el("h4", {}, ASPECT_LABEL[a] || a),
    el("p", { class: `score ${sentClass(d.mean_compound)}` }, `${fmt(d.mean_compound)} ${sentWord(d.mean_compound)}`),
    el("p", { class: "muted small" }, `${d.mentions} sentence(s): ${d.terms.join(", ")}`),
  ]));
  out.append(
    el("div", { class: "result-grid" }, [
      el("div", { class: "result-card", id: "analyze-overall" }, [
        el("h3", {}, ["Overall ", badge("nltk")]),
        el("p", { class: `score ${sentClass(r.compound)}`, style: "font-size:1.8rem;margin:0", "data-compound": r.compound }, fmt(r.compound, 3)),
        el("p", {}, `${sentWord(r.compound)} · VADER compound (−1 to +1)`),
        el("p", { class: "muted small" }, `pos ${r.scores.pos} · neu ${r.scores.neu} · neg ${r.scores.neg} · ${r.n_sentences} sentence(s), ${r.n_tokens} tokens`),
      ]),
      ...aspectCards,
    ]),
    aspectCards.length ? null : el("p", { class: "muted small" }, "No visuals, story, characters or soundtrack words found."),
    el("h3", { style: "margin-top:1rem" }, "Sentence by sentence"),
    el("ol", { class: "sent-list" }, r.sentences.map((s) => el("li", {}, [
      el("span", { class: `score ${sentClass(s.compound)}` }, `${fmt(s.compound, 3)} `), s.text,
      s.aspects.length ? el("span", { class: "muted small" }, ` · ${s.aspects.map((a) => ASPECT_LABEL[a]).join(", ")}`) : null,
    ]))),
    r.top_words.length ? el("p", { class: "muted small" }, `Top content words (NLTK stopwords removed): ${r.top_words.map(([w, n]) => `${w} ×${n}`).join(", ")}`) : null,
  );
  out.hidden = false;
}

box.addEventListener("focus", startWorker, { once: true });
form.addEventListener("submit", async (e) => {
  e.preventDefault();
  const text = box.value.trim();
  if (!text) { status.textContent = "Type or paste a critique first."; box.focus(); return; }
  btn.disabled = true;
  if (!readyInfo) status.textContent = "Loading Python and NLTK in your browser…";
  try {
    const r = await analyze(text);
    render(r);
    status.textContent = `Analyzed ${r.n_sentences} sentence(s) with NLTK VADER in your browser. Overall: ${fmt(r.compound, 3)} (${r.label}).`;
  } catch (err) {
    status.textContent = `Analysis failed: ${err.message}`;
  } finally {
    btn.disabled = false;
  }
});

// Test hook (used by e2e parity tests): run the in-browser analyzer on arbitrary text.
window.__sclAnalyze = analyze;
