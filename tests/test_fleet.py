#!/usr/bin/env python3
"""Focused tests for Craft's manifest-driven fleet controller."""

from __future__ import annotations

from contextlib import redirect_stdout
import importlib.util
import io
import json
import os
from pathlib import Path
import subprocess
import tempfile
import textwrap
import unittest
from unittest import mock


ROOT = Path(__file__).resolve().parents[1]
SPEC = importlib.util.spec_from_file_location("craft_fleet", ROOT / "scripts/fleet.py")
assert SPEC and SPEC.loader
fleet = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(fleet)


def run(*args: str, cwd: Path) -> str:
    completed = subprocess.run(
        args,
        cwd=cwd,
        check=True,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        text=True,
    )
    return completed.stdout.strip()


class FleetTests(unittest.TestCase):
    def setUp(self) -> None:
        self.temporary = tempfile.TemporaryDirectory()
        self.base = Path(self.temporary.name)

    def tearDown(self) -> None:
        self.temporary.cleanup()

    def make_checkout(
        self,
        parent: Path,
        *,
        content: str = "# demo\n",
        manifest_version: str = "1.0.0",
    ) -> Path:
        root = parent / "demo"
        (root / "skills/demo").mkdir(parents=True)
        (root / ".claude-plugin").mkdir()
        (root / ".codex-plugin").mkdir()
        (root / "skills/demo/SKILL.md").write_text(content, encoding="utf-8")
        manifest = {
            "name": "demo",
            "version": manifest_version,
            "skills": "./skills/",
        }
        for relative in (
            ".claude-plugin/plugin.json",
            ".codex-plugin/plugin.json",
        ):
            (root / relative).write_text(json.dumps(manifest), encoding="utf-8")
        run("git", "init", "-q", cwd=root)
        run("git", "config", "user.name", "Fleet Test", cwd=root)
        run("git", "config", "user.email", "fleet@example.invalid", cwd=root)
        run(
            "git",
            "remote",
            "add",
            "origin",
            "git@github.com:example/demo.git",
            cwd=root,
        )
        run("git", "add", "skills", ".claude-plugin", ".codex-plugin", cwd=root)
        run("git", "commit", "-qm", "fixture", cwd=root)
        run("git", "tag", "v1.0.0", cwd=root)
        return root

    def write_bom(self, *, legacy: str = "") -> Path:
        path = self.base / "fleet.toml"
        path.write_text(
            textwrap.dedent(
                f"""
                schema_version = 1
                fleet_version = "test"

                [defaults]
                checkout_root = "{self.base.as_posix()}"
                cursor_installed_roots = []
                backup_root = "{(self.base / 'backups').as_posix()}"

                [runtime_roots]
                claude = []
                codex = []
                cursor = []
                grok = []

                [[packages]]
                name = "demo"
                directory = "demo"
                version = "1.0.0"
                origin = "https://github.com/example/demo.git"
                ref = "v1.0.0"
                hash_paths = ["skills", ".claude-plugin/plugin.json", ".codex-plugin/plugin.json"]

                [packages.runtimes]
                claude = ".claude-plugin/plugin.json"
                codex = ".codex-plugin/plugin.json"

                [packages.install_ids]
                claude = "demo@example"
                codex = "demo@example"

                {legacy}
                """
            ),
            encoding="utf-8",
        )
        return path

    def local_host(
        self,
        checkout_root: Path,
        runtime_root: Path | None = None,
        *,
        expected_runtimes: list[str] | None = None,
        cursor_roots: list[Path] | None = None,
    ) -> dict:
        return {
            "name": "local",
            "transport": "local",
            "reference": True,
            "checkout_root": str(checkout_root),
            "paths": {},
            "expected_runtimes": list(expected_runtimes or []),
            "runtime_roots": {
                "claude": [],
                "codex": [str(runtime_root)] if runtime_root else [],
                "cursor": [],
                "grok": [],
            },
            "installed_roots": {
                "claude": [],
                "codex": [],
                "cursor": [str(path) for path in (cursor_roots or [])],
                "grok": [],
            },
            "backup_root": str(self.base / "backups"),
        }

    def test_public_bom_pins_releases_install_ids_and_retirements(self) -> None:
        bom = fleet.load_bom(ROOT / "fleet.toml")
        versions = {package["name"]: package["version"] for package in bom["packages"]}
        self.assertEqual(
            versions,
            {
                "craft": "0.7.0",
                "team": "0.1.4",
                "intentional-ux": "0.2.2",
                "accessibility": "1.1.2",
                "humanize": "1.2.1",
            },
        )
        for package in bom["packages"]:
            self.assertTrue(
                package["origin"].startswith(
                    "https://github.com/actually-useful-ai/"
                )
            )
            self.assertEqual(set(package["runtimes"]), set(fleet.RUNTIMES))
            self.assertEqual(set(package["install_ids"]), set(fleet.RUNTIMES))
        craft = next(
            package for package in bom["packages"] if package["name"] == "craft"
        )
        self.assertIn("fleet.toml", craft["hash_paths"])

        expected_paths = {
            f"~/.{root}/skills/{name}"
            for root in ("agents", "codex", "claude")
            for name in ("chefs-choice", "exemplar", "intentional-ux", "humanize")
        }
        self.assertEqual(
            {link["path"] for link in bom["legacy_links"]}, expected_paths
        )
        self.assertTrue(
            all("target" not in link and "package" not in link for link in bom["legacy_links"])
        )

    def test_claude_inventory_parser(self) -> None:
        inventory = fleet.parse_claude_plugins(
            json.dumps(
                [
                    {
                        "id": "demo@example",
                        "version": "1.0.0",
                        "enabled": True,
                    },
                    {
                        "id": "off@example",
                        "version": "2.0.0",
                        "enabled": False,
                    },
                ]
            )
        )
        self.assertEqual(inventory["demo@example"]["version"], "1.0.0")
        self.assertTrue(inventory["demo@example"]["enabled"])
        self.assertFalse(inventory["off@example"]["enabled"])
        with self.assertRaises(ValueError):
            fleet.parse_claude_plugins("{}")

    def test_codex_inventory_parser_ignores_available_plugins(self) -> None:
        inventory = fleet.parse_codex_plugins(
            json.dumps(
                {
                    "installed": [
                        {
                            "pluginId": "demo@example",
                            "version": "1.0.0",
                            "installed": True,
                            "enabled": True,
                        }
                    ],
                    "available": [
                        {
                            "pluginId": "not-active@example",
                            "version": "1.0.0",
                            "installed": False,
                            "enabled": False,
                        }
                    ],
                }
            )
        )
        self.assertIn("demo@example", inventory)
        self.assertNotIn("not-active@example", inventory)
        with self.assertRaises(ValueError):
            fleet.parse_codex_plugins("[]")

    def test_grok_inventory_parser_requires_imported_path_version_evidence(self) -> None:
        inventory = fleet.parse_grok_plugins(
            json.dumps(
                {
                    "plugins": [
                        {
                            "name": "demo",
                            "path": "/home/test/.claude/plugins/cache/example/demo/1.0.0",
                            "enabled": True,
                        },
                        {
                            "name": "native",
                            "path": "/home/test/.grok/plugins/native/2.0.0",
                            "enabled": True,
                        },
                    ]
                }
            )
        )
        self.assertEqual(inventory["demo"]["version"], "1.0.0")
        self.assertEqual(inventory["demo"]["source"], "claude-import")
        self.assertEqual(inventory["native"]["source"], "grok-registry")
        with self.assertRaises(ValueError):
            fleet.parse_grok_plugins("{}")

    def test_cursor_inventory_parser_uses_cache_marketplace_and_manifest(self) -> None:
        cache = self.base / "cursor-cache"
        manifest_path = (
            cache
            / "example"
            / "demo"
            / "content-hash"
            / ".cursor-plugin/plugin.json"
        )
        manifest_path.parent.mkdir(parents=True)
        manifest_path.write_text(
            json.dumps({"name": "demo", "version": "1.0.0"}), encoding="utf-8"
        )
        inventory = fleet.parse_cursor_plugins([cache])
        self.assertEqual(inventory["demo@example"]["version"], "1.0.0")
        self.assertEqual(inventory["demo@example"]["source"], "cursor-cache")

    def test_runtime_probes_are_deterministic_and_unexpected_is_na(self) -> None:
        host = self.local_host(
            self.base, expected_runtimes=["claude", "codex", "grok"]
        )
        payloads = {
            "claude": json.dumps(
                [{"id": "demo@example", "version": "1.0.0", "enabled": True}]
            ),
            "codex": json.dumps(
                {
                    "installed": [
                        {
                            "pluginId": "demo@example",
                            "version": "1.0.0",
                            "installed": True,
                            "enabled": True,
                        }
                    ]
                }
            ),
            "grok": json.dumps(
                {
                    "plugins": [
                        {
                            "name": "demo",
                            "path": "/home/test/.claude/plugins/cache/example/demo/1.0.0",
                            "enabled": True,
                        }
                    ]
                }
            ),
        }

        def command_fixture(arguments: list[str]) -> tuple[bool, str, str]:
            return True, payloads[arguments[0]], ""

        with mock.patch.object(
            fleet, "_run_runtime_command", side_effect=command_fixture
        ):
            probes = fleet.probe_runtime_inventories(host)
        self.assertEqual(probes["claude"]["status"], fleet.PASS)
        self.assertEqual(probes["codex"]["status"], fleet.PASS)
        self.assertEqual(probes["grok"]["status"], fleet.PASS)
        self.assertEqual(probes["cursor"]["status"], fleet.NA)

        no_runtime_host = self.local_host(self.base)
        with mock.patch.object(fleet, "_run_runtime_command") as runner:
            probes = fleet.probe_runtime_inventories(no_runtime_host)
        runner.assert_not_called()
        self.assertTrue(
            all(probe["status"] == fleet.NA for probe in probes.values())
        )

    def test_expected_probe_or_active_package_failure_is_not_na(self) -> None:
        bom = fleet.load_bom(self.write_bom())
        package = bom["packages"][0]
        host = self.local_host(self.base, expected_runtimes=["claude", "codex"])
        probes = {
            "claude": {
                "status": fleet.PASS,
                "inventory": {
                    "demo@example": {
                        "version": "1.0.0",
                        "enabled": True,
                        "source": "claude-registry",
                    }
                },
            },
            "codex": {
                "status": fleet.PASS,
                "inventory": {
                    "demo@example": {
                        "version": "0.9.0",
                        "enabled": True,
                        "source": "codex-registry",
                    }
                },
            },
            "cursor": {"status": fleet.NA, "inventory": {}},
            "grok": {"status": fleet.NA, "inventory": {}},
        }
        activation = fleet._activation_checks(package, host, probes)
        self.assertEqual(activation["claude"]["status"], fleet.PASS)
        self.assertEqual(activation["codex"]["status"], fleet.FAIL)
        self.assertEqual(activation["cursor"]["status"], fleet.NA)

        probes["codex"]["inventory"] = {}
        missing = fleet._activation_checks(package, host, probes)
        self.assertEqual(missing["codex"]["status"], fleet.FAIL)
        self.assertIn("absent", missing["codex"]["detail"])

        with mock.patch.object(
            fleet,
            "_run_runtime_command",
            return_value=(False, "", "claude command unavailable"),
        ):
            unavailable = fleet.probe_runtime_inventories(
                self.local_host(self.base, expected_runtimes=["claude"])
            )
        self.assertEqual(unavailable["claude"]["status"], fleet.FAIL)

    def test_grok_activation_requires_claude_import_evidence(self) -> None:
        package = {
            "version": "1.0.0",
            "install_ids": {"grok": "demo"},
        }
        host = {"expected_runtimes": ["grok"]}
        base_probes = {
            runtime: {"status": fleet.NA, "inventory": {}}
            for runtime in fleet.RUNTIMES
        }
        base_probes["grok"] = {
            "status": fleet.PASS,
            "inventory": {
                "demo": {
                    "version": "1.0.0",
                    "enabled": True,
                    "source": "grok-registry",
                }
            },
        }
        native = fleet._activation_checks(package, host, base_probes)
        self.assertEqual(native["grok"]["status"], fleet.FAIL)

        base_probes["grok"]["inventory"]["demo"]["source"] = "claude-import"
        imported = fleet._activation_checks(package, host, base_probes)
        self.assertEqual(imported["grok"]["status"], fleet.PASS)

    def test_cursor_probe_fails_closed_only_when_expected(self) -> None:
        missing = fleet.probe_runtime_inventories(
            self.local_host(self.base, expected_runtimes=["cursor"])
        )
        self.assertEqual(missing["cursor"]["status"], fleet.FAIL)

        cache = self.base / "cursor-cache"
        manifest = cache / "example/demo/hash/.cursor-plugin/plugin.json"
        manifest.parent.mkdir(parents=True)
        manifest.write_text(
            json.dumps({"name": "demo", "version": "1.0.0"}), encoding="utf-8"
        )
        present = fleet.probe_runtime_inventories(
            self.local_host(
                self.base,
                expected_runtimes=["cursor"],
                cursor_roots=[cache],
            )
        )
        self.assertEqual(present["cursor"]["status"], fleet.PASS)
        self.assertIn("demo@example", present["cursor"]["inventory"])

    def test_missing_configured_runtime_root_is_na_only_when_unexpected(self) -> None:
        missing_root = self.base / "missing-skills"
        unexpected = self.local_host(self.base, missing_root)
        roots, _ = fleet._scan_runtime_roots(unexpected)
        self.assertEqual(roots[0]["status"], fleet.NA)

        expected = self.local_host(
            self.base, missing_root, expected_runtimes=["codex"]
        )
        roots, _ = fleet._scan_runtime_roots(expected)
        self.assertEqual(roots[0]["status"], fleet.FAIL)

    def test_clean_checkout_passes_with_activation_distinct_from_support(self) -> None:
        self.make_checkout(self.base)
        bom = fleet.load_bom(self.write_bom())
        report = fleet.audit_fleet(
            bom,
            [self.local_host(self.base)],
            {"ssh_bin": "ssh", "connect_timeout": 1, "ssh_args": []},
        )
        package = report["hosts"][0]["packages"][0]
        self.assertEqual(report["summary"]["status"], fleet.PASS)
        for check in ("origin", "ref", "clean", "manifest", "version"):
            self.assertEqual(package["checks"][check]["status"], fleet.PASS)
        self.assertEqual(
            package["checks"]["logical_hash"]["status"], fleet.REFERENCE
        )
        self.assertEqual(package["checks"]["activation"]["status"], fleet.NA)
        self.assertEqual(package["runtimes"]["claude"]["status"], fleet.PASS)
        self.assertEqual(package["runtimes"]["cursor"]["status"], fleet.NA)
        self.assertEqual(package["activation"]["claude"]["status"], fleet.NA)

        output = io.StringIO()
        with redirect_stdout(output):
            fleet.print_audit(report)
        self.assertIn("support:", output.getvalue())
        self.assertIn("active:", output.getvalue())
        self.assertIn("cursor=N/A", output.getvalue())

    def test_dirty_checkout_and_broken_top_level_link_fail(self) -> None:
        checkout = self.make_checkout(self.base)
        runtime_root = self.base / "runtime-skills"
        runtime_root.mkdir()
        os.symlink("missing-target", runtime_root / "broken")
        (checkout / "skills/demo/SKILL.md").write_text("changed\n", encoding="utf-8")
        bom = fleet.load_bom(self.write_bom())
        report = fleet.audit_fleet(
            bom,
            [self.local_host(self.base, runtime_root)],
            {"ssh_bin": "ssh", "connect_timeout": 1, "ssh_args": []},
        )
        host = report["hosts"][0]
        package = host["packages"][0]
        self.assertEqual(report["summary"]["status"], fleet.FAIL)
        self.assertEqual(package["checks"]["clean"]["status"], fleet.FAIL)
        self.assertEqual(
            host["broken_links"][0]["path"], str(runtime_root / "broken")
        )
        self.assertEqual(host["runtime_roots"][0]["status"], fleet.FAIL)

    def test_logical_hash_detects_cross_host_content_drift(self) -> None:
        reference_parent = self.base / "reference"
        drift_parent = self.base / "drift"
        reference_parent.mkdir()
        drift_parent.mkdir()
        self.make_checkout(reference_parent, content="reference\n")
        self.make_checkout(drift_parent, content="different\n")
        bom = fleet.load_bom(self.write_bom())
        reference = self.local_host(reference_parent)
        drift = self.local_host(drift_parent)
        drift.update(name="second", reference=False)
        report = fleet.audit_fleet(
            bom,
            [reference, drift],
            {"ssh_bin": "ssh", "connect_timeout": 1, "ssh_args": []},
        )
        self.assertEqual(
            report["hosts"][1]["packages"][0]["checks"]["logical_hash"][
                "status"
            ],
            fleet.FAIL,
        )

    def test_external_config_supports_empty_root_override_and_ssh_jump(self) -> None:
        bom = fleet.load_bom(self.write_bom())
        config = self.base / "hosts.toml"
        config.write_text(
            textwrap.dedent(
                """
                [settings]
                ssh_bin = "custom-ssh"
                connect_timeout = 4
                ssh_args = ["-F", "/tmp/fleet-ssh-config"]

                [[hosts]]
                name = "neo"
                transport = "local"
                reference = true
                expected_runtimes = []
                checkout_root = "/srv/plugins"

                [hosts.paths]
                demo = "/srv/demo"

                [hosts.runtime_roots]
                codex = []

                [hosts.installed_roots]
                cursor = []

                [[hosts]]
                name = "drummer"
                transport = "ssh"
                target = "drummer"
                jump = "beast"
                expected_runtimes = ["codex"]
                """
            ),
            encoding="utf-8",
        )
        hosts, settings = fleet.load_hosts(config, bom)
        self.assertEqual(hosts[0]["paths"]["demo"], "/srv/demo")
        self.assertEqual(hosts[0]["runtime_roots"]["codex"], [])
        self.assertEqual(hosts[0]["installed_roots"]["cursor"], [])
        self.assertEqual(hosts[1]["expected_runtimes"], ["codex"])
        self.assertEqual(
            fleet._ssh_command(hosts[1], settings),
            [
                "custom-ssh",
                "-F",
                "/tmp/fleet-ssh-config",
                "-o",
                "BatchMode=yes",
                "-o",
                "ConnectTimeout=4",
                "-J",
                "beast",
                "drummer",
            ],
        )

    def test_host_config_rejects_unknown_and_type_bad_values(self) -> None:
        bom = fleet.load_bom(self.write_bom())
        invalid_hosts = {
            "unknown host field": 'expected_runtimes = []\nwat = 1',
            "expected string": 'expected_runtimes = "codex"',
            "unknown runtime": 'expected_runtimes = ["wat"]',
            "bad root type": (
                'expected_runtimes = []\n[hosts.runtime_roots]\ncodex = "bad"'
            ),
            "unknown root": (
                'expected_runtimes = []\n[hosts.runtime_roots]\nwat = []'
            ),
            "bad installed root": (
                'expected_runtimes = []\n[hosts.installed_roots]\ncursor = "bad"'
            ),
        }
        for label, body in invalid_hosts.items():
            with self.subTest(label=label):
                config = self.base / f"invalid-{label.replace(' ', '-')}.toml"
                config.write_text(
                    textwrap.dedent(
                        f"""
                        [[hosts]]
                        name = "local"
                        transport = "local"
                        {body}
                        """
                    ),
                    encoding="utf-8",
                )
                with self.assertRaises(fleet.ConfigurationError):
                    fleet.load_hosts(config, bom)

        ssh_without_expectation = self.base / "ssh-no-expectation.toml"
        ssh_without_expectation.write_text(
            '[[hosts]]\nname="remote"\ntransport="ssh"\ntarget="remote"\n',
            encoding="utf-8",
        )
        with self.assertRaises(fleet.ConfigurationError):
            fleet.load_hosts(ssh_without_expectation, bom)

        bad_bom = self.base / "bad-bom.toml"
        valid = self.write_bom().read_text(encoding="utf-8")
        bad_bom.write_text(
            valid.replace("schema_version = 1", "schema_version = 1\nwat = 1", 1),
            encoding="utf-8",
        )
        with self.assertRaises(fleet.ConfigurationError):
            fleet.load_bom(bad_bom)

    def test_ssh_probe_streams_controller_without_remote_installation(self) -> None:
        self.make_checkout(self.base)
        bom = fleet.load_bom(self.write_bom())
        fake_ssh = self.base / "fake-ssh.py"
        fake_ssh.write_text(
            textwrap.dedent(
                """\
                #!/usr/bin/env python3
                import subprocess
                import sys

                arguments = sys.argv[1:]
                remote_start = arguments.index("python3")
                completed = subprocess.run(
                    arguments[remote_start:], input=sys.stdin.buffer.read()
                )
                raise SystemExit(completed.returncode)
                """
            ),
            encoding="utf-8",
        )
        fake_ssh.chmod(0o755)
        host = self.local_host(self.base)
        host.update(
            name="remote-fixture",
            transport="ssh",
            reference=False,
            target="fixture",
        )
        result = fleet._remote_probe(
            bom,
            host,
            {"ssh_bin": str(fake_ssh), "connect_timeout": 1, "ssh_args": []},
            "audit",
        )
        self.assertEqual(result["status"], fleet.PASS)
        self.assertEqual(result["transport"], "ssh")
        self.assertEqual(
            result["packages"][0]["checks"]["origin"]["status"], fleet.PASS
        )

    def test_declared_link_retirement_dry_run_apply_backup_and_idempotence(self) -> None:
        self.make_checkout(self.base)
        runtime_root = self.base / "runtime-skills"
        runtime_root.mkdir()
        link = runtime_root / "demo"
        undeclared = runtime_root / "undeclared"
        os.symlink("old-target", link)
        os.symlink("also-missing", undeclared)
        legacy = textwrap.dedent(
            f"""
            [[legacy_links]]
            root = "codex"
            runtime = "codex"
            path = "{link.as_posix()}"
            """
        )
        bom = fleet.load_bom(self.write_bom(legacy=legacy))
        host = self.local_host(self.base, runtime_root)

        dry_run = fleet.repair_local(
            bom, host, apply=False, timestamp="20260804T120000Z"
        )
        self.assertEqual(dry_run["operations"][0]["action"], "retire")
        self.assertEqual(os.readlink(link), "old-target")

        applied = fleet.repair_local(
            bom, host, apply=True, timestamp="20260804T120000Z"
        )
        operation = applied["operations"][0]
        backup = Path(operation["backup"])
        self.assertEqual(operation["action"], "backup-and-retire")
        self.assertEqual(
            backup,
            self.base / "backups/20260804T120000Z/codex/demo",
        )
        self.assertTrue(backup.is_symlink())
        self.assertEqual(os.readlink(backup), "old-target")
        self.assertFalse(os.path.lexists(link))
        self.assertTrue(undeclared.is_symlink())

        second = fleet.repair_local(
            bom, host, apply=True, timestamp="20260804T120001Z"
        )
        self.assertEqual(second["operations"][0]["action"], "none")
        self.assertEqual(second["operations"][0]["detail"], "already absent")
        self.assertFalse(
            (self.base / "backups/20260804T120001Z/codex/demo").exists()
        )

    def test_retirement_blocks_regular_files_and_never_moves_them(self) -> None:
        self.make_checkout(self.base)
        runtime_root = self.base / "runtime-skills"
        runtime_root.mkdir()
        path = runtime_root / "demo"
        path.write_text("keep me", encoding="utf-8")
        legacy = textwrap.dedent(
            f"""
            [[legacy_links]]
            root = "codex"
            runtime = "codex"
            path = "{path.as_posix()}"
            """
        )
        bom = fleet.load_bom(self.write_bom(legacy=legacy))
        result = fleet.repair_local(
            bom,
            self.local_host(self.base, runtime_root),
            apply=True,
            timestamp="20260804T120000Z",
        )
        self.assertEqual(result["status"], fleet.FAIL)
        self.assertEqual(result["operations"][0]["action"], "blocked")
        self.assertEqual(path.read_text(encoding="utf-8"), "keep me")
        self.assertFalse((self.base / "backups").exists())


if __name__ == "__main__":
    unittest.main()
