#!/usr/bin/env python3
"""모범 답안 통과, 잘못된 판정·권한·입력 변경 거부를 확인한다."""
import json
import hashlib
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

    def run_submission(self, mutate=None, missing=False, wrong_path=False):
        output = self.root / "outputs"
        output.mkdir(exist_ok=True)
        path = output / ("other.json" if wrong_path else "review.json")
        path.write_text(json.dumps(self.report, ensure_ascii=False), encoding="utf-8")
        handoff = {
            "input_version": "synthetic-v1", "review_file": "outputs/review.json",
            "review_sha256": hashlib.sha256(path.read_bytes()).hexdigest(),
            "pending_claim_ids": ["C2", "C3"],
            "approval_status": "awaiting-human", "next_actor": "human",
        }
        if mutate:
            mutate(handoff)
        handoff_path = output / "handoff.json"
        if not missing:
            handoff_path.write_text(json.dumps(handoff), encoding="utf-8")
        process = subprocess.run([sys.executable, str(self.root / "check_review.py"), str(path),
                                  "--handoff", str(handoff_path), "--json"], capture_output=True, text=True)
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

    def test_learner_report_and_current_handoff_pass(self):
        # 문자열 복제 여부가 아닌 연결·형식 검증이다. 이유의 의미는 사람이 읽는다.
        self.report["findings"][0]["reason"] = "source-results.csv E1의 한 조건만 설명했다."
        code, result = self.run_submission()
        self.assertEqual(code, 0)
        self.assertEqual(result["status"], "PASS")
        self.assertIn("인계", result["checked"])

    def test_missing_evidence_id_fails(self):
        self.report["findings"][0]["evidence_ids"] = []
        code, result = self.run_submission()
        self.assertEqual(code, 1)
        self.assertTrue(any("근거 ID" in error for error in result["errors"]))

    def test_missing_handoff_file_fails(self):
        code, result = self.run_submission(missing=True)
        self.assertEqual(code, 1)
        self.assertTrue(any("파일 또는 JSON" in error for error in result["errors"]))

    def test_stale_report_hash_fails(self):
        code, result = self.run_submission(lambda h: h.update(review_sha256="0" * 64))
        self.assertEqual(code, 1)
        self.assertTrue(any("review_sha256" in error for error in result["errors"]))

    def test_missing_pending_claim_fails(self):
        code, result = self.run_submission(lambda h: h.update(pending_claim_ids=["C2"]))
        self.assertEqual(code, 1)
        self.assertTrue(any("주장 ID" in error for error in result["errors"]))

    def test_duplicate_pending_claim_fails(self):
        code, result = self.run_submission(lambda h: h.update(pending_claim_ids=["C2", "C2", "C3"]))
        self.assertEqual(code, 1)
        self.assertTrue(any("주장 ID" in error for error in result["errors"]))

    def test_handoff_cannot_claim_approval(self):
        code, result = self.run_submission(lambda h: h.update(approval_status="approved"))
        self.assertEqual(code, 1)
        self.assertTrue(any("approval_status" in error for error in result["errors"]))

    def test_other_report_cannot_stand_in_for_learner_output(self):
        code, result = self.run_submission(wrong_path=True)
        self.assertEqual(code, 1)
        self.assertTrue(any("outputs/review.json" in error for error in result["errors"]))

    def test_malformed_handoff_fails(self):
        code, result = self.run_submission(lambda h: h.pop("next_actor"))
        self.assertEqual(code, 1)
        self.assertTrue(any("필드" in error for error in result["errors"]))


if __name__ == "__main__":
    unittest.main(verbosity=2)
