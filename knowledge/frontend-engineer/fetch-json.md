# Loading static JSON with fetch

Source: https://developer.mozilla.org/en-US/docs/Web/API/Fetch_API/Using_Fetch

- `fetch()` returns a Promise that rejects only on network failure; an HTTP 404/500 still resolves — check `response.ok` / `response.status`.
- `await response.json()` parses the body (throws on invalid JSON — e.g. `NaN` written by a bad build).
- `AbortController` cancels a pending request (use when the user switches films quickly).

```js
async function loadFilm(slug, signal) {
  const res = await fetch(`/data/film/${encodeURIComponent(slug)}.json`, { signal });
  if (!res.ok) throw new Error(`HTTP ${res.status} for ${slug}`);
  return res.json();
}
let ctrl;
async function showFilm(slug) {
  ctrl?.abort(); ctrl = new AbortController();
  try { render(await loadFilm(slug, ctrl.signal)); }
  catch (e) { if (e.name !== 'AbortError') renderError(e); }
}
```
