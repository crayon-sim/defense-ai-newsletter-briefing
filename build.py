"""Build a self-contained archive index and retain the original briefing files."""
import argparse
from datetime import date
from html.parser import HTMLParser
import json
from pathlib import Path
import re
import shutil
from urllib.parse import quote

ROOT = Path(__file__).resolve().parent


class StaticBrief(HTMLParser):
    """Read slide boundaries and visible text without executing the document."""
    def __init__(self):
        super().__init__(convert_charrefs=True)
        self.title = ''
        self.sections = []
        self.heading = ''
        self.in_title = False
        self.ignored = None
        self.parts = []
        self.lines = []

    def line(self):
        line = ' '.join(''.join(self.parts).split())
        if line:
            self.lines.append(line)
        self.parts.clear()

    def section(self):
        self.line()
        if self.heading or self.lines:
            self.sections.append((self.heading, self.lines))
        self.heading = ''
        self.lines = []

    def handle_starttag(self, tag, attrs):
        if self.ignored:
            return
        if tag in ('script', 'style', 'noscript', 'template', 'svg'):
            self.ignored = tag
        elif tag == 'title':
            self.in_title = True
        elif tag in ('h1', 'h2', 'section') or 'slide' in (dict(attrs).get('class') or '').split():
            self.section()
        elif tag in ('p', 'li', 'br', 'div', 'article'):
            self.line()

    def handle_endtag(self, tag):
        if self.ignored:
            if self.ignored == tag:
                self.ignored = None
            return
        if tag == 'title':
            self.in_title = False
        elif tag in ('h1', 'h2'):
            self.heading = ' '.join(''.join(self.parts).split())
            self.parts.clear()
        elif tag in ('p', 'li', 'div', 'h3', 'h4', 'tr', 'article'):
            self.line()

    def handle_data(self, data):
        if self.in_title:
            self.title += data
        elif not self.ignored:
            self.parts.append(data)


def structured(data):
    meta = data['META']
    groups = data['GROUPS']
    slides = [dict(kind='cover', label='표지', title=meta['title'], lead=meta['issue'], note=meta.get('scope', '')),
              dict(kind='summary', label='주간 요약', title='이번 주 핵심 요지', lines=data['BLUF'])]
    for group in groups:
        articles = [(n, data['A'][str(n)]) for n in group['items']]
        slides.append(dict(kind='group', label='유형 ' + group['code'], title=group['name'],
                           lead=group['msg'], lines=[data.get('LABELS', {}).get(str(n), a['label']) for n, a in articles]))
        for n, a in articles:
            slides.append(dict(kind='article', label=group['short'], title=a['label'], lead=a['one'],
                               note=a.get('src', ''), article=n, detail=[
                                   ['국내외 동향', a.get('trend', [])], ['우리 군 시사점', a.get('impl', [])],
                                   ['아카이브 연계 추이', [f'제{r[0]}호 · {r[1]} · {r[2]}' for r in a.get('related', [])]],
                                   ['추이', [a['trendline']] if a.get('trendline') else []]]))
    for key, title in [('RECOMMEND', '우리 군 정책 과제'), ('WATCH', '주요 일정')]:
        if data.get(key):
            slides.append(dict(kind='list', label='종합 브리핑', title=title, pairs=data[key]))
    return dict(title=meta['title'], issue=str(meta['no']), date=meta.get('date', ''), author=meta.get('author', ''),
                scope=meta.get('scope', ''), slides=slides)


def read_issue(path):
    source = path.read_text(encoding='utf-8-sig')
    match = re.search(r'\bconst\s+D\s*=\s*(?=\{)', source)
    data = None
    if match:
        try:
            data, _ = json.JSONDecoder().raw_decode(source[match.end():])
        except ValueError:
            pass
    if isinstance(data, dict) and all(k in data for k in ('META','GROUPS','A','BLUF')):
        issue = structured(data)
    else:
        doc = StaticBrief()
        doc.feed(source)
        doc.close()
        doc.section()
        title = doc.title.strip() or path.stem
        number = re.search(r'제\s*(\d+)\s*호|issue[-_ ]*(\d+)', title + ' ' + path.name, re.I)
        issue_no = next((n for n in number.groups() if n), '') if number else ''
        slides = [dict(kind='cover', label='표지', title=title)]
        slides.extend(dict(kind='list', label='본문', title=heading or title, lines=lines)
                      for heading, lines in doc.sections if lines or (heading and heading != title))
        if len(slides) == 1:
            slides[0]['lead'] = '원본 HTML에서 브리핑을 열 수 있습니다.'
        issue = dict(title=title, issue=issue_no, date='', author='', scope='', slides=slides)
    issue['file'] = 'briefings/' + quote(path.name)
    issue['id'] = path.name
    return issue


def sort_key(issue):
    match = re.search(r'(20\d{2})\D+(\d{1,2})\D+(\d{1,2})', issue['date'] or issue['id'])
    day = date(*map(int, match.groups())).toordinal() if match else 0
    return (int(issue['issue']) if issue['issue'].isdecimal() else -1, day, issue['id'])


def build(out):
    out = out.resolve()
    src = ROOT / 'briefings'
    if out in (ROOT, src) or src in out.parents or out in ROOT.parents:
        raise ValueError('별도 출력 폴더를 지정하세요.')
    paths = [p for p in src.iterdir() if p.is_file() and p.suffix.lower() in ('.html','.htm')]
    issues = sorted([read_issue(p) for p in paths], key=sort_key, reverse=True)
    out.mkdir(parents=True, exist_ok=True)
    shutil.copytree(src, out / 'briefings', dirs_exist_ok=True)
    template = (ROOT / 'viewer' / 'index.html').read_text(encoding='utf-8')
    payload = json.dumps(issues, ensure_ascii=False).replace('<', r'\u003c')
    (out / 'index.html').write_text(template.replace('__BRIEFINGS__', payload), encoding='utf-8')
    print(f'{len(issues)}개 브리핑 · {sum(len(i["slides"]) for i in issues)}장')


if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('--out', type=Path, default=ROOT / 'dist')
    build(parser.parse_args().out)
