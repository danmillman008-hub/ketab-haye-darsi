"""Book boundaries for the grade-12 year.

Grades 10 and 11 are needed because the grade-12 exams also ask for پایه review;
grade 12 is the new material. Only names and printed page numbers live here.
"""
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]

BIO_CHAPTERS = {
    10: [(1, 'دنیای زنده', 1, 16), (2, 'گوارش و جذب مواد', 17, 32),
         (3, 'تبادلات گازی', 33, 46), (4, 'گردش مواد در بدن', 47, 68),
         (5, 'تنظیم اسمزی و دفع مواد زائد', 69, 78), (6, 'از یاخته تا گیاه', 79, 96),
         (7, 'جذب و انتقال مواد در گیاهان', 97, 111)],
    11: [(1, 'تنظیم عصبی', 1, 18), (2, 'حواس', 19, 36), (3, 'دستگاه حرکتی', 37, 52),
         (4, 'تنظیم شیمیایی', 53, 62), (5, 'ایمنی', 63, 78), (6, 'تقسیم یاخته', 79, 96),
         (7, 'تولیدمثل', 97, 118), (8, 'تولیدمثل نهاندانگان', 119, 136),
         (9, 'پاسخ گیاهان به محرک', 137, 152)],
    12: [(1, 'مولکول‌های اطلاعاتی', 1, 20), (2, 'جریان اطلاعات در یاخته', 21, 36),
         (3, 'انتقال اطلاعات در نسل‌ها', 37, 46), (4, 'تغییر در اطلاعات وراثتی', 47, 62),
         (5, 'از ماده به انرژی', 63, 76), (6, 'از انرژی به ماده', 77, 90),
         (7, 'فناوری‌های نوین زیستی', 91, 106), (8, 'رفتارهای جانوران', 107, 124)],
}
PHYS_CHAPTERS = {
    10: [(1, 'فیزیک و اندازه‌گیری', 1, 22), (2, 'ویژگی‌های فیزیکی مواد', 23, 52),
         (3, 'کار، انرژی و توان', 53, 82), (4, 'دما و گرما', 83, 120)],
    11: [(1, 'الکتریسیتهٔ ساکن', 1, 38), (2, 'جریان الکتریکی و مدارها', 39, 64),
         (3, 'مغناطیس و القای الکترومغناطیسی', 65, 104)],
    12: [(1, 'حرکت بر خط راست', 1, 26), (2, 'دینامیک', 27, 52),
         (3, 'نوسان و موج', 53, 94), (4, 'فیزیک اتمی و هسته‌ای', 95, 125)],
}
CHEM_CHAPTERS = {
    10: [(1, 'کیهان، زادگاه الفبای هستی', 1, 46), (2, 'ردپای گازها در زندگی', 47, 84),
         (3, 'آب، آهنگ زندگی', 85, 122)],
    11: [(1, 'قدر هدایای زمینی را بدانیم', 1, 50), (2, 'در پی غذای سالم', 51, 98),
         (3, 'پوشاک، نیازی پایان‌ناپذیر', 99, 123)],
    12: [(1, 'مولکول‌ها در خدمت تندرستی', 1, 36), (2, 'آسایش و رفاه در سایه شیمی', 37, 66),
         (3, 'شیمی، جلوه‌ای از هنر، زیبایی و ماندگاری', 67, 90),
         (4, 'شیمی، راهی به سوی آینده‌ای روشن‌تر', 91, 123)],
}

# Topics the student already handles well: they stay in the scope but are never
# headlined and never used as the optional hint (see PRINCIPLES.md).
LIGHT = {
    ('physics', 10): [(53, 70)],
    ('math', 12): [],
}

_CATALOG = None


def catalog(book):
    global _CATALOG
    if _CATALOG is None:
        _CATALOG = json.loads((ROOT / 'annual/PAGE_CATALOG.json').read_text())['rows']
    return [(r['start'], r['end'], r['chapter'], r['title']) for r in _CATALOG if r['book'] == book]


def chapters_for(subject, grade):
    table = {'bio': BIO_CHAPTERS, 'physics': PHYS_CHAPTERS, 'chem': CHEM_CHAPTERS}[subject][grade]
    return [(a, b, c, t) for c, t, a, b in table]


def units_for(subject, grade):
    if subject == 'bio':
        return catalog(f'b{grade}')
    if subject == 'physics':
        return catalog(f'p{grade}')
    if subject == 'math':
        return catalog(f'm{grade}')
    if subject == 'chem':
        return [(a, b, c, t) for c, t, a, b in CHEM_CHAPTERS[grade]]
    raise KeyError(subject)


def pages(ranges):
    out = []
    for a, b in ranges:
        out.extend(range(a, b + 1))
    return out


def _trim(ranges, lo, hi):
    out = []
    for a, b in ranges:
        a, b = max(a, lo), min(b, hi)
        if a <= b:
            out.append([a, b])
    return out


def split_units(ranges, subject, grade, n):
    """Partition a scope into n contiguous, topic-aligned pieces without gaps."""
    flat = pages(ranges)
    total = len(flat)
    if total < n:
        n = max(1, total)
    starts = {a for a, _ in ranges} | {u[0] for u in units_for(subject, grade)}
    cuts = []
    for i in range(1, n):
        valid = [p for p in flat if p in starts and p > (cuts[-1] if cuts else flat[0] - 1)]
        valid = [p for p in valid if p <= flat[-2]] if len(flat) > 1 else []
        if not valid:
            continue
        cuts.append(min(valid, key=lambda p: abs(flat.index(p) - total * i / n)))
    cuts = sorted(set(cuts))
    bounds = [flat[0]] + cuts + [flat[-1] + 1]
    out = []
    for lo, hi in zip(bounds, bounds[1:]):
        piece = _trim(ranges, lo, hi - 1)
        if piece:
            out.append(piece)
    while len(out) < n:
        idx = max(range(len(out)), key=lambda i: len(pages(out[i])))
        flat_piece = pages(out[idx])
        mid = flat_piece[len(flat_piece) // 2]
        lo_piece = _trim(out[idx], flat_piece[0], mid - 1)
        hi_piece = _trim(out[idx], mid, flat_piece[-1])
        if not lo_piece or not hi_piece:
            break
        out[idx:idx + 1] = [lo_piece, hi_piece]
    return out
