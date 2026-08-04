#!/usr/bin/env python3
"""Compatibility entry point for Craft's canonical Ask transport."""

from __future__ import annotations

import argparse
from pathlib import Path
import subprocess
import sys


ALIASES = {
    "xai": "grok",
    "grok": "grok",
    "anthropic": "anthropic",
    "claude": "anthropic",
    "openai": "openai",
    "gpt": "openai",
}


def main() -> int:
    parser = argparse.ArgumentParser(
        description="Compatibility wrapper; prefer /craft:ask or scripts/ask.sh."
    )
    parser.add_argument("prompt")
    parser.add_argument("--provider", default="grok")
    args = parser.parse_args()

    ask = Path(__file__).with_name("ask.sh")
    if not ask.is_file():
        print("llm-query: canonical Ask transport is missing", file=sys.stderr)
        return 1

    providers = (
        ("grok", "anthropic", "openai")
        if args.provider == "all"
        else (ALIASES.get(args.provider, args.provider),)
    )
    print("llm-query: compatibility mode; routing through craft:ask", file=sys.stderr)
    failed = False
    for provider in providers:
        result = subprocess.run([str(ask), provider, "-"], input=args.prompt, text=True)
        failed = failed or result.returncode != 0
    return 1 if failed else 0


if __name__ == "__main__":
    raise SystemExit(main())
