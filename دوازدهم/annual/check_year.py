"""QA for the grade-12 year: arithmetic, calendar, page ranges and box sanity."""
import json
import re
from pathlib import Path

BASE = Path(__file__).resolve().parents[1]
MANIFEST = json.loads((BASE / 'annual/year_manifest.json').read_text())
FA = str.maketrans('۰۱۲۳۴۵۶۷۸۹', '0123456789')
MIN_PAGES = 4
RNG = re.compile(r'ص\s*([۰-۹]+)(?:\s*[–-]\s*([۰-۹]+))?')
MRNG = re.compile(r'ریاضی\s*([۱۲۳])\s*ص\s*([۰-۹]+)(?:\s*[–-]\s*([۰-۹]+))?')
FULL = {10: {'bio': 111, 'physics': 120, 'chem': 122, 'math': 170},
        11: {'bio': 152, 'physics': 104, 'chem': 123, 'math': 166},
        12: {'bio': 124, 'physics': 125, 'chem': 123, 'math': 148}}


def grade_of(label):
    for key in ('دوازدهم', 'یازدهم', 'دهم'):
        if key in label:
            return {'دوازدهم': 12, 'یازدهم': 11, 'دهم': 10}[key]
    return 12


def parse(text, grade=12):
    """[(grade, a, b)] for the book(s) named in one topic string."""
    out = []
    if 'ریاضی' in text and 'ریاضی۳' in text or 'ریاضی۲' in text or 'ریاضی۱' in text:
        for book, a, b in MRNG.findall(text):
            g = {1: 10, 2: 11, 3: 12}[int(book.translate(FA))]
            out.append((g, int(a.translate(FA)), int((b or a).translate(FA))))
    else:
        for a, b in RNG.findall(text):
            out.append((grade, int(a.translate(FA)), int((b or a).translate(FA))))
    return out


def main():
    report = {'plans': 0, 'hours': 0, 'tests': 0, 'pages': 0, 'boxes': 0,
              'issues': [], 'coverage': {}, 'weeks': {}}
    covered = {g: {s: set() for s in FULL[g]} for g in FULL}
    previous_end = None
    for entry in MANIFEST:
        meta = json.loads((BASE / 'data' / (entry['id'] + '.json')).read_text())
        report['plans'] += 1
        report['pages'] += meta['pages']
        days = meta['days']
        if len(days) != meta['weeks'] * 6:
            report['issues'].append((entry['id'], 'day count'))
        for w in range(meta['weeks']):
            week = days[w * 6:(w + 1) * 6]
            if [d['name'] for d in week] != ['شنبه', 'یکشنبه', 'دوشنبه', 'سه‌شنبه', 'چهارشنبه', 'پنجشنبه']:
                report['issues'].append((entry['id'], f'week {w + 1} day order'))
            if [d['iso'] for d in week] != [d['iso'] for d in sorted(week, key=lambda x: x['iso'])]:
                report['issues'].append((entry['id'], f'week {w + 1} dates not ascending'))
            if len({d['iso'] for d in week}) != 6:
                report['issues'].append((entry['id'], f'week {w + 1} repeated date'))
        hours = sum(d['hours'] for d in days)
        tests = sum(d['tests'] for d in days)
        if (hours, tests) != (meta['hours'], meta['tests']):
            report['issues'].append((entry['id'], 'totals do not add up'))
        report['hours'] += hours
        report['tests'] += tests
        for day in days:
            if sum(b['hours'] for b in day['boxes']) != day['hours']:
                report['issues'].append((entry['id'], f"{day['name']} hours"))
            if not day['boxes']:
                report['issues'].append((entry['id'], f"{day['name']} empty"))
            seen = set()
            for b in day['boxes']:
                report['boxes'] += 1
                if b['topic'] in seen:
                    report['issues'].append((entry['id'], f"{day['name']} repeated box"))
                seen.add(b['topic'])
                if b['kind'] == 'test' and (b['tests'] == 0 or b['hours'] == 0):
                    report['issues'].append((entry['id'], f"{day['name']} empty test box"))
                if b['kind'] == 'test' and b['tests'] > 20 * b['hours']:
                    report['issues'].append((entry['id'], f"{day['name']} too many tests per hour"))
                if b['kind'] in ('review', 'study'):
                    for g, a, bb in parse(b['topic'], grade_of(b['subject'])):
                        if bb - a + 1 < MIN_PAGES and bb - a + 1 < FULL[g][{'زیست': 'bio'}.get(b['subject'].split()[0], b['subject'].split()[0])]:
                            report['issues'].append((entry['id'], f"{b['subject']} short box p{a}-{bb}"))
                        if b['subject'].split()[0] in ('زیست', 'فیزیک', 'شیمی'):
                            key = {'زیست': 'bio', 'فیزیک': 'physics', 'شیمی': 'chem'}[b['subject'].split()[0]]
                            covered[g][key].update(range(a, bb + 1))
                        else:
                            covered[g]['math'].update(range(a, bb + 1))
        if previous_end and meta['start'] <= previous_end:
            report['issues'].append((entry['id'], 'overlapping blocks'))
        previous_end = meta['end']
        report['weeks'][entry['id']] = meta['weeks']
    for g in FULL:
        for subject, pages in FULL[g].items():
            missing = sorted(set(range(1, pages + 1)) - covered[g][subject])
            report['coverage'][f'{subject}{g}'] = missing
    report['hours_total'] = report['hours']
    (BASE / 'annual/YEAR_QA.json').write_text(json.dumps(report, ensure_ascii=False, indent=1) + '\n')
    print('plans', report['plans'], 'pages', report['pages'], 'hours', report['hours'],
          'tests', report['tests'], 'boxes', report['boxes'])
    print('issues', len(report['issues']))
    for issue in report['issues'][:20]:
        print('  ', issue)
    for key, missing in report['coverage'].items():
        if missing:
            print('uncovered', key, len(missing), missing[:12], '...' if len(missing) > 12 else '')


if __name__ == '__main__':
    main()
