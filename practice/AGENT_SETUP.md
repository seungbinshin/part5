# Part 5 — 실제 Subagent 생성·위임·독립 심사

Part 1~4의 Wiki 및 `paper-reading`, `experiment-log` Skill은 유지합니다. Part 5의 새 실습은 **연구 Agent 4개 + 심사자 5개 = 총 9개**를 실제로 생성하고 위임하는 것입니다. 역할을 표에만 적는 것은 Agent 생성이 아닙니다.

## 등록 경로를 구분하세요

- 기존 Part 4 Skill: 작업공간의 `.agents/skills/`, `.claude/skills/` 또는 `skills/`. 기존 경로 그대로 둡니다.
- **Claude Code 프로젝트 Subagent:** 격리된 작업공간의 `.claude/agents/<이름>.md`.
- `practice/agent-definitions/*.md`는 강의 자료의 **설치 원본**입니다. 내려받기만 하면 실제 작업공간에 Agent가 생성되는 것은 아닙니다.
- 다른 코딩 도구라면 해당 도구의 공식 Agent 정의 위치를 확인하세요. `.agents/`에 복사했다고 Claude Code가 이를 로드하는 것은 아닙니다.

## 1단계 — 사본 준비와 네 역할 등록

기존 Part 4 작업공간을 복사한 **격리 사본**에서 진행합니다. 원본·기존 Skill·운영 규칙을 덮어쓰지 마세요. 아래 명령은 **Part 5 강의 폴더의 루트**에서 실행하고 `WIKI_COPY`만 실제 격리 사본의 절대 경로로 바꿉니다.

```bash
WIKI_COPY="/절대/경로/Part4-Wiki-복사본"
python3 practice/install_agents.py plan --project-copy "$WIKI_COPY" --group core
python3 practice/install_agents.py install --project-copy "$WIKI_COPY" --group core --confirm-isolated-copy
python3 practice/install_agents.py verify --project-copy "$WIKI_COPY" --group core
```

PowerShell에서는 `$WIKI_COPY = "C:\경로\Part4-Wiki-복사본"`으로 설정하고, 위 명령의 `"$WIKI_COPY"`를 그대로 쓰되 `python3` 대신 환경에 설치된 `python`을 사용할 수 있습니다.

설치된 정의:
- `literature-reviewer`: 실제 문헌과 주장·조건·반례 대조
- `experiment-planner`: 실행 전 비교 실험 후보와 제약 정리
- `draft-writer`: 확인한 근거와 연결된 초안 작성
- `writing-reviewer`: 원고를 고치지 않고 주장–근거·논리 검토

교육용 정의는 `Read, Grep, Glob`만 허용합니다. 이로 인해 Agent는 내용을 Main으로 **반환**하고, Main이 승인된 새 파일을 격리 사본에 기록합니다. 원강의의 일부 Agent 직접 쓰기 방식과 다르며 기존 자료 보호를 위한 변경입니다.

## 2단계 — 실제 Subagent 위임

Claude Code에서 위 네 이름을 **명시해 별도 호출**합니다. 각 요청에는 목표, 허용된 파일·판본, 금지할 변경, 기대 산출물, 중단 조건을 명시합니다. 명칭을 적은 요청만으로 호출을 입증할 수 없습니다.

다음을 구분해 기록합니다: ① 정의 파일 생성 ② Agent 인식 ③ 실제 별도 Subagent 호출 ④ Main에 반환된 결과. 코드 도구가 Agent를 지원하지 않으면 '정의 준비/호출 미검증'으로 표시합니다. 새로운 디렉터리가 세션 도중 생성되어 Claude Code가 인식하지 못하면 세션을 재시작하고 다시 호출합니다.

## 3단계 — 독립 심사자 다섯 명

```bash
python3 practice/install_agents.py plan --project-copy "$WIKI_COPY" --group reviewers
python3 practice/install_agents.py install --project-copy "$WIKI_COPY" --group reviewers --confirm-isolated-copy
python3 practice/install_agents.py verify --project-copy "$WIKI_COPY" --group all
```

다섯 명은 `reviewer-methodology`(방법론·통계), `reviewer-fairness`(비교 공정성), `reviewer-domain`(분야), `reviewer-novelty`(신규성), `reviewer-writing`(구성·표현)입니다.

Main이 동일한 원고 버전과 근거 자료를 각 리뷰어에게 전달합니다. **다른 리뷰어의 보고서를 다음 리뷰어의 입력에 넣지 마세요.** 읽지 말라는 지시 자체는 OS 수준의 접근 차단이 아니므로, 실제 도구 권한·입력 경로도 확인해야 합니다. 각 호출이 별도 컨텍스트에서 수행됐는지 기록합니다. 병렬 기능을 사용하지 못했다면 병렬 실행이라고 주장하지 않습니다.

Main이 새 `reviews/round01/` 위치에 다섯 보고서를 각각 저장하고 `synthesis.md`에 **공통 지적 / 의견 충돌 / 한 명만 발견한 지적**을 나눠 요약합니다. 최종 판단은 연구자에게 남깁니다.

## 완료 기준과 실패 처리

| 확인 | 기준 |
|---|---|
| 사본 보존 | Part 4 원본 및 기존 Skill·규칙의 바이트가 바뀌지 않음 |
| 등록 | 격리 사본 `.claude/agents/`의 9개 Markdown 파일과 `name`·`description` |
| 정적 검사 | `verify --group all` 종료 코드 0 |
| 실제 실행 | 별도 Subagent 호출·반환 로그 확인, 미실행은 명시 |
| 심사 | 같은 초안 버전, 다섯 개별 결과, 종합 보고, 사람 승인 대기 |

`plan`은 아무것도 쓰지 않고, `install`은 충돌 파일을 덮어쓰지 않으며, 이미 같은 정의가 있으면 중복 설치하지 않습니다. `verify`는 배포본과 설치본의 파일을 비교할 뿐 **실제 Claude Code의 호출 성공이나 심사 독립성을 증명하지는 않습니다.**

### 자주 발생하는 오류

- `.agents/`에 Agent가 보이지 않음: Claude Code 기준으로 `.claude/agents/`를 확인하세요. `.agents/skills/`는 다른 용도입니다.
- `.claude/agents/`도 없음: 강의 폴더에서 `plan`·`install`이 실제 실행됐는지, 지정한 사본 경로가 맞는지 확인하세요.
- 다른 이름의 기존 Agent 충돌: 덮어쓰지 않고 수동으로 차이를 검토합니다.
- 9개 파일이 있는데 호출되지 않음: 프로젝트 루트, YAML frontmatter, 정확한 Agent 이름, 세션 재시작, 실행 권한을 확인합니다.
- Python이 없음: 환경을 임의로 바꾸지 않고 상태를 '미실행'으로 기록합니다.

## 전사문 근거

`Ch01-02`: 4개 역할과 책임 분담 / `Ch02-01`~`Ch02-04`: 네 역할의 생성·호출·검증 / `Ch03-01`: 충돌·중단·인계 / `Ch03-02`: 다섯 리뷰어, 총 9개 정의. 원전사의 `.cloud` 표기는 인식 오류 가능성이 있으므로 실행 경로는 공식 Claude Code 문서인 https://code.claude.com/docs/en/sub-agents 를 따릅니다.
