"""사례 게시 게이트·HTML 경계를 검사한다. 사례는 테스트 실행 중에만 만든다."""
import copy
from datetime import date, timedelta
from html import escape
from html.parser import HTMLParser
import json
from pathlib import Path
import runpy
import shutil
import subprocess
import sys
import tempfile
import unittest


ROOT = Path(__file__).resolve().parents[1]
MODULE = runpy.run_path(str(ROOT / "project_cases.py"))
validate = MODULE["validate"]
render = MODULE["render"]


def synthetic_case():
    """게시 데이터나 실제 프로젝트를 읽지 않는 테스트 전용 가상 입력."""
    return {
        "id": "test-only-case",
        "title": "테스트 전용 가상 사례",
        "summary": "게시용이 아닌 검증 입력입니다.",
        "tags": ["테스트 개념"],
        "category": "연구·검증",
        "evidence_status": "테스트 전용 근거 상태",
        "transfer": "실제 적용이 아닌 테스트용 원칙입니다.",
        "period": "테스트 기간",
        "context": "가상의 시작 상황입니다.",
        "approach": "테스트에서만 구성한 처리 방법입니다.",
        "outcome": "실제 성과를 뜻하지 않는 테스트 결과입니다.",
        "lesson": "형식 검사만 확인합니다.",
        "limits": "실제 프로젝트의 사실이나 검토 증거가 아닙니다.",
        "review": {
            "evidence_checked": True,
            "privacy_checked": True,
            "checked_on": "2000-01-01",
        },
    }


def payload_with(case):
    return {"version": 1, "cases": [case, dict(synthetic_case(), id="test-second"), dict(synthetic_case(), id="test-third")]}


class ParsedHTML(HTMLParser):
    def __init__(self):
        super().__init__(convert_charrefs=True)
        self.elements = []
        self.text = []

    def handle_starttag(self, tag, attrs):
        self.elements.append((tag, dict(attrs)))

    def handle_data(self, data):
        self.text.append(data)


class ProjectCaseTests(unittest.TestCase):
    def test_exactly_three_cases_are_required(self):
        for count in (1, 2, 4, 18):
            with self.subTest(count=count):
                cases = [dict(synthetic_case(), id=f"test-{i}") for i in range(count)]
                with self.assertRaisesRegex(ValueError, "정확히 3개"):
                    validate({"version": 1, "cases": cases}, require_cases=True)

    def test_three_cards_are_visible_without_filter_or_more_controls(self):
        parsed = ParsedHTML()
        parsed.feed(render(validate(payload_with(synthetic_case()), require_cases=True)))
        cards = [attrs for tag, attrs in parsed.elements if attrs.get("class") == "case-item"]
        self.assertEqual(len(cards), 3)
        self.assertTrue(all("hidden" not in attrs for attrs in cards))
        self.assertFalse(any(tag in {"input", "select", "form", "button"} for tag, _ in parsed.elements))
        self.assertEqual(sum(tag == "details" for tag, _ in parsed.elements), 3)

    def test_release_data_contains_only_the_selected_three(self):
        actual = json.loads((ROOT / "data/project-cases.json").read_text())
        self.assertEqual([case["id"] for case in validate(actual, require_cases=True)],
                         ["gpu-ccws-swl", "hexaharness", "dram-atlas"])
        self.assertTrue(all("featured" not in case for case in actual["cases"]))

    def assert_build_blocked_and_outputs_unchanged(self, payload, message=None):
        # 출력 파일은 실제 배포본 대신 테스트 임시 폴더의 sentinel을 사용한다.
        with tempfile.TemporaryDirectory(prefix="part5-case-gate-") as temporary:
            root = Path(temporary)
            shutil.copyfile(ROOT / "build.py", root / "build.py")
            shutil.copyfile(ROOT / "project_cases.py", root / "project_cases.py")
            (root / "data").mkdir()
            (root / "data/project-cases.json").write_text(
                json.dumps(payload, ensure_ascii=False), encoding="utf-8"
            )
            sentinels = {
                "index.html": b"TEST_ONLY_ORIGINAL_INDEX\x00\n",
                "transcripts.html": b"TEST_ONLY_ORIGINAL_TRANSCRIPTS\n",
            }
            for name, content in sentinels.items():
                (root / name).write_bytes(content)
            result = subprocess.run(
                [sys.executable, "-B", str(root / "build.py"), "--require-project-cases"],
                cwd=root, capture_output=True, text=True,
            )
            self.assertEqual(result.returncode, 1, result.stdout + result.stderr)
            if message:
                self.assertIn(message, result.stderr)
            for name, content in sentinels.items():
                self.assertEqual((root / name).read_bytes(), content, name)

    def test_empty_cases_are_preview_only(self):
        payload = {"version": 1, "cases": []}
        self.assertEqual(validate(payload), [])
        self.assertIn("아직 확정된 사례는 없습니다", render([]))
        with self.assertRaisesRegex(ValueError, "게시 보류"):
            validate(payload, require_cases=True)

    def test_empty_publish_build_preserves_both_outputs(self):
        self.assert_build_blocked_and_outputs_unchanged(
            {"version": 1, "cases": []}, message="게시 보류"
        )

    def test_each_review_must_be_explicitly_complete(self):
        for field in ("evidence_checked", "privacy_checked"):
            for incomplete in (False, None, 1, "true"):
                with self.subTest(field=field, value=incomplete):
                    case = synthetic_case()
                    case["review"][field] = incomplete
                    with self.assertRaisesRegex(ValueError, "게시 보류"):
                        validate(payload_with(case), require_cases=True)

    def test_invalid_or_future_review_dates_are_rejected(self):
        invalid_dates = (
            "2024-02-30", "2024-13-01", "2024-1-01", "not-a-date",
            (date.today() + timedelta(days=1)).isoformat(),
        )
        for checked_on in invalid_dates:
            with self.subTest(checked_on=checked_on):
                case = synthetic_case()
                case["review"]["checked_on"] = checked_on
                with self.assertRaises(ValueError):
                    validate(payload_with(case), require_cases=True)

    def test_duplicate_case_ids_are_rejected(self):
        case = synthetic_case()
        duplicate = copy.deepcopy(case)
        duplicate["title"] = "테스트 전용 두 번째 제목"
        with self.assertRaisesRegex(ValueError, "중복"):
            validate({"version": 1, "cases": [case, duplicate]}, require_cases=True)

    def test_invalid_builds_preserve_outputs(self):
        incomplete = synthetic_case()
        incomplete["review"]["privacy_checked"] = False
        wrong_date = synthetic_case()
        wrong_date["review"]["checked_on"] = "2024-02-30"
        duplicate = synthetic_case()
        for name, payload in (
            ("unreviewed", payload_with(incomplete)),
            ("invalid-date", payload_with(wrong_date)),
            ("duplicate-id", {"version": 1, "cases": [duplicate, copy.deepcopy(duplicate)]}),
        ):
            with self.subTest(reason=name):
                self.assert_build_blocked_and_outputs_unchanged(payload)

    def test_user_text_is_escaped_in_content_and_attributes(self):
        case = synthetic_case()
        case.update({
            "title": '검증 <img src=x onerror="alert(1)"> & "제목"',
            "summary": "<script>alert('test')</script>",
            "context": '</dd><iframe src="test-only"></iframe>',
            "approach": '<a href="javascript:alert(1)">방법</a>',
            "outcome": "<svg onload=alert(1)>결과</svg>",
            "lesson": '<b title="가상">배울 점 & 경계</b>',
            "limits": "<style>body{display:none}</style>",
            "period": "<b>가상 기간</b>",
            "tags": ['x\"><img src=x onerror=1>', "근거 & 한계"],
        })
        rendered = render(validate(payload_with(case), require_cases=True))
        parsed = ParsedHTML()
        parsed.feed(rendered)
        dangerous_tags = {"script", "img", "iframe", "svg", "style"}
        self.assertFalse(dangerous_tags & {tag for tag, _ in parsed.elements})
        for _, attributes in parsed.elements:
            self.assertFalse(any(name.startswith("on") or name == "srcdoc" for name in attributes))
        for field in ("title", "summary", "context", "approach", "outcome", "lesson", "limits", "period"):
            self.assertIn(escape(case[field], quote=True), rendered, field)
            self.assertIn(case[field], "".join(parsed.text), field)
        for tag in case["tags"]:
            self.assertIn(tag, "".join(parsed.text))

    def test_review_object_is_not_serialized_into_html(self):
        payload = payload_with(synthetic_case())
        original = copy.deepcopy(payload)
        rendered = render(validate(payload, require_cases=True))
        parsed = ParsedHTML()
        parsed.feed(rendered)
        self.assertEqual(payload, original, "validation/render must not alter the source object")
        self.assertIn("사례 확인일 2000-01-01", "".join(parsed.text))
        for hidden_key in ("evidence_checked", "privacy_checked", "checked_on"):
            self.assertNotIn(hidden_key, rendered)
        self.assertNotIn(json.dumps(payload, ensure_ascii=False), rendered)
        self.assertNotIn('"review"', rendered)
        self.assertFalse(any(tag == "script" for tag, _ in parsed.elements))

    def test_extra_source_or_review_objects_are_rejected(self):
        for extra_at in ("case", "review"):
            with self.subTest(extra_at=extra_at):
                case = synthetic_case()
                destination = case if extra_at == "case" else case["review"]
                destination["source_object"] = {"test_only_note": "must not enter the page"}
                with self.assertRaises(ValueError):
                    validate(payload_with(case), require_cases=True)


if __name__ == "__main__":
    unittest.main(verbosity=2)
