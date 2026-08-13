import shutil
from pathlib import Path
from datetime import datetime
stamp = datetime.now().strftime("%Y%m%d_%H%M%S")

ap = Path("api.py"); s = ap.read_text(encoding="utf-8")
shutil.copyfile("api.py", f"api.py.before_6b_{stamp}")
b = 0

# 1) Insert the resolver helper right before the orders list route
anchor = '@app.route("/api/logistics/orders/list", methods=["GET"])'
helper = '''def _astraa_order_match_item(ln, items, by_id=None, by_ns=None):
    """Resolve an order line to an inventory item: prefer item_id, then name+spec (variant-accurate)."""
    if by_id is None:
        by_id = {}
        for it in items:
            iid = (it.get("id") or "").strip()
            if iid: by_id[iid] = it
    if by_ns is None:
        by_ns = {}
        for it in items:
            by_ns.setdefault(((it.get("name") or "").lower(), (it.get("specification") or "").lower()), it)
    iid = (ln.get("item_id") or "").strip()
    if iid and iid in by_id:
        return by_id[iid]
    return by_ns.get(((ln.get("name") or "").lower(), (ln.get("specification") or "").lower()))

def _astraa_order_annotate(order, items):
    """Attach matched item id, on-hand, reserved and available to each order line (read-only view)."""
    by_id = {}
    for it in items:
        iid = (it.get("id") or "").strip()
        if iid: by_id[iid] = it
    by_ns = {}
    for it in items:
        by_ns.setdefault(((it.get("name") or "").lower(), (it.get("specification") or "").lower()), it)
    for ln in order.get("lines", []):
        it = _astraa_order_match_item(ln, items, by_id, by_ns)
        if it:
            qty = float(it.get("quantity",0) or 0)
            res = float(it.get("reserved",0) or 0)
            ln["matched"] = True
            ln["matched_item_id"] = it.get("id","")
            ln["on_hand"] = round(qty,2)
            ln["item_reserved"] = round(res,2)
            ln["available"] = round(qty - res,2)
            try: want = float(ln.get("quantity",0) or 0)
            except Exception: want = 0.0
            ln["shortfall"] = round(max(0.0, want - (qty - res)),2)
        else:
            ln["matched"] = False
            ln["matched_item_id"] = ""
            ln["on_hand"] = 0.0
            ln["item_reserved"] = 0.0
            ln["available"] = 0.0
            ln["shortfall"] = round(float(ln.get("quantity",0) or 0),2)
    return order

'''
if anchor in s and "_astraa_order_annotate" not in s:
    s = s.replace(anchor, helper + anchor, 1); b += 1

# 2) Wire annotation into the orders list route (annotate each order against live inventory)
list_old = '''    orders = sorted(db.get(key, []), key=lambda x: x.get("created_at",""), reverse=True)
    for o in orders:
        o["total"] = _astraa_order_total(o)'''
list_new = '''    orders = sorted(db.get(key, []), key=lambda x: x.get("created_at",""), reverse=True)
    _inv_db = _astraa_load_logistics()
    _inv_items = _inv_db.get(key, [])
    for o in orders:
        o["total"] = _astraa_order_total(o)
        _astraa_order_annotate(o, _inv_items)'''
if list_old in s and "_astraa_order_annotate(o, _inv_items)" not in s:
    s = s.replace(list_old, list_new, 1); b += 1

ap.write_text(s, encoding="utf-8")
print(f"6b backend changes: {b} (expected 2)")
