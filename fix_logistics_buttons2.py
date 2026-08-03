from pathlib import Path
import shutil
from datetime import datetime

p = Path("astraaspace/module_logistics.js")
s = p.read_text(encoding="utf-8")
stamp = datetime.now().strftime("%Y%m%d_%H%M%S")
shutil.copyfile(p, f"astraaspace/module_logistics.js.bak_btn2_{stamp}")

# Find the closing of the <style> block and inject high-specificity overrides
# that beat the global "#content-area button{background:#1d4ed8}" rule.
override = (
    ".lg-wrap .lg-qbtn{background:#ffffff !important;color:#1d4ed8 !important;border:1px solid #1d4ed8 !important;font-weight:900 !important;}"
    ".lg-wrap .lg-btn{color:#ffffff !important;}"
    ".lg-wrap .lg-btn.ghost{background:#ffffff !important;color:#1d4ed8 !important;border:1px solid #1d4ed8 !important;}"
    ".lg-wrap .lg-btn.danger{background:#ffffff !important;color:#dc2626 !important;border:1px solid #fecaca !important;}"
    ".lg-wrap .lg-btn.ok{background:#16a34a !important;color:#ffffff !important;}"
    ".lg-wrap .lg-btn.sm{color:inherit;}"
)

marker = "</style>"
idx = s.find(marker)
if idx == -1:
    print("ABORT: </style> not found"); raise SystemExit
s = s[:idx] + "'+ '" + override + "' + '" + s[idx:]

# The above concatenation trick may not fit the string-build style; do a safer replace instead.
