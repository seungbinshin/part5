# 선택 확장: 이미 사용하는 모델에 한 번 위임하기

새 계정·결제·플러그인 설치 없이 이미 사용할 수 있는 도구가 있을 때만 진행합니다. 사용량과 요금은 해당 서비스의 현재 계약을 확인합니다. 이 자료를 만든 과정에서는 아래 호출을 실행하지 않았습니다.

처음에는 파일 쓰기 도구를 주지 않고 보고서 JSON을 화면으로만 받으세요. 이 경우 `requested_writes`는 나중에 사람이 저장할 예정 경로를 뜻합니다. 프롬프트의 금지 문구만으로 운영체제 권한이 제한되지는 않습니다. 실제 에이전트로 등록한다면 사용 도구의 읽기 범위와 파일 쓰기 권한도 따로 제한해야 합니다.

아래 요청 뒤에 `manuscript.txt`, `case-data.json`, `source-results.csv`, `source-notes.txt`, `review-template.json`의 내용을 붙입니다. 교육용 합성 자료만 사용하고 개인 연구 파일은 추가하지 않습니다.

```text
writing-reviewer 역할로 다음 합성 초안을 검토해 주세요.

입력: manuscript.txt의 C1~C3, case-data.json의 E1~E2와 역할 계약,
근거 대장이 가리키는 source-results.csv와 source-notes.txt,
review-template.json의 출력 형식. 입력 버전은 synthetic-v1입니다.
독자: 주장과 근거의 범위를 확인하려는 연구자.

각 주장에 대해 근거 대장부터 원본 파일까지 확인하고 논리적 비약과 누락을 점검하세요.
classification은 supported_within_scope, unsupported_generalization,
insufficient_evidence 중 하나로 적으세요. reason에는 대조한 조건을,
next_check에는 추가로 확인할 항목이나 연구자가 고를 방향을 적으세요.

원고·입력 파일을 수정하거나 대체 문장을 쓰지 마세요.
새 수치·인용·실험 결과를 만들지 말고 외부 검색이나 실험도 하지 마세요.
자료가 없거나 버전이 다르면 작업을 멈추고 무엇이 필요한지 보고하세요.
최종 채택·보류는 연구자가 정합니다. approval_status는 awaiting-human입니다.

파일에 쓰지 말고 템플릿 형식의 JSON 보고서 하나만 반환하세요.
requested_writes에는 사람이 저장할 outputs/review.json만 적으세요.
```

받은 보고서를 `outputs/review.json`에 저장하고 검사합니다. 오류가 나면 곧바로 재호출하지 말고 오류 항목과 원문부터 대조합니다. 이유와 다음 확인 항목은 사람이 읽어 판단합니다. 모델이 정답 분류를 맞혀도 문장이 근거를 잘 설명했는지는 별개입니다.
