# Helper profiles

Craft ships optional specialist instructions in `agents/`. A host that exposes
those named profiles may launch them directly. Codex does not discover Claude
Code's `agents/` directory as named agents, so read the matching profile and
give its task to a general subagent instead. Work in the current agent when
delegation is unavailable.

Treat a profile name such as `craft-validator` as a role, not a required runtime
capability. Do not assume a named helper exists merely because a skill mentions
it. Preserve parallel execution when the selected reviews are independent.
