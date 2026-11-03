"""Tests: python3 -m unittest discover -s tests -p test_agent_install.py -v"""
import contextlib
import io
import json
from pathlib import Path
import sys
import tempfile
import unittest
from unittest import mock

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "practice"))
import install_agents as app

class AgentInstallTests(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory()
        self.addCleanup(self.temp.cleanup)
        self.project = Path(self.temp.name) / "wiki-copy"
        self.project.mkdir()
        (self.project / "existing.txt").write_text("keep", encoding="utf-8")

    def run_cli(self, *args):
        out, err = io.StringIO(), io.StringIO()
        with contextlib.redirect_stdout(out), contextlib.redirect_stderr(err):
            code = app.main([*args, "--project-copy", str(self.project)])
        return code, out.getvalue(), err.getvalue()

    def test_plan_does_not_change_project(self):
        rc, out, _ = self.run_cli("plan", "--group", "core")
        self.assertEqual(rc, 0)
        self.assertEqual(len(json.loads(out)["entries"]), 4)
        self.assertFalse((self.project / ".claude").exists())

    def test_install_requires_copy_confirmation(self):
        rc, _, err = self.run_cli("install", "--group", "core")
        self.assertNotEqual(rc, 0)
        self.assertIn("confirm-isolated-copy", err)

    def test_install_four_then_five(self):
        for group, count in (("core", 4), ("reviewers", 5)):
            rc, out, err = self.run_cli("install", "--group", group, "--confirm-isolated-copy")
            self.assertEqual(rc, 0, err)
            self.assertEqual(json.loads(out)["installed"], count)
        rc, out, _ = self.run_cli("verify", "--group", "all")
        self.assertEqual(rc, 0)
        self.assertEqual(json.loads(out)["status"], "VERIFIED")
        self.assertEqual(len(list((self.project / ".claude/agents").glob("*.md"))), 9)
        self.assertEqual((self.project / "existing.txt").read_text(), "keep")

    def test_repeat_install_does_not_duplicate(self):
        self.run_cli("install", "--group", "core", "--confirm-isolated-copy")
        rc, out, _ = self.run_cli("install", "--group", "core", "--confirm-isolated-copy")
        self.assertEqual(rc, 0)
        self.assertEqual(json.loads(out)["status"], "UNCHANGED")

    def test_conflicting_file_not_overwritten(self):
        target = self.project / ".claude/agents"
        target.mkdir(parents=True)
        (target / "literature-reviewer.md").write_text("user agent")
        rc, _, err = self.run_cli("install", "--group", "core", "--confirm-isolated-copy")
        self.assertNotEqual(rc, 0)
        self.assertIn("덮어쓰지", err)
        self.assertEqual((target / "literature-reviewer.md").read_text(), "user agent")
        self.assertEqual(len(list(target.iterdir())), 1)

    def test_verify_detects_changed_definition(self):
        self.run_cli("install", "--group", "all", "--confirm-isolated-copy")
        f = self.project / ".claude/agents/reviewer-novelty.md"
        f.write_text(f.read_text() + "\nchanged\n")
        rc, out, _ = self.run_cli("verify")
        self.assertEqual(rc, 1)
        self.assertEqual(json.loads(out)["status"], "FAILED")

    def test_symlink_agent_dir_refused(self):
        other = Path(self.temp.name) / "other"
        other.mkdir()
        (self.project / ".claude").symlink_to(other, target_is_directory=True)
        rc, _, err = self.run_cli("install", "--confirm-isolated-copy")
        self.assertNotEqual(rc, 0)
        self.assertIn("심볼릭 링크", err)
        self.assertEqual(list(other.iterdir()), [])

    def test_partial_install_failure_rolls_back_only_new_files(self):
        original = app.os.link
        calls = 0
        def fail_second(src, dest):
            nonlocal calls
            calls += 1
            if calls == 2:
                raise OSError("injected failure")
            return original(src, dest)
        with mock.patch.object(app.os, "link", side_effect=fail_second):
            rc, _, err = self.run_cli("install", "--group", "core", "--confirm-isolated-copy")
        self.assertNotEqual(rc, 0)
        self.assertIn("injected failure", err)
        self.assertEqual(list((self.project / ".claude/agents").iterdir()), [])
        self.assertEqual((self.project / "existing.txt").read_text(), "keep")

if __name__ == "__main__":
    unittest.main()
