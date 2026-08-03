import shutil
from pathlib import Path
from datetime import datetime

p = Path("api.py")
s = p.read_text(encoding="utf-8")
stamp = datetime.now().strftime("%Y%m%d_%H%M%S")
shutil.copyfile("api.py", f"api.py.before_logistics3_{stamp}")

anchor = "# ===== END ASTRAA LOGISTICS PHASE 2 ====="
if s.count(anchor) != 1:
    print("ABORT: Phase 2 end marker not found exactly once:", s.count(anchor)); raise SystemExit

block = r'''
# ===== ASTRAA LOGISTICS - PHASE 3: DELIVERIES / SHIPMENTS (hidden) =====
ASTRAA_LOG_DELIVERY_STORE = os.path.join("astraa_data", "astraa_logistics_delivery.json")

def _astraa_delivery_qty(d):
    t = 0.0
    for ln in d.get("lines", []):
        try: t += float(ln.get("quantity",0) or 0)
        except Exception: pass
    return t

@app.route("/api/logistics/delivery/list", methods=["GET"])
def astraa_log_delivery_list():
    identity = astraa_resolve_session_identity(request)
    if not identity:
        return astraa_json_response({"success": False, "error": "Not authenticated."}, 401)
    key = astraa_account_key(identity.get("account_email"))
    db = _astraa_load_json_store(ASTRAA_LOG_DELIVERY_STORE)
    ds = sorted(db.get(key, []), key=lambda x: x.get("created_at",""), reverse=True)
    pending = sum(1 for d in ds if d.get("status") == "Pending")
    transit = sum(1 for d in ds if d.get("status") == "In Transit")
    delivered = sum(1 for d in ds if d.get("status") == "Delivered")
    return astraa_json_response({"success": True, "deliveries": ds,
        "summary": {"pending": pending, "in_transit": transit,
                    "delivered": delivered, "total": len(ds)}})

@app.route("/api/logistics/delivery/add", methods=["POST"])
def astraa_log_delivery_add():
    identity = astraa_resolve_session_identity(request)
    if not identity:
        return astraa_json_response({"success": False, "error": "Not authenticated."}, 401)
    key = astraa_account_key(identity.get("account_email"))
    p = astraa_get_request_json() or {}
    dest = (p.get("destination") or "").strip()
    if not dest:
        return astraa_json_response({"success": False, "error": "Destination is required."}, 400)
    raw = p.get("lines") or []
    lines = []
    for ln in raw:
        nm = (ln.get("name") or "").strip()
        if not nm: continue
        try: q = float(ln.get("quantity") or 0)
        except Exception: q = 0
        lines.append({"item_id": (ln.get("item_id") or "").strip(), "name": nm, "quantity": round(q,2)})
    if not lines:
        return astraa_json_response({"success": False, "error": "Add at least one item to deliver."}, 400)
    dv = {"id": uuid.uuid4().hex[:12], "destination": dest,
          "project": (p.get("project") or "").strip(),
          "status": "Pending",
          "dispatch_date": "", "eta": (p.get("eta") or "").strip(),
          "notes": (p.get("notes") or "").strip(),
          "lines": lines, "created_at": astraa_now_iso(), "updated_at": astraa_now_iso()}
    db = _astraa_load_json_store(ASTRAA_LOG_DELIVERY_STORE)
    db.setdefault(key, []).append(dv)
    _astraa_save_json_store(ASTRAA_LOG_DELIVERY_STORE, db)
    return astraa_json_response({"success": True, "delivery": dv})

@app.route("/api/logistics/delivery/dispatch", methods=["POST"])
def astraa_log_delivery_dispatch():
    identity = astraa_resolve_session_identity(request)
    if not identity:
        return astraa_json_response({"success": False, "error": "Not authenticated."}, 401)
    email = identity.get("account_email"); key = astraa_account_key(email)
    p = astraa_get_request_json() or {}
    did = p.get("id")
    db = _astraa_load_json_store(ASTRAA_LOG_DELIVERY_STORE)
    ds = db.get(key, []); dv = None
    for x in ds:
        if x.get("id") == did: dv = x; break
    if not dv:
        return astraa_json_response({"success": False, "error": "Delivery not found."}, 404)
    if dv.get("status") != "Pending":
        return astraa_json_response({"success": False, "error": "Only pending deliveries can be dispatched."}, 400)

    # Deduct stock from inventory; block if insufficient
    inv = _astraa_load_logistics()
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
    _astraa_save_logistics(inv)

    dv["status"] = "In Transit"
    dv["dispatch_date"] = astraa_today_key()
    dv["updated_at"] = astraa_now_iso()
    _astraa_save_json_store(ASTRAA_LOG_DELIVERY_STORE, db)
    return astraa_json_response({"success": True, "delivery": dv})

@app.route("/api/logistics/delivery/complete", methods=["POST"])
def astraa_log_delivery_complete():
    identity = astraa_resolve_session_identity(request)
    if not identity:
        return astraa_json_response({"success": False, "error": "Not authenticated."}, 401)
    key = astraa_account_key(identity.get("account_email"))
    p = astraa_get_request_json() or {}
    did = p.get("id")
    db = _astraa_load_json_store(ASTRAA_LOG_DELIVERY_STORE)
    ds = db.get(key, []); dv = None
    for x in ds:
        if x.get("id") == did: dv = x; break
    if not dv:
        return astraa_json_response({"success": False, "error": "Delivery not found."}, 404)
    if dv.get("status") not in ("In Transit", "Pending"):
        return astraa_json_response({"success": False, "error": "Delivery already completed."}, 400)
    dv["status"] = "Delivered"
    dv["delivered_at"] = astraa_now_iso()
    dv["updated_at"] = astraa_now_iso()
    _astraa_save_json_store(ASTRAA_LOG_DELIVERY_STORE, db)
    return astraa_json_response({"success": True, "delivery": dv})

@app.route("/api/logistics/delivery/delete", methods=["POST"])
def astraa_log_delivery_delete():
    identity = astraa_resolve_session_identity(request)
    if not identity:
        return astraa_json_response({"success": False, "error": "Not authenticated."}, 401)
    key = astraa_account_key(identity.get("account_email"))
    p = astraa_get_request_json() or {}
    did = p.get("id")
    db = _astraa_load_json_store(ASTRAA_LOG_DELIVERY_STORE)
    ds = db.get(key, [])
    new = [x for x in ds if x.get("id") != did]
    if len(new) == len(ds):
        return astraa_json_response({"success": False, "error": "Delivery not found."}, 404)
    db[key] = new
    _astraa_save_json_store(ASTRAA_LOG_DELIVERY_STORE, db)
    return astraa_json_response({"success": True})
# ===== END ASTRAA LOGISTICS PHASE 3 =====
'''

s = s.replace(anchor, anchor + block, 1)
p.write_text(s, encoding="utf-8")
print("Phase 3 backend inserted. Backup: api.py.before_logistics3_" + stamp)
