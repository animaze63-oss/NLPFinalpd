# Deploy Previews

Source: https://docs.netlify.com/deploy/deploy-types/deploy-previews/

- > "When you open a pull / merge request in a connected site repository from GitHub… Netlify automatically builds a Deploy Preview for you."
- URL: `deploy-preview-<PR number>--<site-name>.netlify.app` (e.g. `deploy-preview-42--mysitename.netlify.app`).
- Per-context overrides in `netlify.toml`: `[context.deploy-preview]`.
- Disable/enable: Project configuration › Developer settings › Continuous deployment › Branches and deploy contexts › Configure.

Project workflow: every PR → Deploy Preview → QA runs Playwright + Lighthouse against the preview URL → merge to `main` → production deploy.
