# netlify.toml (file-based configuration)

Source: https://docs.netlify.com/build/configure-builds/file-based-configuration/

> "The `netlify.toml` is normally stored in the root of your site repository."
> "UI settings are overridden if a `netlify.toml` file is present and a setting for the same property/redirect/header exists in the UI and the TOML file."

```toml
[build]
  base    = "project/"         # base directory
  publish = "build-output/"    # publish directory
  command = "echo 'default context'"
  ignore  = "git diff --quiet HEAD^ HEAD . "   # exit 0 = skip the build

[build.environment]
  VARIABLE = "value"

[context.production]       # production branch
  command = "make publish"
[context.deploy-preview]   # pull/merge requests
  publish = "dist/"
[context.branch-deploy]    # other branches
  command = "echo branch"

[[redirects]]
  from = "/old-path"
  to = "/new-path"
  status = 301
  force = false

[[headers]]
  for = "/*"
  [headers.values]
    X-Frame-Options = "DENY"
```

## Project netlify.toml (starting point)
```toml
[build]
  command = "python -m nltk.downloader -d ./nltk_data punkt_tab stopwords vader_lexicon && NLTK_DATA=./nltk_data python pipeline/build_data.py"
  publish = "site"

[build.environment]
  PYTHON_VERSION = "3.12"

[[headers]]
  for = "/data/*"
  [headers.values]
    Cache-Control = "public, max-age=300, must-revalidate"

[[headers]]
  for = "/pyodide/*"
  [headers.values]
    Cache-Control = "public, max-age=31536000, immutable"

[[headers]]
  for = "/*.wasm"
  [headers.values]
    Content-Type = "application/wasm"

[[redirects]]           # deep links like /film/blade-runner-2049 → SPA shell
  from = "/film/*"
  to = "/index.html"
  status = 200
```
