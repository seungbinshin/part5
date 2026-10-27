# Part 5 출처와 편집 기준

확인일: 2026-10-26. 공개 보완 자료의 1차 확인 기준은 06:53 UTC / 15:53 KST다. 원강의·제품 문서·저자 권고·연구자 실험·이 교재의 설계 판단을 구분한다.

## 원강의

사용자가 지정한 원본은 `HyResearchAgent/part3`의 `transcripts/part5_*`다. 기준 커밋은 `985c36314569e92c8ad76076dcda96e5708b2ace`다. 기존 TXT 8개 1,730줄을 그대로 보존했으며 새 음성 전사라고 표시하지 않는다.

- [원본 저장소](https://github.com/HyResearchAgent/part3/tree/985c36314569e92c8ad76076dcda96e5708b2ace/transcripts)
- [로컬 원문과 편집 요약](../transcripts.html)
- [파일별 해시·시각 범위](transcript-manifest.json)
- [전사 오류 후보와 확인 필요](../TRANSCRIPT_NOTES.md)

타임스탬프는 발화 시작점이다. 마지막 시각을 영상의 정확한 길이라고 부르지 않는다. 원음과 대조하지 않아 자동전사 오류와 누락 없는 완전성은 확인되지 않았다. 특히 Ch02-01의 15:10→15:43, Ch03-01의 06:17→06:47 간격은 원문대로 남겼다. 불명확한 데이터셋·파일명·권고 문구를 문맥만으로 확정하지 않았다.

원본의 `course-materials/part-05/practice-files/`에서 역할표·README·역할 정의·운영 규칙을 교차 확인했다. 다음 차이는 본문에서 드러냈다.

- `agents/writing-reviewer.md`의 tools에는 Write, Edit가 있다. 본문의 경로 금지를 기계적인 접근 차단으로 단정하지 않는다.
- `agents/experiment-planner.md`는 비용 근거가 없으면 산정 불가로 남기도록 정한다. 전사의 추정 허용 설명과 구분한다.
- `rules/manuscript.md`의 분량·섹션 수는 강의 예제 규칙이며 일반적인 논문 규격이 아니다.
- Ch02-04 06:03–06:15는 시연 초안이 합성 데이터에 기반했다고 밝힌다. 시연 수치·분량·지적 건수를 우리의 실측 성과로 사용하지 않았다.

## Part 4 기준선과 디자인

[nufrancis/hyresearchagent](https://github.com/nufrancis/hyresearchagent/tree/0457f15c374544337e1b2977836e428d9d687ca6), commit `0457f15c374544337e1b2977836e428d9d687ca6`의 Part 4 안내·템플릿을 참조했다. 두 참고 강의안의 흰 배경, 테라코타 강조, 목차 점·세로 흐름, 가는 구분선, 본문 가독성을 유지하며 HTML·CSS·JS를 새로 작성했다. 외부 폰트나 원본의 삽화는 복제하지 않았다. 시스템에 Pretendard가 있으면 사용하고 없으면 시스템 한글 글꼴로 표시한다.

수업은 Part 4 완료 후 기존 AI Wiki를 업그레이드하는 전제다. 실제 확인한 기존 Wiki는 `skills/paper-reading/SKILL.md`, `skills/experiment-log/SKILL.md`를 일반 절차 문서로 사용한다. 이 파일의 존재는 등록·자동 로딩의 증거가 아니다. Part 4 참고 저장소의 루트 안내는 `.agents/skills/`를, 일부 묶음 안내는 `.claude/skills/`를 사용한다. 실습은 경로를 검사하며 자동으로 기존 설정을 이전하거나 덮어쓰지 않는다.

핵심 실습은 학습자의 기존 질문·근거·계획 경로를 먼저 매핑하고 격리 사본의 계획된 새 경로에만 산출물을 만든다. 기존 논문·Skill·규칙·index·log·JSON 저장소는 유지한다. 구조가 모호하거나 자료가 없으면 멈춘다. 같은 입력의 재실행은 기존 결과를 재사용하며 중복 문서·기능을 만들지 않는다. 별도 에이전트 등록이나 우리 Wiki 스키마 이식은 요구하지 않는다. part5-lab 고정 합성 예제와 readonly-reviewer.md는 선택 참고 자료다.

## 현대적 보완

| 출처 | 발행·버전 | 수업에 연결한 범위 | 근거 성격 |
|---|---|---|---|
| [Building effective agents](https://www.anthropic.com/research/building-effective-agents) | 2024-12-19 | 고정 워크플로와 자율 에이전트 구분, 단순한 구조부터 비교 | 공급사 저자의 설계 권고 |
| [How we built our multi-agent research system](https://www.anthropic.com/research/multi-agent-research-system) | 2025-06-13 | 독립 탐색 병렬화와 의존 작업의 한계, 조율·토큰 비용 | 공급사 개발 사례·자체 평가 |
| [Effective context engineering for AI agents](https://www.anthropic.com/research/effective-context-engineering-for-ai-agents) | 2025-09-29 | 필요한 정보와 원문 식별자를 인계에 남기기 | 공급사 저자의 설계 권고 |
| [Why Do Multi-Agent LLM Systems Fail?](https://arxiv.org/abs/2503.13657v3) | 최초 2025-03-17 / v3 2025-10-26 | 설계·불일치·과업 검증의 실패 분류 | 연구자 분석; 해당 모델·과제 범위 |
| [How we contain Claude across products](https://www.anthropic.com/research/how-we-contain-claude) | 2026-05-25 | 모델 판단과 환경 권한 구분, 외부 자료와 지시 분리 | 공급사 보안 설계 설명 |
| [More Capable, Less Cooperative?](https://arxiv.org/abs/2604.07821v2) | 최초 2026-04-09 / v2 2026-06-04 | 능력과 협력 성과의 차이, 인계 규칙의 필요를 생각하는 선택 읽기 | 제한된 턴 기반 실험 |
| [Claude Code Subagents](https://code.claude.com/docs/en/sub-agents) | 확인 2026-10-26 / 상시 갱신 문서 | 시작 컨텍스트·fork·도구 제한·등록 경로 | 현재 제품 문서 |

이 교재의 적용 제안은 출처 논문의 실험 결과가 아니다. 에이전트 수·병렬화로 얻는 시간·비용·품질 개선을 직접 측정하지 않았다. 공급사 글의 큰 향상률이나 토큰 배수를 수업 성과로 옮기지 않았다.

## 실습과 윤문

`practice/project-prompts.md`는 자기 프로젝트에 적용하는 핵심 경로다. `practice/`에 남긴 고정 원고, 근거, 사전 검토 결과는 선택 연습용 합성 예제다. 검증기는 정해진 작은 사례의 형식·참조·선언된 경계·원본 해시를 검사한다. 이유의 의미, 실제 연구의 진실성, 모델 품질, 운영체제 권한 격리를 자동으로 보증하지 않는다. 사전 해설은 모델 출력이 아니다. 프롬프트 개편의 실제 실행 확인 범위는 `validation.md`에 기록하며, 모델별 성능·소요 시간·비용은 검증하지 않았다.

윤문은 공식 [im-not-ai](https://github.com/epoko77-ai/im-not-ai)의 v2.3.2, commit `b37e0206d31fffd9149bf57168d4d62eb2086bee`에서 `SKILL.md`, `quick-rules.md`, `diagnosis-rules.md`, `humanize-finalizer.md` 원문을 읽고 텍스트 규칙으로 적용했다. 의미·수치·출처·부정·불확실성을 보존하고 과장·번역투·반복 표현을 국소 수정했다. 원문 TXT는 윤문하지 않는다.

원본 플러그인이 설치된 것은 아니다. 실행 스크립트·정량 shim·공식 게이트는 사용하지 않으므로 변경률·등급·공식 파이프라인 통과를 주장하지 않는다. [MIT 라이선스](im-not-ai-LICENSE.txt)를 보관했다.

## 개인 프로젝트 사례

2026-10-26에 확인한 과거 대화에서 GPU CCWS·SWL 실험, HexaHarness, DRAM ATLAS 세 사례를 골랐다. AI DRAM·연구 수업과의 관련성, 다른 작업에도 적용할 교훈, 당시 보고에서 확인한 구현·검증 경험, 민감자료 없이 설명할 수 있는 범위를 기준으로 선정했다. 전체 조사 기록과 제외한 사례는 저장소 밖 로컬 참고 자료로 보존한다.

- GPU CCWS·SWL: 2024년 사용자 실험 보고다. 캐시 미스율과 IPC·병렬성의 관계를 다뤘으며 이번에 실험을 재현하지 않았다.
- HexaHarness: 당시 Linux·macOS·Windows 시험, 새 설치와 원격 해시 확인 보고를 참고했다. 공개 보조 근거는 [v1.0.0 릴리스](https://github.com/seungbinshin/hexaharness/releases/tag/v1.0.0)다. 도구 시험과 실제 모델 품질 향상 여부를 구분하며 이번 재실행·효과 측정은 없다.
- DRAM ATLAS: 공개 자료를 바탕으로 학습 화면·도식을 구현한 보고다. 교육 모델은 실제 DRAM 장비 동작이나 규격 준수 검증이 아니다. 당시 최종 브라우저 QA는 미확인이며 이번에도 원프로젝트를 실행하지 않았다.

AI DRAM Wiki에 옮길 원칙은 수업 적용 제안이다. 원문 대화·운영 로그·비공개 링크·자격 증명·실명·회사 코드·개인 금융자료를 포함하지 않는다. 공식 im-not-ai의 같은 텍스트 규칙으로 세 사례를 윤문하면서 과거 시점·미실행·미확인·부정 표현을 보존했다.

## 현재 게시 범위

사용자가 저장소 공개 전환과 검증된 세 사례 추가본의 게시를 승인했다. 게시 대상은 `seungbinshin/part5`의 `main`이다. 기존 저장소 가시성·Pages·공동작업자 설정은 변경하지 않는다.

참고 강의 저장소에는 명시적 LICENSE 파일이 없었으므로 원강의 자료의 공개 재배포 권한이 확인된 것으로 표시하지 않는다. 기존 운영 Wiki의 원격 저장소에도 push하지 않는다.

## 실제 Wiki 적용 예시와 프롬프트 개편

실습 탭에는 별도 AI DRAM Wiki의 로컬 구현 `556594c`를 대표 사례로 요약했다. 코드·최종 검사 기록을 대조했으며 운영 배포·새 하드웨어 측정으로 표현하지 않았다. [근거와 한계](wiki-applied-example.md)를 참조한다. 원문 개인 세션·회사 자료·원로그는 복제하지 않았다. 세 단계의 프롬프트와 전후 산출물을 연결하고, 학습자의 기존 질문·구조에 맞춰 만든 산출물과 인계를 검사하도록 변경했다. 근거 연결 누락·낡은 해시의 결함 주입 검사와 반복 실행 시 중복 방지를 완료 기준에 포함했다. 개인 프로젝트 세 사례는 겪은 문제와 해결 과정을 공유하는 선택 읽기다.

## 원전사문 기반 강의 개요

2026-10-27에 첫 탭을 로컬 준비했다. Part 5 원전사문 8개와 Part 4 원전사문 8개를 직접 비교하고, Part 1·2의 관련 구간으로 역할·검증 개념이 앞서 소개됐는지 확인했다. Part 4 공개 합본은 원 TXT 8개와 같은 내용이므로 공개 고정 커밋의 행 링크를 제공한다. Part 3 자체 전사문은 확인하지 못했으며, 해당 내용은 Part 4·5의 회고 범위로 표시했다. [파일·시각·비교 근거](overview-evidence.md)를 따른다.

개요는 원강의의 기대효과와 전사에 기록된 시연을 구분한다. 이 문서의 현대적 보완, 우리 Wiki 업그레이드, 실습 개편·개인 사례를 원강의의 성과로 사용하지 않았다. 원음·영상·실행 환경은 재검증하지 않았다.
