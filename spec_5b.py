import shutil
from pathlib import Path
from datetime import datetime

stamp = datetime.now().strftime("%Y%m%d_%H%M%S")

# ---- BACKEND: add sale_price + markup_percent to clean function ----
ap = Path("api.py")
s = ap.read_text(encoding="utf-8")
shutil.copyfile("api.py", f"api.py.before_5b_{stamp}")

old = '        "unit_cost": round(num(p.get("unit_cost")), 2),\n        "quantity": round(num(p.get("quantity")), 2),'
new = '        "unit_cost": round(num(p.get("unit_cost")), 2),\n        "sale_price": round(num(p.get("sale_price")), 2),\n        "markup_percent": round(num(p.get("markup_percent")), 2),\n        "quantity": round(num(p.get("quantity")), 2),'
if old in s and '"sale_price"' not in s:
    s = s.replace(old, new, 1)
    ap.write_text(s, encoding="utf-8")
    print("Backend: sale_price + markup added:", '"sale_price"' in s)
else:
    print("Backend: already present or anchor missing")

# ---- FRONTEND ----
mp = Path("astraaspace/module_logistics.js")
m = mp.read_text(encoding="utf-8")
shutil.copyfile(mp, f"astraaspace/module_logistics.js.bak_5b_{stamp}")
ch = 0

# 1) Add sale_price + markup fields to the form, after unit_cost line
fold = "+this.field('unit_cost','Unit cost ($)',e.unit_cost,'number')+this.field('quantity','Quantity',e.quantity,'number')"
fnew = ("+this.field('unit_cost','Unit cost ($)',e.unit_cost,'number')+this.field('sale_price','Sale price ($)',e.sale_price,'number')\n"
        "      +this.field('markup_percent','Markup %',e.markup_percent,'number')+this.field('quantity','Quantity',e.quantity,'number')")
if fold in m and "'sale_price'" not in m:
    m = m.replace(fold, fnew, 1); ch += 1

# 2) Add sale_price + markup to gather()
gold = "unit_cost:v('unit_cost'),quantity:v('quantity'),"
gnew = "unit_cost:v('unit_cost'),sale_price:v('sale_price'),markup_percent:v('markup_percent'),quantity:v('quantity'),"
if gold in m and "sale_price:v('sale_price')" not in m:
    m = m.replace(gold, gnew, 1); ch += 1

# 3) Add auto-calc: when markup typed, compute sale_price; add a small handler wired via onchange.
#    Simplent approach: add a helper that recomputes on Save if sale_price blank but markup set.
#    We'll adjust gather-consuming save to fill sale_price from markup if needed - do it in a JS helper.
#    Insert a calcSale helper after gather() definition.
gather_anchor = "reorder_point:v('reorder_point'),supplier:v('supplier'),notes:v('notes')}; },"
calc_helper = (gather_anchor + "\n"
    "  applyMarkup:function(){var c=parseFloat(document.getElementById('lg_unit_cost').value)||0;var mk=parseFloat(document.getElementById('lg_markup_percent').value)||0;if(c>0&&mk>0){document.getElementById('lg_sale_price').value=(c*(1+mk/100)).toFixed(2);}},")
if gather_anchor in m and "applyMarkup:function" not in m:
    m = m.replace(gather_anchor, calc_helper, 1); ch += 1

# 4) Wire markup field onchange to applyMarkup (modify the field render for markup only).
#    field() is generic; instead add an onchange by post-processing: replace the markup input id to include onchange.
mkold = 'id="lg_markup_percent" type="number"'
mknew = 'id="lg_markup_percent" type="number" onchange="LogisticsModule.applyMarkup()"'
if mkold in m and "applyMarkup()" not in m.split("onchange=")m = m.replace(mkold, mknew, 1); ch += 1

# 5) Table header: add Sale + Margin columns after Unit cost
hold = "<th>Unit cost</th><th>Value</th>"
hnew = "<th>Unit cost</th><th>Sale</th><th>Margin</th><th>Value</th>"
if hold in m and "<th>Sale</th>" not in m:
    m = m.replace(hold, hnew, 1); ch += 1

# 6) Table row: add sale + margin cells after unit cost cell
rold = "+'<td>'+self.money(cost)+'</td><td>'+self.money(qty*cost)+'</td>'"
rnew = ("+'<td>'+self.money(cost)+'</td>'"
        "+'<td>'+(Number(it.sale_price||0)>0?self.money(it.sale_price):'-')+'</td>'"
        "+'<td>'+((Number(it.sale_price||0)>0&&cost>0)?(self.money(Number(it.sale_price)-cost)+' ('+Math.round((Number(it.sale_price)-cost)/Number(it.sale_price)*100)+'%)'):'-')+'</td>'"
        "+'<td>'+self.money(qty*cost)+'</td>'")
if rold in m and "it.sale_price" not in m:
    m = m.replace(rold, rnew, 1); ch += 1

mp.write_text(m, encoding="utf-8")
print("Frontend changes applied:", ch)
