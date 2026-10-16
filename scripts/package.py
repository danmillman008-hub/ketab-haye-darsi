from pathlib import Path
import zipfile
files=[Path(p) for p in ['index.html','README.md','plan-1-aban-1405.pdf','plan-1-aban-1405.docx','docs/PLANNING_REFERENCE.md']]
files+=list(Path('assets').glob('*'))
with zipfile.ZipFile('plan-1-aban-1405.zip','w',zipfile.ZIP_DEFLATED) as z:
 for p in files:z.write(p)
print('Packaged PDF, editable Word, offline HTML and planning reference.')
