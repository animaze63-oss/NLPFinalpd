// Scifi Cinema Lens dashboard: film picker -> per-film dashboard.
// Reads only documented fields of data contract 1.x (schemas/*.schema.json) and tolerates
// missing optional ones. Routes: "/" (picker) and "/film/<slug>" (Netlify rewrites to index.html).
import { el, clear, fmt, sentClass, sentWord, badge, quoteEl, dataTable, themeColors } from "./ui.js";

const ASPECTS = ["visuals", "story", "characters", "soundtrack"];
const ASPECT_LABEL = { visuals: "Visuals", story: "Story", characters: "Characters", soundtrack: "Soundtrack" };
const view = document.getElementById("view");
const charts = [];
let films = null;
let currentFilm = null;
let spaNavigation = false; // true after an in-app link click: move focus to the new heading

async function getJSON(url) {
  const r = await fetch(url, { headers: { Accept: "application/json" } });
  if (!r.ok) throw new Error(`${url}: HTTP ${r.status}`);
  return r.json();
}

function destroyCharts() {
  while (charts.length) charts.pop().destroy();
}

function slugFromPath() {
  const m = location.pathname.match(/^\/film\/([a-z0-9-]+)\/?$/);
  return m ? m[1] : null;
}

function legend() {
  return el("section", { class: "legend", "aria-label": "Which library produced each result" }, [
    el("strong", {}, "Legend:"),
    el("dl", {}, [
      el("div", {}, [el("dt", {}, badge("nltk")), el("dd", {}, "tokenizing, stopwords, VADER sentiment, word counts, key phrases")]),
      el("div", {}, [el("dt", {}, badge("spacy")), el("dd", {}, "named entities, EntityRuler, noun chunks, dependency parse")]),
      el("div", {}, [el("dt", {}, badge("combo")), el("dd", {}, "spaCy finds the aspect, NLTK VADER scores it")]),
      el("div", {}, [el("dt", {}, badge("data")), el("dd", {}, "Rotten Tomatoes metadata")]),
    ]),
  ]);
}

function panel({ id, title, source, how, span = "", body }) {
  return el("section", { class: `panel ${span}`, id, "aria-labelledby": `${id}-h` }, [
    el("div", { class: "panel-head" }, [el("h2", { id: `${id}-h` }, title), badge(source)]),
    how ? el("p", { class: "how" }, how) : null,
    ...[].concat(body),
  ]);
}

function setTitle(t) {
  document.title = t ? `${t} | Scifi Cinema Lens` : "Scifi Cinema Lens: what critics say about sci-fi films";
}

// ------------------------------------------------------------------ picker
function renderPicker() {
  destroyCharts();
  currentFilm = null;
  setTitle(null);
  clear(view);
  const list = el("ul", { class: "film-grid", id: "film-list" });
  const search = el("input", { type: "search", id: "film-search", placeholder: "Title or director", autocomplete: "off" });
  const sort = el("select", { id: "film-sort" }, [
    el("option", { value: "year" }, "Release year"),
    el("option", { value: "title" }, "Title"),
    el("option", { value: "sentiment" }, "VADER sentiment (high to low)"),
    el("option", { value: "tomatometer" }, "Tomatometer (high to low)"),
  ]);
  const count = el("p", { class: "muted small", id: "film-count", role: "status" });

  function draw() {
    const q = search.value.trim().toLowerCase();
    let rows = films.films.filter((f) => !q || f.title.toLowerCase().includes(q) || (f.directors || []).join(" ").toLowerCase().includes(q));
    const key = sort.value;
    rows = rows.slice().sort((a, b) =>
      key === "title" ? a.title.localeCompare(b.title)
        : key === "sentiment" ? (b.mean_compound ?? -2) - (a.mean_compound ?? -2)
          : key === "tomatometer" ? (b.tomatometer ?? -1) - (a.tomatometer ?? -1)
            : (a.year ?? 0) - (b.year ?? 0));
    clear(list);
    for (const f of rows) list.append(filmCard(f));
    count.textContent = `${rows.length} of ${films.films.length} films`;
  }
  search.addEventListener("input", draw);
  sort.addEventListener("change", draw);

  view.append(
    el("section", { class: "hero" }, [
      el("h1", {}, "What do critics praise in sci-fi?"),
      el("p", { class: "lead" }, [
        "Pick a science-fiction film to see what critics say about its ",
        el("strong", {}, "visuals"), ", ", el("strong", {}, "story"), ", ", el("strong", {}, "characters"), " and ",
        el("strong", {}, "soundtrack"), `. ${films.build.n_reviews.toLocaleString("en")} Rotten Tomatoes critic reviews of ${films.build.n_films} films, analysed with NLTK and spaCy at build time.`,
      ]),
    ]),
    legend(),
    el("div", { class: "toolbar" }, [
      el("div", { class: "field" }, [el("label", { for: "film-search" }, "Find a film"), search]),
      el("div", { class: "field" }, [el("label", { for: "film-sort" }, "Sort by"), sort]),
      count,
    ]),
    el("h2", { class: "visually-hidden" }, "Films"),
    list,
    overviewPanel(),
  );
  draw();
  drawOverviewChart();
}

function filmCard(f) {
  const chips = el("ul", { class: "chips", "aria-label": "Aspect sentiment (spaCy + NLTK)" });
  for (const a of ASPECTS) {
    const v = f.aspects?.[a];
    chips.append(el("li", { class: "chip" }, [`${ASPECT_LABEL[a]} `, el("span", { class: `score ${sentClass(v)}` }, fmt(v))]));
  }
  return el("li", { class: "film-card" }, [
    el("h3", {}, el("a", { class: "stretched", href: `/film/${f.slug}` }, f.title)),
    el("p", { class: "meta" }, `${f.year ?? ""} · ${(f.directors || []).join(", ")}`),
    el("p", { class: "meta" }, [
      badge("data"), ` Tomatometer ${f.tomatometer ?? "n/a"}%  `, badge("nltk"), " VADER ",
      el("span", { class: `score ${sentClass(f.mean_compound)}` }, fmt(f.mean_compound)),
    ]),
    el("p", { class: "meta" }, [badge("combo"), " Aspect scores"]),
    chips,
    el("p", { class: "meta" }, `${f.n_reviews} reviews`),
  ]);
}

// Aspect colours for spaCy charts (each has >= 3:1 contrast on both theme backgrounds).
const ASPECT_COLOR = { visuals: "#1f8fd6", story: "#8a63d2", characters: "#d97706", soundtrack: "#2a9d5c" };

function spacyOverviewPanel() {
  const rows = films.films.map((f) => [f.title, ...ASPECTS.map((a) => String(f.aspect_mentions?.[a] ?? 0))]);
  return panel({
    id: "spacy-overview", title: "What reviewers talk about: aspect mentions found by spaCy", source: "spacy", span: "span-6",
    how: "For each film, the number of review sentences where spaCy found a visuals, story, characters or soundtrack aspect (lemmas, noun chunks, phrase matches and dependency links).",
    body: [el("div", { class: "chart-box xtall" }, el("canvas", { id: "spacy-overview-chart", role: "img", "aria-label": "Stacked bar chart of aspect mentions found by spaCy for each film; the data table below lists the values." })),
      dataTable("Data table: aspect mentions per film (spaCy)", ["Film", ...ASPECTS.map((a) => ASPECT_LABEL[a])], rows)],
  });
}

function heatCell(v, n) {
  if (v == null || !n) return el("td", { class: "heat na" }, "n/a");
  const pct = Math.round(10 + Math.min(1, Math.abs(v)) * 30);
  const tone = v >= 0.05 ? "--pos" : v <= -0.05 ? "--neg" : "--neu";
  return el("td", { class: "heat", style: `background: color-mix(in srgb, var(${tone}) ${pct}%, transparent)` },
    [el("span", { class: "heat-v" }, `${v >= 0.05 ? "▲" : v <= -0.05 ? "▼" : "●"} ${fmt(v)}`), el("span", { class: "heat-n" }, ` ${n}×`)]);
}

function comboHeatmapPanel() {
  const head = el("tr", {}, [el("th", { scope: "col" }, "Film"), ...ASPECTS.map((a) => el("th", { scope: "col" }, ASPECT_LABEL[a]))]);
  const body = films.films.map((f) => el("tr", {}, [
    el("th", { scope: "row" }, el("a", { href: `/film/${f.slug}` }, f.title)),
    ...ASPECTS.map((a) => heatCell(f.aspects?.[a], f.aspect_mentions?.[a])),
  ]));
  const table = el("table", { class: "heatmap" }, [
    el("caption", { class: "visually-hidden" }, "Mean NLTK VADER score of the sentences where spaCy found each aspect, per film; n× is the number of sentences."),
    el("thead", {}, head), el("tbody", {}, body)]);
  return panel({
    id: "combo-heatmap", title: "Aspect sentiment heatmap: praised ▲ or criticised ▼", source: "combo", span: "span-6",
    how: "spaCy finds the sentences about each aspect; NLTK VADER scores them. Each cell is the mean score (−1 to +1) with the number of sentences. Stronger colour means a stronger opinion.",
    body: el("div", { class: "table-scroll", tabindex: "0", role: "region", "aria-label": "Aspect sentiment heatmap" }, table),
  });
}

function overviewPanel() {
  const rows = films.films.map((f) => [f.title, `${f.tomatometer ?? "n/a"}%`, fmt(f.mean_compound)]);
  return el("div", { class: "grid", style: "margin-top:1.6rem" }, [
    spacyOverviewPanel(),
    comboHeatmapPanel(),
    panel({
      id: "overview", title: "All films: Tomatometer vs average VADER score", source: "nltk",
      how: "Each dot is a film. Horizontal: share of Fresh reviews on Rotten Tomatoes (dataset). Vertical: mean NLTK VADER compound score of the reviews in our sample (-1 to +1).",
      body: [el("div", { class: "chart-box tall" }, el("canvas", { id: "overview-chart", role: "img", "aria-label": "Scatter plot of Tomatometer against mean VADER score per film; the data table below lists the values." })),
        dataTable("Data table: Tomatometer and VADER per film", ["Film", "Tomatometer", "Mean VADER"], rows)],
    }),
  ]);
}

function drawOverviewChart() {
  if (!window.Chart) return;
  const c = themeColors();
  const axis0 = { ticks: { color: c.muted }, grid: { color: c.grid } };
  charts.push(new window.Chart(document.getElementById("spacy-overview-chart"), {
    type: "bar",
    data: { labels: films.films.map((f) => f.title),
      datasets: ASPECTS.map((a) => ({ label: ASPECT_LABEL[a], data: films.films.map((f) => f.aspect_mentions?.[a] ?? 0), backgroundColor: ASPECT_COLOR[a] })) },
    options: { indexAxis: "y", maintainAspectRatio: false, animation: false,
      plugins: { legend: { labels: { color: c.text } } },
      scales: { x: { ...axis0, stacked: true, beginAtZero: true, title: { display: true, text: "Sentences mentioning the aspect (spaCy)", color: c.text } },
        y: { ...axis0, stacked: true, ticks: { color: c.text, autoSkip: false } } } },
  }));
  const ctx = document.getElementById("overview-chart");
  charts.push(new window.Chart(ctx, {
    type: "scatter",
    data: { datasets: [{ label: "Films", data: films.films.map((f) => ({ x: f.tomatometer, y: f.mean_compound, t: f.title })),
      backgroundColor: c.accent, pointRadius: 6, pointHoverRadius: 8 }] },
    options: {
      maintainAspectRatio: false, animation: false,
      plugins: { legend: { display: false }, tooltip: { callbacks: { label: (i) => `${i.raw.t}: ${i.raw.x}% / ${fmt(i.raw.y)}` } } },
      scales: {
        x: { title: { display: true, text: "Tomatometer (%)", color: c.text }, min: 0, max: 100, ticks: { color: c.muted }, grid: { color: c.grid } },
        y: { title: { display: true, text: "Mean VADER compound", color: c.text }, min: -0.2, max: 0.8, ticks: { color: c.muted }, grid: { color: c.grid } },
      },
    },
  }));
}

// ------------------------------------------------------------------ dashboard
async function renderFilm(slug) {
  destroyCharts();
  clear(view);
  view.append(el("p", { class: "notice" }, "Loading film…"));
  let f;
  try {
    f = await getJSON(`/data/film/${slug}.json`);
  } catch (e) {
    clear(view);
    view.append(el("a", { class: "back-link", href: "/" }, "← All films"),
      el("div", { class: "notice error", role: "alert" }, [el("h1", {}, "Film not found"), el("p", {}, `We have no data for “${slug}”. Pick a film from the list.`)]));
    setTitle("Film not found");
    return;
  }
  currentFilm = f;
  setTitle(f.title);
  clear(view);
  const s = f.sentiment;
  view.append(
    el("a", { class: "back-link", href: "/" }, "← All films"),
    el("section", { class: "film-hero", "aria-labelledby": "film-title" }, [
      el("div", { class: "panel-head" }, [badge("data"), el("span", { class: "muted small" }, "Rotten Tomatoes metadata")]),
      el("h1", { id: "film-title", tabindex: "-1" }, f.title),
      el("p", { class: "muted" }, `${f.year ?? ""} · Directed by ${(f.directors || []).join(", ") || "unknown"}${f.studio ? " · " + f.studio : ""}`),
      f.cast?.length ? el("p", { class: "muted small" }, `Starring ${f.cast.join(", ")}`) : null,
      f.critics_consensus ? el("p", { class: "consensus" }, [`Critics consensus: “${f.critics_consensus}” `, el("span", { class: "muted small" }, "(Rotten Tomatoes)")]) : null,
      el("div", { class: "kpis" }, [
        kpi(`${f.tomatometer ?? "n/a"}%`, "Tomatometer (all reviews)"),
        kpi(`${f.n_fresh} / ${f.n_rotten}`, "Fresh / Rotten in our sample"),
        kpi(el("span", { class: sentClass(s.mean_compound) }, fmt(s.mean_compound)), ["Mean VADER score ", badge("nltk")]),
        kpi(String(f.n_reviews), "Reviews analysed"),
      ]),
      el("p", { class: "small", style: "margin-top:0.8rem" }, el("a", { href: f.rt_url }, "See this film on Rotten Tomatoes")),
    ]),
    legend(),
    el("div", { class: "grid" }, [
      aspectsPanel(f),
      sentimentPanel(f),
      quotesPanel(f),
      wordsPanel(f),
      phrasesPanel(f),
      chunksPanel(f),
      entitiesPanel(f),
      timelinePanel(f),
    ]),
  );
  drawFilmCharts(f);
  if (spaNavigation) document.getElementById("film-title").focus({ preventScroll: true });
}

function kpi(v, k) {
  return el("div", { class: "kpi" }, [el("span", { class: "v" }, v), el("span", { class: "k" }, k)]);
}

function aspectsPanel(f) {
  const reels = el("div", { class: "reels" });
  const rows = [];
  for (const a of ASPECTS) {
    const d = f.aspects[a];
    rows.push([ASPECT_LABEL[a], d.mentions, fmt(d.mean_compound), `${d.positive} / ${d.neutral} / ${d.negative}`]);
    const ops = (d.top_opinions || []).slice(0, 6).map((o) =>
      el("li", { class: "chip" }, [o.word, o.negated ? " (negated)" : "", el("span", { class: "src" }, ` ×${o.count}`)]));
    const terms = (d.top_terms || []).slice(0, 5).map(([t, n]) => el("li", { class: "chip" }, `${t} ×${n}`));
    reels.append(el("article", { class: "reel", "aria-labelledby": `reel-${a}` }, [
      el("h3", { id: `reel-${a}` }, [ASPECT_LABEL[a], el("span", { class: `score ${sentClass(d.mean_compound)}` }, `${fmt(d.mean_compound)} ${sentWord(d.mean_compound)}`)]),
      el("p", { class: "muted small" }, `${d.mentions} mentions in ${d.reviews} reviews · ${d.positive} positive, ${d.neutral} neutral, ${d.negative} negative sentences`),
      terms.length ? el("div", {}, [el("span", { class: "small" }, ["Aspect terms ", badge("spacy")]), el("ul", { class: "chips" }, terms)]) : null,
      ops.length ? el("div", {}, [el("span", { class: "small" }, ["Opinion words (dependency links) ", badge("spacy")]), el("ul", { class: "chips" }, ops)])
        : el("p", { class: "muted small" }, "No opinion words linked by the parser."),
      ...(d.quotes || []).map((q) => quoteEl(q)),
      d.mentions === 0 ? el("p", { class: "muted small" }, "Critics in this sample did not mention this aspect.") : null,
    ]));
  }
  return panel({
    id: "aspects", title: "What critics say about each aspect", source: "combo",
    how: "spaCy finds mentions of visuals, story, characters and soundtrack (lemmas, phrases such as “sound design”, and dependency links to opinion adjectives); NLTK VADER scores each sentence that mentions the aspect. Bars show the mean score from -1 (criticised) to +1 (praised).",
    body: [el("div", { class: "chart-box" }, el("canvas", { id: "aspect-chart", role: "img", "aria-label": `Mean sentiment per aspect for ${f.title}; values are in the table below.` })),
      dataTable("Data table: aspect sentiment", ["Aspect", "Mentions", "Mean VADER", "Pos / neu / neg sentences"], rows), reels],
  });
}

function sentimentPanel(f) {
  const s = f.sentiment;
  const rows = s.histogram.map((h) => [`${fmt(h.from)} to ${fmt(h.to)}`, h.n]);
  return panel({
    id: "sentiment", title: "Overall review sentiment", source: "nltk", span: "span-6",
    how: `NLTK VADER compound score of each review, with sci-fi plot words (alien, war, dark…) neutralised. ${s.positive} positive (≥ 0.05), ${s.neutral} neutral, ${s.negative} negative (≤ -0.05).`,
    body: [el("div", { class: "chart-box" }, el("canvas", { id: "sentiment-chart", role: "img", "aria-label": "Histogram of review VADER scores; values in the table below." })),
      dataTable("Data table: review score histogram", ["VADER score range", "Reviews"], rows)],
  });
}

function quotesPanel(f) {
  const pos = (f.quotes?.most_positive || []).slice(0, 2).map((q) => quoteEl(q));
  const neg = (f.quotes?.most_negative || []).slice(0, 2).map((q) => quoteEl(q));
  return panel({
    id: "quotes", title: "Most positive and most negative reviews", source: "nltk", span: "span-6",
    how: "Ranked by NLTK VADER review score. Excerpts are the critics' own words, credited to the critic and publication.",
    body: el("div", { class: "two-col" }, [
      el("div", {}, [el("h3", {}, "Highest VADER score"), ...pos]),
      el("div", {}, [el("h3", {}, "Lowest VADER score"), ...(neg.length ? neg : [el("p", { class: "muted small" }, "No review in this sample scored below zero.")])]),
    ]),
  });
}

function barList(items, cls, labelFn = (x) => x[0], valueFn = (x) => x[1]) {
  const max = Math.max(1, ...items.map(valueFn));
  return el("ul", { class: `barlist ${cls}` }, items.map((x) => el("li", {}, [
    el("span", {}, labelFn(x)),
    el("span", { class: "bar", style: `width:${Math.max(3, (valueFn(x) / max) * 100)}%`, "aria-hidden": "true" }),
    el("span", { class: "score" }, String(valueFn(x))),
  ])));
}

function wordsPanel(f) {
  return panel({
    id: "words", title: "Praise words vs criticism words", source: "nltk", span: "span-6",
    how: "NLTK word_tokenize on each sentence, English stopwords and a film stopword list removed, then FreqDist. Left: sentences VADER rated positive. Right: negative.",
    body: el("div", { class: "two-col" }, [
      el("div", {}, [el("h3", { class: "pos" }, "▲ In praising sentences"), barList(f.top_words.positive.slice(0, 12), "pos")]),
      el("div", {}, [el("h3", { class: "neg" }, "▼ In critical sentences"), f.top_words.negative.length ? barList(f.top_words.negative.slice(0, 12), "neg") : el("p", { class: "muted small" }, "Too few negative sentences.")]),
    ]),
  });
}

function phrasesPanel(f) {
  const lab = (x) => x.phrase;
  const val = (x) => x.count;
  return panel({
    id: "phrases", title: "Key phrases (collocations)", source: "nltk", span: "span-6",
    how: "NLTK BigramCollocationFinder and TrigramCollocationFinder, ranked by likelihood ratio after a frequency filter (seen at least twice). Count = times the phrase appears.",
    body: el("div", { class: "two-col" }, [
      el("div", {}, [el("h3", {}, "All reviews"), f.collocations.all.length ? barList(f.collocations.all.slice(0, 10), "", lab, val) : el("p", { class: "muted small" }, "No repeated phrases.")]),
      el("div", {}, [el("h3", { class: "pos" }, "▲ Praising sentences"), f.collocations.positive.length ? barList(f.collocations.positive.slice(0, 6), "pos", lab, val) : el("p", { class: "muted small" }, "None repeated."),
        el("h3", { class: "neg", style: "margin-top:0.8rem" }, "▼ Critical sentences"), f.collocations.negative.length ? barList(f.collocations.negative.slice(0, 6), "neg", lab, val) : el("p", { class: "muted small" }, "None repeated.")]),
    ]),
  });
}

function chunksPanel(f) {
  const withA = f.noun_chunks.filter((c) => c.aspect);
  const other = f.noun_chunks.filter((c) => !c.aspect);
  const groups = ASPECTS.map((a) => {
    const xs = withA.filter((c) => c.aspect === a).slice(0, 6);
    return xs.length ? el("div", { class: "ent-group" }, [el("h3", {}, ASPECT_LABEL[a]), el("ul", { class: "chips" }, xs.map((c) => el("li", { class: "chip" }, `${c.phrase} ×${c.count}`)))]) : null;
  });
  const top = f.noun_chunks.slice(0, 10);
  const chart = top.length ? [el("div", { class: "chart-box" }, el("canvas", { id: "chunks-chart", role: "img", "aria-label": "Bar chart of the most frequent noun chunks found by spaCy, coloured by aspect; the data table below lists the values." })),
    dataTable("Data table: top noun chunks (spaCy)", ["Noun chunk", "Aspect", "Count"], top.map((c) => [c.phrase, c.aspect ? ASPECT_LABEL[c.aspect] : "other", String(c.count)]))] : [];
  return panel({
    id: "chunks", title: "Noun-chunk aspects", source: "spacy", span: "span-6",
    how: "spaCy noun chunks (determiners and stopwords removed, head noun lemmatised), mapped to an aspect when the chunk contains a lexicon phrase or its head lemma is an aspect trigger.",
    body: [...chart, ...groups, other.length ? el("div", { class: "ent-group" }, [el("h3", {}, "Other frequent topics"), el("ul", { class: "chips" }, other.slice(0, 10).map((c) => el("li", { class: "chip" }, `${c.phrase} ×${c.count}`)))]) : null],
  });
}

const ENT_LABELS = {
  PERSON: "People", WORK_OF_ART: "Films and works compared", FRANCHISE: "Franchises", STUDIO: "Studios",
  FILM_TECH: "Formats and film technology", ORG: "Organisations (model)", GPE: "Places", NORP: "Groups and nationalities",
};
function entitiesPanel(f) {
  const by = {};
  for (const e of f.entities) (by[e.label] ||= []).push(e);
  const order = Object.keys(ENT_LABELS).filter((k) => by[k]).concat(Object.keys(by).filter((k) => !ENT_LABELS[k]));
  const topEnts = [...f.entities].sort((a, b) => b.count - a.count).slice(0, 10);
  const chart = topEnts.length ? [el("div", { class: "chart-box" }, el("canvas", { id: "entities-chart", role: "img", "aria-label": "Bar chart of the most mentioned named entities found by spaCy; the data table below lists the values." })),
    dataTable("Data table: top named entities (spaCy)", ["Entity", "Label", "Found by", "Count"], topEnts.map((e) => [e.text, e.label, e.source === "ruler" ? "EntityRuler" : "model", String(e.count)]))] : [];
  return panel({
    id: "entities", title: "Named entities: people, films, studios, franchises, tech", source: "spacy", span: "span-6",
    how: "spaCy en_core_web_sm NER plus an EntityRuler placed before it. Dashed chips come from the EntityRuler (patterns seeded from this dataset's directors, cast and titles, plus curated STUDIO, FRANCHISE and FILM_TECH lists); solid chips come from the statistical model. In the chart, blue bars were found by the EntityRuler and purple bars by the statistical model.",
    body: order.length ? [...chart, ...order.map((k) => el("div", { class: "ent-group" }, [
      el("h3", {}, `${ENT_LABELS[k] || k} (${k})`),
      el("ul", { class: "chips" }, by[k].slice(0, 10).map((e) => el("li", { class: `chip ${e.source === "ruler" ? "ruler" : ""}` }, [
        e.text, el("span", { class: "src" }, ` ×${e.count} · ${e.source === "ruler" ? "EntityRuler" : "model"}`)]))),
    ]))] : el("p", { class: "muted" }, "No entities found."),
  });
}

function timelinePanel(f) {
  const rows = f.timeline.map((t) => [t.year, t.n, fmt(t.mean_compound)]);
  return panel({
    id: "timeline", title: "Sentiment by review year", source: "nltk", span: "span-6",
    how: "Mean NLTK VADER review score grouped by the year the review was published (bar labels show the number of reviews).",
    body: [el("div", { class: "chart-box" }, el("canvas", { id: "timeline-chart", role: "img", "aria-label": "Mean VADER score by review year; values in the table below." })),
      dataTable("Data table: sentiment by year", ["Year", "Reviews", "Mean VADER"], rows)],
  });
}

function drawFilmCharts(f) {
  if (!window.Chart) return;
  const c = themeColors();
  const colorFor = (v) => (v == null ? c.neu : v >= 0.05 ? c.pos : v <= -0.05 ? c.neg : c.neu);
  const axis = { ticks: { color: c.muted }, grid: { color: c.grid } };
  const av = ASPECTS.map((a) => f.aspects[a].mean_compound);
  charts.push(new window.Chart(document.getElementById("aspect-chart"), {
    type: "bar",
    data: { labels: ASPECTS.map((a) => `${ASPECT_LABEL[a]} (${f.aspects[a].mentions})`),
      datasets: [{ label: "Mean VADER of aspect sentences", data: av.map((v) => v ?? 0), backgroundColor: av.map(colorFor), borderRadius: 6 }] },
    options: { indexAxis: "y", maintainAspectRatio: false, animation: false, plugins: { legend: { display: false } },
      scales: { x: { ...axis, min: -1, max: 1, title: { display: true, text: "◀ criticised   mean VADER compound   praised ▶", color: c.text } }, y: { ...axis, ticks: { color: c.text } } } },
  }));
  const top = f.noun_chunks.slice(0, 10);
  if (top.length) charts.push(new window.Chart(document.getElementById("chunks-chart"), {
    type: "bar",
    data: { labels: top.map((x) => x.phrase), datasets: [{ label: "Mentions", data: top.map((x) => x.count), backgroundColor: top.map((x) => ASPECT_COLOR[x.aspect] || c.neu), borderRadius: 4 }] },
    options: { indexAxis: "y", maintainAspectRatio: false, animation: false, plugins: { legend: { display: false }, tooltip: { callbacks: { afterLabel: (i) => `Aspect: ${top[i.dataIndex].aspect ? ASPECT_LABEL[top[i.dataIndex].aspect] : "other"}` } } },
      scales: { x: { ...axis, beginAtZero: true, ticks: { color: c.muted, precision: 0 } }, y: { ...axis, ticks: { color: c.text } } } },
  }));
  const ents = [...f.entities].sort((a, b) => b.count - a.count).slice(0, 10);
  if (ents.length) charts.push(new window.Chart(document.getElementById("entities-chart"), {
    type: "bar",
    data: { labels: ents.map((e) => `${e.text} (${e.label})`), datasets: [{ label: "Mentions", data: ents.map((e) => e.count), backgroundColor: ents.map((e) => (e.source === "ruler" ? ASPECT_COLOR.visuals : ASPECT_COLOR.story)), borderRadius: 4 }] },
    options: { indexAxis: "y", maintainAspectRatio: false, animation: false, plugins: { legend: { display: false }, tooltip: { callbacks: { afterLabel: (i) => (ents[i.dataIndex].source === "ruler" ? "Found by the EntityRuler" : "Found by the statistical NER model") } } },
      scales: { x: { ...axis, beginAtZero: true, ticks: { color: c.muted, precision: 0 } }, y: { ...axis, ticks: { color: c.text } } } },
  }));
  const h = f.sentiment.histogram;
  charts.push(new window.Chart(document.getElementById("sentiment-chart"), {
    type: "bar",
    data: { labels: h.map((b) => fmt(b.from)), datasets: [{ label: "Reviews", data: h.map((b) => b.n), backgroundColor: h.map((b) => colorFor((b.from + b.to) / 2)), borderRadius: 4 }] },
    options: { maintainAspectRatio: false, animation: false, plugins: { legend: { display: false } },
      scales: { x: { ...axis, title: { display: true, text: "VADER compound (bin start)", color: c.text } }, y: { ...axis, beginAtZero: true, title: { display: true, text: "Reviews", color: c.text } } } },
  }));
  charts.push(new window.Chart(document.getElementById("timeline-chart"), {
    type: "bar",
    data: { labels: f.timeline.map((t) => `${t.year} (${t.n})`), datasets: [{ label: "Mean VADER", data: f.timeline.map((t) => t.mean_compound), backgroundColor: f.timeline.map((t) => colorFor(t.mean_compound)), borderRadius: 4 }] },
    options: { maintainAspectRatio: false, animation: false, plugins: { legend: { display: false } },
      scales: { x: axis, y: { ...axis, min: -1, max: 1 } } },
  }));
}

// ------------------------------------------------------------------ routing
function route() {
  const slug = slugFromPath();
  if (slug) renderFilm(slug);
  else renderPicker();
}

document.addEventListener("click", (e) => {
  const a = e.target.closest?.("a[href]");
  if (!a || e.defaultPrevented || e.button !== 0 || e.metaKey || e.ctrlKey || e.shiftKey || e.altKey) return;
  const url = new URL(a.href, location.href);
  if (url.origin !== location.origin) return;
  if (url.pathname === "/" && url.hash) return; // in-page anchors such as /#analyze
  if (url.pathname === "/" || url.pathname.startsWith("/film/")) {
    e.preventDefault();
    history.pushState({}, "", url.pathname);
    spaNavigation = true;
    route();
    window.scrollTo(0, 0);
  }
});
window.addEventListener("popstate", route);
document.addEventListener("themechange", () => {
  if (currentFilm) { destroyCharts(); drawFilmCharts(currentFilm); } else if (films) { destroyCharts(); drawOverviewChart(); }
});

async function start() {
  try {
    films = await getJSON("/data/films.json");
  } catch (e) {
    clear(view);
    view.append(el("div", { class: "notice error", role: "alert" }, [el("h1", {}, "Could not load the film data"), el("p", {}, String(e.message || e))]));
    return;
  }
  // Chart.js is a deferred classic script; module scripts run after it, but guard anyway.
  if (!window.Chart) await new Promise((r) => window.addEventListener("load", r, { once: true }));
  route();
}
start();
