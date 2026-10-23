"""Approved Thursday extension; quantities retain the sample's test+analysis pace.
A one-hour new block has 10 biology or 15 math tests; geology has 15 tests/hour.
No grade-12 files are read or written by this module.
"""
import copy

def extend(day, grade, biology_scope, math_scope, geology=None):
    assert day['day']==5
    assert len(day['boxes'])==2 and sum(b['hours'] for b in day['boxes'])==4
    assert all(b['kind']=='test' for b in day['boxes'])
    out=copy.deepcopy(day)
    label={10:'دهم',11:'یازدهم'}[grade]
    def test(subject, scope, hours, count):
        return dict(subject=subject,topic=scope['topic'],detail=f'{count} تست جمع‌بندی + تحلیل و ثبت خطا'.translate(str.maketrans('0123456789','۰۱۲۳۴۵۶۷۸۹')),hours=hours,tests=count,kind='test',ranges=copy.deepcopy(scope['ranges']))
    if grade==10:
        assert geology is None
        out['boxes'] += [test('زیست '+label,biology_scope,2,20),test('ریاضی',math_scope,2,30)]
    else:
        assert geology and geology['ranges']
        out['boxes'] += [dict(subject='زمین‌شناسی یازدهم',topic=geology['topic'],detail='مرور متن و شکل‌ها' if geology.get('review') else 'مطالعهٔ متن و شکل‌های کتاب',hours=1,tests=0,kind='review' if geology.get('review') else 'study',ranges=copy.deepcopy(geology['ranges'])),test('زیست '+label,biology_scope,1,10),test('زمین‌شناسی یازدهم',geology,1,15),test('ریاضی',math_scope,1,15)]
    out['hours']=sum(b['hours'] for b in out['boxes'])
    out['tests']=sum(b['tests'] for b in out['boxes'])
    assert out['hours']==8 and len(out['boxes'])<=6
    return out

if __name__=='__main__':
    from pathlib import Path
    import json
    base=Path(__file__).resolve().parents[1]
    for g in [10,11]:
        d=json.loads((base/'data'/f'g{g}-1405-08-15-week1.json').read_text())
        original=copy.deepcopy(d)
        bio=dict(topic='مرور زیست همین هفته',ranges=d['scope']['bio'])
        math=dict(topic='مرور ریاضی همین هفته',ranges=d['scope']['math'])
        geo=dict(topic='آفرینش کیهان و تکوین زمین؛ ص۹–۲۱',ranges=[[9,21]],review=True) if g==11 else None
        result=extend(d['days'][-1],g,bio,math,geo)
        assert d==original, 'Never mutate saved samples'
        assert result['tests']==(105 if g==10 else 95)
        assert len(result['boxes'])==(4 if g==10 else 6)
        print(f'PASS grade {g}: Thursday 8h, {result["tests"]} tests, {len(result["boxes"])} boxes; input unchanged.')
