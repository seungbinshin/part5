# Part 1~5 연속성 및 Part 5 실습 수정 근거

## 범위
- Part 1~2: 메인 AI 작업의 규칙·분해·검증 개념을 소개합니다.
- Part 3: 연구 Wiki의 자료·질문·기록 기반을 마련합니다. Part 3 원전사문은 직접 검증 범위가 제한되며, 후속 강의 회고와 제공 실습 파일로 확인했습니다.
- Part 4: 기존 Wiki 위에 `paper-reading` 및 `experiment-log` Skill을 만들고 검수합니다. `nufrancis/hyresearchagent`와 `HyResearchAgent/part3/course-materials/part-04`의 실습을 대조했습니다.
- **Part 5의 새 범위:** 연구 Subagent 4개 정의와 호출, 다섯 관점의 심사자 5개, 역할 충돌 방지, 인계 및 종합 검토.

## 기존 문제
기존 `practice/project-prompts.md`는 역할 계약과 근거·계획·초안·검토를 요구했지만 Claude Code의 프로젝트 Subagent 정의 파일 생성·등록 단계를 명시하지 않았습니다. `practice/upgrade_wiki.py`는 `part5-lab/`의 합성 연습 자료만 추가하며 `.agents/` 또는 `.claude/agents/`를 만들지 않습니다. 따라서 해당 절차만 실행하면 Agent Markdown 파일은 생성되지 않습니다.

## 변경
1. 강의의 3개 실습 프롬프트에 4개 Agent 등록 → 실제 위임 → 리뷰어 5개 등록 및 심사 순서를 추가합니다.
2. `practice/agent-definitions/`에 9개 정의와 `practice/install_agents.py`의 격리 사본 등록·검증 도구를 추가합니다.
3. `practice/AGENT_SETUP.md`에서 Skill과 Agent 경로, 실제 호출과 파일 검증을 구별합니다.
4. 강의안의 원전사문·합성 리뷰 검사기·기존 Wiki·기존 Skill은 변경하지 않습니다.

## 전사문 확인
`transcripts/Ch01-02.txt` 01:49, 09:12 / `Ch02-01.txt`~`Ch02-04.txt`의 Agent 생성·검토 / `Ch03-01.txt` 03:48~05:11 / `Ch03-02.txt` 01:21~04:48, 15:03~15:13.

## 검증 한계
정의 파일 9개의 존재와 YAML·해시 비교는 정적 검사입니다. 실습 수행자의 Claude Code 환경에서 위임을 실제 실행해 본 결과는 아닙니다. 특정 파일을 읽지 말라는 지시와 실제 도구 접근 제한도 별도입니다.
