const { test, expect } = require("@playwright/test");
const AxeBuilder = require("@axe-core/playwright").default;

test.describe.configure({ mode: "serial" });

test("Pyodide is not loaded until the analyzer is used (lazy)", async ({ page }) => {
  const requested = [];
  page.on("request", (r) => requested.push(r.url()));
  await page.goto("/");
  await page.waitForLoadState("networkidle");
  expect(requested.some((u) => u.includes("/pyodide/"))).toBe(false);
});

test("'Analyze your own critique' returns a VADER score computed in the browser, with no outside requests", async ({ page }) => {
  const outside = [];
  page.on("request", (r) => { if (!r.url().startsWith(new URL(page.url() || "http://127.0.0.1:8888").origin) && !r.url().startsWith("http://127.0.0.1:8888")) outside.push(r.url()); });
  await page.goto("/#analyze");
  await expect(page.getByRole("heading", { name: "Analyze your own critique" })).toBeVisible();
  await expect(page.locator("#analyze")).toContainText("never leaves this device");
  await page.getByLabel("Your critique").fill("The visual effects are stunning, but the third act is a mess. Great score!");
  await page.getByRole("button", { name: "Analyze with NLTK" }).click();
  const overall = page.locator("#analyze-overall [data-compound]");
  await expect(overall).toBeVisible({ timeout: 90_000 });
  const c = Number(await overall.getAttribute("data-compound"));
  expect(c).toBeGreaterThanOrEqual(-1);
  expect(c).toBeLessThanOrEqual(1);
  await expect(page.locator("#analyze-status")).toContainText("NLTK VADER in your browser");
  await expect(page.locator("#analyze-result")).toContainText("Visuals");
  expect(outside).toEqual([]);
  const results = await new AxeBuilder({ page }).include("#analyze").withTags(["wcag2a", "wcag2aa", "wcag22aa"]).analyze();
  expect(results.violations.map((v) => v.id)).toEqual([]);
});

test("browser/build parity: Pyodide output matches site/data/parity.json to 3 dp", async ({ page, request }) => {
  const parity = await (await request.get("/data/parity.json")).json();
  await page.goto("/");
  await page.waitForFunction(() => typeof window.__sclAnalyze === "function");
  const results = await page.evaluate(async (texts) => {
    const out = [];
    for (const t of texts) out.push(await window.__sclAnalyze(t));
    return out;
  }, parity.cases.map((c) => c.text));
  parity.cases.forEach((c, i) => {
    expect(results[i].compound, c.text).toBe(c.result.compound);
    expect(results[i].label, c.text).toBe(c.result.label);
    expect(results[i].aspects, c.text).toEqual(c.result.aspects);
  });
});
