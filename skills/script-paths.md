# Bundled script paths

Set `CRAFT_PLUGIN_ROOT` to Craft's plugin directory before running a bundled
script. Claude Code exposes that directory as `CLAUDE_PLUGIN_ROOT`. In Codex
and other hosts, resolve it from the absolute path of the loaded `SKILL.md`:
the plugin root is the directory that contains both `skills/` and `scripts/`.

Confirm the expected script exists before running it. Do not resolve bundled
scripts from the project working directory, and do not assume a personal
installation path.
