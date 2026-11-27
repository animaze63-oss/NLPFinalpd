# Accessibility testing with axe

Source: https://playwright.dev/docs/accessibility-testing

```js
import { test, expect } from '@playwright/test';
import AxeBuilder from '@axe-core/playwright';     // npm i -D @axe-core/playwright
test('no automatically detectable WCAG A/AA violations', async ({ page }) => {
  await page.goto('/');
  const results = await new AxeBuilder({ page })
    .withTags(['wcag2a', 'wcag2aa', 'wcag21a', 'wcag21aa'])
    .analyze();
  expect(results.violations).toEqual([]);
});
```
> "Automated accessibility tests can detect some common accessibility problems such as missing or invalid properties. But many accessibility problems can only be discovered through manual testing."

Also scan with the Pyodide panel open and in both colour schemes (`page.emulateMedia({ colorScheme: 'dark' })`). Manual checks: keyboard-only walkthrough, focus visibility, screen-reader labels on charts (see ../ux-designer/wcag22.md).
