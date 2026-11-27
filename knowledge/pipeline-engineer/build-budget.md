# Build budget

Sources: https://docs.netlify.com/build/configure-builds/manage-dependencies/, https://spacy.io/usage/processing-pipelines

- Netlify runs `pip install -r requirements.txt` before the build command; spaCy + model + pandas install dominates the first build. Install time is part of the build.
- Build time limit: commonly 15 min by default (not confirmed in the docs we read) — target **< 5 min** for the whole build.
- spaCy: "the statistical models are usually more efficient if you let them work on batches of texts" → `nlp.pipe(..., as_tuples=True, batch_size=500)`. "For shorter tasks… it can be faster to use a smaller number of processes with a larger batch size."
- Measure locally: print timings per stage (`load`, `spacy`, `nltk`, `aggregate`, `write`) and the total review count; record them in `site/data/eval.json` → `build_stats`.
- Keep a fallback: committed JSON in `site/data/` + env flag `SKIP_NLP=1` to publish without re-running the NLP.
