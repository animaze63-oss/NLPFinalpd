# Knowledge — Netlify Deployment Engineer

Reference notes from the official Netlify documentation (docs.netlify.com), retrieved 2026-11-25 to 2026-11-27.
Read every file before answering. Netlify docs change often: re-check a page before relying on a limit.

| File | Topic | Source |
|---|---|---|
| [build-image-and-python.md](build-image-and-python.md) | Ubuntu 24.04 image, Python versions, `PYTHON_VERSION`, `requirements.txt` | https://docs.netlify.com/build/configure-builds/available-software-at-build-time/, https://docs.netlify.com/build/configure-builds/manage-dependencies/ |
| [build-settings.md](build-settings.md) | Base/publish/command, build image selection | https://docs.netlify.com/build/configure-builds/overview/ |
| [netlify-toml.md](netlify-toml.md) | `[build]`, contexts, headers, redirects | https://docs.netlify.com/build/configure-builds/file-based-configuration/ |
| [headers.md](headers.md) | Custom headers, caching, limitations | https://docs.netlify.com/manage/routing/headers/ |
| [deploy-previews.md](deploy-previews.md) | PR previews and URLs | https://docs.netlify.com/deploy/deploy-types/deploy-previews/ |
| [what-not-to-use.md](what-not-to-use.md) | Functions / Edge Functions languages and limits (why we don't use them) | https://docs.netlify.com/build/functions/get-started/, https://docs.netlify.com/build/functions/configuration/, https://docs.netlify.com/build/edge-functions/limits/ |

Project context: ../../docs/04-netlify-deployment.md
