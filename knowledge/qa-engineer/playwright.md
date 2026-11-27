# Playwright Test

Sources: https://playwright.dev/docs/writing-tests, https://playwright.dev/docs/test-webserver

```js
import { test, expect } from '@playwright/test';
test.describe('film dashboard', () => {
  test.beforeEach(async ({ page }) => { await page.goto('/'); });
  test('pick a film', async ({ page }) => {
    await page.getByRole('combobox', { name: 'Choose a film' }).selectOption('blade-runner-2049');
    await expect(page.getByRole('heading', { name: /Blade Runner 2049/ })).toBeVisible();
    await expect(page).toHaveURL(/\/film\/blade-runner-2049/);
  });
});
```
- Playwright auto-waits for actionability; web-first assertions (`toBeVisible`, `toHaveText`, `toHaveURL`) retry until the condition holds — no manual sleeps.
- Hooks: `beforeEach`, `afterEach`, `beforeAll`, `afterAll`.

## webServer + baseURL
```js
// playwright.config.ts
import { defineConfig } from '@playwright/test';
export default defineConfig({
  webServer: {
    command: 'python -m http.server 8888 --directory site',
    url: 'http://localhost:8888',
    reuseExistingServer: !process.env.CI,
    timeout: 120 * 1000,          // default 60000 ms
  },
  use: { baseURL: process.env.BASE_URL ?? 'http://localhost:8888' },
});
```
- `url` must return 2xx/3xx/400–403 when ready. `reuseExistingServer: !process.env.CI` is the recommended pattern.
- `baseURL` lets tests use relative paths (`page.goto('./film/x')`).
- To test a Deploy Preview, set `BASE_URL=https://deploy-preview-<n>--<site>.netlify.app` (our convention; the docs page doesn't cover remote URLs) and skip `webServer`.
- Pass `--trace off` unless debugging (environment rule).
- Note: `python -m http.server` doesn't apply Netlify redirects/headers; deep-link and header tests run against the Deploy Preview.
