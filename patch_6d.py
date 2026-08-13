import shutil
from pathlib import Path
from datetime import datetime
stamp = datetime.now().strftime("%Y%m%d_%H%M%S")

ap = Path("api.py"); s = ap.read_text(encoding="utf-8")
shutil.copyfile("api.py", f"api.py.before_6d_{stamp}")
b = 0

# Insert fulfill route right before the orders cancel route
anchor = '@app.route("/api/logistics/orders/cancel", methods=["POST"])'
block = '''@app.route("/api/logistics/orders/fulfill", methods=["POST"])
def astraa_log_orders_fulfill():
    identity = astraa_resolve_session_identity(request)
    if not identity:
        return astraa_json_response({"success": False, "error": "Not authenticated."}, 401)
    key = astraa_account_key(identity.get("account_email"))
    p = astraa_get_request_json() or {}
    oid = p.get("id")
    db = _astraa_load_json_store(ASTRAA_LOG_ORDERS_STORE)
    orders = db.get(key, [])
    order = next((o for o in orders if o.get("id")==oid), None)
    if not order:
        return astraa_json_response({"success": False, "error": "Order not found."}, 404)
    if order.get("status") not in ("Draft", "Pending"):
        return astraa_json_response({"success": False, "error": "Only draft or pending orders can be fulfilled."}, 400)

    inv = _astraa_load_logistics()
    inv_items = inv.get(key, [])
    by_id = {}
    for it in inv_items:
        iid = (it.get("id") or "").strip()
        if iid: by_id[iid] = it
    by_ns = {}
    for it in inv_items:
        by_ns.setdefault(((it.get("name") or "").lower(), (it.get("specification") or "").lower()), it)

    reservations = order.get("reservations") or {}
    fulfilled_summary = []
    shortfalls = []
    for ln in order.get("lines", []):
        it = _astraa_order_match_item(ln, inv_items, by_id, by_ns)
        try: want = float(ln.get("quantity",0) or 0)
        except Exception: want = 0.0
        if want <= 0: continue
        if not it:
            shortfalls.append({"name": ln.get("name",""), "specification": ln.get("specification",""), "requested": want, "shipped": 0, "short": want})
            continue
        iid = it.get("id","")
        # release any reservation this order held for the item
        held = float(reservations.get(iid, 0) or 0)
        if held > 0:
            cur_res = float(it.get("reserved",0) or 0)
            nr = cur_res - held
            it["reserved"] = round(nr if nr>0 else 0.0, 2)
        # reduce on-hand; allow going negative-in-effect via recorded shortfall (no hard block)
        on_hand = float(it.get("quantity",0) or 0)
        shipped = want if want <= on_hand else on_hand
        short = round(want - shipped, 2)
        it["quantity"] = round(on_hand - shipped, 2)
        it["updated_at"] = astraa_now_iso()
        fulfilled_summary.append({"name": it.get("name"), "specification": it.get("specification",""), "shipped": round(shipped,2)})
        if short > 0:
            shortfalls.append({"name": it.get("name"), "specification": it.get("specification",""), "requested": want, "shipped": round(shipped,2), "short": short})

    inv[key] = inv_items
    _astraa_save_logistics(inv)

    order["status"] = "Fulfilled"
    order["reservations"] = {}
    order["shortfalls"] = shortfalls
    order["fulfilled_at"] = astraa_now_iso()
    order["updated_at"] = astraa_now_iso()
    _astraa_save_json_store(ASTRAA_LOG_ORDERS_STORE, db)
    return astraa_json_response({"success": True, "order": order,
                                 "fulfilled": fulfilled_summary, "shortfalls": shortfalls})

'''
if anchor in s and "astraa_log_orders_fulfill" not in s:
    s = s.replace(anchor, block + anchor, 1); b += 1

ap.write_text(s, encoding="utf-8")
print(f"6d backend changes: {b} (expected 1)")
