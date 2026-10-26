#!/usr/bin/env python3
"""기존 Part4 배포 템플릿·Skill 문서를 임시 복사해 추가와 복구를 검증한다."""
import argparse
import hashlib
import json
from pathlib import Path
import runpy
import shutil
import subprocess
import sys
import tempfile
import unittest
from unittest.mock import patch

HERE = Path(__file__).resolve().parent
REF = None
ACTUAL = None
LAB = Path("llm_wiki/research/part5-lab")


def snapshot(root):
    return {str(p.relative_to(root)): hashlib.sha256(p.read_bytes()).hexdigest()
            for p in root.rglob("*") if p.is_file()}


class UpgradeTests(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory(prefix=".upgrade-test-", dir=HERE)
        self.tmp = Path(self.temp.name)
        self.root = self.tmp / "wiki-copy"
        shutil.copytree(REF / "실습파일/LLM_Wiki_템플릿", self.root)
        shutil.copyfile(REF / "README.md", self.root / "README.md")
        for name in ("paper-reading", "experiment-log"):
            target = self.root / ".agents/skills" / name
            target.mkdir(parents=True)
            shutil.copyfile(REF / "실습파일" / name / "SKILL.md", target / "SKILL.md")
        self.before = snapshot(self.root)
        self.receipt = self.tmp / "plan.json"

    def tearDown(self):
        self.temp.cleanup()

    def command(self, action, *extra):
        return subprocess.run([sys.executable, str(HERE / "upgrade_wiki.py"), action,
                               "--project-copy", str(self.root), *map(str, extra)],
                              capture_output=True, text=True)

    def plan(self, *extra):
        result = self.command("plan", *extra)
        self.assertEqual(result.returncode, 0, result.stderr)
        self.receipt.write_text(result.stdout, encoding="utf-8")
        return json.loads(result.stdout)

    def apply(self):
        return self.command("apply", "--plan", self.receipt, "--confirm-isolated-copy")

    def assert_baseline_unchanged(self):
        current = snapshot(self.root)
        self.assertTrue(all(current.get(name) == value for name, value in self.before.items()))

    def assert_no_staging(self):
        self.assertEqual(list((self.root / "llm_wiki/research").glob(".part5-stage-*")), [])

    def injected_partial_write(self, filename):
        self.plan()
        module = runpy.run_path(str(HERE / "upgrade_wiki.py"))
        real_open = Path.open

        class PartialWriter:
            def __init__(self, stream):
                self.stream = stream

            def __enter__(self):
                self.stream.__enter__()
                return self

            def __exit__(self, *args):
                return self.stream.__exit__(*args)

            def write(self, data):
                self.stream.write(data[:5])
                raise OSError("injected partial write")

        def opening(path, mode="r", *args, **kwargs):
            stream = real_open(path, mode, *args, **kwargs)
            if path.parent.name.startswith(".part5-stage-") and path.name == filename and mode in ("x", "xb"):
                return PartialWriter(stream)
            return stream

        with patch.object(Path, "open", new=opening):
            with self.assertRaisesRegex(OSError, "injected partial write"):
                module["apply"](self.root, self.receipt)
        self.assertEqual(snapshot(self.root), self.before)
        self.assertFalse((self.root / LAB).exists())
        self.assert_no_staging()
        # 오류를 치운 후 같은 계획으로 재시도할 수 있어야 한다.
        self.assertEqual(self.apply().returncode, 0)

    def test_partial_payload_write_leaves_no_target_and_can_retry(self):
        self.injected_partial_write("README.md")

    def test_partial_manifest_write_leaves_no_target_and_can_retry(self):
        self.injected_partial_write(".part5-added-files.json")

    def test_publish_failure_cleans_own_empty_reservation(self):
        self.plan()
        module = runpy.run_path(str(HERE / "upgrade_wiki.py"))
        with patch.object(Path, "rename", side_effect=OSError("injected publish failure")):
            with self.assertRaisesRegex(OSError, "injected publish failure"):
                module["apply"](self.root, self.receipt)
        self.assertEqual(snapshot(self.root), self.before)
        self.assertFalse((self.root / LAB).exists())
        self.assert_no_staging()

    def test_conflict_appearing_during_stage_is_preserved(self):
        self.plan()
        module = runpy.run_path(str(HERE / "upgrade_wiki.py"))
        real_read = module["read_json"]

        def read_and_create_conflict(path):
            result = real_read(path)
            if path.parent.name.startswith(".part5-stage-") and path.name == ".part5-added-files.json":
                target = self.root / LAB
                target.mkdir()
                (target / "user.txt").write_text("사용자가 먼저 만든 파일", encoding="utf-8")
            return result

        with patch.dict(module["apply"].__globals__, {"read_json": read_and_create_conflict}):
            with self.assertRaises(FileExistsError):
                module["apply"](self.root, self.receipt)
        self.assertEqual((self.root / LAB / "user.txt").read_text(encoding="utf-8"), "사용자가 먼저 만든 파일")
        self.assert_baseline_unchanged()
        self.assert_no_staging()

    def test_plan_apply_rollback_roundtrip_preserves_originals(self):
        planned = self.plan()
        self.assertEqual(snapshot(self.root), self.before, "plan must not write")
        self.assertEqual(len(planned["added_sha256"]), 14)
        result = self.apply()
        self.assertEqual(result.returncode, 0, result.stderr)
        self.assert_baseline_unchanged()
        check = subprocess.run([sys.executable, str(self.root / LAB / "check_review.py"),
                                str(self.root / LAB / "expected-review.json")], capture_output=True, text=True)
        self.assertEqual(check.returncode, 0, check.stderr)
        dry = self.command("rollback", "--dry-run")
        self.assertEqual(dry.returncode, 0, dry.stderr)
        self.assertTrue((self.root / LAB / "manuscript.txt").exists())
        result = self.command("rollback", "--confirm-isolated-copy")
        self.assertEqual(result.returncode, 0, result.stderr)
        self.assertEqual(snapshot(self.root), self.before)
        self.assertFalse((self.root / LAB).exists())

    def test_existing_target_is_never_overwritten(self):
        (self.root / LAB).mkdir()
        keep = self.root / LAB / "manuscript.txt"
        keep.write_text("기존 학습자 파일", encoding="utf-8")
        self.assertNotEqual(self.command("plan").returncode, 0)
        self.assertEqual(keep.read_text(encoding="utf-8"), "기존 학습자 파일")

    def test_missing_skill_stops_without_writes(self):
        path = self.root / ".agents/skills/experiment-log/SKILL.md"
        path.unlink()
        before = snapshot(self.root)
        result = self.command("plan")
        self.assertNotEqual(result.returncode, 0)
        self.assertIn("experiment-log/SKILL.md", result.stderr)
        self.assertEqual(snapshot(self.root), before)

    def test_baseline_change_after_plan_stops_apply(self):
        self.plan()
        path = self.root / "llm_wiki/research/_template/plan.md"
        path.write_text(path.read_text(encoding="utf-8") + "\n학습자의 변경\n", encoding="utf-8")
        before = snapshot(self.root)
        self.assertNotEqual(self.apply().returncode, 0)
        self.assertEqual(snapshot(self.root), before)

    def test_apply_requires_reviewed_plan_and_copy_confirmation(self):
        self.assertNotEqual(self.command("apply").returncode, 0)
        self.plan()
        self.assertNotEqual(self.command("apply", "--plan", self.receipt).returncode, 0)
        self.assertFalse((self.root / LAB).exists())

    def test_apply_dry_run_flag_cannot_mutate(self):
        self.plan()
        result = self.command("apply", "--plan", self.receipt, "--confirm-isolated-copy", "--dry-run")
        self.assertNotEqual(result.returncode, 0)
        self.assertEqual(snapshot(self.root), self.before)

    def test_changed_added_file_stops_all_rollback(self):
        self.plan()
        self.assertEqual(self.apply().returncode, 0)
        changed = self.root / LAB / "HANDOFF.md"
        changed.write_text(changed.read_text(encoding="utf-8") + "\n내 결정 기록\n", encoding="utf-8")
        before = snapshot(self.root)
        result = self.command("rollback", "--confirm-isolated-copy")
        self.assertNotEqual(result.returncode, 0)
        self.assertIn("HANDOFF.md", result.stderr)
        self.assertEqual(snapshot(self.root), before)

    def test_unlisted_user_output_survives_rollback(self):
        self.plan()
        self.assertEqual(self.apply().returncode, 0)
        report = self.root / LAB / "outputs/review.json"
        report.parent.mkdir()
        report.write_text('{"my":"result"}', encoding="utf-8")
        self.assertEqual(self.command("rollback", "--confirm-isolated-copy").returncode, 0)
        self.assertEqual(report.read_text(encoding="utf-8"), '{"my":"result"}')
        self.assert_baseline_unchanged()

    def test_tampered_manifest_cannot_target_baseline(self):
        self.plan()
        self.assertEqual(self.apply().returncode, 0)
        path = self.root / LAB / ".part5-added-files.json"
        record = json.loads(path.read_text(encoding="utf-8"))
        record["added_sha256"]["README.md"] = self.before["README.md"]
        path.write_text(json.dumps(record), encoding="utf-8")
        before = snapshot(self.root)
        self.assertNotEqual(self.command("rollback", "--confirm-isolated-copy").returncode, 0)
        self.assertEqual(snapshot(self.root), before)

    def test_symlink_target_is_refused(self):
        (self.root / LAB).symlink_to(self.tmp / "unrelated")
        self.assertNotEqual(self.command("plan").returncode, 0)
        self.assertFalse((self.tmp / "unrelated").exists())

    def test_symlink_project_ancestor_is_refused(self):
        alias = self.tmp / "shortcut"
        alias.symlink_to(self.tmp, target_is_directory=True)
        original = self.root
        self.root = alias / "wiki-copy"
        result = self.command("plan")
        self.assertNotEqual(result.returncode, 0)
        self.assertEqual(snapshot(original), self.before)

    def test_actual_wiki_procedure_docs_layout_is_explicit(self):
        if ACTUAL is None:
            self.skipTest("--actual-wiki-root was not supplied")
        # 실제 프로젝트에서는 필요한 읽기 전용 기준 파일만 임시 복사한다.
        shutil.rmtree(self.root)
        self.root.mkdir()
        names = ["AGENTS.md", "README.md", "llm_wiki/AGENTS.md", "llm_wiki/research/AGENTS.md"]
        names += ["llm_wiki/research/_template/" + n for n in ("index.md", "experiment.md", "plan.md")]
        names += ["skills/" + n + "/SKILL.md" for n in ("paper-reading", "experiment-log")]
        for name in names:
            target = self.root / name
            target.parent.mkdir(parents=True, exist_ok=True)
            shutil.copyfile(ACTUAL / name, target)
        self.before = snapshot(self.root)
        self.assertNotEqual(self.command("plan").returncode, 0)
        result = self.plan("--skills-dir", "skills")
        self.assertIn("등록", result["skill_note"])
        self.assertEqual(self.apply().returncode, 0)
        self.assert_baseline_unchanged()
        self.assertFalse((self.root / ".agents").exists())
        self.assertFalse((self.root / ".claude").exists())


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--part4-reference", type=Path, required=True)
    parser.add_argument("--actual-wiki-root", type=Path)
    args, remainder = parser.parse_known_args()
    REF = args.part4_reference.resolve()
    ACTUAL = args.actual_wiki_root.resolve() if args.actual_wiki_root else None
    unittest.main(argv=[sys.argv[0], *remainder], verbosity=2)
