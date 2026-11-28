const { test, expect } = require("@playwright/test");
const AxeBuilder = require("@axe-core/playwright").default;

const WCAG = ["wcag2a", "wcag2aa", "wcag21a", "wcag21aa", "wcag22aa"];

function trackErrors(page) {
  const errors = [];
  page.on("pageerror", (e) => errors.push(e.message));
  page.on("console", (m) => { if (m.type() === "error") errors.push(m.text()); });
  return errors;
}

test("picker lists films and opens a dashboard", async ({ page }) => {
  const errors = trackErrors(page);
  await page.goto("/");
  await expect(page.locator(".film-card")).toHaveCount(14);
  await page.getByLabel("Find a film").fill("blade");
  await expect(page.locator(".film-card")).toHaveCount(1);
  await page.locator("#film-list").getByRole("link", { name: "Blade Runner 2049" }).click();
  await expect(page).toHaveURL(/\/film\/blade-runner-2049$/);
  await expect(page.getByRole("heading", { level: 1, name: "Blade Runner 2049" })).toBeVisible();
  expect(errors).toEqual([]);
});

test("every result panel is labelled NLTK or spaCy and the legend explains both", async ({ page }) => {
  await page.goto("/film/arrival");
  await expect(page.locator("#aspects")).toBeVisible();
  const legend = page.locator(".legend").first();
  await expect(legend).toContainText("NLTK");
  await expect(legend).toContainText("spaCy");
  const expected = { aspects: "spaCy + NLTK", sentiment: "NLTK", quotes: "NLTK", words: "NLTK", phrases: "NLTK", chunks: "spaCy", entities: "spaCy", timeline: "NLTK" };
  for (const [id, label] of Object.entries(expected)) {
    await expect(page.locator(`#${id} .panel-head .badge`)).toHaveText(label);
  }
});

// Regression: the first deploy showed spaCy and spaCy + NLTK only as legend text on the home page;
// every chart there was NLTK. Both must be drawn as visuals on the landing page and in the film's spaCy panels.
async function canvasHasPixels(page, id) {
  return page.locator(`#${id}`).evaluate((c) => {
    const d = c.getContext("2d").getImageData(0, 0, c.width, c.height).data;
    for (let i = 3; i < d.length; i += 4) if (d[i] !== 0) return true;
    return false;
  });
}

test("home page draws spaCy and spaCy + NLTK visuals, not only NLTK", async ({ page }) => {
  const errors = trackErrors(page);
  await page.goto("/");
  await expect(page.locator("#spacy-overview .panel-head .badge")).toHaveText("spaCy");
  await expect(page.locator("#combo-heatmap .panel-head .badge")).toHaveText("spaCy + NLTK");
  await expect(page.locator("#overview .panel-head .badge")).toHaveText("NLTK");
  expect(await canvasHasPixels(page, "spacy-overview-chart")).toBe(true);
  await expect(page.locator("#combo-heatmap td.heat:not(.na)").first()).toBeVisible();
  expect(await page.locator("#combo-heatmap tbody tr").count()).toBe(14);
  await expect(page.locator(".film-card").first()).toContainText("spaCy + NLTK");
  expect(errors).toEqual([]);
});

test("film page draws charts in the spaCy panels", async ({ page }) => {
  await page.goto("/film/arrival");
  await expect(page.locator("#chunks-chart")).toBeVisible();
  await expect(page.locator("#entities-chart")).toBeVisible();
  expect(await canvasHasPixels(page, "chunks-chart")).toBe(true);
  expect(await canvasHasPixels(page, "entities-chart")).toBe(true);
});

test("deep link works and quotes are attributed to critic and publication", async ({ page }) => {
  await page.goto("/film/mad-max-fury-road");
  await expect(page.getByRole("heading", { level: 1, name: "Mad Max: Fury Road" })).toBeVisible();
  const quotes = page.locator("blockquote.quote");
  await expect(quotes.first()).toBeVisible();
  expect(await quotes.count()).toBeGreaterThan(2);
  for (const footer of await quotes.locator("footer").all()) {
    const cite = footer.locator("cite");
    await expect(cite).not.toBeEmpty();
    await expect(footer).toContainText(",");
  }
});

test("unknown film shows a friendly error", async ({ page }) => {
  await page.goto("/film/not-a-film");
  await expect(page.getByRole("alert")).toContainText("Film not found");
});

test("Resources page is reachable from header and footer and lists every required link", async ({ page }) => {
  await page.goto("/");
  await page.getByRole("navigation", { name: "Main" }).getByRole("link", { name: "Resources" }).click();
  await expect(page).toHaveURL(/resources\.html$/);
  await page.goto("/film/arrival");
  await page.getByRole("navigation", { name: "Footer" }).getByRole("link", { name: /Resources/ }).click();
  await expect(page.getByRole("heading", { level: 1, name: "Resources" })).toBeVisible();
  const hrefs = await page.locator("main a[href]").evaluateAll((as) => as.map((a) => a.getAttribute("href")));
  for (const must of [
    "https://www.nltk.org/", "https://www.nltk.org/howto/sentiment.html", "https://www.nltk.org/data.html",
    "https://spacy.io/", "https://spacy.io/models/en", "https://spacy.io/usage/rule-based-matching#entityruler", "https://spacy.io/usage/visualizers",
    "https://pyodide.org/en/stable/",
    "https://docs.netlify.com/build/configure-builds/file-based-configuration/", "https://docs.netlify.com/build/configure-builds/manage-dependencies/", "https://docs.netlify.com/build/functions/get-started/",
    "https://www.chartjs.org/docs/latest/", "https://pandas.pydata.org/docs/", "https://docs.python.org/3/",
    "https://www.kaggle.com/datasets/stefanoleone992/rotten-tomatoes-movies-and-critic-reviews-dataset",
    "https://github.com/cjhutto/vaderSentiment", "https://www.w3.org/TR/WCAG22/",
    "https://github.com/animaze63-oss/NLPFinalpd", "https://github.com/animaze63-oss/NLPFinalpd#readme",
  ]) expect(hrefs, must).toContain(must);
});

test("methodology page shows evaluation numbers and displaCy examples", async ({ page }) => {
  await page.goto("/methodology.html");
  await expect(page.locator("#eval table").first()).toContainText("Baseline: always Fresh");
  await expect(page.locator("#examples svg").first()).toBeVisible();
});

test("works at 360px without horizontal scroll", async ({ page }) => {
  await page.setViewportSize({ width: 360, height: 800 });
  for (const url of ["/", "/film/the-martian", "/resources.html", "/methodology.html"]) {
    await page.goto(url);
    await page.waitForLoadState("networkidle");
    const overflow = await page.evaluate(() => document.documentElement.scrollWidth - document.documentElement.clientWidth);
    expect(overflow, url).toBeLessThanOrEqual(0);
  }
});

for (const theme of ["dark", "light"]) {
  for (const url of ["/", "/film/arrival", "/resources.html", "/methodology.html"]) {
    test(`axe: no WCAG A/AA violations on ${url} (${theme})`, async ({ page }) => {
      await page.emulateMedia({ colorScheme: theme });
      await page.goto(url);
      await page.waitForLoadState("networkidle");
      // open the chart data tables so they are audited too
      await page.locator("details.data-table").evaluateAll((ds) => ds.forEach((d) => { d.open = true; }));
      const results = await new AxeBuilder({ page }).withTags(WCAG).analyze();
      const summary = results.violations.map((v) => `${v.id}: ${v.nodes.slice(0, 3).map((n) => n.target.join(" ")).join(" | ")}`);
      expect(summary).toEqual([]);
    });
  }
}
