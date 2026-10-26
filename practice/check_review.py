#!/usr/bin/env python3
"""교육용 정답·보고 범위·입력 무결성을 대조한다. AI 추론이나 샌드박스가 아니다."""
import argparse
import hashlib
import json
from pathlib import Path
import sys


def read_json(path):
    return json.loads(path.read_text(encoding="utf-8"))


def check(report, root):
    errors = []
    expected = read_json(root / "expected-review.json")
    checksums = read_json(root / "input-checksums.json")
    for name, expected_hash in checksums.items():
        path = root / name
        if not path.is_file() or hashlib.sha256(path.read_bytes()).hexdigest() != expected_hash:
            errors.append("입력 파일이 없거나 바뀌었습니다: " + name)
    if not isinstance(report, dict):
        return errors + ["보고서는 JSON 객체여야 합니다."]
    if set(report) != set(expected):
        errors.append("보고서의 필드가 템플릿과 다릅니다.")
    for key in ("schema_version", "input_version", "reviewer", "requested_writes",
                "manuscript_changes", "approval_status"):
        if type(report.get(key)) is not type(expected[key]) or report.get(key) != expected[key]:
            errors.append("역할 계약과 다른 값: " + key)
    findings = report.get("findings")
    if not isinstance(findings, list):
        return errors + ["findings는 목록이어야 합니다."]
    wanted = {item["claim_id"]: item for item in expected["findings"]}
    seen = set()
    for item in findings:
        if not isinstance(item, dict):
            errors.append("각 finding은 JSON 객체여야 합니다.")
            continue
        claim = item.get("claim_id")
        if not isinstance(claim, str) or claim not in wanted or claim in seen:
            errors.append("알 수 없거나 중복된 claim_id: " + repr(claim))
            continue
        seen.add(claim)
        if set(item) != set(wanted[claim]):
            errors.append(claim + ": 지적의 필드가 템플릿과 다릅니다.")
        if item.get("classification") != wanted[claim]["classification"]:
            errors.append(claim + ": 교육용 판정 기준과 다릅니다.")
        if item.get("evidence_ids") != wanted[claim]["evidence_ids"]:
            errors.append(claim + ": 근거 ID가 다릅니다.")
        for key in ("reason", "next_check"):
            if not isinstance(item.get(key), str) or not item[key].strip():
                errors.append(claim + ": " + key + "를 작성하세요.")
    if seen != set(wanted):
        errors.append("C1, C2, C3를 빠짐없이 한 번씩 검토하세요.")
    decisions = report.get("human_decisions")
    if not isinstance(decisions, list) or not decisions or not all(isinstance(x, str) and x.strip() for x in decisions):
        errors.append("연구자에게 남길 결정 항목을 작성하세요.")
    return errors


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("report", type=Path, help="검수할 JSON 보고서")
    parser.add_argument("--json", action="store_true", help="검사 결과를 JSON으로 출력")
    args = parser.parse_args()
    root = Path(__file__).resolve().parent
    try:
        errors = check(read_json(args.report), root)
    except (OSError, ValueError, TypeError) as exc:
        errors = ["파일 또는 JSON을 읽을 수 없습니다: " + str(exc)]
    result = {
        "status": "FAIL" if errors else "PASS",
        "errors": errors,
        "checked": "교육용 판정 3개, 근거 ID, 보고한 쓰기 범위, 입력 파일 무결성",
        "manual_review": "reason과 next_check의 의미, 원고 변경 여부, 연구자의 최종 결정은 직접 확인하세요.",
        "limits": "실제 연구의 진실성이나 모델 품질을 평가하지 않습니다. 파일 접근을 차단하는 샌드박스가 아닙니다."
    }
    if args.json:
        print(json.dumps(result, ensure_ascii=False, indent=2))
    else:
        print(result["status"] + ": " + result["checked"])
        for error in errors:
            print("- " + error)
        print("수동 확인: " + result["manual_review"])
        print(result["limits"])
    return 1 if errors else 0


if __name__ == "__main__":
    sys.exit(main())
