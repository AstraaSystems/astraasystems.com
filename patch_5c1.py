import shutil
from pathlib import Path
from datetime import datetime
stamp = datetime.now().strftime("%Y%m%d_%H%M%S")

# ---------- BACKEND ----------
ap = Path("api.py"); s = ap.read_text(encoding="utf-8")
shutil.copyfile("api.py", f"api.py.before_5c1_{stamp}")
b = 0
b_old = '        "quantity": round(num(p.get("quantity")), 2),'
b_new = ('        "quantity": round(num(p.get("quantity")), 2),\n'
         '        "reserved": round(num(p.get("reserved")), 2),')
if b_old in s and '"reserved": round(num(p.get("reserved"))' not in s:
    s = s.replace(b_old, b_new, 1); b += 1
ap.write_text(s, encoding="utf-8")
print(f"Backend reserved field: {b} (expected 1)")

# ---------- FRONTEND ----------
mp = Path("astraaspace/module_logistics.js"); m = mp.read_text(encoding="utf-8")
shutil.copyfile(mp, f"astraaspace/module_logistics.js.bak_5c1_{stamp}")
ch = 0

# 1) header: Reserved + Available after Qty
h_old = "<th>Qty</th><th>Unit cost</th>"
h_new = "<th>Qty</th><th>Reserved</th><th>Available</th><th>Unit cost</th>"
if h_old in m and "<th>Reserved</th>" not in m:
    m = m.replace(h_old, h_new, 1); ch += 1

# 2) row vars: add reserved + available
v_old = ",rp=Number(it.reorder_point||0);"
v_new = (",rp=Number(it.reorder_point||0),reserved=Number(it.reserved||0),"
         "available=(qty-reserved);")
if v_old in m and "reserved=Number(it.reserved" not in m:
    m = m.replace(v_old, v_new, 1); ch += 1

# 3) low-stock now keys off AVAILABLE + build avail display/tint
l_old = "var low=(rp>0&&qty<=rp);"
l_new = ("var availColor=(available<=0?'#dc2626':(rp>0&&available<=rp?'#eab308':'#16a34a'));"
         "var low=(rp>0&&available<=rp);")
if l_old in m and "availColor=" not in m:
    m = m.replace(l_old, l_new, 1); ch += 1

# 4) row cells: Reserved + Available right after the Qty cell
c_old = ("'+qty+'<button class=\"lg-qbtn\" onclick=\"LogisticsModule.adjust("
         "\\''+it.id+'\\',1)\">+</button></span></td>'")
c_new = (c_old +
         "\n        +'<td>'+reserved+'</td>'"
         "+'<td style=\"color:'+availColor+';font-weight:600\">'+available+'</td>'")
if c_old in m and "+'<td>'+reserved+'</td>'" not in m:
    m = m.replace(c_old, c_new, 1); ch += 1

# 5) form field: Reserved (so it round-trips; Phase 6 will set it programmatically)
f_old = "+this.field('reorder_point','Reorder point',e.reorder_point,'number')"
f_new = (f_old +
         "+this.field('reserved','Reserved (committed)',e.reserved,'number')")
if f_old in m and "'reserved'" not in m:
    m = m.replace(f_old, f_new, 1); ch += 1

# 6) gather(): include reserved
g_old = "reorder_point:v('reorder_point'),supplier:v('supplier'),notes:v('notes')}"
g_new = "reorder_point:v('reorder_point'),reserved:v('reserved'),supplier:v('supplier'),notes:v('notes')}"
if g_old in m and "reserved:v('reserved')" not in m:
    m = m.replace(g_old, g_new, 1); ch += 1

mp.write_text(m, encoding="utf-8")
print(f"Frontend changes: {ch} (expected 6)")
