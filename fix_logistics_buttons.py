from pathlib import Path
import shutil
from datetime import datetime

p = Path("astraaspace/module_logistics.js")
s = p.read_text(encoding="utf-8")
stamp = datetime.now().strftime("%Y%m%d_%H%M%S")
shutil.copyfile(p, f"astraaspace/module_logistics.js.bak_btn_{stamp}")

changes = 0

# 1. Fix qty +/- buttons: force visible dark text, light bg, real characters
old_qbtn = ".lg-qbtn{min-width:28px;height:28px;padding:0 8px;border:1px solid #cbd5e1;background:#eff6ff;border-radius:6px;cursor:pointer;font-weight:900;color:#1d4ed8;font-size:1rem;line-height:1;}"
new_qbtn = ".lg-qbtn{min-width:30px;height:30px;padding:0 10px;border:1px solid #1d4ed8;background:#fff;border-radius:6px;cursor:pointer;font-weight:900;color:#1d4ed8 !important;font-size:1.1rem;line-height:1;display:inline-flex;align-items:center;justify-content:center;}"
if old_qbtn in s:
    s = s.replace(old_qbtn, new_qbtn, 1); changes += 1

# 2. Replace &minus; entity with a plain minus sign (renders reliably)
if "&minus;" in s:
    s = s.replace("&minus;", "-"); changes += 1

# 3. Ensure .lg-btn.sm.ghost keeps visible blue text (Edit + Add line buttons)
old_ghost = ".lg-btn.ghost{background:#fff;color:#1d4ed8;border:1px solid #bfdbfe;}"
new_ghost = ".lg-btn.ghost{background:#fff;color:#1d4ed8 !important;border:1px solid #1d4ed8;}"
if old_ghost in s:
    s = s.replace(old_ghost, new_ghost, 1); changes += 1

p.write_text(s, encoding="utf-8")
print("Button fixes applied:", changes, "(expected 3)")
