#!/usr/bin/env python3
"""Install/verify Part 5 Claude Code subagents in an isolated project copy.

This checks files, not actual Claude Code execution.
"""
import argparse
import hashlib
import json
import os
from pathlib import Path
import re
import sys
import tempfile

HERE = Path(__file__).resolve().parent
PACKAGE = HERE / "agent-definitions"
CORE = ("literature-reviewer", "experiment-planner", "draft-writer", "writing-reviewer")
REVIEWERS = ("reviewer-methodology", "reviewer-fairness", "reviewer-domain", "reviewer-novelty", "reviewer-writing")
GROUPS = {"core": CORE, "reviewers": REVIEWERS, "all": CORE + REVIEWERS}

def digest(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()

def project_root(raw):
    root = Path(raw).expanduser().absolute()
    if not root.is_dir() or ".." in root.parts:
        raise ValueError("격리된 프로젝트 디렉터리를 확인하세요: " + str(root))
    if any(p.is_symlink() for p in (root, *root.parents)):
        raise ValueError("프로젝트 경로에 심볼릭 링크가 있습니다: " + str(root))
    return root.resolve()

def dest_dir(root):
    parent = root / ".claude"
    dest = parent / "agents"
    if parent.is_symlink() or dest.is_symlink():
        raise ValueError("Agent 경로의 심볼릭 링크를 허용하지 않습니다")
    if (parent.exists() and not parent.is_dir()) or (dest.exists() and not dest.is_dir()):
        raise ValueError("Agent 경로가 디렉터리가 아닙니다")
    return dest

def sources(group):
    found = []
    for name in GROUPS[group]:
        path = PACKAGE / (name + ".md")
        if not path.is_file() or path.is_symlink():
            raise ValueError("Agent 정의 누락: " + str(path))
        text = path.read_text(encoding="utf-8")
        front = re.match(r"\A---\n(.*?)\n---\n", text, re.S)
        if not front:
            raise ValueError("YAML frontmatter 누락: " + name)
        fields = front.group(1)
        if not re.search(r"(?m)^name:\s*" + re.escape(name) + r"\s*$", fields):
            raise ValueError("Agent 이름이 파일명과 다릅니다: " + name)
        if not re.search(r"(?m)^description:\s*\S", fields):
            raise ValueError("description 누락: " + name)
        found.append((name, path))
    return found

def inspect(root, group):
    target = dest_dir(root)
    entries = []
    for name, src in sources(group):
        dst = target / (name + ".md")
        if dst.is_symlink():
            status = "conflict-symlink"
        elif not dst.exists():
            status = "missing"
        elif not dst.is_file():
            status = "conflict-type"
        elif digest(dst) != digest(src):
            status = "conflict-content"
        else:
            status = "identical"
        entries.append({"name": name, "status": status, "path": str(dst)})
    return target, entries

def install(root, group):
    target, entries = inspect(root, group)
    conflicts = [e["name"] for e in entries if e["status"].startswith("conflict")]
    if conflicts:
        raise ValueError("기존 Agent 정의를 덮어쓰지 않습니다: " + ", ".join(conflicts))
    missing = [(name, src) for name, src in sources(group) if next(e for e in entries if e["name"] == name)["status"] == "missing"]
    if not missing:
        return {"status": "UNCHANGED", "installed": 0, "verified": len(entries), "target": str(target)}
    target.parent.mkdir(exist_ok=True)
    target.mkdir(exist_ok=True)
    created = []
    try:
        with tempfile.TemporaryDirectory(prefix=".part5-stage-", dir=target.parent) as stage_name:
            stage = Path(stage_name)
            for name, src in missing:
                staged = stage / src.name
                staged.write_bytes(src.read_bytes())
                if digest(staged) != digest(src):
                    raise ValueError("임시 파일 해시 불일치: " + name)
            for name, src in missing:
                dest = target / src.name
                os.link(stage / src.name, dest)  # exclusive creation; never overwrite
                created.append(dest)
                if digest(dest) != digest(src):
                    raise ValueError("설치 파일 해시 불일치: " + name)
        _, after = inspect(root, group)
        if any(e["status"] != "identical" for e in after):
            raise ValueError("설치 후 검증 실패")
    except Exception:
        for path in reversed(created):
            if path.is_file() and not path.is_symlink():
                path.unlink()
        raise
    return {"status": "INSTALLED", "installed": len(created), "verified": len(after), "target": str(target)}

def main(argv=None):
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("action", choices=("plan", "install", "verify"))
    parser.add_argument("--project-copy", required=True)
    parser.add_argument("--group", choices=GROUPS, default="all")
    parser.add_argument("--confirm-isolated-copy", action="store_true")
    args = parser.parse_args(argv)
    try:
        root = project_root(args.project_copy)
        if args.action == "install":
            if not args.confirm_isolated_copy:
                raise ValueError("설치에는 --confirm-isolated-copy가 필요합니다")
            result = install(root, args.group)
        else:
            target, entries = inspect(root, args.group)
            result = {"status": "PLAN" if args.action == "plan" else "VERIFIED", "target": str(target), "entries": entries}
            if args.action == "verify" and any(e["status"] != "identical" for e in entries):
                result["status"] = "FAILED"
                print(json.dumps(result, ensure_ascii=False, indent=2))
                return 1
        result["runtime_invocation"] = "NOT_TESTED"
        print(json.dumps(result, ensure_ascii=False, indent=2))
        return 0
    except (OSError, ValueError, UnicodeError) as exc:
        print("중단: " + str(exc), file=sys.stderr)
        return 1

if __name__ == "__main__":
    sys.exit(main())
