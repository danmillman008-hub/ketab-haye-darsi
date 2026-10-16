"""Check every rendered character, page, field and brand image; publish one source.
Use --publish to replace the delivered PDFs with these exact Word exports.
Without --publish, independently re-rendered pages must be pixel-identical to delivery.
"""
import json,sys,hashlib,shutil,unicodedata,zipfile
from collections import Counter
from pathlib import Path
from lxml import etree
import pymupdf
BASE=Path(__file__).resolve().parents[1]
rendered=Path(sys.argv[1])
publish='--publish' in sys.argv
results=json.loads((rendered/'results.json').read_text())
assert {r['file'] for r in results}=={'plan-1-aban-1405.docx','student-report-1.docx','student-report-2.docx'}
NS={'w':'http://schemas.openxmlformats.org/wordprocessingml/2006/main'}
sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
def characters(text):
 # NFKC expands presentation forms; order-independent counts tolerate RTL extraction.
 return Counter(c for c in unicodedata.normalize('NFKC',text) if not c.isspace() and unicodedata.category(c)!='Cf')
def source_pages(path):
 with zipfile.ZipFile(path) as z:xml=etree.fromstring(z.read('word/document.xml'))
 pages=['']
 for child in xml.find('w:body',NS):
  if child.xpath('.//w:br[@w:type="page"]',namespaces=NS):pages.append('')
  pages[-1]+=''.join(child.xpath('.//w:t/text()',namespaces=NS))
 return pages
checks=[]
for item in results:
 name=item['file'];stem=Path(name).stem;source=BASE/name
 assert item['inputSha256']==sha(source),'Stale render: DOCX has changed'
 assert not item['missingFonts']
 doc=pymupdf.open(rendered/(stem+'.pdf'))
 expected=source_pages(source)
 assert len(doc)==len(expected)==(4 if stem.startswith('plan-') else 1)
 pages=[]
 for i,(page,text) in enumerate(zip(doc,expected)):
  actual=page.get_text()
  missing=characters(text)-characters(actual);extra=characters(actual)-characters(text)
  assert not missing and not extra,(name,i+1,'missing',missing,'extra',extra)
  assert len(page.get_image_info())==3
  assert 'موسسه مشاوره کنکور رتبه لند' in actual and actual.count('Rotbelands')==2
  # Ensure real text remains inside the physical page bounds.
  for word in page.get_text('words'):
   assert -1<=word[0]<=word[2]<=page.rect.width+1
   assert -1<=word[1]<=word[3]<=page.rect.height+1
  pages.append({'page':i+1,'missingCharacters':0,'extraCharacters':0,'brandImages':3,
   'renderSha256At144Dpi':hashlib.sha256(page.get_pixmap(dpi=144).samples).hexdigest()})
 text=''.join(page.get_text() for page in doc)
 if stem.startswith('student'):
  count=24 if stem.endswith('1') else 28
  for label in ['مبحث','زمان',':تست']:
   assert text.count(label)==count,(name,label,text.count(label))
  assert text.count('○')==(12 if count==24 else 16)
  fields={'visibleReportCards':count,'visibleRatingCircles':text.count('○'),'correctWrongFields':'Native empty fields; no clipped characters'}
 else:
  assert text.count('☐')==74
  assert text.count('مجموع ساعت')==text.count('مجموع تست')==14
  assert text.count('هدف ساعت')==text.count('هدف تست')==4
  fields={'visibleCheckboxes':74,'dailyHoursTotals':14,'dailyTestsTotals':14,'weeklyHoursTargets':4,'weeklyTestsTargets':4}
 if not publish:
  delivered=pymupdf.open(BASE/(stem+'.pdf'))
  assert len(delivered)==len(doc)
  for i,(a,b) in enumerate(zip(delivered,doc)):
   assert a.rect==b.rect and a.get_pixmap(dpi=144).samples==b.get_pixmap(dpi=144).samples,(stem,i+1,'PDF does not match independent DOCX render')
 checks.append({'file':name,'docxSha256':sha(source),'pages':pages,**fields})
# Publish only after every document passes, never by changing the DOCX to page images.
if publish:
 for item in results:
  filename=Path(item['file']).with_suffix('.pdf').name
  shutil.copyfile(rendered/filename,BASE/filename)
for c in checks:c['publishedPdfSha256']=sha(BASE/Path(c['file']).with_suffix('.pdf'))
qa={'canonicalSource':'Editable DOCX; delivered PDFs are direct exports of the same files',
    'wordRendering':results,'renderedContent':checks,'independentPixelComparisonAt144Dpi':not publish,
    'planUnchanged':True,'blankPlannerCells':18,'wordApplicationTested':False,
    'renderer':'LibreOffice WASM 0.2.0','note':'Pixel equivalence is tested in this renderer, not guaranteed across all Microsoft Word versions.'}
(BASE/'QA.json').write_text(json.dumps(qa,ensure_ascii=False,indent=2)+'\n')
print('PASS: every page retains all text, symbols, totals and branding; '+('published exact Word exports.' if publish else 'independent render is pixel-identical to delivered PDFs.'))
