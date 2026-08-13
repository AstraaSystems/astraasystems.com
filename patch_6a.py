import shutil
from pathlib import Path
from datetime import datetime
stamp = datetime.now().strftime("%Y%m%d_%H%M%S")

ap = Path("api.py"); s = ap.read_text(encoding="utf-8")
shutil.copyfile("api.py", f"api.py.before_6a_{stamp}")
b = 0

anchor = 'ASTRAA_LOG_PO_STORE = os.path.join("astraa_data", "astraa_logistics_po.json")'
block = anchor + '''
ASTRAA_LOG_ORDERS_STORE = os.path.join("astraa_data", "astraa_logistics_orders.json")

def _astraa_order_total(order):
    t = 0.0
    for ln in order.get("lines", []):
        try:
            t += float(ln.get("quantity",0) or 0) * float(ln.get("sale_price",0) or 0)
        except Exception:
            pass
    return round(t, 2)

def _astraa_order_clean_lines(raw):
    lines = []
    for ln in (raw or []):
        nm = (ln.get("name") or "").strip()
        if not nm: continue
        try: q = float(ln.get("quantity") or 0)
        except Exception: q = 0.0
        try: sp = float(ln.get("sale_price") or 0)
        except Exception: sp = 0.0
        lines.append({"item_id": (ln.get("item_id") or "").strip(),
                      "name": nm,
                      "specification": (ln.get("specification") or "").strip(),
                      "quantity": round(q,2),
                      "sale_price": round(sp,2)})
    return lines

@app.route("/api/logistics/orders/list", methods=["GET"])
def astraa_log_orders_list():
    identity = astraa_resolve_session_identity(request)
    if not identity:
        return astraa_json_response({"success": False, "error": "Not authenticated."}, 401)
    key = astraa_account_key(identity.get("account_email"))
    db = _astraa_load_json_store(ASTRAA_LOG_ORDERS_STORE)
    orders = sorted(db.get(key, []), key=lambda x: x.get("created_at",""), reverse=True)
    for o in orders:
        o["total"] = _astraa_order_total(o)
    pending_value = sum(_astraa_order_total(o) for o in orders if o.get("status") == "Pending")
    return astraa_json_response({"success": True, "orders": orders,
        "summary": {"draft": sum(1 for o in orders if o.get("status")=="Draft"),
                    "pending": sum(1 for o in orders if o.get("status")=="Pending"),
                    "fulfilled": sum(1 for o in orders if o.get("status")=="Fulfilled"),
                    "pending_value": round(pending_value,2),
                    "total_orders": len(orders)}})

@app.route("/api/logistics/orders/add", methods=["POST"])
def astraa_log_orders_add():
    identity = astraa_resolve_session_identity(request)
    if not identity:
        return astraa_json_response({"success": False, "error": "Not authenticated."}, 401)
    key = astraa_account_key(identity.get("account_email"))
    p = astraa_get_request_json() or {}
    order = {
        "id": uuid.uuid4().hex[:12],
        "customer": (p.get("customer") or "").strip(),
        "status": "Draft",
        "notes": (p.get("notes") or "").strip(),
        "lines": _astraa_order_clean_lines(p.get("lines")),
        "created_at": astraa_now_iso(),
        "updated_at": astraa_now_iso()
    }
    db = _astraa_load_json_store(ASTRAA_LOG_ORDERS_STORE)
    db.setdefault(key, []).append(order)
    _astraa_save_json_store(ASTRAA_LOG_ORDERS_STORE, db)
    return astraa_json_response({"success": True, "order": order})

@app.route("/api/logistics/orders/delete", methods=["POST"])
def astraa_log_orders_delete():
    identity = astraa_resolve_session_identity(request)
    if not identity:
        return astraa_json_response({"success": False, "error": "Not authenticated."}, 401)
    key = astraa_account_key(identity.get("account_email"))
    p = astraa_get_request_json() or {}
    oid = p.get("id")
    db = _astraa_load_json_store(ASTRAA_LOG_ORDERS_STORE)
    items = db.get(key, [])
    newitems = [x for x in items if x.get("id") != oid]
    if len(newitems) == len(items):
        return astraa_json_response({"success": False, "error": "Order not found."}, 404)
    db[key] = newitems
    _astraa_save_json_store(ASTRAA_LOG_ORDERS_STORE, db)
    return astraa_json_response({"success": True})
'''
if anchor in s and "ASTRAA_LOG_ORDERS_STORE" not in s:
    s = s.replace(anchor, block, 1); b += 1

ap.write_text(s, encoding="utf-8")
print(f"6a backend changes: {b} (expected 1)")
