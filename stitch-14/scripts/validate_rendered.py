"""Verify actual LibreOffice PDF content, not only the editable DOCX structure."""
import json,sys
from pathlib import Path
import pymupdf
BASE=Path(__file__).resolve().parents[1]
rendered=Path(sys.argv[1])
results=json.loads((rendered/'results.json').read_text())
checks=[]
for item in results:
 name=item['file']
 doc=pymupdf.open(rendered/(Path(name).stem+'.pdf'))
 assert len(doc)==(4 if name.startswith('plan-') else 1)
 for page in doc:
  assert len(page.get_image_info())==3, 'Logo and both social icons must actually render'
  assert 'موسسه مشاوره کنکور رتبه لند' in page.get_text()
  assert page.get_text().count('Rotbelands')==2
 if name.startswith('student'):
  count=24 if name=='student-report-1.docx' else 28
  text=doc[0].get_text()
  for label in ['مبحث','زمان']:
   assert text.count(label)==count, (name,label,text.count(label))
  assert text.count(':تست')==count
  assert text.count('○')==(12 if count==24 else 16)
  checks.append({'file':name,'visibleCards':count,'visibleRatingCircles':text.count('○'),'visibleBrandImages':3})
 else:
  assert sum(page.get_text().count('☐') for page in doc)==74
  checks.append({'file':name,'visibleCheckboxes':74,'visibleBrandImagesPerPage':3})
qa={'wordRendering':results,'renderedContent':checks,
    'browserLayout':json.loads((BASE/'QA-browser.json').read_text()),
    'planUnchanged':True,'blankPlannerCells':18,'reportFields':'Native nested tables with empty dotted-border paragraphs',
    'wordApplicationTested':False,'renderer':'LibreOffice WASM 0.2.0'}
(BASE/'QA.json').write_text(json.dumps(qa,ensure_ascii=False,indent=2)+'\n')
print('PASS: all rendered report labels, rating circles, planner checkboxes and branding images visible.')
