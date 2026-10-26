"""검토가 끝난 비식별 사례 요약만 정적 HTML로 렌더링한다."""
from datetime import date
from html import escape
import re


LIMITS = {
    "title": 100, "summary": 300, "context": 600, "approach": 600,
    "outcome": 400, "lesson": 600, "limits": 400,
    "evidence_status": 200, "transfer": 600,
}
CATEGORIES = ("연구·검증", "도구·자동화", "교육·콘텐츠", "제품·사용경험")


def text(value, name, limit):
    if not isinstance(value, str) or not value.strip() or value != value.strip() or len(value) > limit:
        raise ValueError(f"{name}: 앞뒤 공백 없는 1~{limit}자 텍스트가 필요합니다.")
    return value


def validate(payload, require_cases=False):
    if not isinstance(payload, dict) or set(payload) != {"version", "cases"} or type(payload["version"]) is not int or payload["version"] != 1:
        raise ValueError("사례 데이터는 version=1과 cases만 포함해야 합니다.")
    cases = payload["cases"]
    if not isinstance(cases, list):
        raise ValueError("cases는 목록이어야 합니다.")
    if require_cases and not cases:
        raise ValueError("게시 보류: 검토가 끝난 개인 프로젝트 사례가 없습니다.")
    ids = set()
    required = set(LIMITS) | {"id", "tags", "review", "category"}
    for case in cases:
        if not isinstance(case, dict) or not required <= set(case) or set(case) - required - {"period"}:
            raise ValueError("사례의 필수 필드가 빠졌거나 허용하지 않은 필드가 있습니다.")
        ident = case["id"]
        if not isinstance(ident, str) or not re.fullmatch(r"[a-z][a-z0-9-]{0,59}", ident) or ident in ids:
            raise ValueError("사례 id는 중복 없는 영문 소문자·숫자·하이픈이어야 합니다.")
        ids.add(ident)
        if case["category"] not in CATEGORIES:
            raise ValueError("사례 범주를 확인하세요.")
        for name, limit in LIMITS.items():
            text(case[name], name, limit)
        if "period" in case:
            text(case["period"], "period", 60)
        tags = case["tags"]
        if not isinstance(tags, list) or not 1 <= len(tags) <= 4:
            raise ValueError("tags는 연결 개념 1~4개를 담아야 합니다.")
        for tag in tags:
            text(tag, "tag", 30)
        if len(tags) != len(set(tags)):
            raise ValueError("같은 사례에 중복 태그를 넣을 수 없습니다.")
        review = case["review"]
        if not isinstance(review, dict) or set(review) != {"evidence_checked", "privacy_checked", "checked_on"}:
            raise ValueError("review에는 근거·개인정보 검토 여부와 확인일만 넣습니다.")
        if review["evidence_checked"] is not True or review["privacy_checked"] is not True:
            raise ValueError("게시 보류: 근거 확인과 개인정보 검토가 모두 끝나야 합니다.")
        checked = review["checked_on"]
        if not isinstance(checked, str) or not re.fullmatch(r"\d{4}-\d{2}-\d{2}", checked):
            raise ValueError("확인일은 YYYY-MM-DD 형식이어야 합니다.")
        if date.fromisoformat(checked) > date.today():
            raise ValueError("미래 날짜를 검토 완료일로 기록할 수 없습니다.")
    if cases and len(cases) != 3:
        raise ValueError("선정 사례는 정확히 3개여야 합니다.")
    return cases


def render(cases):
    if not cases:
        return '<div class="case-empty case-preparing"><h2>사례를 정리하고 있습니다</h2><p>함께 진행한 프로젝트를 확인한 뒤 이곳에 추가합니다. 아직 확정된 사례는 없습니다.</p></div>'
    html = ['<p class="small case-count">연구 지표 · 도구 검증 · 교육 모델을 살펴보는 세 사례입니다. 관심 있는 과정만 펼쳐 읽으세요.</p>', '<ul id="case-list" class="case-list">']
    for case in cases:
        heading = 'case-heading-' + case['id']
        html.append(f'<li class="case-item" aria-labelledby="{heading}"><div class="case-meta"><span class="case-category">{escape(case["category"])}</span>')
        html += [f'<span class="case-tag">{escape(tag)}</span>' for tag in case['tags']]
        if case.get('period'):
            html.append(f'<span class="small case-period">{escape(case["period"])}</span>')
        html.append(f'</div><h2 id="{heading}">{escape(case["title"])}</h2><p class="case-summary">{escape(case["summary"])}</p><p class="case-evidence">{escape(case["evidence_status"])}</p><details><summary aria-label="{escape(case["title"], quote=True)}: 과정과 배울 점">과정·배울 점·한계</summary><div class="detail case-detail"><dl>')
        for name, label in [('context', '문제'), ('approach', '해결을 시도한 과정'), ('outcome', '당시 기록에서 확인한 결과'), ('lesson', '배울 점'), ('transfer', '다른 연구 작업에서 참고한다면'), ('limits', '한계와 미확인 사항')]:
            html.append(f'<dt>{label}</dt><dd>{escape(case[name])}</dd>')
        html.append(f'</dl><p class="small">사례 확인일 {case["review"]["checked_on"]}</p></div></details></li>')
    html.append('</ul>')
    return ''.join(html)
