import shutil
from pathlib import Path
from datetime import datetime
stamp = datetime.now().strftime("%Y%m%d_%H%M%S")

ap = Path("api.py"); s = ap.read_text(encoding="utf-8")
shutil.copyfile("api.py", f"api.py.before_6e_{stamp}")
b = 0

anchor = '''    _astraa_save_json_store(ASTRAA_LOG_ORDERS_STORE, db)
    return astraa_json_response({"success": True, "order": order,
                                 "fulfilled": fulfilled_summary, "shortfalls": shortfalls})'''

replacement = '''    # PHASE 6e: auto-log a spec-aware sales invoice into Finance (non-fatal)
    invoice_logged = False
    if p.get("log_income", True):
        try:
            _amt = _astraa_order_total(order)
            if _amt > 0:
                _parts = []
                for _ln in order.get("lines", []):
                    _nm = (_ln.get("name") or "").strip()
                    if not _nm: continue
                    _sp = (_ln.get("specification") or "").strip()
                    _label = _nm + ((" (" + _sp + ")") if _sp else "")
                    try: _q = float(_ln.get("quantity",0) or 0)
                    except Exception: _q = 0.0
                    try: _pr = float(_ln.get("sale_price",0) or 0)
                    except Exception: _pr = 0.0
                    _parts.append(_label + " x" + str(int(_q) if _q==int(_q) else _q) + " @ $" + format(_pr, ".2f"))
                _email = identity.get("account_email")
                _client = order.get("customer","").strip() or "Walk-in Customer"
                _inv = {"id": uuid.uuid4().hex[:12],
                        "client": _client,
                        "description": "Sales Order #" + str(order.get("id","")) + " - " + "; ".join(_parts),
                        "amount": round(_amt, 2),
                        "status": "Pending",
                        "comment": "Auto-logged from Sales Order",
                        "date": datetime.now().strftime("%Y-%m-%d"),
                        "created_at": astraa_now_iso()}
                _fdb, _fkey = _astraa_fin_bucket(_email)
                _fdb[_fkey]["invoices"].append(_inv)
                _astraa_save_fin(_fdb)
                order["invoice_id"] = _inv["id"]
                invoice_logged = True
        except Exception:
            invoice_logged = False

    _astraa_save_json_store(ASTRAA_LOG_ORDERS_STORE, db)
    return astraa_json_response({"success": True, "order": order,
                                 "fulfilled": fulfilled_summary, "shortfalls": shortfalls,
                                 "invoice_logged": invoice_logged})'''

if anchor in s and 'PHASE 6e' not in s:
    s = s.replace(anchor, replacement, 1); b += 1

ap.write_text(s, encoding="utf-8")
print(f"6e backend changes: {b} (expected 1)")
