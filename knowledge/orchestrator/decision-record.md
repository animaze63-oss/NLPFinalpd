# Decision record (non-negotiable)

1. Everything runs on Netlify. No outside servers, APIs or databases.
2. Build time: NLTK + spaCy process the committed sci-fi review subset and write static JSON.
3. Runtime: static site on Netlify's CDN reads that JSON.
4. "Analyze your own review": NLTK (VADER) runs in the browser via Pyodide. spaCy never runs in the browser.
5. No Netlify Functions or Edge Functions for NLP (they can't run Python).
6. Review text is attributed (critic + publisher). User-typed text never leaves the browser.

Reject or send back any proposal that breaks these, and say which rule it breaks.
