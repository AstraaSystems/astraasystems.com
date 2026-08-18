import shutil
from pathlib import Path
from datetime import datetime
stamp = datetime.now().strftime("%Y%m%d_%H%M%S")
ap = Path("api.py"); s = ap.read_text(encoding="utf-8")
shutil.copyfile("api.py", f"api.py.before_s3a_{stamp}")
b = 0

d_old = ('            "last_activity_at": ""}')
d_new = ('            "last_activity_at": "",\n'
         '            "quote_index": (str(p.get("quote_index")).strip() if p.get("quote_index") not in (None,"") else ""),\n'
         '            "quote_title": (p.get("quote_title") or "").strip()}')
if d_old in s and '"quote_index"' not in s:
    s = s.replace(d_old, d_new, 1); b += 1

ap.write_text(s, encoding="utf-8")
print(f"S3a backend changes: {b} (expected 1)")
