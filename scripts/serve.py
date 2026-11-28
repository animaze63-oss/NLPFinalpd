"""Local static server that mimics Netlify for site/: applies netlify.toml redirects
(status 200 rewrites) and [[headers]] so local tests see the same CSP and MIME types.

    python scripts/serve.py --port 8888

Development/test helper only; production is served by Netlify's CDN.
"""
from __future__ import annotations

import argparse
import fnmatch
import http.server
import tomllib
from functools import partial
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
CONF = tomllib.loads((ROOT / "netlify.toml").read_text())
SITE = ROOT / CONF["build"]["publish"]


def _match(pattern: str, path: str) -> bool:
    return fnmatch.fnmatchcase(path, pattern.replace("*", "*"))


class Handler(http.server.SimpleHTTPRequestHandler):
    extensions_map = {**http.server.SimpleHTTPRequestHandler.extensions_map,
                      ".mjs": "text/javascript", ".js": "text/javascript", ".wasm": "application/wasm",
                      ".json": "application/json", ".svg": "image/svg+xml", ".py": "text/plain"}

    def _rewrite(self) -> None:
        path = self.path.split("?", 1)[0]
        if (SITE / path.lstrip("/")).is_file():
            return
        for r in CONF.get("redirects", []):
            if r.get("status") == 200 and _match(r["from"], path):
                self.path = r["to"]
                return

    def do_GET(self):  # noqa: N802
        self._orig = self.path.split("?", 1)[0]
        self._rewrite()
        return super().do_GET()

    def do_HEAD(self):  # noqa: N802
        self._orig = self.path.split("?", 1)[0]
        self._rewrite()
        return super().do_HEAD()

    def end_headers(self):
        path = getattr(self, "_orig", self.path)
        for h in CONF.get("headers", []):
            if _match(h["for"], path):
                for k, v in h["values"].items():
                    self.send_header(k, v)
        super().end_headers()

    def send_header(self, keyword, value):
        # netlify.toml Content-Type overrides the guessed type
        if keyword.lower() == "content-type" and getattr(self, "_ct_sent", False):
            return
        if keyword.lower() == "content-type":
            path = getattr(self, "_orig", self.path)
            for h in CONF.get("headers", []):
                if _match(h["for"], path) and "Content-Type" in h["values"]:
                    value = h["values"]["Content-Type"]
            self._ct_sent = True
        super().send_header(keyword, value)

    def log_message(self, fmt, *args):
        pass


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("--port", type=int, default=8888)
    args = ap.parse_args()
    handler = partial(Handler, directory=str(SITE))
    with http.server.ThreadingHTTPServer(("127.0.0.1", args.port), handler) as httpd:
        print(f"serving {SITE} on http://127.0.0.1:{args.port}")
        httpd.serve_forever()


if __name__ == "__main__":
    main()
