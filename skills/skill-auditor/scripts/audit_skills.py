#!/usr/bin/env python3
"""Read-only, profile-aware audit for Agent Skills and plugin packages."""

from __future__ import annotations

import argparse
import ast
import json
import os
import re
import sys
from dataclasses import asdict, dataclass
from pathlib import Path
from typing import Iterable
from urllib.parse import unquote


NAME_RE = re.compile(r"^[a-z0-9]+(?:-[a-z0-9]+)*$")
FIELD_RE = re.compile(r"^([A-Za-z0-9_-]+):(?:[ \t]*(.*))?$")
LINK_RE = re.compile(r"(?<!!)\[[^\]\n]+\]\(([^)\n]+)\)")
FENCE_RE = re.compile(r"^\s*(```|~~~)")
INLINE_CODE_RE = re.compile(r"`+[^`\n]*`+")
ABSOLUTE_RE = re.compile(r"(?<![\w.])(/Users/[A-Za-z0-9._-]+/|/home/[A-Za-z0-9._-]+/)")
TRIGGER_RE = re.compile(
    r"\b(use|when|request|ask|mention|invoke|trigger|for tasks?|working with|needs? to)\b",
    re.IGNORECASE,
)


@dataclass(frozen=True, order=True)
class Finding:
    severity: str
    code: str
    path: str
    line: int
    message: str
    fix: str


@dataclass
class SkillRecord:
    path: Path
    root: Path
    name: str | None
    description: str | None
    fields: dict[str, str]
    body: str
    lines: int


SEVERITY_ORDER = {"Critical": 0, "High": 1, "Medium": 2, "Low": 3}


def strip_quotes(value: str) -> str:
    value = value.strip()
    if len(value) >= 2 and value[0] == value[-1] and value[0] in {'"', "'"}:
        try:
            parsed = ast.literal_eval(value)
            if isinstance(parsed, str):
                return parsed
        except (SyntaxError, ValueError):
            return value[1:-1]
    return value


def parse_frontmatter(path: Path, root: Path) -> tuple[SkillRecord, list[Finding]]:
    text = path.read_text(encoding="utf-8", errors="replace")
    lines = text.splitlines()
    findings: list[Finding] = []
    fields: dict[str, str] = {}
    body = text
    if not lines or lines[0].strip() != "---":
        findings.append(
            Finding("High", "S001", str(path), 1, "Missing leading YAML frontmatter.", "Add a leading frontmatter block with name and description.")
        )
    else:
        end = next((i for i in range(1, len(lines)) if lines[i].strip() == "---"), None)
        if end is None:
            findings.append(
                Finding("High", "S001", str(path), 1, "Frontmatter has no closing delimiter.", "Close the YAML block with ---.")
            )
        else:
            front = lines[1:end]
            body = "\n".join(lines[end + 1 :])
            index = 0
            while index < len(front):
                match = FIELD_RE.match(front[index])
                if not match:
                    index += 1
                    continue
                key, raw = match.group(1), (match.group(2) or "").strip()
                if raw in {">", "|", ">-", "|-"}:
                    parts: list[str] = []
                    index += 1
                    while index < len(front) and (front[index].startswith(" ") or not front[index].strip()):
                        parts.append(front[index].strip())
                        index += 1
                    fields[key] = " ".join(part for part in parts if part)
                    continue
                fields[key] = strip_quotes(raw)
                index += 1
    name = fields.get("name") or None
    description = fields.get("description") or None
    if not name:
        findings.append(Finding("High", "S002", str(path), 1, "Missing skill name.", "Add a unique lowercase kebab-case name."))
    elif not NAME_RE.fullmatch(name):
        findings.append(Finding("High", "S003", str(path), 1, f"Invalid skill name: {name!r}.", "Use lowercase letters, digits, and internal hyphens."))
    if not description:
        findings.append(Finding("High", "S002", str(path), 1, "Missing skill description.", "Describe what the skill does and when it should trigger."))
    elif len(description) < 40 or len(description) > 600:
        findings.append(
            Finding("Medium", "T001", str(path), 1, f"Description length is {len(description)} characters.", "Keep enough detail for routing without turning metadata into a workflow.")
        )
    elif not TRIGGER_RE.search(description):
        findings.append(
            Finding("Medium", "T002", str(path), 1, "Description does not state useful trigger context.", "Add a concise use/when clause to the description.")
        )
    if len(lines) > 1000:
        findings.append(Finding("High", "C001", str(path), 1, f"SKILL.md is {len(lines)} lines.", "Move conditional detail into directly linked references or scripts."))
    elif len(lines) > 500:
        findings.append(Finding("Medium", "C001", str(path), 1, f"SKILL.md is {len(lines)} lines.", "Review for progressive-disclosure opportunities."))
    return SkillRecord(path, root, name, description, fields, body, len(lines)), findings


def visible_lines(text: str) -> Iterable[tuple[int, str]]:
    fenced = False
    marker = ""
    for number, line in enumerate(text.splitlines(), 1):
        match = FENCE_RE.match(line)
        if match:
            token = match.group(1)
            if not fenced:
                fenced, marker = True, token
            elif token == marker:
                fenced, marker = False, ""
            continue
        if not fenced:
            yield number, line


def audit_links(record: SkillRecord) -> list[Finding]:
    findings: list[Finding] = []
    text = record.path.read_text(encoding="utf-8", errors="replace")
    for line_number, line in visible_lines(text):
        line = INLINE_CODE_RE.sub("", line)
        for raw in LINK_RE.findall(line):
            target = raw.strip().split(maxsplit=1)[0].strip("<>")
            if not target or target.startswith(("#", "http://", "https://", "mailto:", "skill://")):
                continue
            target = unquote(target).split("#", 1)[0].split("?", 1)[0]
            if not target or any(token in target for token in ("<", ">", "{", "}", "*")):
                continue
            resolved = (record.path.parent / target).resolve(strict=False)
            if not resolved.exists():
                findings.append(
                    Finding("High", "R001", str(record.path), line_number, f"Broken relative Markdown link: {raw!r}.", "Create the referenced resource or correct/remove the link.")
                )
    return findings


def audit_portability(record: SkillRecord, profile: str) -> list[Finding]:
    if profile not in {"cross-runtime", "codex", "agent-skills"}:
        return []
    findings: list[Finding] = []
    for line_number, line in visible_lines(record.path.read_text(encoding="utf-8", errors="replace")):
        line = INLINE_CODE_RE.sub("", line)
        match = ABSOLUTE_RE.search(line)
        if match:
            findings.append(
                Finding("Medium", "X001", str(record.path), line_number, f"Machine-specific absolute path: {match.group(1)!r}.", "Use a portable root, runtime discovery, or an explicitly host-local profile.")
            )
    return findings


def load_json(path: Path, findings: list[Finding]) -> dict | None:
    try:
        value = json.loads(path.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError) as exc:
        findings.append(Finding("High", "P001", str(path), 1, f"Invalid plugin JSON: {exc}.", "Repair the JSON before packaging."))
        return None
    if not isinstance(value, dict):
        findings.append(Finding("High", "P001", str(path), 1, "Plugin metadata is not a JSON object.", "Use an object at the document root."))
        return None
    return value


def local_source_path(manifest: Path, source: object) -> Path | None:
    if isinstance(source, str):
        if source.startswith(("http://", "https://", "git@")):
            return None
        return (manifest.parent.parent / source).resolve(strict=False)
    if isinstance(source, dict):
        candidate = source.get("path") or source.get("url")
        if not isinstance(candidate, str) or candidate.startswith(("http://", "https://", "git@")):
            return None
        if manifest.parent.name == "plugins" and manifest.parent.parent.name == ".agents":
            base = manifest.parents[2]
        else:
            base = manifest.parent
        return (base / candidate).resolve(strict=False)
    return None


def audit_manifests(root: Path) -> tuple[list[Finding], int]:
    findings: list[Finding] = []
    manifests: dict[str, tuple[Path, dict]] = {}
    for runtime, relative in {
        "claude": ".claude-plugin/plugin.json",
        "codex": ".codex-plugin/plugin.json",
    }.items():
        path = root / relative
        if path.exists():
            data = load_json(path, findings)
            if data is not None:
                manifests[runtime] = (path, data)
                skills = data.get("skills")
                if isinstance(skills, str):
                    resolved = (root / skills).resolve(strict=False)
                    if not resolved.exists():
                        findings.append(Finding("High", "P002", str(path), 1, f"Manifest skills path does not exist: {skills!r}.", "Correct the path or create the skills directory."))
    if len(manifests) == 2:
        claude = manifests["claude"][1]
        codex = manifests["codex"][1]
        for field in ("name", "version", "repository"):
            if claude.get(field) != codex.get(field):
                findings.append(
                    Finding("High", "P003", str(manifests["codex"][0]), 1, f"Claude/Codex manifest mismatch for {field}: {claude.get(field)!r} != {codex.get(field)!r}.", "Align shared plugin identity fields.")
                )
    for relative in (".claude-plugin/marketplace.json", ".agents/plugins/marketplace.json"):
        path = root / relative
        if not path.exists():
            continue
        data = load_json(path, findings)
        if data is None:
            continue
        plugins = data.get("plugins", [])
        if not isinstance(plugins, list):
            findings.append(Finding("High", "P001", str(path), 1, "Marketplace plugins value is not a list.", "Use a plugins array."))
            continue
        for plugin in plugins:
            if not isinstance(plugin, dict):
                continue
            resolved = local_source_path(path, plugin.get("source"))
            if resolved is not None and not resolved.exists():
                findings.append(Finding("High", "P002", str(path), 1, f"Marketplace source path does not exist: {plugin.get('source')!r}.", "Correct the source relative to the marketplace file."))
    return findings, len(manifests)


def discover_skills(root: Path) -> list[Path]:
    if root.is_file():
        return [root] if root.name == "SKILL.md" else []
    skills: list[Path] = []
    seen_directories: set[tuple[int, int]] = set()
    for directory, children, files in os.walk(root, followlinks=True):
        path = Path(directory)
        try:
            stat = path.stat()
        except OSError:
            children[:] = []
            continue
        identity = (stat.st_dev, stat.st_ino)
        if identity in seen_directories:
            children[:] = []
            continue
        seen_directories.add(identity)
        children[:] = sorted(child for child in children if child != ".git")
        if "SKILL.md" in files:
            skills.append(path / "SKILL.md")
    return sorted(skills)


def discover_package_roots(root: Path) -> list[Path]:
    if not root.is_dir():
        return []
    package_roots = {root}
    seen_directories: set[tuple[int, int]] = set()
    for directory, children, files in os.walk(root, followlinks=True):
        path = Path(directory)
        try:
            stat = path.stat()
        except OSError:
            children[:] = []
            continue
        identity = (stat.st_dev, stat.st_ino)
        if identity in seen_directories:
            children[:] = []
            continue
        seen_directories.add(identity)
        children[:] = sorted(child for child in children if child != ".git")
        if path.name in {".claude-plugin", ".codex-plugin"} and "plugin.json" in files:
            package_roots.add(path.parent)
        if path.parts[-2:] == (".agents", "plugins") and "marketplace.json" in files:
            package_roots.add(path.parents[1])
    return sorted(package_roots)


def detect_profile(roots: list[Path], requested: str) -> str:
    if requested != "auto":
        return requested
    has_codex = any((root / ".codex-plugin/plugin.json").exists() for root in roots if root.is_dir())
    has_claude = any((root / ".claude-plugin/plugin.json").exists() for root in roots if root.is_dir())
    if has_codex and has_claude:
        return "cross-runtime"
    if has_codex:
        return "codex"
    if has_claude:
        return "claude"
    return "agent-skills"


def audit(roots: list[Path], profile: str) -> tuple[list[SkillRecord], list[Finding], int]:
    records: list[SkillRecord] = []
    findings: list[Finding] = []
    plugin_count = 0
    for root in roots:
        if not root.exists():
            findings.append(Finding("Critical", "S000", str(root), 1, "Audit root does not exist.", "Correct the scope path."))
            continue
        for path in discover_skills(root):
            record, parsed = parse_frontmatter(path, root)
            records.append(record)
            findings.extend(parsed)
            findings.extend(audit_links(record))
            findings.extend(audit_portability(record, profile))
        for package_root in discover_package_roots(root):
            manifest_findings, count = audit_manifests(package_root)
            findings.extend(manifest_findings)
            plugin_count += count
    by_name: dict[str, list[SkillRecord]] = {}
    for record in records:
        if record.name:
            by_name.setdefault(record.name, []).append(record)
    for name, matches in sorted(by_name.items()):
        if len(matches) > 1:
            for record in matches:
                findings.append(Finding("High", "S003", str(record.path), 1, f"Duplicate skill name {name!r} appears in {len(matches)} audited packages.", "Choose one owner or give compatibility routes unique names."))
    unique = {(item.severity, item.code, item.path, item.line, item.message, item.fix): item for item in findings}
    ordered = sorted(unique.values(), key=lambda item: (SEVERITY_ORDER[item.severity], item.code, item.path, item.line, item.message))
    return records, ordered, plugin_count


def markdown_report(roots: list[Path], profile: str, records: list[SkillRecord], findings: list[Finding], plugin_count: int) -> str:
    affected = {item.path for item in findings}
    counts = {severity: sum(item.severity == severity for item in findings) for severity in SEVERITY_ORDER}
    output = [
        "# Skill and Plugin Audit",
        "",
        "## Summary",
        f"- Profile: {profile}",
        f"- Roots: {len(roots)}",
        f"- Skills: {len(records)}",
        f"- Plugin manifests: {plugin_count}",
        *[f"- {severity}: {counts[severity]}" for severity in SEVERITY_ORDER],
        f"- Clean skills: {sum(str(record.path) not in affected for record in records)} / {len(records)}",
    ]
    for severity in SEVERITY_ORDER:
        output.extend(["", f"## {severity} findings"])
        selected = [item for item in findings if item.severity == severity]
        if not selected:
            output.append("None.")
            continue
        for item in selected:
            output.append(f"- `{item.code}` `{item.path}:{item.line}` — {item.message} **Fix:** {item.fix}")
    clean = sorted(str(record.path) for record in records if str(record.path) not in affected)
    output.extend(["", "## Clean skills"])
    output.extend(f"- `{path}`" for path in clean) if clean else output.append("None.")
    return "\n".join(output) + "\n"


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("roots", nargs="+", type=Path)
    parser.add_argument("--profile", choices=("auto", "agent-skills", "codex", "claude", "cross-runtime"), default="auto")
    parser.add_argument("--format", choices=("markdown", "json"), default="markdown")
    args = parser.parse_args()
    roots = [path.expanduser().resolve(strict=False) for path in args.roots]
    profile = detect_profile(roots, args.profile)
    records, findings, plugin_count = audit(roots, profile)
    if args.format == "json":
        payload = {
            "profile": profile,
            "roots": [str(path) for path in roots],
            "skills": len(records),
            "plugin_manifests": plugin_count,
            "findings": [asdict(item) for item in findings],
        }
        print(json.dumps(payload, indent=2, sort_keys=True))
    else:
        print(markdown_report(roots, profile, records, findings, plugin_count), end="")
    return 1 if any(item.severity in {"Critical", "High"} for item in findings) else 0


if __name__ == "__main__":
    sys.exit(main())
