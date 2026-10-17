from pathlib import Path
import json,hashlib,csv
root=Path.cwd();reg=json.loads((root/'annual/BOOK_EDITIONS.json').read_text());books=reg['books']
fa=lambda x:str(x).translate(str.maketrans('0123456789','۰۱۲۳۴۵۶۷۸۹'))
names={'b':'زیست','c':'شیمی','m':'ریاضی','p':'فیزیک'};grades={10:'دهم',11:'یازدهم',12:'دوازدهم'}
s='# منابع فعال — چاپ ۱۴۰۵\n\nاین فهرست جایگزین فهرست چاپ‌های قدیمی است. مبنا ۱۲ فایل پوشهٔ [کتاب‌های درسی تجربی ۱۴۰۵](https://drive.google.com/drive/folders/1jUwSmhyhmG7gYwdYWs1LzMuzTw4tKPNV) است. سال چاپ به معنی تأیید رسمی منابع یک کنکور خاص نیست.\n\n| کتاب | صفحات محتوای آموزشی | صفحات PDF | اختلاف شماره PDF با چاپی | منبع |\n|---|---:|---:|---:|---|\n'
for b in books:
 k=b['key'];s+=f"| {names[k[0]]} {grades[int(k[1:])]} | ۱–{fa(b['printed_content_end'])} | {fa(b['pdf_pages'])} | +{fa(b['pdf_offset'])} | [PDF](https://drive.google.com/file/d/{b['drive_id']}/view) |\n"
s+='\nشمارهٔ PDF = شمارهٔ چاپی + اختلاف فوق. شمار محتوای آموزشی، جلد، مقدمه، واژه‌نامه و منابع پایانی را دربر نمی‌گیرد. فهرست صفحات PDF، اثرانگشت‌ها و مسیر فایل‌ها در BOOK_EDITIONS.json ثبت شده‌اند.\n\n## تطبیق مباحث\n\n- ۶۹ شروع گفتار زیست با متن صفحهٔ مربوط در فایل‌های جدید کنترل شده؛ مرز فصل‌ها و گفتارها به‌صرف تغییر چاپ جابه‌جا نشده‌اند.\n- مرز درس‌های تابع دهم: مفهوم و نمایش تا ص۱۰۰، دامنه و برد ص۱۰۱–۱۰۸، انواع تابع ص۱۰۹–۱۱۷؛ تقسیم قدیمی اصلاح شد.\n- شیمی دهم: فصل‌ها از ۱، ۴۷ و ۸۵؛ قسمت در میلیون ص۹۵ و تمرین آن در۹۶، استخراج نمک تا۹۷، غلظت مولی از۹۸.\n- شیمی یازدهم: فصل‌ها از۱،۵۱،۹۹؛ قانون هس از۷۴ تا بخشی از۷۷؛ ادامهٔ غذای سالم و سرعت واکنش در همان۷۷ آغاز می‌شود.\n- شیمی دوازدهم: فصل‌ها از۱،۳۷،۶۷،۹۱؛ سفر هدایت‌شدهٔ الکترون در۴۴، آبکاری۶۰–۶۱، آمونیاک۱۰۳، ارزش فناوری۱۱۱.\n- بعضی صفحه‌ها مشترک‌اند؛ دستور «قبل از عنوان» یعنی حذف ادامهٔ آن صفحه، نه حذف تمام صفحه. حجم این صفحات به صورت یک صفحهٔ درگیر محاسبه می‌شود.\n- فیزیک۱۱ پایان تمرین‌ها۱۰۴ است؛ پیوست۱۰۵ و واژه‌نامه/منابع۱۰۶ به بعد، جزو حجم آموزشیِ مرور نیستند، حتی اگر بازهٔ ماز تا۱۰۸ آمده باشد.\n- فیزیک۱۲: ساختار هسته۱۱۲، درحالی‌که ردیف۱۷اردیبهشت ماز۱۰۳–۱۲۵ نوشته است؛ برنامه مرور۱۰۳–۱۱۱ را نیز حفظ می‌کند و آن را هسته‌ای نمی‌نامد.\n'
(root/'annual/BOOK_EDITIONS.md').write_text(s)
maz=root/'google_drive/nnn1pTQT401yrhukz2t0zJLr3KNuRZVJwGoorjHP.pdf'
sources={'edition_registry':'BOOK_EDITIONS.json','maz_verified_pages':[5,6,7],'files':{b['file']:{'bytes':(root/b['file']).stat().st_size,'sha256':b['sha256'],'drive_id':b['drive_id']} for b in books},'review_scope':'Chapter/lesson/goftar boundaries, MAZ rows and planning boundary pages; not a line-by-line scientific proofread.'}
sources['files'][str(maz.relative_to(root))]={'bytes':maz.stat().st_size,'sha256':hashlib.sha256(maz.read_bytes()).hexdigest(),'drive_id':'1NLhRx-u-d3I2DiOGixzBNDsyqF_PFkZS'}
(root/'annual/SOURCES.json').write_text(json.dumps(sources,ensure_ascii=False,indent=2)+'\n')
# Page-volume guide is part of the planner, not the earlier independent assessment.
text='# راهنمای حجم صفحات — بازنویسی چاپ ۱۴۰۵\n\nاعداد زیر «صفحات چاپیِ محدوده» هستند؛ تعداد صفحات خوانده‌شده یا سختی مبحث نیستند. یک صفحهٔ مشترکِ مرزی یک بار شمرده شده و تکرار همان صفحه در دو باکس تست حجم را دو برابر نمی‌کند. جمع چند هفته ممکن است مرور یک صفحه را دوباره حساب کند؛ پس جمع سالانه تعداد صفحات یکتای کتاب‌ها نیست.\n\nدر برنامه‌های جامع، این محدوده ظرف انتخاب متن، شکل و سؤال نشان‌دار است؛ مطالعهٔ اولیهٔ کل آن در یک ساعت ادعا نشده است. در دو هفتهٔ موضوعی اردیبهشت، صفحات اصلی/فصل‌های دربرگیرنده شمرده شده‌اند و نکات پراکندهٔ موضوعی عدد دقیق ندارند.\n\n| آزمون | هفته | زیست | شیمی | فیزیک | ریاضی | نوع |\n|---|---:|---:|---:|---:|---:|---|\n'
rows=[]
for e in json.loads((root/'annual/manifest.json').read_text()):
 d=json.loads((root/'annual/data'/(e['id']+'.json')).read_text())
 for i,w in enumerate(d['scopes'],1):
  counts=[w['page_volume'][k]['unique_pages_in_scope'] for k in ['biology','chemistry','physics','math']]
  mode='موضوعی؛ حد شمارش محدود' if w.get('bio_thematic') else 'مرور انتخابی' if w['review'] else 'پیشروی / مرور بودجه'
  text+='| '+e['title']+' | '+fa(i)+' | '+' | '.join(fa(c) for c in counts)+' | '+mode+' |\n'
  rows.append([e['id'],i,*counts,mode])
text+='\n## مرزهای مهم هنگام اجرا\n\n- ۱ آبان: شیمی دهم ص۱۹–۴۶ مطابق ردیف صریح ماز؛ ادعای قبلیِ لزوم کل فصل۱ نادرست بود و اصلاح شد.\n- ۲۹ آبان: شیمی دهم تا پایان استخراج سدیم‌کلرید ص۹۷؛ غلظت مولی ص۹۸ به برنامهٔ۱۳آذر تعلق دارد.\n- ۲۷ آذر: شیمی۱۲ از عنوان سفر الکترون در۴۴ تا پایان آبکاری در۶۱؛ فرایند هال خارج از این قطعه است.\n- صفحات مرزی در فیزیک و شیمی را فقط تا عنوان تعیین‌شده در باکس بخوانید.\n- حجم متفاوت صفحات مجوز افزایش یا کاهش تعداد باکس، ساعت یا تعداد تست نیست.\n- ۱ آبان زیست دهم اکنون ۲۵–۳۲،۳۳–۳۹،۴۰–۴۶ است: ۸،۷،۷ صفحه با حفظ گفتارها و همان سه نوبت مطالعه.\n'
(root/'برنامه تحصیلی/راهنمای حجم صفحات.md').write_text(text)
with (root/'برنامه تحصیلی/حجم صفحات.csv').open('w',encoding='utf-8-sig',newline='') as f:
 writer=csv.writer(f);writer.writerow(['آزمون','هفته','زیست','شیمی','فیزیک','ریاضی','نوع شمارش']);writer.writerows(rows)
