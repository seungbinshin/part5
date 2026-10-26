#!/usr/bin/env python3
"""기존 Part 4 Wiki 복사본에 독립 실습 폴더만 추가한다. 설치·등록·기존 파일 수정은 하지 않는다."""
import argparse
import hashlib
import json
from pathlib import Path
import sys
import tempfile

PACKAGE = Path(__file__).resolve().parent
LAB = Path("llm_wiki/research/part5-lab")
MANIFEST = ".part5-added-files.json"
FILES = (
    "README.md", "UPGRADE.md", "manuscript.txt", "case-data.json",
    "source-results.csv", "source-notes.txt", "review-template.json",
    "expected-review.json", "input-checksums.json", "check_review.py",
    "optional-agent-prompt.md", "role-contracts.md", "HANDOFF.md",
)


def digest(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def read_json(path):
    return json.loads(path.read_text(encoding="utf-8"))


def safe_path(root, relative):
    relative = Path(relative)
    if relative.is_absolute() or ".." in relative.parts:
        raise ValueError("허용하지 않은 상대 경로: " + str(relative))
    path = root
    for part in relative.parts:
        path = path / part
        if path.is_symlink():
            raise ValueError("심볼릭 링크는 처리하지 않습니다: " + str(path))
    return path


def project_root(raw):
    path = Path(raw).expanduser().absolute()
    if ".." in path.parts or not path.is_dir():
        raise ValueError("프로젝트 복사본의 실제 디렉터리를 지정하세요: " + str(path))
    if any(part.is_symlink() for part in (path, *path.parents)):
        raise ValueError("프로젝트 경로의 상위 디렉터리도 심볼릭 링크일 수 없습니다: " + str(path))
    return path.resolve()


def baseline(root, skills):
    required = ["llm_wiki/research/_template/" + name for name in ("index.md", "experiment.md", "plan.md")]
    required += [str(Path(skills) / name / "SKILL.md") for name in ("paper-reading", "experiment-log")]
    for folder in ("", "llm_wiki", "llm_wiki/research"):
        choices = [str(Path(folder) / name) for name in ("AGENTS.md", "README.md", "CLAUDE.md")]
        found = [name for name in choices if safe_path(root, name).is_file()]
        if not found:
            raise ValueError("기존 운영 규칙이 없습니다. 확인할 경로: " + ", ".join(choices))
        required.extend(found)
    missing = [name for name in required if not safe_path(root, name).is_file()]
    if missing:
        raise ValueError("기존 Part 4 선행 파일을 확인하세요: " + ", ".join(missing))
    return {name: digest(safe_path(root, name)) for name in sorted(set(required))}


def plan(root, skills):
    target = safe_path(root, LAB)
    if target.exists():
        raise ValueError("추가할 경로가 이미 있습니다. 덮어쓰지 않습니다: " + str(target))
    return {
        "format": "part5-delta-v1", "project_copy": str(root), "skills_dir": skills,
        "scope": "별도 복사본에 part5-lab만 추가; 기존 규칙·Skill·연구 기록 무변경",
        "skill_note": "파일 존재만 확인합니다. 설치·등록·자동 로드 여부를 증명하지 않습니다.",
        "baseline_sha256": baseline(root, skills),
        "added_sha256": {str(LAB / name): digest(PACKAGE / name) for name in FILES},
    }


def compare_baseline(root, entries):
    if not isinstance(entries, dict) or not entries:
        raise ValueError("기준 파일 해시 목록이 없습니다.")
    for name, value in entries.items():
        path = safe_path(root, name)
        if not path.is_file() or digest(path) != value:
            raise ValueError("기존 기준 파일이 계획 이후 바뀌었습니다. 아무것도 변경하지 않습니다: " + name)


def apply(root, receipt):
    old = read_json(receipt)
    if not isinstance(old, dict):
        raise ValueError("dry-run 계획은 JSON 객체여야 합니다.")
    current = plan(root, old.get("skills_dir", ".agents/skills"))
    if old != current:
        raise ValueError("dry-run 계획과 현재 입력·대상·배포 파일이 다릅니다. 계획을 다시 확인하세요.")
    target = safe_path(root, LAB)
    # 같은 파일시스템의 비공개 임시 폴더에서 완성한다. 부분 쓰기는 최종 경로에 남기지 않는다.
    with tempfile.TemporaryDirectory(prefix=".part5-stage-", dir=target.parent) as temporary:
        stage = Path(temporary)
        for name in FILES:
            dest = stage / name
            with dest.open("xb") as stream:
                stream.write((PACKAGE / name).read_bytes())
            if digest(dest) != current["added_sha256"][str(LAB / name)]:
                raise ValueError("추가 파일이 계획과 다릅니다. 게시하지 않습니다: " + name)
        # 생성한 파일만 기록한다. baseline 목록은 보존 여부를 확인할 때만 쓴다.
        with (stage / MANIFEST).open("x", encoding="utf-8") as stream:
            json.dump(current, stream, ensure_ascii=False, indent=2)
            stream.write("\n")
        if read_json(stage / MANIFEST) != current:
            raise ValueError("추가 기록을 검증하지 못했습니다. 게시하지 않습니다.")
        compare_baseline(root, current["baseline_sha256"])
        target = safe_path(root, LAB)
        # 다른 작업이 먼저 만든 경로를 바꾸지 않도록 빈 목적지를 배타적으로 확보한다.
        target.mkdir(exist_ok=False)
        reserved = target.stat()
        try:
            # 목적지는 이 호출이 만든 빈 디렉터리뿐이다. 완성본 디렉터리를 한 번에 옮긴다.
            stage.rename(target)
        except Exception:
            if target.is_dir() and not target.is_symlink():
                state = target.stat()
                if (state.st_dev, state.st_ino) == (reserved.st_dev, reserved.st_ino) and not any(target.iterdir()):
                    target.rmdir()
            raise
    return {"status": "ADDED", "added_files": len(FILES), "manifest": str(target / MANIFEST)}


def rollback(root, dry_run):
    target = safe_path(root, LAB)
    manifest_path = safe_path(root, LAB / MANIFEST)
    record = read_json(manifest_path)
    if not isinstance(record, dict):
        raise ValueError("추가 기록은 JSON 객체여야 합니다.")
    if record.get("format") != "part5-delta-v1" or record.get("project_copy") != str(root):
        raise ValueError("이 복사본의 추가 기록이 아닙니다.")
    compare_baseline(root, record.get("baseline_sha256"))
    entries = record.get("added_sha256")
    allowed = {str(LAB / name) for name in FILES}
    if not isinstance(entries, dict) or set(entries) != allowed:
        raise ValueError("추가 파일 목록이 배포 범위와 다릅니다. 삭제하지 않습니다.")
    paths = []
    for name, value in entries.items():
        path = safe_path(root, name)
        if not path.is_file() or digest(path) != value:
            raise ValueError("추가 파일이 수정되었거나 없습니다. 전체 복구를 중단합니다: " + name)
        paths.append(path)
    result = {"status": "ROLLBACK_PLAN" if dry_run else "ROLLED_BACK", "files": sorted(entries),
              "preserved": "manifest에 없는 파일과 기존 Wiki 파일은 삭제하지 않습니다."}
    if not dry_run:
        for path in paths:
            path.unlink()
        manifest_path.unlink()
        # 학습자가 만든 outputs 등은 목록에 없으므로 그대로 남긴다.
        if not any(target.iterdir()):
            target.rmdir()
    return result


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("action", choices=("plan", "apply", "rollback"))
    parser.add_argument("--project-copy", required=True, help="원본이 아닌 기존 Wiki 복사본의 명시적 경로")
    parser.add_argument("--skills-dir", default=".agents/skills", help="기존 Skill/절차 문서 디렉터리; 복사본 내부 상대 경로")
    parser.add_argument("--plan", type=Path, help="앞서 plan 출력으로 저장한 JSON 파일")
    parser.add_argument("--dry-run", action="store_true", help="rollback 삭제 예정 목록만 확인")
    parser.add_argument("--confirm-isolated-copy", action="store_true", help="원본이 아닌 복사본 또는 격리된 작업트리임을 확인")
    args = parser.parse_args()
    try:
        root = project_root(args.project_copy)
        if args.action == "plan":
            result = plan(root, args.skills_dir)
        elif args.action == "apply":
            if args.dry_run:
                raise ValueError("apply와 --dry-run은 함께 사용할 수 없습니다. plan으로 변경 목록을 확인하세요.")
            if not args.confirm_isolated_copy or not args.plan:
                raise ValueError("apply에는 --plan과 --confirm-isolated-copy가 모두 필요합니다.")
            result = apply(root, args.plan)
        else:
            if not args.dry_run and not args.confirm_isolated_copy:
                raise ValueError("실제 복구에는 --confirm-isolated-copy가 필요합니다. 먼저 --dry-run으로 확인하세요.")
            result = rollback(root, args.dry_run)
        print(json.dumps(result, ensure_ascii=False, indent=2))
        return 0
    except (OSError, ValueError, TypeError, KeyError) as exc:
        print("중단: " + str(exc), file=sys.stderr)
        return 1


if __name__ == "__main__":
    sys.exit(main())
