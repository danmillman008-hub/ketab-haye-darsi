"""Minimal debug pass over the approved grade-12 plans.

Nothing about the shape of the year is redesigned here. The only edits are the
two the user asked for:

1. no tiny `درسنامه` box: a study box that covers one or two printed pages — and
   a chemistry chapter cut into three or more short pieces inside one week — is
   folded into the week's main study box of the same subject, and its slot
   becomes a test box on the same pages;
2. maths and physics test boxes carry the whole studied scope as their title and
   keep the narrow former title as a grey «* ترجیحاً:» line under it.

The source is `annual/data` (the files behind `برنامه تحصیلی/`); the output is a
copy under `دوازدهم/`, so the published programme is never touched.
"""
import json
import re
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
BASE = Path(__file__).resolve().parents[1]
SRC = ROOT / 'annual/data'
DST = BASE / 'annual/data'
FA = str.maketrans('۰۱۲۳۴۵۶۷۸۹', '0123456789')
RNG = re.compile(r'ص\s*([۰-۹]+)(?:\s*[–-]\s*([۰-۹]+))?')
MATHY = ('ریاضی', 'فیزیک')
RATE = {'زیست': 10, 'شیمی': 12, 'ریاضی': 15, 'فیزیک': 15}
TEST_DETAIL = {
    'زیست': ' تست آموزشی + تحلیل همهٔ گزینه‌ها',
    'شیمی': ' تست مرتبط + تحلیل کامل',
    'ریاضی': ' تست + تحلیل',
    'فیزیک': ' تست + تحلیل',
}


def fa(x):
    return str(x).translate(str.maketrans('0123456789', '۰۱۲۳۴۵۶۷۸۹'))


def ranges(topic):
    out = []
    for a, b in RNG.findall(topic):
        a, b = int(a.translate(FA)), int((b or a).translate(FA))
        out.append((a, b))
    return out


def span(topic):
    covered = set()
    for a, b in ranges(topic):
        covered.update(range(a, b + 1))
    return len(covered)


def family(subject):
    for key in RATE:
        if subject.startswith(key):
            return key
    return None


def is_study(box):
    return box['tests'] == 0 and box['subject'] != 'دروس نهایی' and ranges(box['topic'])


def merge_topic(main_topic, extra_topic):
    """Main title, then the union of the printed pages, as one clean label."""
    head = main_topic.split('؛')[0].strip()
    extra_head = extra_topic.split('؛')[0].strip()
    if extra_head not in head:
        head = head + ' + ' + extra_head
    pages = sorted({p for a, b in ranges(main_topic) + ranges(extra_topic) for p in range(a, b + 1)})
    spans = []
    for p in pages:
        if spans and p == spans[-1][1] + 1:
            spans[-1][1] = p
        else:
            spans.append([p, p])
    main_parts = [seg.strip() for seg in main_topic.split('؛')[1:]]
    extra_parts = [seg.strip() for seg in extra_topic.split('؛')[1:]]
    main_tail = [seg for seg in main_parts if seg.startswith('از ')]
    extra_tail = [seg for seg in extra_parts if seg.startswith('تا ')]
    chapter = []
    ch_num = None
    gs = []
    for seg in main_parts + extra_parts:
        m = re.search(r'فصل\s*([۰-۹]+)', seg)
        if m and ch_num is None:
            ch_num = int(m.group(1).translate(FA))
        for g in re.finditer(r'گفتار[^؛]*', seg):
            gs += [int(n.translate(FA)) for n in re.findall(r'[۰-۹]+', g.group(0))]
    if ch_num is not None:
        label = 'فصل ' + fa(ch_num)
        if gs:
            label += '، گفتار ' + (fa(min(gs)) + '–' + fa(max(gs)) if max(gs) > min(gs) else fa(min(gs)))
        chapter = [label]
    body = 'ص ' + ' و '.join(fa(a) + '–' + fa(b) for a, b in spans)
    if chapter:
        body = '؛ '.join(chapter) + '؛ ' + body
    if main_tail and extra_tail:
        body += '؛ ' + main_tail[-1] + ' ' + extra_tail[-1]
    elif extra_tail:
        body += '؛ ' + extra_tail[-1]
    elif main_tail:
        body += '؛ ' + main_tail[-1]
    return head + '؛ ' + body


def fold_tiny_boxes(plan):
    """1–2 page study boxes (and split-up chemistry chapters) go into the main box."""
    touched = []
    for week in sorted({day['week'] for day in plan['days']}):
        days = [d for d in plan['days'] if d['week'] == week]
        subjects = {}
        for day in days:
            for box in day['boxes']:
                if is_study(box):
                    subjects.setdefault((family(box['subject']), box['subject']), []).append(box)
        for (fam, _), studies in subjects.items():
            if len(studies) < 2:
                continue
            small = [b for b in studies if span(b['topic']) <= 2]
            if fam == 'شیمی' and len(studies) >= 3 and all(span(b['topic']) <= 3 for b in studies):
                small = [b for b in studies if b is not max(studies, key=lambda x: span(x['topic']))]
            if not small:
                continue
            main = max(studies, key=lambda b: span(b['topic']))
            if any(b is main for b in small):
                small = [b for b in small if b is not main]
            for box in small:
                main['topic'] = merge_topic(main['topic'], box['topic'])
                box['tests'] = RATE[fam] * box['hours']
                box['detail'] = fa(box['tests']) + TEST_DETAIL[fam]
                touched.append((plan['id'], box['subject'], box['topic']))
    return touched


def short_title(topic):
    """Head of the studied scope plus its printed pages, without the long sub-lists."""
    parts = [seg.strip() for seg in topic.split('؛') if seg.strip()]
    if not parts:
        return topic
    head = parts[0]
    pages = next((seg for seg in parts[1:] if 'ص' in seg), None)
    return head + ('؛ ' + pages if pages else '')


def scope_titles(plan):
    """Main study-box title per (week, subject family), used for test titles."""
    out = {}
    for day in plan['days']:
        for box in day['boxes']:
            if not is_study(box):
                continue
            fam = family(box['subject'])
            if fam not in MATHY:
                continue
            key = (day['week'], box['subject'])
            if key not in out or span(box['topic']) > span(out[key]['topic']):
                out[key] = box
    return out


def retitle_tests(plan):
    scopes = scope_titles(plan)
    changed = []
    for day in plan['days']:
        for box in day['boxes']:
            if box['tests'] == 0:
                continue
            fam = family(box['subject'])
            if fam not in MATHY:
                continue
            scope = scopes.get((day['week'], box['subject']))
            if not scope:
                continue
            title = short_title(scope['topic'])
            if box['topic'] == title:
                continue
            old = box['topic']
            box['topic'] = title
            box['preference'] = '* ترجیحاً: ' + old
            changed.append((plan['id'], day['name'], box['subject'], old))
    return changed


def main():
    DST.mkdir(parents=True, exist_ok=True)
    report = {'folded': [], 'retitled': 0, 'plans': 0}
    for path in sorted(SRC.glob('*.json')):
        plan = json.loads(path.read_text())
        plan['directory'] = plan['directory'].replace('برنامه تحصیلی', 'دوازدهم', 1)
        report['folded'] += fold_tiny_boxes(plan)
        changed = retitle_tests(plan)
        report['retitled'] = report['retitled'] + len(changed)
        report['plans'] += 1
        (DST / path.name).write_text(json.dumps(plan, ensure_ascii=False, indent=1) + '\n')
    (BASE / 'annual/DEBUG_REPORT.json').write_text(json.dumps(report, ensure_ascii=False, indent=1) + '\n')
    print('plans', report['plans'], 'folded boxes', len(report['folded']),
          'retitled test boxes', report['retitled'])
    for item in report['folded']:
        print('  folded', item)


if __name__ == '__main__':
    main()
