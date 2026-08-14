from pathlib import Path

p = Path("api.py")
s = p.read_text()

marker = "# ASTRAA_BUSINESS_SALES_MVP_V1"
if marker in s:
    print("Sales API block already exists. No patch needed.")
    raise SystemExit(0)

anchor = "# ASTRAA_MARKETING_MVP_V1"
if anchor not in s:
    print("ERROR: Marketing anchor not found. Cannot safely insert Sales API block.")
    raise SystemExit(1)

block = r'''
# ASTRAA_BUSINESS_SALES_MVP_V1 — opportunities + sales pipeline
# Separate department from Marketing. This is for Business > Sales, not Logistics Sales Orders.

import uuid as _astraa_sales_uuid
from datetime import datetime as _astraa_sales_datetime

ASTRAA_SALES_STORE_PATH = os.path.join("astraa_data", "astraa_sales.json")

def astraa_sales_now_iso():
    return _astraa_sales_datetime.utcnow().isoformat() + "Z"

def astraa_sales_load_store():
    try:
        os.makedirs(os.path.dirname(ASTRAA_SALES_STORE_PATH), exist_ok=True)
        if not os.path.exists(ASTRAA_SALES_STORE_PATH):
            return {}
        with open(ASTRAA_SALES_STORE_PATH, "r", encoding="utf-8") as f:
            data = json.load(f)
        return data if isinstance(data, dict) else {}
    except Exception:
        return {}

def astraa_sales_save_store(data):
    os.makedirs(os.path.dirname(ASTRAA_SALES_STORE_PATH), exist_ok=True)
    with open(ASTRAA_SALES_STORE_PATH, "w", encoding="utf-8") as f:
        json.dump(data, f, indent=2)

def astraa_sales_identity_or_response():
    identity = astraa_resolve_session_identity(request)
    if not identity:
        return None, (jsonify({
            "success": False,
            "error": "Not authenticated."
        }), 401)

    account_email = identity.get("account_email") or identity.get("account_id")
    if not account_email:
        return None, (jsonify({
            "success": False,
            "error": "No account identity available."
        }), 401)

    return account_email, None

def astraa_sales_clean_text(value):
    return str(value or "").strip()

def astraa_sales_float(value, default=0.0):
    try:
        if value is None or value == "":
            return default
        return float(value)
    except Exception:
        return default

@app.route("/api/sales/list", methods=["GET"])
def astraa_sales_list():
    account_email, error_response = astraa_sales_identity_or_response()
    if error_response:
        return error_response

    store = astraa_sales_load_store()
    records = store.get(account_email, [])
    if not isinstance(records, list):
        records = []

    return jsonify({
        "success": True,
        "items": records,
        "opportunities": records
    }), 200

@app.route("/api/sales/add", methods=["POST"])
def astraa_sales_add():
    account_email, error_response = astraa_sales_identity_or_response()
    if error_response:
        return error_response

    payload = request.get_json(silent=True) or {}

    title = (
        astraa_sales_clean_text(payload.get("title"))
        or astraa_sales_clean_text(payload.get("opportunity"))
        or astraa_sales_clean_text(payload.get("name"))
        or "Untitled opportunity"
    )

    item = {
        "id": _astraa_sales_uuid.uuid4().hex[:12],
        "title": title,
        "company": astraa_sales_clean_text(payload.get("company")),
        "client": astraa_sales_clean_text(payload.get("client")),
        "contact": astraa_sales_clean_text(payload.get("contact")),
        "stage": astraa_sales_clean_text(payload.get("stage")) or "Prospecting",
        "value": astraa_sales_float(payload.get("value"), 0.0),
        "probability": astraa_sales_float(payload.get("probability"), 0.0),
        "expected_close": astraa_sales_clean_text(payload.get("expected_close") or payload.get("close_date")),
        "source": astraa_sales_clean_text(payload.get("source")),
        "owner": astraa_sales_clean_text(payload.get("owner")),
        "notes": astraa_sales_clean_text(payload.get("notes")),
        "created_at": astraa_sales_now_iso(),
        "updated_at": astraa_sales_now_iso()
    }

    store = astraa_sales_load_store()
    records = store.get(account_email, [])
    if not isinstance(records, list):
        records = []

    records.append(item)
    store[account_email] = records
    astraa_sales_save_store(store)

    return jsonify({
        "success": True,
        "item": item
    }), 200

@app.route("/api/sales/update", methods=["POST"])
def astraa_sales_update():
    account_email, error_response = astraa_sales_identity_or_response()
    if error_response:
        return error_response

    payload = request.get_json(silent=True) or {}
    item_id = astraa_sales_clean_text(payload.get("id"))

    if not item_id:
        return jsonify({
            "success": False,
            "error": "Sales opportunity id is required."
        }), 400

    store = astraa_sales_load_store()
    records = store.get(account_email, [])
    if not isinstance(records, list):
        records = []

    updated_item = None
    allowed = {
        "title", "opportunity", "name", "company", "client", "contact",
        "stage", "value", "probability", "expected_close", "close_date",
        "source", "owner", "notes"
    }

    for item in records:
        if str(item.get("id")) == item_id:
            if "title" in payload or "opportunity" in payload or "name" in payload:
                item["title"] = (
                    astraa_sales_clean_text(payload.get("title"))
                    or astraa_sales_clean_text(payload.get("opportunity"))
                    or astraa_sales_clean_text(payload.get("name"))
                    or item.get("title", "Untitled opportunity")
                )
            for key in allowed:
                if key in payload and key not in {"title", "opportunity", "name", "close_date"}:
                    if key in {"value", "probability"}:
                        item[key] = astraa_sales_float(payload.get(key), 0.0)
                    else:
                        item[key] = astraa_sales_clean_text(payload.get(key))
            if "close_date" in payload:
                item["expected_close"] = astraa_sales_clean_text(payload.get("close_date"))
            item["updated_at"] = astraa_sales_now_iso()
            updated_item = item
            break

    if not updated_item:
        return jsonify({
            "success": False,
            "error": "Sales opportunity not found."
        }), 404

    store[account_email] = records
    astraa_sales_save_store(store)

    return jsonify({
        "success": True,
        "item": updated_item
    }), 200

@app.route("/api/sales/delete", methods=["POST"])
def astraa_sales_delete():
    account_email, error_response = astraa_sales_identity_or_response()
    if error_response:
        return error_response

    payload = request.get_json(silent=True) or {}
    item_id = astraa_sales_clean_text(payload.get("id"))

    if not item_id:
        return jsonify({
            "success": False,
            "error": "Sales opportunity id is required."
        }), 400

    store = astraa_sales_load_store()
    records = store.get(account_email, [])
    if not isinstance(records, list):
        records = []

    before = len(records)
    records = [item for item in records if str(item.get("id")) != item_id]

    if len(records) == before:
        return jsonify({
            "success": False,
            "error": "Sales opportunity not found."
        }), 404

    store[account_email] = records
    astraa_sales_save_store(store)

    return jsonify({
        "success": True,
        "deleted_id": item_id
    }), 200

# ASTRAA_BUSINESS_SALES_MVP_V1_END

'''

s = s.replace(anchor, block + "\n" + anchor)

p.write_text(s)
print("Inserted Business Sales API block before Marketing MVP.")
