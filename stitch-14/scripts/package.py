from pathlib import Path
import zipfile
BASE=Path(__file__).resolve().parents[1]
files=[BASE/n for n in ['plan-1-aban-1405.pdf','plan-1-aban-1405.docx','student-report-1.docx','student-report-1.pdf','student-report-2.docx','student-report-2.pdf','index.html','README.md','QA.json','QA-browser.json']]
files.extend(p for p in (BASE/'assets').rglob('*') if p.is_file())
with zipfile.ZipFile(BASE/'stitch-14-deliverables.zip','w',zipfile.ZIP_DEFLATED) as z:
 for p in files:z.write(p,p.relative_to(BASE))
print('Packaged three matching PDF/Word pairs and reference HTML.')
