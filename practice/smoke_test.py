#!/usr/bin/env python3
"""모범 답안 통과, 잘못된 판정·권한·입력 변경 거부를 확인한다."""
import json
from pathlib import Path
import shutil
import subprocess
import sys
import tempfile
import unittest

ROOT = Path(__file__).resolve().parent


class ReviewSmokeTests(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory(prefix=".smoke-", dir=ROOT)
        self.root = Path(self.temp.name)
        for name in ("check_review.py", "expected-review.json", "input-checksums.json", "case-data.json", "manuscript.txt", "source-results.csv", "source-notes.txt"):
            shutil.copyfile(ROOT / name, self.root / name)
        self.report = json.loads((ROOT / "expected-review.json").read_text(encoding="utf-8"))

    def tearDown(self):
        self.temp.cleanup()

    def run_check(self):
        path = self.root / "test-report.json"
        path.write_text(json.dumps(self.report, ensure_ascii=False), encoding="utf-8")
        process = subprocess.run([sys.executable, str(self.root / "check_review.py"), str(path), "--json"], capture_output=True, text=True)
        return process.returncode, json.loads(process.stdout)

    def test_expected_report_passes(self):
        code, result = self.run_check()
        self.assertEqual(code, 0)
        self.assertEqual(result["status"], "PASS")

    def test_wrong_generalization_fails(self):
        self.report["findings"][1]["classification"] = "supported_within_scope"
        code, result = self.run_check()
        self.assertEqual(code, 1)
        self.assertTrue(any("C2" in error for error in result["errors"]))

    def test_out_of_scope_write_fails(self):
        self.report["requested_writes"].append("manuscript.txt")
        code, result = self.run_check()
        self.assertEqual(code, 1)
        self.assertTrue(any("requested_writes" in error for error in result["errors"]))

    def test_approval_cannot_be_claimed(self):
        self.report["approval_status"] = "approved"
        code, result = self.run_check()
        self.assertEqual(code, 1)
        self.assertTrue(any("approval_status" in error for error in result["errors"]))

    def test_input_change_fails(self):
        with (self.root / "manuscript.txt").open("a", encoding="utf-8") as stream:
            stream.write("\n허용하지 않은 원고 수정\n")
        code, result = self.run_check()
        self.assertEqual(code, 1)
        self.assertTrue(any("manuscript.txt" in error for error in result["errors"]))

    def test_missing_claim_fails(self):
        self.report["findings"].pop()
        code, result = self.run_check()
        self.assertEqual(code, 1)
        self.assertTrue(any("빠짐없이" in error for error in result["errors"]))


if __name__ == "__main__":
    unittest.main(verbosity=2)
