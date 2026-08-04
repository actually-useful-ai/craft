# Check catalog

## Universal errors

- `S001` Missing or unterminated YAML frontmatter.
- `S002` Missing `name` or `description`.
- `S003` Invalid or duplicate skill name.
- `R001` Broken relative Markdown link outside a fenced code block.
- `P001` Invalid plugin or marketplace JSON.
- `P002` Manifest `skills` or local marketplace source path does not exist.
- `P003` Identity/version mismatch between manifests describing one plugin.

## High-confidence warnings

- `T001` Description is implausibly short or too large for reliable routing.
- `T002` Description names capability but no useful trigger context.
- `C001` `SKILL.md` exceeds 500 lines; over 1,000 lines is High severity.
- `C002` An entry file unconditionally loads several references or variants.
- `X001` Machine-specific absolute path appears in portable content.
- `X002` Named external capability has no detection or fallback.
- `X003` Provider, model, or platform “current” roster is duplicated as prose.
- `I001` Installed content differs from its canonical source/version.
- `I002` One runtime resolves the same skill name from several active roots.

## Manual semantic checks

- Trigger collisions and negative-trigger exclusions.
- Executor, overlay, governor, and auditor role clarity.
- Authorization boundaries and reversibility.
- Completion criteria that can be observed or tested.
- Boilerplate shared across leaf skills.
- Quality language that rewards verbosity, ornamental architecture, or ceremonial tool use.

## Reference parsing rules

- Inspect Markdown link destinations, not every token ending in `.md`.
- Ignore fenced code blocks, URLs, `mailto:`, anchors, templated placeholders, and deliberately non-local examples.
- Resolve links relative to the file containing the link.
- Strip query and anchor suffixes before checking the filesystem.
- A directory link is valid when the directory exists.
