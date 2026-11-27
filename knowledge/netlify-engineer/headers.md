# Custom headers

Source: https://docs.netlify.com/manage/routing/headers/

- Two ways: a `_headers` file in the publish dir, or `[[headers]]` in `netlify.toml` (`for` = path, `[headers.values]` = map).
- "Header field names are case insensitive." Lines starting with `#` in `_headers` are comments.
- Path matching: `*` wildcards can appear anywhere inside a path segment; `:placeholders` only at the start of a segment; you can't mix them in one segment.
- Multi-value headers: repeat the field in `_headers`; use a TOML multiline string in `netlify.toml`:
  ```toml
  cache-control = '''
  max-age=0,
  no-cache,
  no-store,
  must-revalidate'''
  ```
- Limitations:
  - "Custom headers apply only to files Netlify serves from its own backing store" — not to proxied, Function or Edge Function responses (we don't use those anyway).
  - Headers are global for all builds and "cannot be scoped for specific branches or deploy contexts".
  - Ignored names: `Accept-Ranges, Age, Allow, Alt-Svc, Connection, Content-Encoding, Content-Length, Content-Range, Date, Location, Server, Set-Cookie, Trailer, Transfer-Encoding, Upgrade`.
- The page doesn't state default `Cache-Control` values; check response headers on a Deploy Preview with `curl -I`.

Project: long immutable caching for versioned Pyodide assets; short caching for `/data/*.json`; `Content-Type: application/wasm` for `.wasm`; security headers (`X-Content-Type-Options: nosniff`, `Referrer-Policy`) on `/*`.
