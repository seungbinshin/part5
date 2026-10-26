# Part 5 · 기존 AI Wiki에 연구 역할과 검토 흐름 더하기

Part 4까지 완료한 AI Wiki를 전제로 하는 한국어 정적 강의안입니다. **배울 점**, **실습**, **개인 프로젝트 사례**를 큰 탭으로 구분합니다. 실습은 Wiki 사본에 필요한 파일만 추가하며 기존 자료·Skill·규칙을 덮어쓰지 않습니다.

개인 프로젝트 사례는 필수 실습과 분리한 선택 읽기입니다. GPU CCWS·SWL 실험, HexaHarness, DRAM ATLAS 세 사례를 짧은 카드로 보고 관심 있는 과정만 펼칩니다. 과거 보고와 미확인 결과, AI DRAM Wiki에 적용할 제안을 구분했습니다. 원본 프로젝트를 이번에 재실행하거나 성능을 측정한 자료는 아닙니다.

기존 게시 저장소: [seungbinshin/part5](https://github.com/seungbinshin/part5). 현재 세 사례 추가본은 사용자 지시에 따라 로컬에서만 준비했으며 원격에 게시하지 않았습니다. [강의안 파일](https://github.com/seungbinshin/part5/blob/main/index.html)과 [전사문 파일](https://github.com/seungbinshin/part5/blob/main/transcripts.html)은 아래 방법으로 내려받아 엽니다.

## 읽기

- `index.html`을 브라우저에서 열면 됩니다. 라이브러리 설치나 API 키가 필요하지 않습니다.
- GitHub에서 **Code → Download ZIP**을 선택하고 압축을 푼 뒤 엽니다. `index.html`만 따로 내려받지 말고 `assets/`, `practice/`, `transcripts/` 등 전체 폴더를 함께 보관합니다.
- `transcripts.html`에는 기존 전사문 8개의 원문과 읽기용 요약이 있습니다.
- `practice/UPGRADE.md`에는 사본 만들기, 변경 예정 목록, 추가, 검토, 인계, 원복 절차가 있습니다.
- `docs/sources.md`는 출처·확인일·기술 설명의 차이·윤문 범위를 기록합니다.
- [검증 기록과 화면](docs/validation.md)에서 실습 테스트와 브라우저 확인 범위를 볼 수 있습니다.

복사 버튼이 로컬 파일에서 제한되면 코드가 선택됩니다. 직접 복사하거나 이미 있는 Python으로 이 폴더를 로컬에서 열 수 있습니다.

```sh
python3 -m http.server 8000 --bind 127.0.0.1
```

이후 `http://127.0.0.1:8000`으로 접속합니다. 다른 프로그램이 해당 포트를 사용하면 다른 포트를 선택합니다. 외부 공개 서버를 만들 필요는 없습니다.

## 파일과 편집

| 파일 | 내용 |
|---|---|
| `src/index.html` | 강의안 본문 원본 |
| `assets/styles.css`, `assets/app.js` | 화면·세 탭·툴팁·복사·작은 실습 |
| `build.py` | 본문·합성 자료·전사문을 정적 HTML로 조립 |
| `data/project-cases.json` | 선정한 개인 프로젝트 3개의 비식별 요약 |
| `project_cases.py` | 사례 형식 검사·HTML 이스케이프·정적 카드 생성 |
| `transcripts/*.txt` | 원문 보존본 8개 |
| `docs/transcript-manifest.json` | 원문 출처·해시·타임스탬프 범위 |
| `practice/` | 기존 Wiki 사본에 추가할 작은 합성 실습·검증기·원복 도구 |

본문 수정 후 `python3 build.py --require-project-cases`를 실행합니다. 전사문 해시가 다르거나 검토된 사례가 정확히 세 개가 아니면 빌드가 중단됩니다. 사례의 근거·민감정보 검토는 사람이 수행하며, 검증기는 그 판단을 대신하지 않습니다. [사례 편집 기준](docs/project-cases-editing.md)을 함께 확인하세요. 툴팁과 탭은 키보드로 사용할 수 있고, 작은 화면에서는 목차 버튼을 누릅니다. 주요 용어 설명은 마우스·포커스·탭으로 열리고 Escape로 닫힙니다.

## 범위

전사문은 `HyResearchAgent/part3/transcripts/part5_*`의 기존 자료입니다. 이번에 음성을 새로 전사하지 않았고 원음 대조도 하지 않았습니다. 불확실한 자동전사 표현은 별도 기록에 남겼습니다.

합성 실습에는 실제 연구 성과·실험 결과·모델 실행 결과를 사용하지 않았습니다. 선택 모델 호출은 기존에 사용하는 환경에서만 진행하며 비용·지연은 미측정입니다.

현재는 로컬 검토본이며 추가본의 원격 게시는 보류했습니다. 저장소 공개 전환은 사용자 의도임을 확인했지만 이번 작업에서 visibility·원격 파일·Pages 설정은 변경하지 않았습니다. GitHub는 저장소의 HTML을 수업 화면으로 바로 렌더링하지 않으므로 저장소를 내려받아 `index.html`을 열어 주세요. 기존 운영 Wiki의 원격 저장소는 변경하지 않습니다.
