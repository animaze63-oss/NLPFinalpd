// Methodology page: renders eval.json (nlp-evaluator), displaCy examples and the lexicon.
import { el, clear, fmt, badge, scrollTable } from "./ui.js";

const get = (u) => fetch(u).then((r) => { if (!r.ok) throw new Error(`${u}: HTTP ${r.status}`); return r.json(); });

function metricsTable(caption, rows) {
  return scrollTable(caption, el("table", {}, [el("caption", { class: "muted small", style: "text-align:left" }, caption),
    el("thead", {}, el("tr", {}, ["Model", "Accuracy", "Balanced accuracy", "Macro-F1", "Rotten recall"].map((h) => el("th", { scope: "col" }, h)))),
    el("tbody", {}, rows.map(([name, m]) => el("tr", {}, [name, m.accuracy, m.balanced_accuracy, m.macro_f1, m.per_class.Rotten.recall].map((c) => el("td", {}, String(c))))))]));
}

async function main() {
  const box = document.getElementById("eval");
  try {
    const [ev, ex, lex] = await Promise.all([get("/data/eval.json"), get("/data/examples.json"), get("/data/lexicon.json")]);
    clear(box);
    const t = ev.vader_vs_labels;
    box.append(
      el("p", {}, ["Measured by the build on ", el("strong", {}, `${ev.dataset.n_reviews} reviews`), ` (${ev.dataset.n_fresh} Fresh, ${ev.dataset.n_rotten} Rotten). Versions: NLTK ${ev.versions.nltk}, spaCy ${ev.versions.spacy}, ${ev.versions.model}, Python ${ev.versions.python}. `, badge("nltk")]),
      metricsTable("VADER review score vs Rotten Tomatoes Fresh/Rotten (2-class: compound ≥ 0 → Fresh)", [
        ["Baseline: always Fresh", ev.baseline_majority],
        ["VADER + sci-fi overrides", t.two_class],
        ["VADER, stock lexicon", ev.ablation.without_overrides.two_class],
      ]),
      el("p", { class: "small" }, `3-class rule (±0.05): ${t.three_class_non_neutral.neutral_excluded} reviews fall in the neutral band; on the remaining ${t.three_class_non_neutral.n} the accuracy is ${t.three_class_non_neutral.accuracy} (balanced ${t.three_class_non_neutral.balanced_accuracy}).`),
      el("p", { class: "small" }, `Regression check: ${ev.regression.cases.filter((c) => c.pass).length} of ${ev.regression.cases.length} reference sentences from the NLTK sentiment how-to reproduce exactly.`),
    );
    if (ev.aspect_extraction?.available) {
      const ae = ev.aspect_extraction;
      const rows = ["visuals", "story", "characters", "soundtrack"].map((a) => [a, ae.spacy_build[a].precision ?? "n/a", ae.spacy_build[a].recall ?? "n/a", ae.keyword_browser[a].precision ?? "n/a", ae.keyword_browser[a].recall ?? "n/a", ae.spacy_build[a].support]);
      rows.push(["micro", ae.spacy_build.micro.precision, ae.spacy_build.micro.recall, ae.keyword_browser.micro.precision, ae.keyword_browser.micro.recall, ""]);
      box.append(el("h3", {}, ["Aspect detection on hand-labelled sentences ", badge("spacy")]),
        el("p", { class: "small muted" }, `${ae.n_sentences} review sentences; ${ae.annotation.annotator}. ${ae.annotation.note}`),
        scrollTable("Aspect detection precision and recall", el("table", {}, [el("thead", {}, el("tr", {}, ["Aspect", "spaCy precision", "spaCy recall", "Keyword (browser) precision", "Keyword recall", "Gold count"].map((h) => el("th", { scope: "col" }, h)))),
          el("tbody", {}, rows.map((r) => el("tr", {}, r.map((c) => el("td", {}, String(c))))))])));
    }
    box.append(el("h3", {}, "What this means"), el("ul", {}, ev.methodology.map((m) => el("li", {}, m))));
    if (ev.errors?.length) {
      box.append(el("h3", {}, "Where VADER disagrees most with the critic's label"),
        ...ev.errors.map((e) => el("blockquote", { class: "quote" }, [el("p", {}, `“${e.text}”`),
          el("footer", {}, ["— ", el("cite", {}, e.critic), `, ${e.publisher} · labelled ${e.label}, VADER ${fmt(e.compound)}`])])));
    }
    const exBox = document.getElementById("examples");
    for (const x of ex.examples) {
      const fig = el("figure", { style: "margin:0 0 1.2rem" });
      const svgWrap = el("div", { class: "displacy", role: "img", tabindex: "0", "aria-label": `Dependency parse of: ${x.text}` });
      // Trusted, build-generated SVG from spaCy displaCy (no user input involved).
      svgWrap.innerHTML = x.dep_svg;
      fig.append(svgWrap, el("figcaption", { class: "small" }, [
        `“${x.text}” — `, el("cite", {}, x.critic), `, ${x.publisher}. Links found: `,
        x.links.map((l) => `${l.term} (${l.aspect}) ← ${l.opinions.join(", ")}`).join("; "), ".",
      ]));
      exBox.append(fig);
    }
    const lexBox = document.getElementById("lexicon");
    lexBox.append(el("ul", {}, [
      ...lex.aspects.map((a) => el("li", {}, [el("strong", {}, a), `: ${lex.aspect_terms[a].join(", ")}; phrases: ${lex.aspect_phrases[a].join(", ")}`])),
      el("li", {}, [el("strong", {}, "VADER overrides (set to 0)"), `: ${Object.keys(lex.vader_overrides).join(", ")}`]),
    ]));
  } catch (e) {
    clear(box);
    box.append(el("p", { class: "notice error", role: "alert" }, `Could not load evaluation data: ${e.message}`));
  }
}
main();
