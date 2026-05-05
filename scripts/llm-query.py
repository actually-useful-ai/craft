#!/usr/bin/env python3
"""llm-query.py — Multi-LLM second-opinion query.

Tries, in order:
1. ~/shared/llm_providers (geepers-kernel) — unified ProviderFactory
2. Direct API calls to xAI / OpenAI / Mistral via env vars
3. CLI tools (codex/gemini/aider) if reachable
4. Graceful Claude-only fallback (just print the prompt and bail)

Env vars consulted:
  XAI_API_KEY, OPENAI_API_KEY, MISTRAL_API_KEY, PERPLEXITY_API_KEY
  LLM_PROVIDERS_PATH (default: ~/shared)

Usage: python3 llm-query.py "<prompt>" [--provider xai|openai|mistral|all]
"""

from __future__ import annotations

import json
import os
import subprocess
import sys
import urllib.request
from pathlib import Path

DEFAULT_TIMEOUT = 60


def try_provider_factory(prompt: str, provider: str = "all") -> bool:
    """Try the geepers-kernel ProviderFactory if present. Returns True on success."""
    shared_path = os.environ.get("LLM_PROVIDERS_PATH", str(Path.home() / "shared"))
    if not Path(shared_path).is_dir():
        return False
    if shared_path not in sys.path:
        sys.path.insert(0, shared_path)
    try:
        from llm_providers import ProviderFactory  # type: ignore
    except ImportError:
        return False

    print(f"## via ProviderFactory ({shared_path})", file=sys.stderr)
    factory = ProviderFactory()
    targets = ["xai", "openai", "mistral"] if provider == "all" else [provider]
    for name in targets:
        try:
            client = factory.get_provider(name)
            response = client.complete(prompt)
            print(f"\n### {name}\n{response}\n")
        except Exception as exc:  # noqa: BLE001 — surface, don't swallow
            print(f"\n### {name}: FAILED — {exc}\n", file=sys.stderr)
    return True


def try_direct_api(prompt: str, provider: str = "all") -> bool:
    """Direct curl-equivalent calls to xAI / OpenAI / Mistral."""
    targets = []
    if (provider in ("all", "xai")) and os.environ.get("XAI_API_KEY"):
        targets.append(("xai", "https://api.x.ai/v1/chat/completions", "grok-4-fast", "XAI_API_KEY"))
    if (provider in ("all", "openai")) and os.environ.get("OPENAI_API_KEY"):
        targets.append(("openai", "https://api.openai.com/v1/chat/completions", "gpt-4o-mini", "OPENAI_API_KEY"))
    if (provider in ("all", "mistral")) and os.environ.get("MISTRAL_API_KEY"):
        targets.append(("mistral", "https://api.mistral.ai/v1/chat/completions", "mistral-large-latest", "MISTRAL_API_KEY"))

    if not targets:
        return False

    print("## via direct API", file=sys.stderr)
    for name, url, model, key_var in targets:
        body = json.dumps({
            "model": model,
            "messages": [{"role": "user", "content": prompt}],
            "temperature": 0.2,
            "max_tokens": 1500,
        }).encode("utf-8")
        req = urllib.request.Request(
            url,
            data=body,
            headers={
                "Authorization": f"Bearer {os.environ[key_var]}",
                "Content-Type": "application/json",
            },
        )
        try:
            with urllib.request.urlopen(req, timeout=DEFAULT_TIMEOUT) as resp:
                data = json.loads(resp.read())
            content = data.get("choices", [{}])[0].get("message", {}).get("content", "")
            print(f"\n### {name} ({model})\n{content}\n")
        except Exception as exc:  # noqa: BLE001
            print(f"\n### {name}: FAILED — {exc}\n", file=sys.stderr)
    return True


def try_cli(prompt: str) -> bool:
    """Try external CLIs as a last resort."""
    plugin_root = os.environ.get("CLAUDE_PLUGIN_ROOT", str(Path(__file__).parent.parent))
    invoke = Path(plugin_root) / "scripts" / "cli-invoke.sh"
    if not invoke.exists():
        return False

    found_any = False
    for cli in ("codex", "gemini", "aider", "cursor-agent"):
        if subprocess.run(["which", cli], capture_output=True).returncode != 0:
            continue
        found_any = True
        print(f"\n### {cli}", file=sys.stderr)
        result = subprocess.run(
            ["bash", str(invoke), cli, prompt, str(DEFAULT_TIMEOUT)],
            capture_output=True,
            text=True,
        )
        if result.returncode == 0:
            print(result.stdout)
        else:
            print(f"  FAILED — {result.stderr.strip()[:200]}", file=sys.stderr)
    return found_any


def main() -> None:
    args = sys.argv[1:]
    if not args:
        print("usage: python3 llm-query.py '<prompt>' [--provider xai|openai|mistral|all]", file=sys.stderr)
        sys.exit(2)

    provider = "all"
    if "--provider" in args:
        idx = args.index("--provider")
        provider = args[idx + 1] if idx + 1 < len(args) else "all"
        args = args[:idx] + args[idx + 2:]

    prompt = args[0]

    if try_provider_factory(prompt, provider):
        return
    if try_direct_api(prompt, provider):
        return
    if try_cli(prompt):
        return

    print(
        "## no LLM transport reachable\n"
        "## prompt was:\n" + prompt,
        file=sys.stderr,
    )
    sys.exit(1)


if __name__ == "__main__":
    main()
