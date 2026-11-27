# Agent knowledge

One folder per agent in `.claude/agents/`. Each agent reads its folder's `README.md`, and every file it lists, before answering.
Notes come from official documentation and keep their source links. The Meta Agent maintains them.

| Folder | Agent | Main sources |
|---|---|---|
| [orchestrator](orchestrator/README.md) | Nova Reyes | code.claude.com (subagents), project docs |
| [meta-agent](meta-agent/README.md) | Echo Lindqvist | code.claude.com (subagents, skills) |
| [ux-designer](ux-designer/README.md) | Lumen Okafor | w3.org WCAG 2.2, MDN |
| [dataset-curator](dataset-curator/README.md) | Archie Vault | kaggle.com, Kaggle CLI docs, pandas.pydata.org, IMDb, Stanford |
| [nltk-expert](nltk-expert/README.md) | Nell Tokes | nltk.org |
| [spacy-expert](spacy-expert/README.md) | Sy Parsons | spacy.io |
| [pipeline-engineer](pipeline-engineer/README.md) | Reel Martinez | docs.python.org, python-jsonschema, spaCy, Netlify |
| [frontend-engineer](frontend-engineer/README.md) | Pixel Andersen | chartjs.org, MDN |
| [pyodide-engineer](pyodide-engineer/README.md) | Wasm Kowalski | pyodide.org |
| [nlp-evaluator](nlp-evaluator/README.md) | Dr. Imani Gauge | scikit-learn.org, NLTK, citations |
| [qa-engineer](qa-engineer/README.md) | Quinn Assure | docs.pytest.org, playwright.dev |
| [netlify-engineer](netlify-engineer/README.md) | Dock Harbor | docs.netlify.com |
