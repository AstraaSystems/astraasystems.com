import shutil
from pathlib import Path
from datetime import datetime
stamp = datetime.now().strftime("%Y%m%d_%H%M%S")

ap = Path("api.py"); s = ap.read_text(encoding="utf-8")
shutil.copyfile("api.py", f"api.py.before_6c_{stamp}")
b = 0

# Insert confirm + cancel routes right before the orders delete route
anchor = '@app.route("/api/logistics/orders/delete", methods=["POST"])'
block = '''def _astraa_order_apply_reservation(order, inv_items, direction):
    """direction=+1 reserves, -1 releases. Records per-order reservation deltas for exact reversal."""
    by_id = {}
    for it in inv_items:
        iid = (it.get("id") or "").strip()
        if iid: by_id[iid] = it
    by_ns = {}
    for it in inv_items:
        by_ns.setdefault(((it.get("name") or "").lower(), (it.get("specification") or "").lower()), it)
    applied = {}
    for ln in order.get("lines", []):
        it = _astraa_order_match_item(ln, inv_items, by_id, by_ns)
        if not it: continue
        try: q = float(ln.get("quantity",0) or 0)
        except Exception: q = 0.0
        if q <= 0: continue
        cur = float(it.get("reserved",0) or 0)
        newres = cur + (direction * q)
        if newres < 0: newres = 0.0
        it["reserved"] = round(newres,2)
        it["updated_at"] = astraa_now_iso()
        iid = it.get("id","")
        applied[iid] = round(applied.get(iid,0.0) + q,2)
    return applied

@app.route("/api/logistics/orders/confirm", methods=["POST"])
def astraa_log_orders_confirm():
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
    if order.get("status") != "Draft":
        return astraa_json_response({"success": False, "error": "Only draft orders can be confirmed."}, 400)
    inv = _astraa_load_logistics()
    inv_items = inv.get(key, [])
    applied = _astraa_order_apply_reservation(order, inv_items, +1)
    inv[key] = inv_items
    _astraa_save_logistics(inv)
    order["status"] = "Pending"
    order["reservations"] = applied
    order["confirmed_at"] = astraa_now_iso()
    order["updated_at"] = astraa_now_iso()
    _astraa_save_json_store(ASTRAA_LOG_ORDERS_STORE, db)
    return astraa_json_response({"success": True, "order": order, "reserved": applied})

@app.route("/api/logistics/orders/cancel", methods=["POST"])
def astraa_log_orders_cancel():
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
    if order.get("status") == "Fulfilled":
        return astraa_json_response({"success": False, "error": "Fulfilled orders cannot be cancelled."}, 400)
    if order.get("status") == "Pending":
        inv = _astraa_load_logistics()
        inv_items = inv.get(key, [])
        by_id = {}
        for it in inv_items:
            iid = (it.get("id") or "").strip()
            if iid: by_id[iid] = it
        for iid, qty in (order.get("reservations") or {}).items():
            it = by_id.get(iid)
            if it:
                cur = float(it.get("reserved",0) or 0)
                nr = cur - float(qty or 0)
                it["reserved"] = round(nr if nr>0 else 0.0,2)
                it["updated_at"] = astraa_now_iso()
        inv[key] = inv_items
        _astraa_save_logistics(inv)
    order["status"] = "Cancelled"
    order["reservations"] = {}
    order["cancelled_at"] = astraa_now_iso()
    order["updated_at"] = astraa_now_iso()
    _astraa_save_json_store(ASTRAA_LOG_ORDERS_STORE, db)
    return astraa_json_response({"success": True, "order": order})

'''
if anchor in s and "astraa_log_orders_confirm" not in s:
    s = s.replace(anchor, block + anchor, 1); b += 1

ap.write_text(s, encoding="utf-8")
print(f"6c backend changes: {b} (expected 1)")
