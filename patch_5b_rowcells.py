import shutil
from pathlib import Path
from datetime import datetime

p = Path("astraaspace/module_logistics.js")
m = p.read_text(encoding="utf-8")
stamp = datetime.now().strftime("%Y%m%d_%H%M%S")
shutil.copyfile(p, f"astraaspace/module_logistics.js.bak_rowcells_{stamp}")
ch = 0

# 1) Add sale + margin vars to the row loop
old1 = "var qty=Number(it.quantity||0),cost=Number(it.unit_cost||0),rp=Number(it.reorder_point||0);"
new1 = ("var qty=Number(it.quantity||0),cost=Number(it.unit_cost||0),"
        "sale=Number(it.sale_price||0),rp=Number(it.reorder_point||0); "
        "var marginPct=(sale>0?((sale-cost)/sale*100):0); "
        "var marginTxt=(sale>0?marginPct.toFixed(0)+'%':'-'); "
        "var marginColor=(sale<=0?'#94a3b8':(marginPct>=30?'#16a34a':(marginPct>=10?'#eab308':'#dc2626')));")
if old1 in m and "sale=Number(it.sale_price" not in m:
    m = m.replace(old1, new1, 1); ch += 1

# 2) Emit the Sale + Margin cells before the Value cell
old2 = "+'<td>'+self.money(cost)+'</td><td>'+self.money(qty*cost)+'</td><td>'+(it.location||'')+'</td>'"
new2 = ("+'<td>'+self.money(cost)+'</td>'"
        "+'<td>'+self.money(sale)+'</td>'"
        "+'<td style=\"color:'+marginColor+';font-weight:600\">'+marginTxt+'</td>'"
        "+'<td>'+self.money(qty*cost)+'</td><td>'+(it.location||'')+'</td>'")
if old2 in m and "self.money(sale)" not in m:
    m = m.replace(old2, new2, 1); ch += 1

p.write_text(m, encoding="utf-8")
print(f"Row cells patch applied: {ch} (expected 2)")
