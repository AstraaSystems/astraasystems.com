import shutil
from pathlib import Path
from datetime import datetime

p = Path("api.py")
s = p.read_text(encoding="utf-8")
stamp = datetime.now().strftime("%Y%m%d_%H%M%S")
shutil.copyfile("api.py", f"api.py.before_spec5a2_{stamp}")

changes = 0

# ---- PO RECEIVE: build (name,spec) index; match on it; carry spec into new items ----
recv_old = '''    inv = _astraa_load_logistics()
    items = inv.get(key, [])
    by_id = {it.get("id"): it for it in items}
    received_summary = []
    for ln in po.get("lines", []):
        qty = float(ln.get("quantity",0) or 0)
        cost = float(ln.get("unit_cost",0) or 0)
        iid = ln.get("item_id")
        if iid and iid in by_id:
            it = by_id[iid]
            it["quantity"] = round(float(it.get("quantity",0) or 0) + qty, 2)
            if cost > 0: it["unit_cost"] = round(cost, 2)
            it["updated_at"] = astraa_now_iso()
            received_summary.append({"name": it.get("name"), "added": qty})
        else:
            new_it = {"id": uuid.uuid4().hex[:12], "name": ln.get("name"),
                      "sku": "", "category": "General", "unit": "each",
                      "unit_cost": round(cost,2), "quantity": round(qty,2),
                      "location": "", "reorder_point": 0,
                      "supplier": po.get("supplier_name",""), "notes": "Created from PO",
                      "created_at": astraa_now_iso(), "updated_at": astraa_now_iso()}
            items.append(new_it)
            received_summary.append({"name": new_it["name"], "added": qty})
    inv[key] = items
    _astraa_save_logistics(inv)'''

recv_new = '''    inv = _astraa_load_logistics()
    items = inv.get(key, [])
    by_id = {it.get("id"): it for it in items}
    by_ns = {}
    for it in items:
        by_ns.setdefault(((it.get("name") or "").lower(), (it.get("specification") or "").lower()), it)
    received_summary = []
    for ln in po.get("lines", []):
        qty = float(ln.get("quantity",0) or 0)
        cost = float(ln.get("unit_cost",0) or 0)
        iid = ln.get("item_id")
        spec = (ln.get("specification") or "").strip()
        it = None
        if iid and iid in by_id:
            it = by_id[iid]
        else:
            it = by_ns.get(((ln.get("name") or "").lower(), spec.lower()))
        if it:
            it["quantity"] = round(float(it.get("quantity",0) or 0) + qty, 2)
            if cost > 0: it["unit_cost"] = round(cost, 2)
            it["updated_at"] = astraa_now_iso()
            received_summary.append({"name": it.get("name"), "specification": it.get("specification",""), "added": qty})
        else:
            new_it = {"id": uuid.uuid4().hex[:12], "name": ln.get("name"),
                      "sku": "", "specification": spec, "category": "General", "unit": "each",
                      "unit_cost": round(cost,2), "quantity": round(qty,2),
                      "location": "", "reorder_point": 0,
                      "supplier": po.get("supplier_name",""), "notes": "Created from PO",
                      "created_at": astraa_now_iso(), "updated_at": astraa_now_iso()}
            items.append(new_it)
            by_ns[((new_it["name"] or "").lower(), spec.lower())] = new_it
            received_summary.append({"name": new_it["name"], "specification": spec, "added": qty})
    inv[key] = items
    _astraa_save_logistics(inv)'''

if recv_old in s:
    s = s.replace(recv_old, recv_new, 1); changes += 1
    print("PO receive: variant matching applied")
else:
    print("PO receive: anchor NOT found")

# ---- DELIVERY DISPATCH: match on (name,spec) in both validate and deduct passes ----
disp_old = '''    inv = _astraa_load_logistics()
    items = inv.get(key, [])
    by_id = {it.get("id"): it for it in items}
    by_name = {}
    for it in items:
        by_name.setdefault((it.get("name") or "").lower(), it)
    # First pass: validate availability
    for ln in dv.get("lines", []):
        need = float(ln.get("quantity",0) or 0)
        it = by_id.get(ln.get("item_id")) or by_name.get((ln.get("name") or "").lower())
        have = float(it.get("quantity",0) or 0) if it else 0
        if not it:
            return astraa_json_response({"success": False, "error": "Item not in inventory: " + str(ln.get("name"))}, 400)
        if need > have:
            return astraa_json_response({"success": False, "error": "Not enough stock for " + str(ln.get("name")) + " (need " + str(need) + ", have " + str(have) + ")."}, 400)
    # Second pass: deduct
    for ln in dv.get("lines", []):
        need = float(ln.get("quantity",0) or 0)
        it = by_id.get(ln.get("item_id")) or by_name.get((ln.get("name") or "").lower())
        it["quantity"] = round(float(it.get("quantity",0) or 0) - need, 2)
        it["updated_at"] = astraa_now_iso()
    inv[key] = items
    _astraa_save_logistics(inv)'''

disp_new = '''    inv = _astraa_load_logistics()
    items = inv.get(key, [])
    by_id = {it.get("id"): it for it in items}
    by_ns = {}
    for it in items:
        by_ns.setdefault(((it.get("name") or "").lower(), (it.get("specification") or "").lower()), it)
    def _match(ln):
        iid = ln.get("item_id")
        if iid and iid in by_id: return by_id[iid]
        return by_ns.get(((ln.get("name") or "").lower(), (ln.get("specification") or "").lower()))
    def _label(ln):
        sp = (ln.get("specification") or "").strip()
        return str(ln.get("name")) + (" (" + sp + ")" if sp else "")
    # First pass: validate availability
    for ln in dv.get("lines", []):
        need = float(ln.get("quantity",0) or 0)
        it = _match(ln)
        have = float(it.get("quantity",0) or 0) if it else 0
        if not it:
            return astraa_json_response({"success": False, "error": "Item not in inventory: " + _label(ln)}, 400)
        if need > have:
            return astraa_json_response({"success": False, "error": "Not enough stock for " + _label(ln) + " (need " + str(need) + ", have " + str(have) + ")."}, 400)
    # Second pass: deduct
    for ln in dv.get("lines", []):
        need = float(ln.get("quantity",0) or 0)
        it = _match(ln)
        it["quantity"] = round(float(it.get("quantity",0) or 0) - need, 2)
        it["updated_at"] = astraa_now_iso()
    inv[key] = items
    _astraa_save_logistics(inv)'''

if disp_old in s:
    s = s.replace(disp_old, disp_new, 1); changes += 1
    print("Delivery dispatch: variant matching applied")
else:
    print("Delivery dispatch: anchor NOT found")

p.write_text(s, encoding="utf-8")
print("Total changes:", changes, "(expected 2)")
