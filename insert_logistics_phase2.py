import shutil
from pathlib import Path
from datetime import datetime

p = Path("api.py")
s = p.read_text(encoding="utf-8")
stamp = datetime.now().strftime("%Y%m%d_%H%M%S")
shutil.copyfile("api.py", f"api.py.before_logistics2_{stamp}")

anchor = "# ===== END ASTRAA LOGISTICS PHASE 1 ====="
if s.count(anchor) != 1:
    print("ABORT: Phase 1 end marker not found exactly once:", s.count(anchor)); raise SystemExit

block = r'''
# ===== ASTRAA LOGISTICS - PHASE 2: SUPPLIERS & PURCHASE ORDERS (hidden) =====
ASTRAA_LOG_SUPPLIERS_STORE = os.path.join("astraa_data", "astraa_logistics_suppliers.json")
ASTRAA_LOG_PO_STORE = os.path.join("astraa_data", "astraa_logistics_po.json")

def _astraa_load_json_store(path):
    try:
        with open(path, "r", encoding="utf-8") as f:
            return json.load(f)
    except Exception:
        return {}

def _astraa_save_json_store(path, d):
    os.makedirs("astraa_data", exist_ok=True)
    tmp = path + ".tmp"
    with open(tmp, "w", encoding="utf-8") as f:
        json.dump(d, f)
    os.replace(tmp, path)

# ---- Suppliers ----
@app.route("/api/logistics/suppliers/list", methods=["GET"])
def astraa_log_suppliers_list():
    identity = astraa_resolve_session_identity(request)
    if not identity:
        return astraa_json_response({"success": False, "error": "Not authenticated."}, 401)
    key = astraa_account_key(identity.get("account_email"))
    db = _astraa_load_json_store(ASTRAA_LOG_SUPPLIERS_STORE)
    items = sorted(db.get(key, []), key=lambda x: x.get("name","").lower())
    return astraa_json_response({"success": True, "suppliers": items})

@app.route("/api/logistics/suppliers/add", methods=["POST"])
def astraa_log_suppliers_add():
    identity = astraa_resolve_session_identity(request)
    if not identity:
        return astraa_json_response({"success": False, "error": "Not authenticated."}, 401)
    key = astraa_account_key(identity.get("account_email"))
    p = astraa_get_request_json() or {}
    name = (p.get("name") or "").strip()
    if not name:
        return astraa_json_response({"success": False, "error": "Supplier name is required."}, 400)
    sup = {"id": uuid.uuid4().hex[:12], "name": name,
           "contact": (p.get("contact") or "").strip(),
           "email": (p.get("email") or "").strip(),
           "phone": (p.get("phone") or "").strip(),
           "notes": (p.get("notes") or "").strip(),
           "created_at": astraa_now_iso()}
    db = _astraa_load_json_store(ASTRAA_LOG_SUPPLIERS_STORE)
    db.setdefault(key, []).append(sup)
    _astraa_save_json_store(ASTRAA_LOG_SUPPLIERS_STORE, db)
    return astraa_json_response({"success": True, "supplier": sup})

@app.route("/api/logistics/suppliers/delete", methods=["POST"])
def astraa_log_suppliers_delete():
    identity = astraa_resolve_session_identity(request)
    if not identity:
        return astraa_json_response({"success": False, "error": "Not authenticated."}, 401)
    key = astraa_account_key(identity.get("account_email"))
    p = astraa_get_request_json() or {}
    sid = p.get("id")
    db = _astraa_load_json_store(ASTRAA_LOG_SUPPLIERS_STORE)
    items = db.get(key, [])
    newitems = [x for x in items if x.get("id") != sid]
    if len(newitems) == len(items):
        return astraa_json_response({"success": False, "error": "Supplier not found."}, 404)
    db[key] = newitems
    _astraa_save_json_store(ASTRAA_LOG_SUPPLIERS_STORE, db)
    return astraa_json_response({"success": True})

# ---- Purchase Orders ----
def _astraa_po_total(po):
    t = 0.0
    for ln in po.get("lines", []):
        try:
            t += float(ln.get("quantity",0) or 0) * float(ln.get("unit_cost",0) or 0)
        except Exception:
            pass
    return round(t, 2)

@app.route("/api/logistics/po/list", methods=["GET"])
def astraa_log_po_list():
    identity = astraa_resolve_session_identity(request)
    if not identity:
        return astraa_json_response({"success": False, "error": "Not authenticated."}, 401)
    key = astraa_account_key(identity.get("account_email"))
    db = _astraa_load_json_store(ASTRAA_LOG_PO_STORE)
    pos = sorted(db.get(key, []), key=lambda x: x.get("created_at",""), reverse=True)
    for po in pos:
        po["total"] = _astraa_po_total(po)
    open_value = sum(_astraa_po_total(po) for po in pos if po.get("status") != "Received")
    return astraa_json_response({"success": True, "orders": pos,
        "summary": {"open_orders": sum(1 for po in pos if po.get("status")!="Received"),
                    "open_value": round(open_value,2), "total_orders": len(pos)}})

@app.route("/api/logistics/po/add", methods=["POST"])
def astraa_log_po_add():
    identity = astraa_resolve_session_identity(request)
    if not identity:
        return astraa_json_response({"success": False, "error": "Not authenticated."}, 401)
    key = astraa_account_key(identity.get("account_email"))
    p = astraa_get_request_json() or {}
    supplier_name = (p.get("supplier_name") or "").strip()
    if not supplier_name:
        return astraa_json_response({"success": False, "error": "Supplier is required."}, 400)
    raw_lines = p.get("lines") or []
    lines = []
    for ln in raw_lines:
        nm = (ln.get("name") or "").strip()
        if not nm:
            continue
        def num(v):
            try: return float(v)
            except Exception: return 0.0
        lines.append({"item_id": (ln.get("item_id") or "").strip(),
                      "name": nm, "quantity": round(num(ln.get("quantity")),2),
                      "unit_cost": round(num(ln.get("unit_cost")),2)})
    if not lines:
        return astraa_json_response({"success": False, "error": "Add at least one line item."}, 400)
    po = {"id": uuid.uuid4().hex[:12],
          "supplier_id": (p.get("supplier_id") or "").strip(),
          "supplier_name": supplier_name,
          "status": "Ordered",
          "expected_date": (p.get("expected_date") or "").strip(),
          "notes": (p.get("notes") or "").strip(),
          "lines": lines,
          "created_at": astraa_now_iso(), "updated_at": astraa_now_iso()}
    db = _astraa_load_json_store(ASTRAA_LOG_PO_STORE)
    db.setdefault(key, []).append(po)
    _astraa_save_json_store(ASTRAA_LOG_PO_STORE, db)
    po["total"] = _astraa_po_total(po)
    return astraa_json_response({"success": True, "order": po})

@app.route("/api/logistics/po/receive", methods=["POST"])
def astraa_log_po_receive():
    identity = astraa_resolve_session_identity(request)
    if not identity:
        return astraa_json_response({"success": False, "error": "Not authenticated."}, 401)
    email = identity.get("account_email"); key = astraa_account_key(email)
    p = astraa_get_request_json() or {}
    pid = p.get("id")
    db = _astraa_load_json_store(ASTRAA_LOG_PO_STORE)
    pos = db.get(key, [])
    po = None
    for x in pos:
        if x.get("id") == pid: po = x; break
    if not po:
        return astraa_json_response({"success": False, "error": "Order not found."}, 404)
    if po.get("status") == "Received":
        return astraa_json_response({"success": False, "error": "Order already received."}, 400)

    # Increase inventory stock for matching items (by item_id, else create new item)
    inv = _astraa_load_logistics()
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
    _astraa_save_logistics(inv)

    po["status"] = "Received"
    po["received_at"] = astraa_now_iso()
    po["updated_at"] = astraa_now_iso()
    _astraa_save_json_store(ASTRAA_LOG_PO_STORE, db)
    return astraa_json_response({"success": True, "order": po, "received": received_summary})

@app.route("/api/logistics/po/delete", methods=["POST"])
def astraa_log_po_delete():
    identity = astraa_resolve_session_identity(request)
    if not identity:
        return astraa_json_response({"success": False, "error": "Not authenticated."}, 401)
    key = astraa_account_key(identity.get("account_email"))
    p = astraa_get_request_json() or {}
    pid = p.get("id")
    db = _astraa_load_json_store(ASTRAA_LOG_PO_STORE)
    pos = db.get(key, [])
    newpos = [x for x in pos if x.get("id") != pid]
    if len(newpos) == len(pos):
        return astraa_json_response({"success": False, "error": "Order not found."}, 404)
    db[key] = newpos
    _astraa_save_json_store(ASTRAA_LOG_PO_STORE, db)
    return astraa_json_response({"success": True})
# ===== END ASTRAA LOGISTICS PHASE 2 =====
'''

s = s.replace(anchor, anchor + block, 1)
p.write_text(s, encoding="utf-8")
print("Phase 2 backend inserted. Backup: api.py.before_logistics2_" + stamp)
