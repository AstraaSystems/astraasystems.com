import shutil
from pathlib import Path
from datetime import datetime
stamp = datetime.now().strftime("%Y%m%d_%H%M%S")
ap = Path("api.py"); s = ap.read_text(encoding="utf-8")
shutil.copyfile("api.py", f"api.py.before_logiprice_{stamp}")
b = 0

# 1) price map
p_old = '    "research_analyst": "49.99",\n'
p_new = '    "research_analyst": "49.99",\n    "logistics": "99.00",\n'
if p_old in s and '"logistics":' not in s:
    s = s.replace(p_old, p_new, 1); b += 1

# 2) checkout label map (line ~1333)
l_old = '"research_analyst":"Astraa Research Analyst",'
l_new = '"research_analyst":"Astraa Research Analyst","logistics":"Astraa Logistics",'
if l_old in s and '"logistics":"Astraa Logistics"' not in s:
    s = s.replace(l_old, l_new, 1); b += 1

ap.write_text(s, encoding="utf-8")
print(f"backend price+label changes: {b} (expected 2)")
