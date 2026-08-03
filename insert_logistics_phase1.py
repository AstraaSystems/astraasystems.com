import shutil
from pathlib import Path
from datetime import datetime

p = Path("api.py")
s = p.read_text(encoding="utf-8")
stamp = datetime.now().strftime("%Y%m%d_%H%M%S")
shutil.copyfile("api.py", f"api.py.before_logistics1_{stamp}")

anchor = "# ===== ASTRAA RESEARCH ANALYST (read-only, cross-tool, what-if capable) ====="
if s.count(anchor) != 1:
    print("ABORT: anchor not found exactly once:", s.count(anchor)); raise SystemExit

block = r'''# ===== ASTRAA LOGISTICS - PHASE 1: INVENTORY CORE (hidden/coming-soon) =====
ASTRAA_LOGISTICS_STORE = os.path.join("astraa_data", "astraa_logistics.json")

def _astraa_load_logistics():
    try:
        with open(ASTRAA_LOGISTICS_STORE, "r", encoding="utf-8") as f:
            return json.load(f)
    except Exception:
        return {}

def _astraa_save_logistics(d):
    os.makedirs("astraa_data", exist_ok=True)
    tmp = ASTRAA_LOGISTICS_STORE + ".tmp"
    with open(tmp, "w", encoding="utf-8") as f:
        json.dump(d, f)
    os.replace(tmp, ASTRAA_LOGISTICS_STORE)

def _astraa_logistics_summary(items):
    total_value = 0.0
    low = 0
    for it in items:
        qty = float(it.get("quantity", 0) or 0)
        cost = float(it.get("unit_cost", 0) or 0)
        total_value += qty * cost
        rp = float(it.get("reorder_point", 0) or 0)
        if rp > 0 and qty <= rp:
            low += 1
    return {
        "item_count": len(items),
        "total_value": round(total_value, 2),
        "low_stock_count": low
    }

def _astraa_logistics_clean(p):
    def num(v):
        try: return float(v)
        except Exception: return 0.0
    return {
        "name": (p.get("name") or "").strip(),
        "sku": (p.get("sku") or "").strip(),
        "category": (p.get("category") or "General").strip(),
        "unit": (p.get("unit") or "each").strip(),
        "unit_cost": round(num(p.get("unit_cost")), 2),
        "quantity": round(num(p.get("quantity")), 2),
        "location": (p.get("location") or "").strip(),
        "reorder_point": round(num(p.get("reorder_point")), 2),
        "supplier": (p.get("supplier") or "").strip(),
        "notes": (p.get("notes") or "").strip()
    }

@app.route("/api/logistics/list", methods=["GET"])
def astraa_logistics_list():
    identity = astraa_resolve_session_identity(request)
    if not identity:
        return astraa_json_response({"success": False, "error": "Not authenticated."}, 401)
    email = identity.get("account_email"); key = astraa_account_key(email)
    db = _astraa_load_logistics()
    items = db.get(key, [])
    items_sorted = sorted(items, key=lambda x: x.get("name", "").lower())
    return astraa_json_response({"success": True, "items": items_sorted,
                                 "summary": _astraa_logistics_summary(items)})

@app.route("/api/logistics/add", methods=["POST"])
def astraa_logistics_add():
    identity = astraa_resolve_session_identity(request)
    if not identity:
        return astraa_json_response({"success": False, "error": "Not authenticated."}, 401)
    email = identity.get("account_email"); key = astraa_account_key(email)
    p = astraa_get_request_json() or {}
    item = _astraa_logistics_clean(p)
    if not item["name"]:
        return astraa_json_response({"success": False, "error": "Item name is required."}, 400)
    item["id"] = uuid.uuid4().hex[:12]
    item["created_at"] = astraa_now_iso()
    item["updated_at"] = astraa_now_iso()
    db = _astraa_load_logistics()
    db.setdefault(key, []).append(item)
    _astraa_save_logistics(db)
    return astraa_json_response({"success": True, "item": item})

@app.route("/api/logistics/update", methods=["POST"])
def astraa_logistics_update():
    identity = astraa_resolve_session_identity(request)
    if not identity:
        return astraa_json_response({"success": False, "error": "Not authenticated."}, 401)
    email = identity.get("account_email"); key = astraa_account_key(email)
    p = astraa_get_request_json() or {}
    iid = p.get("id")
    db = _astraa_load_logistics(); items = db.get(key, [])
    found = None
    for it in items:
        if it.get("id") == iid:
            fields = _astraa_logistics_clean(p)
            if not fields["name"]:
                return astraa_json_response({"success": False, "error": "Item name is required."}, 400)
            it.update(fields)
            it["updated_at"] = astraa_now_iso()
            found = it
            break
    if not found:
        return astraa_json_response({"success": False, "error": "Item not found."}, 404)
    _astraa_save_logistics(db)
    return astraa_json_response({"success": True, "item": found})

@app.route("/api/logistics/adjust", methods=["POST"])
def astraa_logistics_adjust():
    identity = astraa_resolve_session_identity(request)
    if not identity:
        return astraa_json_response({"success": False, "error": "Not authenticated."}, 401)
    email = identity.get("account_email"); key = astraa_account_key(email)
    p = astraa_get_request_json() or {}
    iid = p.get("id")
    try:
        delta = float(p.get("delta") or 0)
    except Exception:
        delta = 0
    db = _astraa_load_logistics(); items = db.get(key, [])
    found = None
    for it in items:
        if it.get("id") == iid:
            newq = float(it.get("quantity", 0) or 0) + delta
            if newq < 0: newq = 0
            it["quantity"] = round(newq, 2)
            it["updated_at"] = astraa_now_iso()
            found = it
            break
    if not found:
        return astraa_json_response({"success": False, "error": "Item not found."}, 404)
    _astraa_save_logistics(db)
    return astraa_json_response({"success": True, "item": found})

@app.route("/api/logistics/delete", methods=["POST"])
def astraa_logistics_delete():
    identity = astraa_resolve_session_identity(request)
    if not identity:
        return astraa_json_response({"success": False, "error": "Not authenticated."}, 401)
    email = identity.get("account_email"); key = astraa_account_key(email)
    p = astraa_get_request_json() or {}
    iid = p.get("id")
    db = _astraa_load_logistics(); items = db.get(key, [])
    newitems = [it for it in items if it.get("id") != iid]
    if len(newitems) == len(items):
        return astraa_json_response({"success": False, "error": "Item not found."}, 404)
    db[key] = newitems
    _astraa_save_logistics(db)
    return astraa_json_response({"success": True})
# ===== END ASTRAA LOGISTICS PHASE 1 =====

'''

s = s.replace(anchor, block + anchor, 1)
p.write_text(s, encoding="utf-8")
print("Logistics Phase 1 backend inserted. Backup: api.py.before_logistics1_" + stamp)
