// Runs against the locally built site served by scripts/serve.py (applies netlify.toml
// redirects + headers), or against a Deploy Preview with BASE_URL=https://deploy-preview-N--site.netlify.app
const { defineConfig } = require("@playwright/test");
const BASE_URL = process.env.BASE_URL || "http://127.0.0.1:8888";
module.exports = defineConfig({
  testDir: "./tests",
  timeout: 120_000,
  fullyParallel: true,
  reporter: [["list"]],
  use: { baseURL: BASE_URL, trace: "off" },
  webServer: process.env.BASE_URL ? undefined : {
    command: "python3 ../scripts/serve.py --port 8888",
    url: "http://127.0.0.1:8888/",
    reuseExistingServer: true,
  },
});
