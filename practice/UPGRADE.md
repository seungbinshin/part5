# 기존 Part 4 Wiki에 Part 5 실습만 추가하기

이미 만든 Wiki의 **복사본 또는 격리된 작업트리**에서 이어서 합니다. 원본 프로젝트 경로를 아래 명령에 넣지 마세요. 기존 논문·질문·실험 기록·규칙·Skill을 새 템플릿으로 교체하지 않습니다. 별도 서버나 Skill 설치도 필요 없습니다.

## 기존 경로부터 확인합니다

이 강의의 Part 4 HTML은 `.agents/skills/<이름>/SKILL.md`와 `AGENTS.md`를 안내합니다. 배포 실습 안내에는 `.claude/skills`와 `CLAUDE.md`가 있어 자료끼리 경로가 다릅니다. 자신의 완료된 Wiki에 있는 경로를 직접 확인하고 사용합니다.

확인한 기존 연구위키 구현에는 `AGENTS.md`, `llm_wiki/AGENTS.md`, `llm_wiki/research/AGENTS.md`와 `skills/paper-reading/SKILL.md`, `skills/experiment-log/SKILL.md`가 있습니다. 그 `skills/` 파일은 **설치·등록·자동 로드되지 않는 절차 문서**입니다. 경로가 있다는 이유만으로 등록 완료라고 하지 않습니다. 이 경우 아래의 `--skills-dir skills`를 사용해 기존 문서를 참조합니다. 실제 위키 원본에서는 이 업그레이드 명령을 실행하지 않았습니다.

복사본에는 다음이 있어야 합니다. 스크립트는 빠진 정확한 경로를 출력하고 멈춥니다. 누락을 피하려고 빈 Skill 파일을 만들지 마세요.

- `llm_wiki/research/_template/index.md`, `experiment.md`, `plan.md`
- 기존 `paper-reading/SKILL.md`, `experiment-log/SKILL.md` 두 문서
- 루트·`llm_wiki/`·`llm_wiki/research/` 각각의 `AGENTS.md`, `README.md`, `CLAUDE.md` 중 실제 운영 규칙

## 변경 전후

```text
기존 Wiki 복사본/
├── AGENTS.md 또는 기존 루트 규칙                 유지
├── .agents/skills/ 또는 실제 skills 경로         유지
│   ├── paper-reading/SKILL.md
│   └── experiment-log/SKILL.md
└── llm_wiki/research/
    ├── _template/                              유지
    ├── 기존 연구 프로젝트/                      유지
    └── part5-lab/                              새로 추가
        ├── manuscript.txt, case-data.json
        ├── source-results.csv, source-notes.txt
        ├── review-template.json, expected-review.json
        ├── input-checksums.json, check_review.py
        ├── README.md, UPGRADE.md, optional-agent-prompt.md
        ├── role-contracts.md, HANDOFF.md
        └── .part5-added-files.json               추가 경로·해시 기록
```

`role-contracts.md`는 기존 문헌 읽기·실험 기록 절차와 네 역할의 인계를 연결합니다. `HANDOFF.md`에는 보존한 기준, 실제 추가 파일, 검토 결과와 사람의 결정을 나눠 기록합니다. 핵심 실습의 새 산출물은 `outputs/review.json`입니다. 기존 Wiki의 `data/wiki.json`, 허브, index, log 또는 정적 빌드에 자동 편입하지 않습니다. 기존 Skill을 다시 생성하거나 실행하지 않고, 그 입력·검증·보존 원칙 위에 별도 리뷰 단계를 추가합니다.

## Python으로 추가하기

Python 3.8 이상, 표준 라이브러리만 사용합니다. 아래 명령은 내려받은 **Part 5 배포 폴더의 루트**에서 실행합니다. `WIKI_COPY`는 실제 복사본 경로로 바꿉니다. 이 예시는 기존 문서가 `skills/`에 있는 Wiki에 맞춥니다. `.agents/skills/`를 쓰는 완료본이면 `--skills-dir .agents/skills`로 바꿉니다.

```sh
WIKI_COPY="/절대/경로/기존-Wiki-복사본"
(set -C
python3 practice/upgrade_wiki.py plan --project-copy "$WIKI_COPY" --skills-dir skills > part5-upgrade-plan.json)
```

`plan`은 프로젝트를 수정하지 않습니다. 괄호 안의 `set -C`는 해당 명령에서 기존 계획 파일을 덮어쓰지 않게 합니다. 출력 JSON에서 대상 경로, 기존 파일 해시, `added_sha256`의 추가 파일 목록을 읽습니다. 명령이 실패했다면 생긴 빈 계획 파일로 다음 단계에 가지 마세요. 기존 계획 파일이 있다면 다른 이름을 써서 보관합니다.

검토한 계획과 같은 입력으로 적용합니다. `--confirm-isolated-copy`는 별도 복사본임을 확인하는 표시입니다. 스크립트가 경로만으로 원본 여부를 판별하는 것은 아닙니다.

```sh
python3 practice/upgrade_wiki.py apply --project-copy "$WIKI_COPY" --plan part5-upgrade-plan.json --confirm-isolated-copy
python3 "$WIKI_COPY/llm_wiki/research/part5-lab/check_review.py" "$WIKI_COPY/llm_wiki/research/part5-lab/expected-review.json"
```

정상 결과는 `ADDED`, `added_files: 13`과 추가 기록 파일 경로입니다. 이어진 검수기는 `PASS`를 출력합니다. 그다음 복사본의 `part5-lab/README.md`를 따라 자신의 보고서를 작성합니다. Skill 경로를 찾았다는 사실은 해당 도구가 자동 로드한다는 검증을 대신하지 않습니다.

## Python 없이 추가하기

파일 관리자로 기존 Wiki를 별도 복사한 뒤 `llm_wiki/research/part5-lab`이 없는지 확인합니다. 있으면 병합하거나 덮어쓰지 말고 중단합니다. 없는 경우에만 새 폴더를 만들고 위 트리의 **추가 파일 13개**를 내려받은 `practice/`에서 그곳으로 복사합니다. `upgrade_wiki.py`, 테스트 코드, 선택 에이전트 정의는 필수 추가 파일에 포함하지 않습니다.

복사한 파일 목록을 별도 메모에 남깁니다. Python 없는 경로에서는 자동 해시 manifest가 만들어지지 않습니다. 정리는 추가 목록과 자신이 고친 파일을 대조한 뒤 직접 합니다. 기존 Wiki의 규칙·Skill·연구 기록은 이동하거나 덮어쓰지 않습니다. 실습 답은 `expected-review.json`과 직접 비교할 수 있습니다.

## 중단 메시지 읽기

| 상황 | 의미와 다음 행동 |
|---|---|
| 선행 파일 또는 운영 규칙 없음 | 실제 Part 4 경로를 확인합니다. `--skills-dir`는 복사본 내부의 기존 문서 경로만 지정합니다. |
| `part5-lab`이 이미 존재 | 아무것도 덮어쓰지 않습니다. 앞서 한 작업을 확인합니다. |
| 계획과 현재 상태가 다름 | 계획 뒤 기존 규칙·Skill·배포본이 바뀌었는지 확인하고 새 계획을 검토합니다. |
| 심볼릭 링크 발견 | 원본을 가리킬 수 있어 중단합니다. 링크가 아닌 격리된 사본을 준비합니다. |
| 실습 보고서가 FAIL | `part5-lab/README.md`의 검수 항목을 확인합니다. Wiki 업그레이드 실패와 구분합니다. |

## 추가한 파일만 복구하기

먼저 삭제 예정 목록을 읽습니다.

```sh
python3 practice/upgrade_wiki.py rollback --project-copy "$WIKI_COPY" --dry-run
python3 practice/upgrade_wiki.py rollback --project-copy "$WIKI_COPY" --confirm-isolated-copy
```

복구는 `.part5-added-files.json`에 기록된 추가 파일이 모두 그대로일 때만 진행합니다. 기존 기준 파일이나 추가 파일이 바뀌었거나 목록이 맞지 않으면 전체 복구를 중단하고 경로를 표시합니다. 그 파일을 지워 진행하지 말고 변경 내용을 먼저 보관·확인하세요. 목록에 없는 `outputs/review.json` 등 학습자가 만든 파일은 삭제하지 않습니다. 따라서 복구 후에도 `part5-lab` 폴더가 남을 수 있습니다.

원본 Wiki, 기존 AGENTS, Skill, 연구 기록에는 쓰지 않습니다. 선택형 읽기 전용 에이전트 등록은 이 추가 작업과 별도이며 기존 정의를 덮어쓰지 않는지 따로 확인합니다.
