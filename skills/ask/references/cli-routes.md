# Native CLI setup and evidence

Ask invokes installed executables. It does not install software, log in, pull
models, or switch to a gateway. Python 3.11+, a POSIX host, and the selected CLI
are required. `--list` / `--status` inspect executable presence only; authentication
remains unchecked until an authorized call succeeds.

## Private configuration

Use mode 600 (or 400) for `~/.config/craft/ask.env` and any credential file.
The parser accepts literal `KEY=value` lines without executing shell code.
Environment values take precedence. Supported options:

| Option | Meaning |
|---|---|
| `ASK_DEFAULT_PROVIDER` | `claude`, `grok`, `zai`, or `ollama` |
| `ASK_TIMEOUT` | Deadline in seconds, default 120, maximum 3600 |
| `ASK_CLAUDE_CLI`, `ASK_GROK_CLI`, `ASK_ZAI_CLI`, `ASK_OLLAMA_CLI` | Executable path; Z.ai defaults to `claude` |
| `ASK_CLAUDE_MODEL`, `ASK_GROK_MODEL`, `ASK_ZAI_MODEL`, `ASK_OLLAMA_MODEL` | Requested model or CLI alias |
| `ZAI_API_KEY_FILE` | Private key file; defaults to `~/.config/craft/zai.key` |
| `ZAI_API_KEY` | Alternative secret environment/config value |
| `OLLAMA_HOST` | Selected local or remote Ollama server |

`--model` overrides a route's configured model for one call. Claude defaults to
its `opus` alias; Grok uses the CLI default; Z.ai requests `glm-5.3`. Ollama
requires an explicit model already installed on the selected server. No models
are downloaded by Ask. Claude API keys and OAuth tokens already in the process
environment remain usable only for the Anthropic route; native subscription
login remains the ordinary default. Login using each CLI's own supported flow.

## Z.ai isolation

[Z.ai's Claude Code guide](https://docs.z.ai/devpack/tool/claude) documents the
Coding Plan's Anthropic-compatible endpoint and token. Ask sets
`ANTHROPIC_BASE_URL=https://api.z.ai/api/anthropic` only in the Z.ai subprocess,
uses a private temporary `CLAUDE_CONFIG_DIR`, and removes it after the call.
It never rewrites `~/.claude/settings.json` or replaces an Anthropic login.
The ordinary Claude route uses the Anthropic endpoint explicitly and does not
inherit Z.ai endpoint variables. The key is not passed on the command line.

## Execution constraints

Claude Code print mode uses JSON output, no tools or MCP servers, disabled
hooks and memory, no persisted session, one turn, and no project/user settings.
Grok uses single-turn JSON output, an explicit empty tool allowlist, denied
tool permissions, no web search or subagents, and verbatim prompting. Its
private temporary `GROK_HOME` copies only the native OAuth record, disables
compatibility hooks/MCP/instructions, and disables discovered skills/plugins.
Native token refresh is retained only while the source credential is unchanged.
The user home and ordinary CLI configuration remain unchanged. An empty string
for Grok `--tools` means default tools, so the adapter instead selects a tool
name that matches none. This distinction is covered by a regression fixture.
See [Grok settings](https://docs.x.ai/build/settings/reference) and the
[upstream CLI parser](https://github.com/xai-org/grok-build/blob/main/crates/codegen/xai-grok-pager/src/headless/cli.rs). Both run in a new private scratch
directory. Ollama's native `list` inventory must contain the exact configured tag before
`run` can execute; this prevents its automatic download behavior. `run` consumes
stdin without an agent/tool loop.
Timeout kills the process group; failures do not retry or fall back. Error bodies
are classified without being echoed, since a CLI may include secrets in errors.
A CLI may maintain its own account/session logs; Ask's scratch cleanup does not
promise removal of provider-side or native CLI records.

CLI flags were checked against Claude Code 2.1.272, Grok 1.0.25, and Ollama
0.32.x. Older versions missing required safety flags must fail and be upgraded;
never retry with those protections removed.

## Provenance and failures

JSON output separates the configured provider, requested model, and model
reported by the CLI. Claude's `modelUsage` map can supply a reported model when
it contains exactly one model. A CLI alias such as `opus` may resolve to a newer
model; concrete requested model IDs must match a reported ID. An absent model
is `null`, with `provenance: requested-only`. Ollama CLI's plain output does not
report model identity, so its configured selection is never relabeled as a
verified model response. Missing metadata may still provide advisory prose,
but must not count as verified model diversity in Consensus.

Exit codes: 2 invalid input; 3 credentials/config permissions; 4 unavailable
CLI/model; 5 quota/rate limit; 6 process/transport/deadline; 7 malformed response,
empty content, or model mismatch. No all-provider health sweep is provided.
