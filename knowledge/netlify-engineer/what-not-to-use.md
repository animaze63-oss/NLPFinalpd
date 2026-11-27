# What Netlify can't do for us (and why we don't use it)

Sources:
- https://docs.netlify.com/build/functions/get-started/ — language picker: **TypeScript, JavaScript, Go** ("To write functions in Go, use the Lambda-compatible functions API").
- https://docs.netlify.com/build/functions/configuration/ — defaults: memory 1024 MB; synchronous limit **60 s**; scheduled 30 s; background 15 min (not configurable).
- https://docs.netlify.com/build/functions/lambda-compatibility/ — streaming: 10 s execution, 20 MB response.
- https://docs.netlify.com/build/edge-functions/limits/ — Edge (Deno): 20 MB compressed code, 512 MB memory, **50 ms CPU per request**, 40 s response-header timeout.
- https://answers.netlify.com/t/python-lambda-functions/3423 — no Python Lambda functions on Netlify.

**Rule:** no Python can run on Netlify after deploy. All NLTK/spaCy work happens at build time; live NLTK runs in the visitor's browser via Pyodide. Reject any PR that adds `netlify/functions/` or `netlify/edge-functions/` for NLP, or calls an outside API.
