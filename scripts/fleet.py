#!/usr/bin/env python3
"""Audit and safely repair a manifest-declared plugin fleet."""

from __future__ import annotations

import argparse
import base64
import datetime as dt
import hashlib
import json
import os
from pathlib import Path
import re
import shutil
import subprocess
import sys
import tomllib
from typing import Any, Iterable
from urllib.parse import urlsplit, urlunsplit


ROOT = Path(__file__).resolve().parents[1]
DEFAULT_BOM = ROOT / "fleet.toml"
DEFAULT_HOSTS = Path("~/.config/craft/fleet-hosts.toml").expanduser()
RUNTIMES = ("claude", "codex", "cursor", "grok")
PASS = "pass"
FAIL = "fail"
NA = "na"
REFERENCE = "reference"
IGNORED_NAMES = {".DS_Store", "__pycache__"}
IGNORED_SUFFIXES = {".pyc", ".pyo"}
SEMVER_PATH = re.compile(r"(?:^|/)(\d+\.\d+\.\d+(?:[-+][0-9A-Za-z.-]+)?)(?:/|$)")


class ConfigurationError(ValueError):
    """Raised when the public BOM or personal host config is unsafe."""


def _read_toml(path: Path) -> dict[str, Any]:
    try:
        with path.open("rb") as handle:
            return tomllib.load(handle)
    except FileNotFoundError as error:
        raise ConfigurationError(f"configuration not found: {path}") from error
    except tomllib.TOMLDecodeError as error:
        raise ConfigurationError(f"invalid TOML in {path}: {error}") from error


def _relative_path(value: str, label: str) -> str:
    if not isinstance(value, str):
        raise ConfigurationError(f"{label} must be a string")
    path = Path(value)
    if path.is_absolute() or ".." in path.parts or value in ("", "."):
        raise ConfigurationError(f"{label} must be a non-empty relative path: {value!r}")
    return path.as_posix()


def _string_list(value: Any, label: str) -> list[str]:
    if not isinstance(value, list) or any(not isinstance(item, str) for item in value):
        raise ConfigurationError(f"{label} must be an array of strings")
    return list(value)


def _runtime_mapping(value: Any, label: str) -> dict[str, Any]:
    if not isinstance(value, dict):
        raise ConfigurationError(f"{label} must be a table")
    unknown = set(value) - set(RUNTIMES)
    if unknown:
        raise ConfigurationError(f"{label} has unknown runtimes: {sorted(unknown)}")
    return value


def load_bom(path: Path) -> dict[str, Any]:
    data = _read_toml(path)
    unknown_top = set(data) - {
        "schema_version",
        "fleet_version",
        "defaults",
        "runtime_roots",
        "packages",
        "legacy_links",
    }
    if unknown_top:
        raise ConfigurationError(f"fleet.toml has unknown fields: {sorted(unknown_top)}")
    if data.get("schema_version") != 1:
        raise ConfigurationError("fleet.toml schema_version must be 1")
    if not isinstance(data.get("fleet_version"), str) or not data["fleet_version"]:
        raise ConfigurationError("fleet.toml fleet_version must be a string")
    packages = data.get("packages")
    if not isinstance(packages, list) or not packages:
        raise ConfigurationError("fleet.toml must declare at least one [[packages]] entry")
    defaults = data.get("defaults", {})
    if not isinstance(defaults, dict):
        raise ConfigurationError("defaults must be a table")
    unknown_defaults = set(defaults) - {
        "checkout_root",
        "cursor_installed_roots",
        "backup_root",
    }
    if unknown_defaults:
        raise ConfigurationError(
            f"defaults has unknown fields: {sorted(unknown_defaults)}"
        )
    checkout_root = defaults.get("checkout_root", "~/plugins")
    backup_root = defaults.get(
        "backup_root", "~/.local/state/craft/fleet-backups"
    )
    if not isinstance(checkout_root, str) or not checkout_root:
        raise ConfigurationError("defaults.checkout_root must be a string")
    if not isinstance(backup_root, str) or not backup_root:
        raise ConfigurationError("defaults.backup_root must be a string")
    defaults["cursor_installed_roots"] = _string_list(
        defaults.get("cursor_installed_roots", ["~/.cursor/plugins/cache"]),
        "defaults.cursor_installed_roots",
    )
    data["defaults"] = defaults

    seen: set[str] = set()
    for package in packages:
        if not isinstance(package, dict):
            raise ConfigurationError("every package must be a table")
        unknown_package = set(package) - {
            "name",
            "directory",
            "version",
            "origin",
            "ref",
            "hash_paths",
            "runtimes",
            "install_ids",
        }
        if unknown_package:
            raise ConfigurationError(
                f"package has unknown fields: {sorted(unknown_package)}"
            )
        required = ("name", "directory", "version", "origin", "ref", "hash_paths")
        missing = [key for key in required if not package.get(key)]
        if missing:
            raise ConfigurationError(
                f"package is missing required fields {', '.join(missing)}"
            )
        for field in ("name", "directory", "version", "origin", "ref"):
            if not isinstance(package[field], str):
                raise ConfigurationError(f"package.{field} must be a string")
        name = package["name"]
        if name in seen:
            raise ConfigurationError(f"duplicate package name: {name}")
        seen.add(name)
        package["directory"] = _relative_path(package["directory"], f"{name}.directory")
        package["hash_paths"] = [
            _relative_path(item, f"{name}.hash_paths")
            for item in _string_list(package["hash_paths"], f"{name}.hash_paths")
        ]
        runtimes = _runtime_mapping(package.get("runtimes", {}), f"{name}.runtimes")
        package["runtimes"] = {
            runtime: _relative_path(manifest, f"{name}.{runtime} manifest")
            for runtime, manifest in runtimes.items()
        }
        install_ids = _runtime_mapping(
            package.get("install_ids", {}), f"{name}.install_ids"
        )
        if set(install_ids) != set(package["runtimes"]):
            raise ConfigurationError(
                f"{name}.install_ids must cover exactly its declared runtimes"
            )
        if any(not isinstance(install_id, str) or not install_id for install_id in install_ids.values()):
            raise ConfigurationError(f"{name}.install_ids values must be non-empty strings")
        package["install_ids"] = dict(install_ids)

    roots = _runtime_mapping(data.get("runtime_roots", {}), "runtime_roots")
    data["runtime_roots"] = {
        runtime: _string_list(roots.get(runtime, []), f"runtime_roots.{runtime}")
        for runtime in RUNTIMES
    }

    seen_links: set[str] = set()
    for link in data.get("legacy_links", []):
        if not isinstance(link, dict):
            raise ConfigurationError("every legacy link must be a table")
        unknown_link = set(link) - {"root", "runtime", "path"}
        if unknown_link:
            raise ConfigurationError(
                f"legacy link has unknown fields: {sorted(unknown_link)}"
            )
        missing = [key for key in ("root", "runtime", "path") if not link.get(key)]
        if missing:
            raise ConfigurationError(
                f"legacy link is missing required fields {', '.join(missing)}"
            )
        if link["runtime"] not in RUNTIMES:
            raise ConfigurationError(f"legacy link has unknown runtime {link['runtime']!r}")
        if not isinstance(link["root"], str) or not re.fullmatch(r"[a-z0-9-]+", link["root"]):
            raise ConfigurationError("legacy link root must be lower-case letters, digits, or hyphens")
        if not isinstance(link["path"], str) or link["path"] in seen_links:
            raise ConfigurationError(f"legacy link paths must be unique strings: {link['path']!r}")
        seen_links.add(link["path"])
    return data


def _default_host(bom: dict[str, Any]) -> dict[str, Any]:
    expected = []
    commands = {
        "claude": "claude",
        "codex": "codex",
        "cursor": "cursor-agent",
        "grok": "grok",
    }
    for runtime, command in commands.items():
        if shutil.which(command) or (runtime == "cursor" and shutil.which("cursor")):
            expected.append(runtime)
    return {
        "name": "local",
        "transport": "local",
        "reference": True,
        "checkout_root": bom.get("defaults", {}).get("checkout_root", "~/plugins"),
        "runtime_roots": bom["runtime_roots"],
        "expected_runtimes": expected,
        "installed_roots": {
            "claude": [],
            "codex": [],
            "cursor": list(
                bom.get("defaults", {}).get(
                    "cursor_installed_roots", ["~/.cursor/plugins/cache"]
                )
            ),
            "grok": [],
        },
        "backup_root": bom.get("defaults", {}).get(
            "backup_root", "~/.local/state/craft/fleet-backups"
        ),
        "paths": {},
    }


def load_hosts(path: Path | None, bom: dict[str, Any]) -> tuple[list[dict[str, Any]], dict[str, Any]]:
    if path is None:
        if DEFAULT_HOSTS.is_file():
            path = DEFAULT_HOSTS
        else:
            return [_default_host(bom)], {
                "ssh_bin": "ssh",
                "connect_timeout": 10,
                "ssh_args": [],
            }

    data = _read_toml(path)
    unknown_top = set(data) - {"settings", "hosts"}
    if unknown_top:
        raise ConfigurationError(f"host config has unknown fields: {sorted(unknown_top)}")
    settings = data.get("settings", {})
    if not isinstance(settings, dict):
        raise ConfigurationError("settings must be a table")
    unknown_settings = set(settings) - {"ssh_bin", "connect_timeout", "ssh_args"}
    if unknown_settings:
        raise ConfigurationError(
            f"settings has unknown fields: {sorted(unknown_settings)}"
        )
    hosts = data.get("hosts")
    if not isinstance(hosts, list) or not hosts:
        raise ConfigurationError("host config must contain at least one [[hosts]] entry")

    names: set[str] = set()
    package_names = {package["name"] for package in bom["packages"]}
    normalized: list[dict[str, Any]] = []
    for raw in hosts:
        if not isinstance(raw, dict):
            raise ConfigurationError("every host must be a table")
        unknown_host = set(raw) - {
            "name",
            "transport",
            "reference",
            "checkout_root",
            "target",
            "jump",
            "ssh_args",
            "paths",
            "runtime_roots",
            "installed_roots",
            "expected_runtimes",
            "backup_root",
        }
        if unknown_host:
            raise ConfigurationError(
                f"host has unknown fields: {sorted(unknown_host)}"
            )
        host = dict(raw)
        name = host.get("name")
        transport = host.get("transport")
        if not name or name in names:
            raise ConfigurationError(f"host names must be present and unique: {name!r}")
        if transport not in ("local", "ssh"):
            raise ConfigurationError(f"host {name} transport must be local or ssh")
        if transport == "ssh" and not host.get("target"):
            raise ConfigurationError(f"SSH host {name} requires target")
        if "reference" in host and not isinstance(host["reference"], bool):
            raise ConfigurationError(f"host {name}.reference must be boolean")
        for field in ("checkout_root", "target", "jump"):
            if field in host and (
                not isinstance(host[field], str) or not host[field]
            ):
                raise ConfigurationError(f"host {name}.{field} must be a string")
        expected = host.get("expected_runtimes")
        if expected is None:
            if transport == "ssh":
                raise ConfigurationError(
                    f"SSH host {name} requires expected_runtimes"
                )
            expected = _default_host(bom)["expected_runtimes"]
        expected = _string_list(expected, f"host {name}.expected_runtimes")
        unknown_expected = set(expected) - set(RUNTIMES)
        if unknown_expected:
            raise ConfigurationError(
                f"host {name} has unknown expected runtimes: {sorted(unknown_expected)}"
            )
        if len(expected) != len(set(expected)):
            raise ConfigurationError(f"host {name}.expected_runtimes contains duplicates")
        host["expected_runtimes"] = expected
        names.add(name)
        host.setdefault(
            "checkout_root", bom.get("defaults", {}).get("checkout_root", "~/plugins")
        )
        host.setdefault("paths", {})
        if not isinstance(host["paths"], dict) or any(
            package not in package_names or not isinstance(value, str)
            for package, value in host["paths"].items()
        ):
            raise ConfigurationError(f"host {name}.paths must map known packages to strings")
        root_overrides = _runtime_mapping(
            host.get("runtime_roots", {}), f"host {name}.runtime_roots"
        )
        runtime_roots = dict(bom["runtime_roots"])
        runtime_roots.update(root_overrides)
        host["runtime_roots"] = {
            runtime: _string_list(
                runtime_roots.get(runtime, []), f"host {name}.runtime_roots.{runtime}"
            )
            for runtime in RUNTIMES
        }
        installed_overrides = _runtime_mapping(
            host.get("installed_roots", {}), f"host {name}.installed_roots"
        )
        installed_roots = {
            "claude": [],
            "codex": [],
            "cursor": list(
                bom.get("defaults", {}).get(
                    "cursor_installed_roots", ["~/.cursor/plugins/cache"]
                )
            ),
            "grok": [],
        }
        installed_roots.update(installed_overrides)
        host["installed_roots"] = {
            runtime: _string_list(
                installed_roots[runtime], f"host {name}.installed_roots.{runtime}"
            )
            for runtime in RUNTIMES
        }
        backup_root = host.get(
            "backup_root",
            bom.get("defaults", {}).get(
                "backup_root", "~/.local/state/craft/fleet-backups"
            ),
        )
        if not isinstance(backup_root, str) or not backup_root:
            raise ConfigurationError(f"host {name}.backup_root must be a string")
        host["backup_root"] = backup_root
        if "ssh_args" in host:
            host["ssh_args"] = _string_list(host["ssh_args"], f"host {name}.ssh_args")
        normalized.append(host)

    if sum(bool(host.get("reference")) for host in normalized) > 1:
        raise ConfigurationError("only one host may be marked reference = true")
    if not any(host.get("reference") for host in normalized):
        next((host for host in normalized if host["transport"] == "local"), normalized[0])[
            "reference"
        ] = True
    ssh_bin = settings.get("ssh_bin", "ssh")
    timeout = settings.get("connect_timeout", 10)
    if not isinstance(ssh_bin, str) or not ssh_bin:
        raise ConfigurationError("settings.ssh_bin must be a non-empty string")
    if isinstance(timeout, bool) or not isinstance(timeout, int) or timeout <= 0:
        raise ConfigurationError("settings.connect_timeout must be a positive integer")
    return normalized, {
        "ssh_bin": ssh_bin,
        "connect_timeout": timeout,
        "ssh_args": _string_list(settings.get("ssh_args", []), "settings.ssh_args"),
    }


def _expand(value: str) -> Path:
    return Path(os.path.expandvars(os.path.expanduser(value))).absolute()


def _package_root(package: dict[str, Any], host: dict[str, Any]) -> Path:
    override = host.get("paths", {}).get(package["name"])
    if override:
        return _expand(override)
    return _expand(host["checkout_root"]) / package["directory"]


def _run_git(root: Path, *args: str) -> tuple[bool, str]:
    try:
        completed = subprocess.run(
            ["git", "-C", str(root), *args],
            check=False,
            stdout=subprocess.PIPE,
            stderr=subprocess.DEVNULL,
            text=True,
            timeout=15,
        )
    except (OSError, subprocess.TimeoutExpired):
        return False, ""
    return completed.returncode == 0, completed.stdout.strip()


def _safe_origin(value: str) -> str:
    """Remove credentials and normalize common GitHub remote spellings."""
    if not value:
        return ""
    if value.startswith("git@github.com:"):
        value = "https://github.com/" + value.split(":", 1)[1]
    elif value.startswith("ssh://git@github.com/"):
        value = "https://github.com/" + value.split("github.com/", 1)[1]
    parts = urlsplit(value)
    if parts.scheme and parts.hostname:
        host = parts.hostname.lower()
        port = f":{parts.port}" if parts.port else ""
        value = urlunsplit((parts.scheme.lower(), host + port, parts.path, "", ""))
    return value[:-4] if value.endswith(".git") else value


def _status(ok: bool, *, actual: Any = None, expected: Any = None, detail: str = "") -> dict[str, Any]:
    result: dict[str, Any] = {"status": PASS if ok else FAIL}
    if actual is not None:
        result["actual"] = actual
    if expected is not None:
        result["expected"] = expected
    if detail:
        result["detail"] = detail
    return result


def _plugin_record(
    version: Any, enabled: Any, source: str
) -> dict[str, Any]:
    return {
        "version": version if isinstance(version, str) else None,
        "enabled": enabled is True,
        "source": source,
    }


def parse_claude_plugins(payload: str) -> dict[str, dict[str, Any]]:
    data = json.loads(payload)
    if not isinstance(data, list):
        raise ValueError("Claude plugin inventory must be a list")
    inventory: dict[str, dict[str, Any]] = {}
    for item in data:
        if not isinstance(item, dict) or not isinstance(item.get("id"), str):
            continue
        inventory[item["id"]] = _plugin_record(
            item.get("version"), item.get("enabled"), "claude-registry"
        )
    return inventory


def parse_codex_plugins(payload: str) -> dict[str, dict[str, Any]]:
    data = json.loads(payload)
    if not isinstance(data, dict) or not isinstance(data.get("installed"), list):
        raise ValueError("Codex plugin inventory must contain installed[]")
    inventory: dict[str, dict[str, Any]] = {}
    for item in data["installed"]:
        if not isinstance(item, dict) or not isinstance(item.get("pluginId"), str):
            continue
        inventory[item["pluginId"]] = _plugin_record(
            item.get("version"),
            item.get("installed") is True and item.get("enabled") is True,
            "codex-registry",
        )
    return inventory


def _version_from_path(value: Any) -> str | None:
    if not isinstance(value, str):
        return None
    matches = list(SEMVER_PATH.finditer(value.replace("\\", "/")))
    return matches[-1].group(1) if matches else None


def parse_grok_plugins(payload: str) -> dict[str, dict[str, Any]]:
    data = json.loads(payload)
    if not isinstance(data, dict) or not isinstance(data.get("plugins"), list):
        raise ValueError("Grok inventory must contain plugins[]")
    inventory: dict[str, dict[str, Any]] = {}
    for item in data["plugins"]:
        if not isinstance(item, dict) or not isinstance(item.get("name"), str):
            continue
        normalized_path = str(item.get("path", "")).replace("\\", "/")
        source = (
            "claude-import"
            if "/.claude/plugins/" in normalized_path
            else "grok-registry"
        )
        inventory[item["name"]] = _plugin_record(
            item.get("version") or _version_from_path(normalized_path),
            item.get("enabled"),
            source,
        )
    return inventory


def parse_cursor_plugins(roots: Iterable[Path]) -> dict[str, dict[str, Any]]:
    inventory: dict[str, dict[str, Any]] = {}
    for root in roots:
        manifests: list[Path]
        direct = root / ".cursor-plugin/plugin.json"
        if direct.is_file():
            manifests = [direct]
        else:
            manifests = sorted(root.glob("*/*/*/.cursor-plugin/plugin.json"))
        for manifest_path in manifests:
            try:
                manifest = json.loads(manifest_path.read_text(encoding="utf-8"))
            except (OSError, UnicodeError, json.JSONDecodeError):
                continue
            if not isinstance(manifest, dict) or not isinstance(manifest.get("name"), str):
                continue
            relative = manifest_path.relative_to(root)
            install_id = manifest["name"]
            if len(relative.parts) >= 5:
                marketplace = relative.parts[0]
                install_id = f"{manifest['name']}@{marketplace}"
            inventory[install_id] = _plugin_record(
                manifest.get("version"), True, "cursor-cache"
            )
    return inventory


def _run_runtime_command(arguments: list[str]) -> tuple[bool, str, str]:
    if not shutil.which(arguments[0]):
        return False, "", f"{arguments[0]} command unavailable"
    try:
        completed = subprocess.run(
            arguments,
            check=False,
            stdout=subprocess.PIPE,
            stderr=subprocess.DEVNULL,
            text=True,
            timeout=20,
        )
    except (OSError, subprocess.TimeoutExpired) as error:
        return False, "", type(error).__name__
    if completed.returncode != 0:
        return False, "", f"command exited {completed.returncode}"
    return True, completed.stdout, ""


def probe_runtime_inventories(host: dict[str, Any]) -> dict[str, dict[str, Any]]:
    expected = set(host["expected_runtimes"])
    probes: dict[str, dict[str, Any]] = {}
    command_specs = {
        "claude": (["claude", "plugin", "list", "--json"], parse_claude_plugins),
        "codex": (["codex", "plugin", "list", "--json"], parse_codex_plugins),
        "grok": (["grok", "inspect", "--json"], parse_grok_plugins),
    }
    for runtime in RUNTIMES:
        if runtime not in expected:
            probes[runtime] = {"status": NA, "inventory": {}}
            continue
        if runtime == "cursor":
            roots = [_expand(path) for path in host["installed_roots"]["cursor"]]
            existing = [root for root in roots if root.is_dir()]
            if not existing:
                probes[runtime] = {
                    "status": FAIL,
                    "inventory": {},
                    "detail": "no configured Cursor installed root is available",
                }
                continue
            inventory = parse_cursor_plugins(existing)
            probes[runtime] = {
                "status": PASS,
                "inventory": inventory,
                "count": len(inventory),
                "roots": [str(root) for root in existing],
            }
            continue
        arguments, parser = command_specs[runtime]
        ok, payload, detail = _run_runtime_command(arguments)
        if not ok:
            probes[runtime] = {
                "status": FAIL,
                "inventory": {},
                "detail": detail,
            }
            continue
        try:
            inventory = parser(payload)
        except (ValueError, json.JSONDecodeError) as error:
            probes[runtime] = {
                "status": FAIL,
                "inventory": {},
                "detail": f"invalid {runtime} inventory: {error}",
            }
            continue
        probes[runtime] = {
            "status": PASS,
            "inventory": inventory,
            "count": len(inventory),
        }
    return probes


def _activation_checks(
    package: dict[str, Any],
    host: dict[str, Any],
    probes: dict[str, dict[str, Any]],
) -> dict[str, dict[str, Any]]:
    expected_runtimes = set(host["expected_runtimes"])
    results: dict[str, dict[str, Any]] = {}
    for runtime in RUNTIMES:
        install_id = package["install_ids"].get(runtime)
        if runtime not in expected_runtimes:
            results[runtime] = {
                "status": NA,
                "expected": False,
                "install_id": install_id,
            }
            continue
        if not install_id:
            results[runtime] = {
                "status": FAIL,
                "expected": True,
                "detail": "package has no install ID for expected runtime",
            }
            continue
        probe = probes[runtime]
        if probe["status"] != PASS:
            results[runtime] = {
                "status": FAIL,
                "expected": True,
                "install_id": install_id,
                "detail": probe.get("detail", "runtime inventory unavailable"),
            }
            continue
        record = probe["inventory"].get(install_id)
        if not record:
            results[runtime] = {
                "status": FAIL,
                "expected": True,
                "install_id": install_id,
                "expected_version": package["version"],
                "detail": "expected active package is absent",
            }
            continue
        source_ok = runtime != "grok" or record["source"] == "claude-import"
        ok = (
            record["enabled"]
            and record["version"] == package["version"]
            and source_ok
        )
        detail = "active with expected version"
        if not record["enabled"]:
            detail = "package is installed but disabled"
        elif record["version"] != package["version"]:
            detail = "active package version differs from BOM"
        elif not source_ok:
            detail = "Grok package lacks imported Claude path/version evidence"
        results[runtime] = {
            "status": PASS if ok else FAIL,
            "expected": True,
            "install_id": install_id,
            "actual_version": record["version"],
            "expected_version": package["version"],
            "source": record["source"],
            "detail": detail,
        }
    return results


def _iter_logical_files(root: Path, relative_paths: Iterable[str]) -> tuple[list[Path], list[str]]:
    files: list[Path] = []
    missing: list[str] = []
    for relative in relative_paths:
        candidate = root / relative
        if not os.path.lexists(candidate):
            missing.append(relative)
            continue
        if candidate.is_symlink() or candidate.is_file():
            files.append(candidate)
            continue
        if not candidate.is_dir():
            missing.append(relative)
            continue
        for directory, dirnames, filenames in os.walk(candidate, followlinks=False):
            dirnames[:] = sorted(
                name for name in dirnames if name not in IGNORED_NAMES and name != ".git"
            )
            for filename in sorted(filenames):
                path = Path(directory) / filename
                if filename in IGNORED_NAMES or path.suffix in IGNORED_SUFFIXES:
                    continue
                files.append(path)
    return sorted(set(files), key=lambda path: path.relative_to(root).as_posix()), missing


def logical_hash(root: Path, relative_paths: Iterable[str]) -> tuple[str | None, list[str]]:
    files, missing = _iter_logical_files(root, relative_paths)
    if missing or not files:
        return None, missing or ["no logical files"]
    digest = hashlib.sha256()
    for path in files:
        relative = path.relative_to(root).as_posix().encode("utf-8")
        digest.update(len(relative).to_bytes(8, "big"))
        digest.update(relative)
        if path.is_symlink():
            content = ("SYMLINK\0" + os.readlink(path)).encode("utf-8")
        else:
            content = path.read_bytes()
        digest.update(len(content).to_bytes(8, "big"))
        digest.update(content)
    return digest.hexdigest(), []


def _runtime_checks(root: Path, package: dict[str, Any]) -> dict[str, dict[str, Any]]:
    results: dict[str, dict[str, Any]] = {}
    for runtime in RUNTIMES:
        relative = package["runtimes"].get(runtime)
        if not relative:
            results[runtime] = {
                "status": NA,
                "manifest": {"status": NA},
                "version": {"status": NA},
            }
            continue
        path = root / relative
        result: dict[str, Any] = {"path": relative}
        try:
            manifest = json.loads(path.read_text(encoding="utf-8"))
            skills_value = manifest.get("skills") if isinstance(manifest, dict) else None
            skills_ok = skills_value in ("skills", "./skills/")
            if skills_value is None and runtime in ("claude", "grok"):
                # Claude plugins discover a conventional root skills/ directory
                # without requiring an explicit manifest field. Grok imports that
                # same Claude package, so the identical convention applies there.
                skills_ok = (root / "skills").is_dir()
            valid = (
                isinstance(manifest, dict)
                and manifest.get("name") == package["name"]
                and skills_ok
            )
            result["manifest"] = _status(
                valid,
                actual=manifest.get("name") if isinstance(manifest, dict) else None,
                expected=package["name"],
                detail="valid JSON with matching name and skills path" if valid else "invalid package identity or skills path",
            )
            actual_version = manifest.get("version") if isinstance(manifest, dict) else None
            result["version"] = _status(
                actual_version == package["version"],
                actual=actual_version,
                expected=package["version"],
            )
        except (OSError, UnicodeError, json.JSONDecodeError):
            result["manifest"] = _status(False, detail="missing or invalid JSON manifest")
            result["version"] = _status(False, expected=package["version"])
        result["status"] = (
            PASS
            if result["manifest"]["status"] == PASS and result["version"]["status"] == PASS
            else FAIL
        )
        results[runtime] = result
    return results


def _aggregate_runtime(results: dict[str, dict[str, Any]], field: str) -> dict[str, Any]:
    statuses = [result[field]["status"] for result in results.values()]
    applicable = [status for status in statuses if status != NA]
    if not applicable:
        return {"status": NA}
    return {"status": PASS if all(status == PASS for status in applicable) else FAIL}


def _aggregate_status(results: dict[str, dict[str, Any]]) -> dict[str, Any]:
    applicable = [result["status"] for result in results.values() if result["status"] != NA]
    if not applicable:
        return {"status": NA}
    return {"status": PASS if all(status == PASS for status in applicable) else FAIL}


def audit_package(
    package: dict[str, Any],
    host: dict[str, Any],
    probes: dict[str, dict[str, Any]],
) -> dict[str, Any]:
    root = _package_root(package, host)
    result: dict[str, Any] = {
        "name": package["name"],
        "path": str(root),
        "expected": {
            "origin": _safe_origin(package["origin"]),
            "ref": package["ref"],
            "version": package["version"],
        },
    }
    checkout_ok = root.is_dir() and (root / ".git").exists()
    checks: dict[str, dict[str, Any]] = {
        "checkout": _status(checkout_ok, actual=str(root), expected="Git checkout")
    }
    result["checks"] = checks
    activation = _activation_checks(package, host, probes)
    result["activation"] = activation
    checks["activation"] = _aggregate_status(activation)

    if not checkout_ok:
        for name in ("origin", "ref", "clean", "manifest", "version", "logical_hash"):
            checks[name] = _status(False, detail="checkout unavailable")
        result["runtimes"] = _runtime_checks(root, package)
        return result

    origin_ok, origin = _run_git(root, "remote", "get-url", "origin")
    safe_actual_origin = _safe_origin(origin)
    safe_expected_origin = _safe_origin(package["origin"])
    checks["origin"] = _status(
        origin_ok and safe_actual_origin == safe_expected_origin,
        actual=safe_actual_origin or None,
        expected=safe_expected_origin,
    )

    head_ok, head = _run_git(root, "rev-parse", "HEAD")
    ref_ok, ref_head = _run_git(root, "rev-parse", "--verify", f"{package['ref']}^{{commit}}")
    checks["ref"] = _status(
        head_ok and ref_ok and head == ref_head,
        actual=head[:12] if head_ok else None,
        expected=package["ref"],
    )

    clean_ok, porcelain = _run_git(root, "status", "--porcelain", "--untracked-files=all")
    checks["clean"] = _status(clean_ok and not porcelain, actual="clean" if clean_ok and not porcelain else "dirty")

    runtimes = _runtime_checks(root, package)
    result["runtimes"] = runtimes
    checks["manifest"] = _aggregate_runtime(runtimes, "manifest")
    checks["version"] = _aggregate_runtime(runtimes, "version")

    try:
        digest, missing = logical_hash(root, package["hash_paths"])
        checks["logical_hash"] = (
            {"status": PASS, "actual": digest}
            if digest
            else _status(False, detail=f"missing logical paths: {', '.join(missing)}")
        )
    except OSError:
        checks["logical_hash"] = _status(False, detail="logical content is unreadable")
    return result


def _scan_runtime_roots(host: dict[str, Any]) -> tuple[list[dict[str, Any]], list[dict[str, Any]]]:
    roots: list[dict[str, Any]] = []
    links: list[dict[str, Any]] = []
    expected = set(host["expected_runtimes"])
    for runtime in RUNTIMES:
        for configured in host["runtime_roots"].get(runtime, []):
            root = _expand(configured)
            if not os.path.lexists(root):
                roots.append(
                    {
                        "runtime": runtime,
                        "path": str(root),
                        "status": FAIL if runtime in expected else NA,
                        "detail": "configured runtime root is absent",
                    }
                )
                continue
            if not root.is_dir():
                roots.append({"runtime": runtime, "path": str(root), "status": FAIL, "detail": "not a directory"})
                continue
            broken = 0
            try:
                children = sorted(root.iterdir(), key=lambda path: path.name)
            except OSError:
                roots.append({"runtime": runtime, "path": str(root), "status": FAIL, "detail": "unreadable"})
                continue
            for child in children:
                if child.is_symlink() and not child.exists():
                    broken += 1
                    links.append(
                        {
                            "runtime": runtime,
                            "path": str(child),
                            "target": os.readlink(child),
                            "status": FAIL,
                            "detail": "broken top-level symlink",
                        }
                    )
            roots.append(
                {
                    "runtime": runtime,
                    "path": str(root),
                    "status": FAIL if broken else PASS,
                    "broken_links": broken,
                }
            )
    return roots, links


def _host_failed(host_result: dict[str, Any]) -> bool:
    if host_result.get("error"):
        return True
    for package in host_result.get("packages", []):
        if any(check["status"] == FAIL for check in package["checks"].values()):
            return True
    return any(root["status"] == FAIL for root in host_result.get("runtime_roots", []))


def audit_local(bom: dict[str, Any], host: dict[str, Any]) -> dict[str, Any]:
    probes = probe_runtime_inventories(host)
    packages = [audit_package(package, host, probes) for package in bom["packages"]]
    roots, links = _scan_runtime_roots(host)
    public_probes = {
        runtime: {key: value for key, value in probe.items() if key != "inventory"}
        for runtime, probe in probes.items()
    }
    result = {
        "name": host["name"],
        "transport": host["transport"],
        "reference": bool(host.get("reference")),
        "expected_runtimes": list(host["expected_runtimes"]),
        "runtime_probes": public_probes,
        "packages": packages,
        "runtime_roots": roots,
        "broken_links": links,
    }
    result["status"] = FAIL if _host_failed(result) else PASS
    return result


def _ssh_command(host: dict[str, Any], settings: dict[str, Any]) -> list[str]:
    command = [settings["ssh_bin"], *settings.get("ssh_args", [])]
    command.extend(["-o", "BatchMode=yes", "-o", f"ConnectTimeout={settings['connect_timeout']}"])
    command.extend(host.get("ssh_args", []))
    if host.get("jump"):
        command.extend(["-J", host["jump"]])
    command.append(host["target"])
    return command


def _remote_probe(
    bom: dict[str, Any],
    host: dict[str, Any],
    settings: dict[str, Any],
    action: str,
    *,
    apply: bool = False,
    timestamp: str | None = None,
) -> dict[str, Any]:
    public_host = {
        key: value
        for key, value in host.items()
        if key not in {"target", "jump", "ssh_args"}
    }
    public_host["transport"] = "local"
    payload = base64.urlsafe_b64encode(
        json.dumps(
            {
                "bom": bom,
                "host": public_host,
                "action": action,
                "apply": apply,
                "timestamp": timestamp,
            }
        ).encode("utf-8")
    ).decode("ascii")
    command = _ssh_command(host, settings)
    command.extend(["python3", "-", "--probe", payload])
    try:
        completed = subprocess.run(
            command,
            input=Path(__file__).read_bytes(),
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            check=False,
            timeout=max(30, settings["connect_timeout"] + 20),
        )
    except (OSError, subprocess.TimeoutExpired) as error:
        return {"name": host["name"], "transport": "ssh", "status": FAIL, "error": type(error).__name__}
    if completed.returncode not in (0, 1):
        detail = completed.stderr.decode("utf-8", "replace").strip().splitlines()
        return {
            "name": host["name"],
            "transport": "ssh",
            "status": FAIL,
            "error": detail[-1][:240] if detail else f"remote probe exited {completed.returncode}",
        }
    try:
        result = json.loads(completed.stdout)
    except json.JSONDecodeError:
        return {"name": host["name"], "transport": "ssh", "status": FAIL, "error": "remote probe returned invalid JSON"}
    result["name"] = host["name"]
    result["transport"] = "ssh"
    result["reference"] = bool(host.get("reference"))
    return result


def _apply_hash_parity(results: list[dict[str, Any]]) -> None:
    reference = next((host for host in results if host.get("reference") and not host.get("error")), None)
    reference_hashes: dict[str, str] = {}
    if reference:
        for package in reference.get("packages", []):
            check = package["checks"]["logical_hash"]
            if check["status"] == PASS and check.get("actual"):
                reference_hashes[package["name"]] = check["actual"]
                check["status"] = REFERENCE

    for host in results:
        if host is reference:
            continue
        for package in host.get("packages", []):
            check = package["checks"]["logical_hash"]
            if check["status"] != PASS:
                continue
            expected = reference_hashes.get(package["name"])
            if not expected:
                check["status"] = NA
                check["detail"] = "reference hash unavailable"
            else:
                check["expected"] = expected
                check["status"] = PASS if check.get("actual") == expected else FAIL
        host["status"] = FAIL if _host_failed(host) else PASS


def audit_fleet(
    bom: dict[str, Any], hosts: list[dict[str, Any]], settings: dict[str, Any]
) -> dict[str, Any]:
    results = []
    for host in hosts:
        if host["transport"] == "local":
            results.append(audit_local(bom, host))
        else:
            results.append(_remote_probe(bom, host, settings, "audit"))
    _apply_hash_parity(results)
    failures = sum(host.get("status") == FAIL for host in results)
    return {
        "schema_version": 1,
        "fleet_version": bom["fleet_version"],
        "generated_at": dt.datetime.now(dt.timezone.utc).isoformat(),
        "hosts": results,
        "summary": {"hosts": len(results), "failed_hosts": failures, "status": FAIL if failures else PASS},
    }


def _legacy_operations(
    bom: dict[str, Any], host: dict[str, Any], *, apply: bool, timestamp: str
) -> list[dict[str, Any]]:
    operations: list[dict[str, Any]] = []
    backup_root = _expand(host["backup_root"]) / timestamp
    for declaration in bom.get("legacy_links", []):
        path = _expand(declaration["path"])
        runtime_roots = [_expand(root) for root in host["runtime_roots"][declaration["runtime"]]]
        operation = {
            "root": declaration["root"],
            "runtime": declaration["runtime"],
            "path": str(path),
            "mode": "apply" if apply else "dry-run",
        }

        if not os.path.lexists(path):
            operation.update(status=PASS, action="none", detail="already absent")
        elif not any(path.parent == root for root in runtime_roots):
            operation.update(status=FAIL, action="blocked", detail="link is not top-level in a declared runtime root")
        elif not path.is_symlink():
            operation.update(status=FAIL, action="blocked", detail="path is a file or directory; only symlinks may be retired")
        elif not apply:
            operation.update(status=PASS, action="retire", detail="planned")
        else:
            try:
                backup = backup_root / declaration["root"] / path.name
                backup.parent.mkdir(parents=True, exist_ok=True)
                suffix = 1
                candidate = backup
                while os.path.lexists(candidate):
                    candidate = backup.with_name(f"{backup.name}-{suffix}")
                    suffix += 1
                os.replace(path, candidate)
                operation["backup"] = str(candidate)
                operation.update(
                    status=PASS, action="backup-and-retire", detail="applied"
                )
            except OSError as error:
                operation.update(
                    status=FAIL,
                    action="blocked",
                    detail=f"filesystem operation failed: {error.strerror or type(error).__name__}",
                )
        operations.append(operation)
    return operations


def repair_local(
    bom: dict[str, Any], host: dict[str, Any], *, apply: bool, timestamp: str
) -> dict[str, Any]:
    operations = _legacy_operations(bom, host, apply=apply, timestamp=timestamp)
    failed = any(operation["status"] == FAIL for operation in operations)
    return {
        "name": host["name"],
        "transport": host["transport"],
        "status": FAIL if failed else PASS,
        "mode": "apply" if apply else "dry-run",
        "operations": operations,
    }


def repair_fleet(
    bom: dict[str, Any],
    hosts: list[dict[str, Any]],
    settings: dict[str, Any],
    *,
    apply: bool,
) -> dict[str, Any]:
    timestamp = dt.datetime.now(dt.timezone.utc).strftime("%Y%m%dT%H%M%SZ")
    results = []
    for host in hosts:
        if host["transport"] == "local":
            results.append(repair_local(bom, host, apply=apply, timestamp=timestamp))
        else:
            results.append(
                _remote_probe(
                    bom, host, settings, "repair", apply=apply, timestamp=timestamp
                )
            )
    failures = sum(host.get("status") == FAIL for host in results)
    return {
        "schema_version": 1,
        "fleet_version": bom["fleet_version"],
        "generated_at": dt.datetime.now(dt.timezone.utc).isoformat(),
        "mode": "apply" if apply else "dry-run",
        "hosts": results,
        "summary": {"hosts": len(results), "failed_hosts": failures, "status": FAIL if failures else PASS},
    }


def _human_status(value: str) -> str:
    return {PASS: "PASS", FAIL: "FAIL", NA: "N/A", REFERENCE: "REF"}.get(value, value.upper())


def print_audit(report: dict[str, Any]) -> None:
    print("HOST       PACKAGE          ORIGIN REF  CLEAN MANIFEST VERSION HASH ACTIVE")
    for host in report["hosts"]:
        if host.get("error"):
            print(f"{host['name']:<10} {'-':<16} FAIL   FAIL FAIL  FAIL     FAIL    N/A  FAIL")
            print(f"  error: {host['error']}")
            continue
        for package in host["packages"]:
            checks = package["checks"]
            fields = [
                "origin",
                "ref",
                "clean",
                "manifest",
                "version",
                "logical_hash",
                "activation",
            ]
            values = [_human_status(checks[field]["status"]) for field in fields]
            print(
                f"{host['name']:<10} {package['name']:<16} "
                f"{values[0]:<6} {values[1]:<4} {values[2]:<5} {values[3]:<8} "
                f"{values[4]:<7} {values[5]:<4} {values[6]}"
            )
            support_text = " ".join(
                f"{runtime}={_human_status(package['runtimes'][runtime]['status'])}"
                for runtime in RUNTIMES
            )
            activation_text = " ".join(
                f"{runtime}={_human_status(package['activation'][runtime]['status'])}"
                for runtime in RUNTIMES
            )
            print(f"  support: {support_text}")
            print(f"  active:  {activation_text}")
        for link in host.get("broken_links", []):
            print(f"  broken {link['runtime']} link: {link['path']} -> {link['target']}")
    print(
        f"Summary: {report['summary']['hosts']} host(s), "
        f"{report['summary']['failed_hosts']} failed"
    )


def print_repair(report: dict[str, Any]) -> None:
    print(f"Legacy-link retirement ({report['mode']})")
    for host in report["hosts"]:
        if host.get("error"):
            print(f"{host['name']}: FAIL — {host['error']}")
            continue
        for operation in host.get("operations", []):
            line = (
                f"{host['name']} {_human_status(operation['status'])} "
                f"{operation['action']}: {operation['path']}"
            )
            if operation.get("backup"):
                line += f" (backup: {operation['backup']})"
            print(line)
    print(
        f"Summary: {report['summary']['hosts']} host(s), "
        f"{report['summary']['failed_hosts']} failed"
    )


def _filter_hosts(hosts: list[dict[str, Any]], names: list[str]) -> list[dict[str, Any]]:
    if not names:
        return hosts
    requested = set(names)
    selected = [host for host in hosts if host["name"] in requested]
    missing = requested - {host["name"] for host in selected}
    if missing:
        raise ConfigurationError(f"unknown host(s): {', '.join(sorted(missing))}")
    return selected


def _parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        description="Audit a manifest-declared plugin fleet and repair only declared legacy links."
    )
    subparsers = parser.add_subparsers(dest="command", required=True)
    for command in ("audit", "repair"):
        description = (
            "Audit the manifest-declared plugin fleet."
            if command == "audit"
            else "Dry-run or apply safe, manifest-declared legacy-link repairs."
        )
        sub = subparsers.add_parser(command, description=description)
        sub.add_argument("--bom", type=Path, default=DEFAULT_BOM)
        sub.add_argument(
            "--hosts",
            type=Path,
            help=f"personal host config (default: {DEFAULT_HOSTS} when present)",
        )
        sub.add_argument("--host", action="append", default=[], help="limit to a named host")
        sub.add_argument("--json", action="store_true", help="emit machine-readable JSON")
        if command == "repair":
            sub.add_argument(
                "--apply",
                action="store_true",
                help="apply declared repairs; default is dry-run",
            )
    return parser


def _probe(payload: str) -> int:
    try:
        spec = json.loads(base64.urlsafe_b64decode(payload.encode("ascii")))
        if spec["action"] == "audit":
            result = audit_local(spec["bom"], spec["host"])
        elif spec["action"] == "repair":
            result = repair_local(
                spec["bom"],
                spec["host"],
                apply=bool(spec["apply"]),
                timestamp=spec["timestamp"],
            )
        else:
            raise ConfigurationError("unknown remote action")
        print(json.dumps(result, sort_keys=True))
        return 1 if result["status"] == FAIL else 0
    except Exception as error:  # remote boundary: return a bounded diagnostic
        print(json.dumps({"status": FAIL, "error": f"{type(error).__name__}: {error}"}))
        return 2


def main(argv: list[str] | None = None) -> int:
    args_list = list(sys.argv[1:] if argv is None else argv)
    if len(args_list) == 2 and args_list[0] == "--probe":
        return _probe(args_list[1])
    try:
        args = _parser().parse_args(args_list)
        bom = load_bom(args.bom.expanduser().resolve())
        hosts, settings = load_hosts(
            args.hosts.expanduser().resolve() if args.hosts else None, bom
        )
        hosts = _filter_hosts(hosts, args.host)
        if args.command == "audit":
            report = audit_fleet(bom, hosts, settings)
            if args.json:
                print(json.dumps(report, indent=2, sort_keys=True))
            else:
                print_audit(report)
        else:
            report = repair_fleet(bom, hosts, settings, apply=args.apply)
            if args.json:
                print(json.dumps(report, indent=2, sort_keys=True))
            else:
                print_repair(report)
        return 1 if report["summary"]["status"] == FAIL else 0
    except ConfigurationError as error:
        print(f"fleet configuration error: {error}", file=sys.stderr)
        return 2


if __name__ == "__main__":
    raise SystemExit(main())
