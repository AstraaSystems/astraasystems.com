import shutil
from pathlib import Path
from datetime import datetime

# --- Backend: api.py ---
ap = Path("api.py")
s = ap.read_text(encoding="utf-8")
stamp = datetime.now().strftime("%Y%m%d_%H%M%S")
shutil.copyfile("api.py", f"api.py.before_spec5a1_{stamp}")

old = '        "sku": (p.get("sku") or "").strip(),\n        "category": (p.get("category") or "General").strip(),'
new = '        "sku": (p.get("sku") or "").strip(),\n        "specification": (p.get("specification") or "").strip(),\n        "category": (p.get("category") or "General").strip(),'
if old in s and '"specification"' not in s:
    s = s.replace(old, new, 1)
    ap.write_text(s, encoding="utf-8")
    print("Backend: specification field added:", '"specification"' in s)
else:
    print("Backend: already present or anchor missing")

# --- Frontend: module_logistics.js ---
mp = Path("astraaspace/module_logistics.js")
m = mp.read_text(encoding="utf-8")
shutil.copyfile(mp, f"astraaspace/module_logistics.js.bak_spec5a1_{stamp}")

# 1) Add spec input to the form, right after SKU
fold = "+this.field('name','Item name',e.name)+this.field('sku','SKU',e.sku)"
fnew = "+this.field('name','Item name',e.name)+this.field('sku','SKU',e.sku)\n      +this.field('specification','Specification / Size',e.specification)"
if fold in m and "'specification'" not in m:
    m = m.replace(fold, fnew, 1)

# 2) Add spec to the gather() function
gold = "return {name:v('name'),sku:v('sku'),category:v('category'),"
gnew = "return {name:v('name'),sku:v('sku'),specification:v('specification'),category:v('category'),"
if gold in m and "specification:v('specification')" not in m:
    m = m.replace(gold, gnew, 1)

# 3) Add Spec column to the inventory table header (after SKU)
hold = "<th>Item</th><th>SKU</th><th>Category</th>"
hnew = "<th>Item</th><th>SKU</th><th>Spec</th><th>Category</th>"
if hold in m and "<th>Spec</th>" not in m:
    m = m.replace(hold, hnew, 1)

# 4) Add spec cell to each table row (after the SKU cell)
rold = "+(it.sku||'')+'</td><td>'+(it.category||'')+'</td>'"
rnew = "+(it.sku||'')+'</td><td>'+(it.specification||'')+'</td><td>'+(it.category||'')+'</td>'"
if rold in m and "it.specification" not in m:
    m = m.replace(rold, rnew, 1)

mp.write_text(m, encoding="utf-8")
print("Frontend: form field:", "'specification'" in m)
print("Frontend: gather:", "specification:v('specification')" in m)
print("Frontend: table header:", "<th>Spec</th>" in m)
print("Frontend: table cell:", "it.specification" in m)
