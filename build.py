#!/usr/bin/env python3
"""로컬 원문·합성 자료로 정적 HTML을 만든다. 네트워크나 외부 패키지를 쓰지 않는다."""
from pathlib import Path
from html import escape
import json
import re
import hashlib
import argparse
import tempfile
from project_cases import validate, render

ROOT = Path(__file__).resolve().parent

def write_html(path, content):
    # 완성된 파일로 교체해 미리보기나 다른 읽기가 부분 HTML을 보지 않게 한다.
    staging = None
    try:
        with tempfile.NamedTemporaryFile(mode='w', encoding='utf-8', dir=path.parent, delete=False) as temporary:
            staging = Path(temporary.name)
            temporary.write(content)
        staging.replace(path)
    finally:
        if staging is not None:
            staging.unlink(missing_ok=True)

parser = argparse.ArgumentParser(description=__doc__)
parser.add_argument('--require-project-cases', action='store_true', help='게시 전 필수: 검토가 끝난 개인 프로젝트 사례가 없으면 중단')
options = parser.parse_args()
try:
 cases = validate(json.loads((ROOT/'data/project-cases.json').read_text()), options.require_project_cases)
except (ValueError, OSError) as error:
 parser.exit(1, str(error)+'\n')
manifest = json.loads((ROOT / 'docs/transcript-manifest.json').read_text())
summaries = {
 'Ch01-01': 'Skill의 절차와 Subagent의 책임을 구분하고, 목표·입력·제약·출력·중지 조건을 위임 명세서에 적습니다.',
 'Ch01-02': '문헌 검토·실험 계획·초안 작성·초안 검토의 책임을 나눕니다. 역할마다 입력과 판단 범위를 정하고 공용 파일의 갱신을 조율합니다.',
 'Ch02-01': '문헌 검토 역할의 호출 조건과 결과 위치를 정합니다. 기존 paper-reading 절차를 재사용하며 같은 답의 재생성과 원문 검증을 구분합니다.',
 'Ch02-02': '질문·기록·문헌·자원 제약을 보고 실험 후보를 비교합니다. 기록과 제안을 표시하고 순위가 뒤집힐 조건과 승인 필요 항목을 남깁니다.',
 'Ch02-03': '원고 규칙과 근거 대장을 먼저 준비한 뒤 초안을 씁니다. 형식 점검을 통과한 것과 주장의 타당성을 검토한 것은 구분합니다.',
 'Ch02-04': '주장·대장·원본을 대조하고 논리와 독자 흐름을 검토합니다. 리뷰어는 지적을 반환하며 원고 수정과 채택은 연구자가 결정합니다. 시연 초안은 합성 데이터 기반입니다.',
 'Ch03-01': '공유 공간에서 역할이 충돌할 때 중지·보고·승인·인계의 순서를 정합니다. 제안과 실제 변경, 미완료 항목을 구분해 반환합니다.',
 'Ch03-02': '같은 원고를 다섯 관점으로 검토하고 겹침·충돌·고유 지적을 종합합니다. 실제 입력 경로와 원고 버전을 지정하고, 의견의 차이만으로 독립성을 판단하지 않습니다.'
}

parts = ['<!doctype html><html lang="ko"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1"><title>Part 5 · 전사문 원문과 정리</title><link rel="stylesheet" href="assets/styles.css"></head><body><main class="transcript-shell"><a href="index.html">← Part 5 강의안</a><p class="eyebrow">Source notebook · 8 clips</p><h1>전사문 원문과 읽기용 정리</h1><p>기존 Part 5 전사문 8개, 총 1,730줄을 보존했습니다. 아래 요약은 편집자가 작성한 정리이며 새로운 음성 전사가 아닙니다.</p><p class="notice">원음·영상과 대조하지 않았습니다. 자동전사로 의심되는 용어와 시간 간격을 임의로 복원하지 않았습니다. <a href="TRANSCRIPT_NOTES.md">오류 후보와 확인 필요 기록</a> · <a href="docs/transcript-manifest.json">파일별 출처·해시</a></p><nav class="transcript-nav" aria-label="전사문 목차">']
for f in manifest['files']:
 parts.append(f'<a href="#{f["id"]}">{f["id"]}</a>')
parts.append('</nav>')
for f in manifest['files']:
 raw = ROOT / 'transcripts' / (f['id']+'.txt')
 assert hashlib.sha256(raw.read_bytes()).hexdigest() == f['sha256'], '원문 해시가 다릅니다: '+str(raw)
 prefix='c'+f['id'][2:].replace('-','')
 parts.append(f'<section class="transcript-clip" id="{f["id"]}"><h2>{f["id"]} · {escape(f["title"])}</h2><p class="small">{f["first_timestamp"]}–{f["last_timestamp"]} · {f["line_count"]}줄 · 마지막 시각은 파일의 마지막 발화 시작점입니다.</p><div class="summary"><span class="pill design">읽기용 정리 · 편집자</span><p>{summaries[f["id"]]}</p></div><p><a href="transcripts/{f["id"]}.txt" download>원문 TXT 내려받기</a></p><details><summary>타임스탬프 원문 전체 펼치기</summary><div class="detail">')
 for line in raw.read_text().splitlines():
  match=re.match(r'\[(\d{2}:\d{2}:\d{2})\]\s*(.*)',line)
  assert match, '원문 타임스탬프 형식을 확인하세요'
  timestamp,text=match.groups();anchor=prefix+'-'+timestamp.replace(':','')
  parts.append(f'<p class="transcript-line" id="{anchor}"><a class="timestamp" href="#{anchor}">{timestamp}</a>{escape(text)}</p>')
 parts.append('</div></details></section>')
parts.append('<p class="source">출처: HyResearchAgent/part3 · commit '+manifest['commit']+' · 확인 2026-10-26. 원문은 수정하지 않았으며 원음 대비 완전성은 미확인입니다.</p></main><script>function reveal(){const id=decodeURIComponent(location.hash.slice(1));const el=document.getElementById(id);if(!el)return;const detail=el.closest("details");if(detail)detail.open=true;requestAnimationFrame(()=>el.scrollIntoView());}addEventListener("hashchange",reveal);reveal();</script></body></html>')
write_html(ROOT/'transcripts.html', '\n'.join(parts))

data=json.loads((ROOT/'practice/case-data.json').read_text())
expected=json.loads((ROOT/'practice/expected-review.json').read_text())
claims=dict(re.findall(r'^(C\d)\. (.*)$',(ROOT/'practice/manuscript.txt').read_text(),re.M))
labels={'supported_within_scope':'근거의 조건 안에서 지지됨','unsupported_generalization':'근거보다 넓게 일반화함','insufficient_evidence':'판단할 근거가 부족함'}
lab=['<div class="card-grid"><div class="card"><h3>E1 · 같은 조건의 기록</h3><p>가상의 도시 A, 맑은 야간, night-demo 평가 묶음에서 같은 규칙으로 남긴 한 번의 예시 기록입니다. 단위 없는 합성 점수는 기준 모델 60, 후보 A 63입니다.</p><p class="small">원본: source-results.csv의 E1 · 실제 성능·통계적 유의성이 아님</p></div><div class="card"><h3>E2 · 측정 예정 메모</h3><p>후보 B의 속도를 점검할 예정이라고 적혀 있습니다. 지연 시간·비교 조건·실행 장비는 기록되어 있지 않습니다.</p><p class="small">원본: source-notes.txt의 E2</p></div></div><p class="small">위 카드는 위키 사본에 추가하는 동일 자료의 미리보기입니다. 파일에서는 manuscript.txt → case-data.json → 원본 CSV·메모 순서로 대조하세요.</p><form id="review-exercise">']
for i,item in enumerate(expected['findings'],1):
 claim=item['claim_id'];labelid='answer-'+claim
 lab.append(f'<div class="question" data-answer="{item["classification"]}" data-explanation="{escape(item["reason"],quote=True)}"><p><strong>{claim}</strong> · {escape(claims[claim])}</p><label for="{labelid}">{claim} 판정</label><select id="{labelid}" name="{claim}" aria-describedby="feedback-{claim}"><option value="">판정을 선택하세요</option>')
 for key,label in labels.items():lab.append(f'<option value="{key}">{label}</option>')
 lab.append(f'</select><p class="feedback" id="feedback-{claim}"></p></div>')
lab.append('<div class="button-row"><button class="button primary" type="submit">판정 확인</button><button class="button" type="button" id="reset-exercise">다시 해보기</button></div><div class="result" id="review-result" role="status" tabindex="-1"></div></form>')
template=(ROOT/'src/index.html').read_text()
index=re.sub(r'<!-- LAB:START -->.*?<!-- LAB:END -->','<!-- LAB:START -->\n'+''.join(lab)+'\n<!-- LAB:END -->',template,flags=re.S)
index=re.sub(r'<!-- PROJECT_CASES:START -->.*?<!-- PROJECT_CASES:END -->',lambda _: '<!-- PROJECT_CASES:START -->\n'+render(cases)+'\n<!-- PROJECT_CASES:END -->',index,flags=re.S)
index=index.replace('<!-- PROJECT_CASE_COUNT -->', str(len(cases))+'개 사례' if cases else '확인 중')
write_html(ROOT/'index.html', index)
print('Built index.html and transcripts.html. Preserved 8 raw transcript hashes.')
