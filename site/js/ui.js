// Small DOM helpers shared by the dashboard, methodology page and analyzer.
// All text goes through textContent (never innerHTML) so review text can't inject markup.

export function el(tag, attrs = {}, children = []) {
  const n = document.createElement(tag);
  for (const [k, v] of Object.entries(attrs || {})) {
    if (v == null || v === false) continue;
    n.setAttribute(k, v === true ? "" : String(v));
  }
  for (const c of [].concat(children)) {
    if (c == null || c === false) continue;
    n.append(c instanceof Node ? c : document.createTextNode(String(c)));
  }
  return n;
}

export function clear(n) {
  while (n.firstChild) n.removeChild(n.firstChild);
}

export function fmt(v, dp = 2) {
  if (v == null || Number.isNaN(v)) return "n/a";
  const s = Number(v).toFixed(dp);
  return v > 0 ? `+${s}` : s.replace("-", "−");
}

export function sentClass(v) {
  if (v == null) return "neu";
  return v >= 0.05 ? "pos" : v <= -0.05 ? "neg" : "neu";
}

export function sentWord(v) {
  if (v == null) return "";
  return v >= 0.05 ? "▲ praised" : v <= -0.05 ? "▼ criticised" : "● neutral";
}

const BADGES = {
  nltk: ["badge-nltk", "NLTK", "Result computed with NLTK"],
  spacy: ["badge-spacy", "spaCy", "Result computed with spaCy"],
  combo: ["badge-combo", "spaCy + NLTK", "Aspects found by spaCy, scored by NLTK VADER"],
  data: ["badge-data", "Dataset", "From the Rotten Tomatoes dataset"],
};
export function badge(kind) {
  const [cls, text, title] = BADGES[kind];
  return el("span", { class: `badge ${cls}`, title }, text);
}

export function quoteEl(q) {
  const cls = q.compound >= 0.05 ? "is-pos" : q.compound <= -0.05 ? "is-neg" : "";
  return el("blockquote", { class: `quote ${cls}` }, [
    el("p", {}, `“${q.text}”`),
    el("footer", {}, [
      "— ", el("cite", {}, q.critic), `, ${q.publisher}`, q.top_critic ? " (Top Critic)" : "",
      ` · ${q.review_type} · VADER ${fmt(q.compound)}`,
    ]),
  ]);
}

export function dataTable(summary, headers, rows) {
  return el("details", { class: "data-table" }, [
    el("summary", {}, summary),
    scrollTable(summary, el("table", {}, [
      el("thead", {}, el("tr", {}, headers.map((h) => el("th", { scope: "col" }, h)))),
      el("tbody", {}, rows.map((r) => el("tr", {}, r.map((c) => el("td", {}, String(c)))))),
    ])),
  ]);
}

export function themeColors() {
  const cs = getComputedStyle(document.documentElement);
  const v = (n) => cs.getPropertyValue(n).trim();
  return { text: v("--text"), muted: v("--muted"), grid: v("--border"), accent: v("--accent"), pos: v("--pos"), neg: v("--neg"), neu: v("--neu") };
}

// Wide tables scroll inside a keyboard-focusable region instead of widening the page.
export function scrollTable(label, table) {
  return el("div", { class: "table-scroll", tabindex: "0", role: "region", "aria-label": label }, table);
}
