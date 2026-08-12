import shutil
from pathlib import Path
from datetime import datetime
stamp = datetime.now().strftime("%Y%m%d_%H%M%S")

# ---------- BACKEND ----------
ap = Path("api.py"); s = ap.read_text(encoding="utf-8")
shutil.copyfile("api.py", f"api.py.before_5c2_{stamp}")
b = 0

# 1) Insert the on-order helper right before the list route
anchor = '@app.route("/api/logistics/list", methods=["GET"])\ndef astraa_logistics_list():'
helper = '''def _astraa_logistics_on_order(items, pos):
    """Annotate each item with on_order (sum of open-PO line qty) and on_order_eta (earliest expected_date)."""
    incoming = {}
    eta = {}
    def line_keys(ln):
        ks = []
        iid = (ln.get("item_id") or "").strip()
        if iid: ks.append(("id", iid))
        nm = (ln.get("name") or "").strip().lower()
        sp = (ln.get("specification") or "").strip().lower()
        if nm: ks.append(("ns", nm, sp))
        return ks
    for po in pos:
        if po.get("status") == "Received":
            continue
        exp = (po.get("expected_date") or "").strip()
        for ln in po.get("lines", []):
            try: q = float(ln.get("quantity", 0) or 0)
            except Exception: q = 0.0
            if q <= 0: continue
            for k in line_keys(ln):
                incoming[k] = incoming.get(k, 0.0) + q
                if exp:
                    cur = eta.get(k)
                    if (cur is None) or (exp < cur): eta[k] = exp
    for it in items:
        idk = ("id", (it.get("id") or "").strip())
        nsk = ("ns", (it.get("name") or "").strip().lower(), (it.get("specification") or "").strip().lower())
        if idk in incoming:
            it["on_order"] = round(incoming[idk], 2); it["on_order_eta"] = eta.get(idk, "")
        elif nsk in incoming:
            it["on_order"] = round(incoming[nsk], 2); it["on_order_eta"] = eta.get(nsk, "")
        else:
            it["on_order"] = 0.0; it["on_order_eta"] = ""
    return items

'''
if anchor in s and "_astraa_logistics_on_order" not in s:
    s = s.replace(anchor, helper + anchor, 1); b += 1

# 2) Wire it into the list route (annotate after sort)
sort_old = '    items_sorted = sorted(items, key=lambda x: x.get("name", "").lower())'
sort_new = (sort_old + '\n'
            '    try:\n'
            '        _po_db = _astraa_load_json_store(ASTRAA_LOG_PO_STORE)\n'
            '        items_sorted = _astraa_logistics_on_order(items_sorted, _po_db.get(key, []))\n'
            '    except Exception:\n'
            '        pass')
if sort_old in s and "_astraa_logistics_on_order(items_sorted" not in s:
    s = s.replace(sort_old, sort_new, 1); b += 1

ap.write_text(s, encoding="utf-8")
print(f"Backend changes: {b} (expected 2)")

# ---------- FRONTEND ----------
mp = Path("astraaspace/module_logistics.js"); m = mp.read_text(encoding="utf-8")
shutil.copyfile(mp, f"astraaspace/module_logistics.js.bak_5c2_{stamp}")
ch = 0

# 1) header: On-Order + ETA after Available
h_old = "<th>Reserved</th><th>Available</th><th>Unit cost</th>"
h_new = "<th>Reserved</th><th>Available</th><th>On-Order</th><th>ETA</th><th>Unit cost</th>"
if h_old in m and "<th>On-Order</th>" not in m:
    m = m.replace(h_old, h_new, 1); ch += 1

# 2) row vars: on-order + eta + overdue tint
v_old = "var low=(rp>0&&available<=rp);"
v_new = (v_old +
    "var onOrder=Number(it.on_order||0);var eta=(it.on_order_eta||'');"
    "var onOrderTxt=(onOrder>0?'+'+onOrder:'—');var onOrderColor=(onOrder>0?'#2563eb':'#94a3b8');"
    "var etaTxt=(eta?eta:'—');var etaOverdue=false;"
    "if(eta){var _t=new Date(eta+'T00:00:00');var _n=new Date();_n.setHours(0,0,0,0);etaOverdue=(_t<_n);}"
    "var etaColor=(etaOverdue?'#dc2626':'#334155');")
if v_old in m and "var onOrder=Number(it.on_order" not in m:
    m = m.replace(v_old, v_new, 1); ch += 1

# 3) row cells: On-Order + ETA after the Available cell
c_old = "+'<td style=\"color:'+availColor+';font-weight:600\">'+available+'</td>'"
c_new = (c_old +
    "\n        +'<td style=\"color:'+onOrderColor+';font-weight:600\">'+onOrderTxt+'</td>'"
    "+'<td style=\"color:'+etaColor+'\">'+etaTxt+'</td>'")
if c_old in m and "onOrderColor" not in m.split("var onOrderColor")[0] and "+onOrderTxt+'</td>'" not in m:
    m = m.replace(c_old, c_new, 1); ch += 1

mp.write_text(m, encoding="utf-8")
print(f"Frontend changes: {ch} (expected 3)")
