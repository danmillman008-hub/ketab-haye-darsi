"""Reviewed corrections for the current Drive editions; MAZ remains the scope authority.
Printed page counts include boundary pages, not fractions of pages or test repetitions.
"""
from curriculum import *
import copy,re

def apply():
 NORMAL['1405-08-01']=[
 W(12,B(12,1,20),P('حرکت؛ ص۱–۱۵؛ پایان صفحهٔ ۱۵ فقط تا قبل از شتاب ثابت','مکان و جابه‌جایی، سرعت متوسط','سرعت لحظه‌ای و نمودار مکان–زمان','شتاب متوسط و لحظه‌ای','حرکت با سرعت ثابت','ترکیبی حرکت؛ بدون شتاب ثابت'),FUNC,[C(12,1,24,'تندرستی؛ صفحهٔ ۲۴ فقط تا قبل از pH')]),
 W(10,B(10,25,46),P('ویژگی‌های فیزیکی مواد؛ ص۲۳–۵۲','حالت‌ها و نیروهای بین‌مولکولی','فشار در شاره‌ها','شناوری و ارشمیدس','شاره در حرکت و برنولی','ترکیبی فصل۲ و تمرین‌های ص۴۸–۵۲'),M('تابع و معادلهٔ درجهٔ دوم؛ ریاضی۱ ص۷۰–۸۲ و ریاضی۲ ص۱۱–۱۸','روش‌های حل معادلهٔ درجهٔ دوم','سهمی، رأس و نمودار تابع درجهٔ دوم','دلتا و تعداد ریشه‌ها','مجموع و حاصل‌ضرب ریشه‌ها','ترکیبی تابع و معادلهٔ درجهٔ دوم'),[C(10,19,46,'کیهان؛ ادامهٔ فصل۱ طبق ماز')])]
 # Do not transplant the rejected old 2+2+1 bio distribution; all weeks use
 # the same goftar-aware volume allocator, without changing the formula.
 NORMAL['1405-08-29'][1]['chem']=[C(10,70,84,'پایان گازها'),C(10,85,97,'آب؛ تا پایان ppm و استخراج سدیم‌کلرید؛ بدون غلظت مولی')]
 NORMAL['1405-09-13'][1]['chem']=[C(10,98,122,'آب؛ از غلظت مولی تا پایان فصل')]
 NORMAL['1405-09-27'][0]['chem']=[C(12,44,61,'از عنوان سفر الکترون در ص۴۴ تا پایان آبکاری؛ بدون فرایند هال')]
 # Printed boundaries can share a page: never call the whole boundary page
 # "excluded" merely because the next heading begins on it.
 boundary_notes={
 '1405-07-17':('انتهای ص۱۰ پیش از عنوان شتاب متوسط و لحظه‌ای','انتهای ص۱۴ پیش از باهم‌بیندیشیم'),
 '1405-08-15':('', 'انتهای ص۳۰ پیش از عنوان شوینده‌های خورنده'),
 '1405-08-29':('انتهای ص۳۷ پیش از نیروی اصطکاک','انتهای ص۴۴ پیش از عنوان سفر الکترون'),
 '1405-09-13':('انتهای ص۴۴ پیش از عنوان تکانه','انتهای ص۵۰ پیش از عنوان سلول سوختی'),
 '1405-11-09':('انتهای ص۶۴ پیش از موج عرضی','انتهای ص۷۷ پیش از هنرنمایی شاره‌ها'),
 '1405-11-23':('انتهای ص۷۶ پیش از بازتاب موج','انتهای ص۸۶ پیش از خودرابیازمایید وانادیم'),
 }
 for key,(p,c) in boundary_notes.items():
  w=NORMAL[key][0]
  if p:w['physics_boundary']=p
  if c:w['chem_boundary']=c
 NORMAL['1405-11-09'][1]['physics_boundary']='انتهای ص۴۵ پیش از عوامل مؤثر بر مقاومت'
 NORMAL['1405-12-07'][1]['physics_boundary']='انتهای ص۸۵ پیش از عنوان القای الکترومغناطیسی'
 NORMAL['1405-11-23'][1]['chem_boundary']='ص۷۷ فقط تا پایان تمرین قانون هس'
 NORMAL['1405-12-07'][1]['chem_boundary']='ص۷۷ از آغاز بحث غذای سالم و سرعت واکنش'
 for key in ['1405-10-25','1406-01-20']:
  SPECIAL[key][-1]['physics_boundary']='انتهای ص۶۲ پیش از عنوان مشخصه‌های موج'
 SPECIAL['1406-02-03'][0]['chem_boundary']='انتهای ص۱۱۱ پیش از عنوان ارزش فناوری؛ ادامه در آزمون بعد'
 SPECIAL['1406-02-03'][1]['chem']=[C(11,31,43,'هیدروکربن‌ها'),C(11,70,72,'اتر، کتون و آلدهید'),C(11,84,84,'کربوکسیلیک‌اسید'),C(11,102,121,'پلیمر، آمین و آمید')]
 # Every broad thematic assignment gets explicit book identity and pages.
 SPECIAL['1406-02-03'][1]['bio']=[(10,79,111),(11,119,152),(12,77,90)]
 SPECIAL['1406-02-03'][1]['bio_thematic']=True
 SPECIAL['1406-02-03'][1]['bio_daily']=[('زیست دهم','گیاهی؛ فصل۶ و۷؛ ص۷۹–۱۱۱؛ ۳۳ صفحه + نکات گیاهی سایر فصل‌ها'),('زیست یازدهم','گیاهی؛ فصل۸ و۹؛ ص۱۱۹–۱۵۲؛ ۳۴ صفحه + نکات گیاهی سایر فصل‌ها'),('زیست دوازدهم','فتوسنتز؛ فصل۶ ص۷۷–۹۰؛ ۱۴ صفحه + نکات گیاهی سایر فصل‌ها')]
 SPECIAL['1406-02-17'][1]['bio_thematic']=True
 SPECIAL['1406-02-17'][1]['bio']=[(10,17,78),(11,1,118),(12,107,124)]
 SPECIAL['1406-02-17'][1]['bio_daily']=[('زیست دهم','جانوری؛ فصل۲–۵ ص۱۷–۷۸؛ ۶۲ صفحه + نکات جانوری فصل۱'),('زیست یازدهم','جانوری؛ فصل۱–۷ ص۱–۱۱۸؛ ۱۱۸ صفحه؛ انتخاب متن و شکل‌های جانوری'),('زیست دوازدهم','رفتار؛ فصل۸ ص۱۰۷–۱۲۴؛ ۱۸ صفحه + نکات جانوری سایر فصل‌ها')]
 # Scope of the thematic extras cannot be described as an exact count.
 for key in ['1406-02-03','1406-02-17']:
  SPECIAL[key][1]['volume_qualifier']='شمار صفحات اصلی؛ نکات پراکندهٔ موضوعی در سایر فصل‌ها جداست؛ مرور انتخابی، نه خواندن کامل در یک ساعت.'
 for w in [SPECIAL['1406-03-28'][0],SPECIAL['1406-04-04'][0]]:enrich_final(w)

def enrich_final(w):
 w['bio_daily']=[('زیست '+GRADES[g],f'مرور انتخابی فصل‌های ۱–{len(BIO[g])}؛ ص۱–'+str({10:111,11:152,12:124}[g])+'؛ شکل‌ها و خطاهای قبلی') for g in [10,11,12]]
 w['chem_daily']=[('شیمی '+GRADES[g],'مرور انتخابی کل کتاب؛ ص۱–'+str({10:122,11:123,12:123}[g])+'؛ مفاهیم و مسائل نشان‌دار') for g in [10,11,12]]
 return w

def physics_ranges(w):
 if 'physics_daily_grades' in w:return [(10,1,120),(11,1,104),(12,1,125)]
 s=w['physics'][0];m=re.search(r'ص\s*([۰-۹0-9]+)–([۰-۹0-9]+)',s)
 if m:return [(w['grade'],int(m[1]),int(m[2]))]
 return [(w['grade'],1,{10:120,11:104,12:125}[w['grade']])]

# Exact union of MAZ math ranges per weekly header (inclusive printed pages).
MATH_SCOPES={}
def register(obj,ranges):MATH_SCOPES[obj[0]]=ranges
for obj,ranges in [
 (FUNC,[(10,94,117),(11,47,70),(12,1,29)]),(FUNC_EARLY,[(10,94,117),(11,47,56),(12,1,14)]),
 (EQU,[(10,83,93),(11,19,24)]),(TRIG1,[(10,28,46),(11,71,94),(12,31,41)]),(TRIG2,[(10,28,46),(11,71,94),(12,42,48)]),
 (ALG,[(10,47,68)]),(EXP,[(11,95,118)]),(SEQ,[(10,1,27)]),(STAT,[(10,152,170),(11,153,166)]),
 (LIMIT_D,[(11,119,142),(12,49,76)]),(DERIV,[(12,77,100)]),(APPL1,[(12,101,112)]),(APPL2,[(12,101,120)]),
 (GEO1,[(11,1,10),(11,25,30)]),(GEO2,[(11,31,46)]),(COUNT,[(10,118,140)]),(PROB,[(10,141,151),(11,143,152)]),
 (GEO12,[(12,121,142)]),(ALL_PROB,[(10,118,151),(11,143,152),(12,143,148)]),
 (FIRST_HALF_M1,[(10,28,46),(10,94,117),(11,47,94),(12,1,48)]),
 (FIRST_HALF_M2,[(11,119,142),(12,49,76)])]:register(obj,ranges)
for g in [10,11,12]:register(full_math(g),[(g,1,{10:170,11:166,12:148}[g])])
def math_ranges(w):
 s=w['math'][0]
 if s in MATH_SCOPES:return MATH_SCOPES[s]
 if s.startswith('تابع و معادلهٔ درجهٔ دوم'):return [(10,70,82),(11,11,18)]
 if s.startswith('مرور تابع، مثلثات و حد بی'):return [(10,28,46),(10,94,117),(11,47,94),(11,119,142),(12,1,57)]
 if s.startswith('مسیر مرور ۵۰درصدی'):return [(12,77,120)]
 if s.startswith('مرور نیم‌سال دوم'):return [(12,65,148)]
 if s.startswith('مرور ریاضی سه پایه'):return [(10,1,170),(11,1,166),(12,1,148)]
 raise ValueError('Unmapped mathematics scope: '+s)

def count(ranges):return len({(g,p) for g,a,b in ranges for p in range(a,b+1)})
def volumes(w):
 b=w['bio'];c=[x[:3] for x in w['chem']]
 if not b and 'bio_daily' in w and w['label']=='سه پایه':b=[(10,1,111),(11,1,152),(12,1,124)]
 if not c and 'chem_daily' in w and w['label']=='سه پایه':c=[(10,1,122),(11,1,123),(12,1,123)]
 if not c and w['label']=='پایه':
  # Thematic calculations touch selected problems, not every page of these chapters.
  c=[(10,47,122),(11,1,123)]
 return {k:{'ranges':v,'unique_pages_in_scope':count(v)} for k,v in [('biology',b),('chemistry',c),('physics',physics_ranges(w)),('math',math_ranges(w))]}
