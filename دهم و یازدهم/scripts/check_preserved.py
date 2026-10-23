"""Read-only integrity check for the pre-existing repository deliverables."""
from pathlib import Path
import hashlib,json
BASE=Path(__file__).resolve().parents[1]
ROOT=BASE.parent
for name,digest in json.loads((BASE/'preserved.json').read_text()).items():
 assert (ROOT/name).is_file(), f'Missing pre-existing file: {name}'
 assert hashlib.sha256((ROOT/name).read_bytes()).hexdigest()==digest, f'Pre-existing file modified: {name}'
print('PASS: all pre-existing tracked files remain byte-for-byte unchanged.')
