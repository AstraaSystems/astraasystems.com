import shutil
from pathlib import Path
from datetime import datetime

p = Path("api.py")
s = p.read_text(encoding="utf-8")
stamp = datetime.now().strftime("%Y%m%d_%H%M%S")
shutil.copyfile("api.py", f"api.py.before_phase4a_{stamp}")

# Anchor: the PO receive function saves the PO then returns. Inject before that return.
anchor = ('    po["status"] = "Received"\n'
          '    po["received_at"] = astraa_now_iso()\n'
          '    po["updated_at"] = astraa_now_iso()\n'
          '    _astraa_save_json_store(ASTRAA_LOG_PO_STORE, db)\n'
          '    return astraa_json_response({"success": True, "order": po, "received": received_summary})')

if anchor not in s:
    print("ABORT: PO receive anchor not found"); raise SystemExit

new = ('    po["status"] = "Received"\n'
       '    po["received_at"] = astraa_now_iso()\n'
       '    po["updated_at"] = astraa_now_iso()\n'
       '    _astraa_save_json_store(ASTRAA_LOG_PO_STORE, db)\n'
       '\n'
       '    # PHASE 4a: auto-log the PO cost as an Expense (non-fatal)\n'
       '    expense_logged = False\n'
       '    if p.get("log_expense", True):\n'
       '        try:\n'
       '            total = _astraa_po_total(po)\n'
       '            if total > 0:\n'
       '                from datetime import datetime as _dt\n'
       '                entry = {"id": uuid.uuid4().hex[:12],\n'
       '                         "date": _dt.now().strftime("%Y-%m-%d"),\n'
       '                         "category": "Materials",\n'
       '                         "amount": round(total, 2),\n'
       '                         "vendor": po.get("supplier_name", ""),\n'
       '                         "project": "",\n'
       '                         "notes": "Auto-logged from Logistics PO",\n'
       '                         "created_at": astraa_now_iso()}\n'
       '                edb = _astraa_load_expenses()\n'
       '                edb.setdefault(key, []).append(entry)\n'
       '                _astraa_save_expenses(edb)\n'
       '                expense_logged = True\n'
       '        except Exception:\n'
       '            expense_logged = False\n'
       '\n'
       '    return astraa_json_response({"success": True, "order": po, "received": received_summary, "expense_logged": expense_logged})')

s = s.replace(anchor, new, 1)
p.write_text(s, encoding="utf-8")
print("Phase 4a inserted. Backup: api.py.before_phase4a_" + stamp)
