#!/usr/bin/env python3
"""data-fetch.py — Unified data fetching helper.

Tries ~/shared/data_fetching (geepers-kernel) first for the unified ClientFactory
covering 17 sources (arXiv, Census, GitHub, NASA, Wikipedia, YouTube, News,
Weather, OpenLibrary, Semantic Scholar, Wayback, FEC, Judiciary, Finance, PubMed,
Wolfram, etc).

Falls back to direct API calls for the most common sources if ClientFactory
isn't available.

Usage: python3 data-fetch.py <source> <query> [--json]
  source: github | arxiv | wikipedia | pypi | npm
  query: source-specific query string
"""

from __future__ import annotations

import json
import os
import sys
import urllib.parse
import urllib.request
from pathlib import Path

UA = "craft/0.1 (https://github.com/actually-useful-ai/craft)"
TIMEOUT = 30


def try_client_factory(source: str, query: str, as_json: bool) -> bool:
    """Try geepers-kernel's ClientFactory if available."""
    shared_path = os.environ.get("DATA_FETCHING_PATH", str(Path.home() / "shared"))
    if not Path(shared_path).is_dir():
        return False
    if shared_path not in sys.path:
        sys.path.insert(0, shared_path)
    try:
        from data_fetching import ClientFactory  # type: ignore
    except ImportError:
        return False

    factory = ClientFactory()
    try:
        client = factory.get_client(source)
    except Exception as exc:  # noqa: BLE001
        print(f"## ClientFactory has no client for '{source}': {exc}", file=sys.stderr)
        return False

    result = client.search(query) if hasattr(client, "search") else client.fetch(query)
    if as_json:
        print(json.dumps(result, indent=2, default=str))
    else:
        print(result if isinstance(result, str) else json.dumps(result, indent=2, default=str))
    return True


def fetch_github(query: str, as_json: bool) -> None:
    """GitHub repo or user search."""
    url = f"https://api.github.com/search/repositories?q={urllib.parse.quote(query)}&per_page=10"
    req = urllib.request.Request(url, headers={"User-Agent": UA, "Accept": "application/vnd.github+json"})
    with urllib.request.urlopen(req, timeout=TIMEOUT) as resp:
        data = json.loads(resp.read())
    if as_json:
        print(json.dumps(data, indent=2))
        return
    for item in data.get("items", [])[:10]:
        print(f"  {item['full_name']:50s} ⭐ {item['stargazers_count']:>6d}  {item.get('description', '')[:80]}")


def fetch_arxiv(query: str, as_json: bool) -> None:
    """arXiv abstract search."""
    url = f"http://export.arxiv.org/api/query?search_query=all:{urllib.parse.quote(query)}&max_results=10"
    req = urllib.request.Request(url, headers={"User-Agent": UA})
    with urllib.request.urlopen(req, timeout=TIMEOUT) as resp:
        body = resp.read().decode("utf-8")
    if as_json:
        print(body)
        return
    # Quick-and-dirty: just show entry titles
    import re
    for title in re.findall(r"<title>([^<]+)</title>", body)[1:11]:
        print(f"  {title.strip()}")


def fetch_wikipedia(query: str, as_json: bool) -> None:
    """Wikipedia summary."""
    url = f"https://en.wikipedia.org/api/rest_v1/page/summary/{urllib.parse.quote(query)}"
    req = urllib.request.Request(url, headers={"User-Agent": UA})
    with urllib.request.urlopen(req, timeout=TIMEOUT) as resp:
        data = json.loads(resp.read())
    if as_json:
        print(json.dumps(data, indent=2))
        return
    print(f"  {data.get('title', query)}")
    print(f"  {data.get('extract', '(no summary)')}")


def fetch_pypi(name: str, as_json: bool) -> None:
    url = f"https://pypi.org/pypi/{urllib.parse.quote(name)}/json"
    req = urllib.request.Request(url, headers={"User-Agent": UA})
    with urllib.request.urlopen(req, timeout=TIMEOUT) as resp:
        data = json.loads(resp.read())
    if as_json:
        print(json.dumps(data["info"], indent=2))
        return
    info = data["info"]
    print(f"  {info['name']} {info['version']}")
    print(f"  {info.get('summary', '(no summary)')}")
    print(f"  home: {info.get('home_page', '(none)')}")


def fetch_npm(name: str, as_json: bool) -> None:
    url = f"https://registry.npmjs.org/{urllib.parse.quote(name)}"
    req = urllib.request.Request(url, headers={"User-Agent": UA})
    with urllib.request.urlopen(req, timeout=TIMEOUT) as resp:
        data = json.loads(resp.read())
    if as_json:
        print(json.dumps(data, indent=2))
        return
    latest = data.get("dist-tags", {}).get("latest", "?")
    print(f"  {data.get('name')} {latest}")
    print(f"  {data.get('description', '(no description)')}")


FALLBACK = {
    "github": fetch_github,
    "arxiv": fetch_arxiv,
    "wikipedia": fetch_wikipedia,
    "pypi": fetch_pypi,
    "npm": fetch_npm,
}


def main() -> None:
    args = sys.argv[1:]
    as_json = "--json" in args
    args = [a for a in args if a != "--json"]
    if len(args) < 2:
        print("usage: python3 data-fetch.py <source> <query> [--json]", file=sys.stderr)
        print(f"  fallback sources: {', '.join(FALLBACK.keys())}", file=sys.stderr)
        sys.exit(2)
    source, query = args[0], args[1]

    if try_client_factory(source, query, as_json):
        return

    if source not in FALLBACK:
        print(f"## ClientFactory unavailable; fallback has no '{source}' (try: {', '.join(FALLBACK)})", file=sys.stderr)
        sys.exit(3)

    FALLBACK[source](query, as_json)


if __name__ == "__main__":
    main()
