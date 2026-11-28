"""Self-host Pyodide 314.0.8 + the nltk/regex wheels + English NLTK data under site/.

Owners: pyodide-engineer (what the worker needs) + netlify-engineer (runs in the build).
Runs in the Netlify build (see netlify.toml) and locally with the same command:

    python scripts/prepare_pyodide.py

Decision record: nothing is loaded from a CDN at runtime. Everything the in-browser
analyzer needs is downloaded here, at build time, from the official Pyodide GitHub
release, checked against the sha256 hashes in pyodide-lock.json, and published by Netlify.

Writes (all git-ignored, regenerated every build):
  site/pyodide/v314.0.8/  pyodide.mjs, pyodide.asm.mjs, pyodide.asm.wasm, python_stdlib.zip,
                     pyodide-lock.json, package.json, nltk-*.whl, regex-*.whl
  site/nltk_data/browser-nltk-data.zip   sentiment/vader_lexicon.zip, tokenizers/punkt_tab/english,
                                         corpora/stopwords/english (about 100 KB)
Downloads are cached in .cache/pyodide/ so repeat local builds are fast.
"""
from __future__ import annotations

import hashlib
import io
import json
import os
import shutil
import sys
import tarfile
import time
import urllib.request
import zipfile
from pathlib import Path

VERSION = "314.0.8"
BASE = f"https://github.com/pyodide/pyodide/releases/download/{VERSION}"
CORE = f"{BASE}/pyodide-core-{VERSION}.tar.bz2"
FULL = f"{BASE}/pyodide-{VERSION}.tar.bz2"   # 337 MB; streamed, we stop after the 2 wheels
CORE_FILES = ["pyodide.mjs", "pyodide.js", "pyodide.asm.mjs", "pyodide.asm.wasm", "python_stdlib.zip",
              "pyodide-lock.json", "package.json"]
PACKAGES = ["nltk"]  # plus their dependencies from pyodide-lock.json (regex)

ROOT = Path(__file__).resolve().parents[1]
SITE = ROOT / "site"
DEST = SITE / "pyodide" / f"v{VERSION}"   # versioned path -> safe to cache as immutable
CACHE = ROOT / ".cache" / "pyodide"
NLTK_DATA = Path(os.environ.get("NLTK_DATA", ROOT / "nltk_data"))


def fetch(url: str, retries: int = 4):
    for attempt in range(1, retries + 1):
        try:
            return urllib.request.urlopen(url, timeout=120)
        except OSError as e:  # network hiccup: back off and retry
            if attempt == retries:
                raise
            print(f"[pyodide] {e}; retry {attempt}/{retries - 1}")
            time.sleep(2 ** attempt)


def sha256(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


def core() -> dict:
    CACHE.mkdir(parents=True, exist_ok=True)
    cached = CACHE / f"pyodide-core-{VERSION}.tar.bz2"
    if not cached.exists():
        print(f"[pyodide] downloading {CORE}")
        cached.write_bytes(fetch(CORE).read())
    DEST.mkdir(parents=True, exist_ok=True)
    with tarfile.open(cached, "r:bz2") as t:
        for name in CORE_FILES:
            data = t.extractfile(f"pyodide/{name}").read()
            (DEST / name).write_bytes(data)
    return json.loads((DEST / "pyodide-lock.json").read_text())


def wanted_wheels(lock: dict) -> dict[str, str]:
    pk = lock["packages"]
    names, stack = set(), list(PACKAGES)
    while stack:
        n = stack.pop()
        if n not in names:
            names.add(n)
            stack.extend(pk[n]["depends"])
    return {pk[n]["file_name"]: pk[n]["sha256"] for n in sorted(names)}


def wheels(lock: dict) -> None:
    want = wanted_wheels(lock)
    missing = {}
    for fname, digest in want.items():
        c = CACHE / fname
        if c.exists() and sha256(c.read_bytes()) == digest:
            continue
        missing[fname] = digest
    if missing:
        print(f"[pyodide] streaming {FULL} for {sorted(missing)}")
        with tarfile.open(fileobj=fetch(FULL), mode="r|bz2") as t:
            for m in t:
                name = m.name.split("/")[-1]
                if name in missing:
                    data = t.extractfile(m).read()
                    if sha256(data) != missing[name]:
                        sys.exit(f"[pyodide] sha256 mismatch for {name}")
                    (CACHE / name).write_bytes(data)
                    del missing[name]
                    if not missing:
                        break
        if missing:
            sys.exit(f"[pyodide] not found in release: {sorted(missing)}")
    for fname, digest in want.items():
        data = (CACHE / fname).read_bytes()
        assert sha256(data) == digest
        (DEST / fname).write_bytes(data)
    print(f"[pyodide] wheels: {', '.join(want)}")


def nltk_bundle() -> Path:
    """Zip only the English NLTK data the browser analyzer needs."""
    files = {
        "sentiment/vader_lexicon.zip": NLTK_DATA / "sentiment" / "vader_lexicon.zip",
        "corpora/stopwords/english": NLTK_DATA / "corpora" / "stopwords" / "english",
    }
    for p in (NLTK_DATA / "tokenizers" / "punkt_tab" / "english").iterdir():
        files[f"tokenizers/punkt_tab/english/{p.name}"] = p
    for k, p in files.items():
        if not p.exists():
            sys.exit(f"[pyodide] missing NLTK data {p}; run python -m nltk.downloader -d ./nltk_data "
                     "punkt_tab stopwords vader_lexicon first")
    out = SITE / "nltk_data" / "browser-nltk-data.zip"
    out.parent.mkdir(parents=True, exist_ok=True)
    buf = io.BytesIO()
    with zipfile.ZipFile(buf, "w", zipfile.ZIP_DEFLATED) as z:
        for arc, p in sorted(files.items()):
            z.write(p, arc)
    out.write_bytes(buf.getvalue())
    return out


def main() -> None:
    t0 = time.perf_counter()
    if DEST.parent.exists():
        shutil.rmtree(DEST.parent)
    lock = core()
    assert lock["info"]["python"].startswith("3.14"), lock["info"]
    wheels(lock)
    b = nltk_bundle()
    size = sum(p.stat().st_size for p in DEST.iterdir())
    print(f"[pyodide] {DEST.relative_to(ROOT)} {size / 1e6:.1f} MB, {b.relative_to(ROOT)} {b.stat().st_size / 1024:.0f} KB, "
          f"{time.perf_counter() - t0:.1f}s")


if __name__ == "__main__":
    main()
