from pathlib import Path
import shutil
from datetime import datetime

p = Path("astraaspace/module_logistics.js")
s = p.read_text(encoding="utf-8")
stamp = datetime.now().strftime("%Y%m%d_%H%M%S")
shutil.copyfile(p, f"astraaspace/module_logistics.js.bak_btn3_{stamp}")

# The exact style-close line (from grep line 50)
anchor = "    + '</style>';"
if anchor not in s:
    print("ABORT: style-close anchor not found"); raise SystemExit

# High-specificity overrides to beat "#content-area button{background:#1d4ed8}"
override_line = (
    "    + '.lg-wrap .lg-qbtn{background:#ffffff !important;color:#1d4ed8 !important;border:1px solid #1d4ed8 !important;}'\n"
    "    + '.lg-wrap button.lg-btn{background:#1d4ed8 !important;color:#ffffff !important;}'\n"
    "    + '.lg-wrap button.lg-btn.ghost{background:#ffffff !important;color:#1d4ed8 !important;border:1px solid #1d4ed8 !important;}'\n"
    "    + '.lg-wrap button.lg-btn.danger{background:#ffffff !important;color:#dc2626 !important;border:1px solid #fecaca !important;}'\n"
    "    + '.lg-wrap button.lg-btn.ok{background:#16a34a !important;color:#ffffff !important;}'\n"
)

s = s.replace(anchor, override_line + anchor, 1)
p.write_text(s, encoding="utf-8")
print("Override injected:", ".lg-wrap .lg-qbtn{background:#ffffff" in s)
