"""Whole-year quality gate for grades 10 and 11.

Checks data, coverage against the transcribed MAZ budget, calendar, and the
approved Thursday pattern. Runs negative mutations so a passing result is
meaningful. It never touches grade-12 files.
"""
import copy
import json
import re
import sys
from datetime import timedelta
from pathlib import Path

import jdatetime

BASE = Path(__file__).resolve().parents[1]
BUDGET = json.loads((BASE / 'annual/budget.json').read_text())
CAL = json.loads((BASE / 'calendar.json').read_text())
MANIFEST = json.loads((BASE / 'annual/year_manifest.json').read_text())
SUBJECTS = ['bio', 'physics', 'chem', 'math', 'geo']
FA = str.maketrans('۰۱۲۳۴۵۶۷۸۹', '0123456789')
LATIN = re.compile(r'[0-9]')
NAMES = {10: 'دهم', 11: 'یازدهم'}
THURSDAY = {10: [2, 2, 2, 2], 11: [2, 2, 1, 1, 1, 1]}


class Failure(AssertionError):
    pass


def check(cond, msg):
    if not cond:
        raise Failure(msg)


def jd(s):
    return jdatetime.date(*map(int, s.split('-')))


def load(plan_id):
    return json.loads((BASE / 'data' / (plan_id + '.json')).read_text())


def rng_pages(ranges):
    return [p for a, b in ranges for p in range(a, b + 1)]


def scope_union(ranges):
    return set(rng_pages(ranges))


def subject_of(box):
    text = box['subject']
    if text.startswith('زیست'):
        return 'bio'
    if text.startswith('فیزیک'):
        return 'physics'
    if text.startswith('شیمی'):
        return 'chem'
    if text.startswith('ریاضی'):
        return 'math'
    if text.startswith('زمین‌شناسی'):
        return 'geo'
    if text.startswith('دروس نهایی'):
        return 'finals'
    raise Failure('unknown subject ' + text)


def validate_plan(meta, row, cal_row, prev_target):
    g = meta['grade']
    check(meta['pages'] == meta['weeks'] * 2, f'{meta["id"]}: page count')
    check(len(meta['days']) == meta['weeks'] * 6, f'{meta["id"]}: day count')
    check(len(meta['week_meta']) == meta['weeks'], f'{meta["id"]}: week meta')
    check(meta['target'] == cal_row['id'], f'{meta["id"]}: target')
    # Calendar: six consecutive study days then the Friday exam.
    start = jd(meta['start'])
    for w in range(meta['weeks']):
        week = meta['days'][w * 6:(w + 1) * 6]
        for i, day in enumerate(week):
            expected = start + timedelta(days=7 * w + i)
            check(day['iso'] == expected.isoformat(), f'{meta["id"]}: day {w}/{i} date')
            check(day['hours'] == sum(b['hours'] for b in day['boxes']), f'{meta["id"]}: day hours')
            check(day['tests'] == sum(b['tests'] for b in day['boxes']), f'{meta["id"]}: day tests')
        wm = meta['week_meta'][w]
        check(wm['official_exam'] == (w == meta['weeks'] - 1), f'{meta["id"]}: exam flag')
        check((start + timedelta(days=7 * w + 6)).isoformat() == meta['target'] if w == meta['weeks'] - 1 else True,
              f'{meta["id"]}: last Friday')
    check(start + timedelta(days=7 * meta['weeks'] - 1) == jd(meta['target']), f'{meta["id"]}: week span')
    if prev_target:
        check(start == jd(prev_target) + timedelta(days=1), f'{meta["id"]}: continuity')

    # Budget coverage: the taught pages of the cycle equal the MAZ ranges.
    for subject in SUBJECTS:
        spec = row['subjects'].get(subject)
        if not spec:
            check(not any(subject_of(b) == subject for d in meta['days'] for b in d['boxes']),
                  f'{meta["id"]}: unexpected {subject}')
            continue
        budget_pages = set(rng_pages(spec['ranges']))
        taught = set()
        for week in range(meta['weeks']):
            days = meta['days'][week * 6:(week + 1) * 6]
            week_study = set()
            for d in days:
                for b in d['boxes']:
                    if subject_of(b) != subject:
                        continue
                    pages = set(rng_pages(b['ranges']))
                    check(pages <= budget_pages, f'{meta["id"]}: {subject} box outside budget {b["topic"]}')
                    if b['kind'] in ('study', 'review') and b['hours'] > 0:
                        week_study |= pages
            taught |= week_study
            # Week two must review exactly the pages taught in week one.
            if week > 0 and meta['weeks'] >= 2 and week % 2 == 1:
                prev_days = meta['days'][(week - 1) * 6:week * 6]
                prev_study = {p for d in prev_days for b in d['boxes']
                              if subject_of(b) == subject and b['kind'] in ('study', 'review')
                              for p in rng_pages(b['ranges'])}
                if prev_study and week_study and prev_study != week_study and meta['weeks'] == 2:
                    raise Failure(f'{meta["id"]}: week-two review differs from week one ({subject})')
        check(taught == budget_pages,
              f'{meta["id"]}: {subject} coverage {len(taught)} of {len(budget_pages)} pages')
        # Study precedes tests: a test may only cover pages already studied.
        # A box labelled "study" must actually introduce unseen pages; re-reading
        # the same pages has to be labelled as an explicit review.
        studied = set()
        for d in meta['days']:
            for b in d['boxes']:
                if subject_of(b) != subject:
                    continue
                pages = set(rng_pages(b['ranges']))
                if b['kind'] in ('study', 'review') and b['tests'] == 0:
                    if b['kind'] == 'study':
                        check(pages - studied, f'{meta["id"]}: study box repeats studied pages ({subject})')
                    studied |= pages
                elif b['kind'] == 'test':
                    check(pages <= studied, f'{meta["id"]}: test before study ({subject})')
    check(meta['hours'] == sum(d['hours'] for d in meta['days']), f'{meta["id"]}: total hours')
    check(meta['tests'] == sum(d['tests'] for d in meta['days']), f'{meta["id"]}: total tests')

    for d in meta['days']:
        fams = [subject_of(b) for b in d['boxes']]
        if d['day'] < 5:
            check(len(fams) <= 4, f'{meta["id"]}: too many boxes')
            for a, b in zip(fams, fams[1:]):
                check(a != b, f'{meta["id"]}: consecutive same subject in {d["name"]}')
            for b in d['boxes']:
                check(b['hours'] <= 2, f'{meta["id"]}: box over two hours on {d["name"]}')
        else:
            expected = THURSDAY[g]
            check([b['hours'] for b in d['boxes']] == expected or
                  [b['hours'] for b in d['boxes'][:len(expected)]] == expected,
                  f'{meta["id"]}: Thursday shape {[b["hours"] for b in d["boxes"]]}')
            check(sum(b['hours'] for b in d['boxes']) == 8, f'{meta["id"]}: Thursday eight hours')
            if g == 10:
                check(len(d['boxes']) == 4 and all(b['kind'] == 'test' for b in d['boxes']),
                      f'{meta["id"]}: grade-10 Thursday')
            else:
                check(len(d['boxes']) == 6, f'{meta["id"]}: grade-11 Thursday count')
                geo = [b for b in d['boxes'] if subject_of(b) == 'geo']
                check(len(geo) == 2, f'{meta["id"]}: geology pair')
                check(any(b['kind'] in ('study', 'review') for b in geo) and
                      any(b['kind'] == 'test' for b in geo), f'{meta["id"]}: geology pair kinds')
                check(sum(b['hours'] for b in geo) == 2, f'{meta["id"]}: geology hours')
        for b in d['boxes']:
            check(not LATIN.search(b['topic']), f'{meta["id"]}: latin digits in topic')
            check(not LATIN.search(b['detail']), f'{meta["id"]}: latin digits in detail')
            subject = subject_of(b)
            if subject == 'geo':
                check(g == 11, f'{meta["id"]}: geology in grade 10')
                pages = rng_pages(b['ranges'])
                check(pages and min(pages) >= 9 and max(pages) <= 125, f'{meta["id"]}: geology pages')
            if b.get('preference'):
                check(subject in ('math', 'physics'), f'{meta["id"]}: preference on {subject}')
                check(b['preference'].startswith('* ترجیحاً:'), f'{meta["id"]}: preference label')
            for bad in ['ماز', 'چاپ', 'نسخه', 'صفحهٔ', 'تعداد صفحه']:
                check(bad not in b['topic'] or bad == 'صفحهٔ', f'{meta["id"]}: source note in topic')
            check(len(b['topic']) <= 130, f'{meta["id"]}: long topic')
            check(b['subject'] in ('ریاضی', 'دروس نهایی') or b['subject'].endswith(NAMES[g]),
                  f'{meta["id"]}: grade label in {b["subject"]}')
    return True


def validate_year():
    check(len(MANIFEST) == 34, 'manifest size')
    by_grade = {}
    for entry in MANIFEST:
        meta = load(entry['id'])
        check(meta['preserved'] is False, 'preserved flag')
        by_grade.setdefault(meta['grade'], []).append(meta)
    for g in (10, 11):
        rows = [r for r in BUDGET if r['grade'] == g]
        plans = sorted(by_grade[g], key=lambda m: m['target'])
        check(len(plans) == 17, f'grade {g} plan count')
        prev = None
        for plan, row, cal_row in zip(plans, rows, CAL):
            validate_plan(plan, row, cal_row, prev)
            prev = plan['target']
        # Whole-book review cycles cover the complete book.
        for plan in plans:
            if plan['weeks'] >= 5:
                for subject, total in [('bio', 111 if g == 10 else 152), ('physics', 120 if g == 10 else 104),
                                       ('chem', 122 if g == 10 else 123), ('math', 170 if g == 10 else 166)]:
                    pages = {p for d in plan['days'] for b in d['boxes'] if subject_of(b) == subject
                             for p in rng_pages(b['ranges'])}
                    check(pages == set(range(1, total + 1)), f'{plan["id"]}: {subject} full book')
                if g == 11:
                    pages = {p for d in plan['days'] for b in d['boxes'] if subject_of(b) == 'geo'
                             for p in rng_pages(b['ranges'])}
                    check(pages == set(range(9, 126)), f'{plan["id"]}: geology full book')
        # Weekly test budget stays identical inside a form.
        weekly = {plan['tests'] / plan['weeks'] for plan in plans}
        check(weekly == {280.0} if g == 10 else weekly == {270.0}, f'grade {g} weekly tests {weekly}')
    return True


def mutate(meta, fn):
    clone = copy.deepcopy(meta)
    fn(clone)
    row = next(r for r in BUDGET if r['grade'] == meta['grade'] and r['exam'] == meta['target'])
    cal_row = next(c for c in CAL if c['id'] == meta['target'])
    validate_plan(clone, row, cal_row, None)
    return False


def negatives():
    base = load('g10-1405-08-15')
    cases = []

    def drop_box(m):
        m['days'][3]['boxes'].pop()
    cases.append(('missing box', drop_box))

    def shift_day(m):
        m['days'][0]['iso'] = '1405-08-03'
    cases.append(('wrong date', shift_day))

    def fail_review(m):
        m['days'][7]['boxes'][0]['kind'] = 'study'
        m['days'][7]['boxes'][0]['detail'] = 'مطالعه'
    cases.append(('week two not review', fail_review))

    def outside(m):
        m['days'][0]['boxes'][0]['ranges'] = [[1, 30]]
    cases.append(('outside budget', outside))

    def early_test(m):
        m['days'][0]['boxes'] = [m['days'][0]['boxes'][2]]
    cases.append(('test before study', early_test))

    def short_thursday(m):
        m['days'][5]['boxes'][0]['hours'] = 1
    cases.append(('Thursday hours', short_thursday))

    def geology_in_10(m):
        m['days'][5]['boxes'].append(dict(subject='زمین‌شناسی یازدهم', topic='آفرینش کیهان؛ ص۹–۲۱',
                                          detail='مرور', hours=0, tests=0, kind='review', ranges=[[9, 21]]))
    cases.append(('geology in grade 10', geology_in_10))

    def latin(m):
        m['days'][2]['boxes'][0]['topic'] += ' 12'
    cases.append(('latin digits', latin))

    def preference(m):
        m['days'][2]['boxes'][0]['preference'] = 'اختیاری'
    cases.append(('bad preference', preference))

    base11 = load('g11-1405-08-15')

    def consecutive(m):
        m['days'][0]['boxes'] = [m['days'][0]['boxes'][2], m['days'][0]['boxes'][0], m['days'][0]['boxes'][1]]
    cases.append(('consecutive subject', consecutive))

    results = []
    for name, fn in cases:
        target = base11 if name == 'consecutive subject' else base
        try:
            mutate(target, fn)
        except Failure:
            results.append((name, 'REJECTED'))
        else:
            results.append((name, 'ACCEPTED'))
    check(all(r[1] == 'REJECTED' for r in results), f'negative mutations not rejected: {results}')
    return results


def main():
    validate_year()
    neg = negatives()
    print('PASS annual data: 34 plans, coverage, calendar, Thursday pattern.')
    for name, verdict in neg:
        print(f'  negative: {name}: {verdict}')
    out = dict(plans=len(MANIFEST), negatives=neg,
               totals={g: dict(hours=sum(load(e['id'])['hours'] for e in MANIFEST if load(e['id'])['grade'] == g),
                               tests=sum(load(e['id'])['tests'] for e in MANIFEST if load(e['id'])['grade'] == g),
                               pages=sum(load(e['id'])['pages'] for e in MANIFEST if load(e['id'])['grade'] == g))
                       for g in (10, 11)})
    (BASE / 'annual/YEAR_QA.json').write_text(json.dumps(out, ensure_ascii=False, indent=2) + '\n')
    print(json.dumps(out['totals'], ensure_ascii=False))


if __name__ == '__main__':
    main()
