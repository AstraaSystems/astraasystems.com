import shutil
from pathlib import Path
from datetime import datetime
stamp = datetime.now().strftime("%Y%m%d_%H%M%S")
ap = Path("api.py"); s = ap.read_text(encoding="utf-8")
shutil.copyfile("api.py", f"api.py.before_s2a_{stamp}")
b = 0

# 1) extend deal record with activities[] + next-action fields
d_old = ('            "stage_changed_at": ((p.get("stage_changed_override") or "").strip() or (p.get("created_override") or "").strip() or astraa_now_iso())}')
d_new = ('            "stage_changed_at": ((p.get("stage_changed_override") or "").strip() or (p.get("created_override") or "").strip() or astraa_now_iso()),\n'
         '            "activities": [],\n'
         '            "next_action": (p.get("next_action") or "").strip(),\n'
         '            "next_action_date": (p.get("next_action_date") or "").strip(),\n'
         '            "last_activity_at": ""}')
if d_old in s and '"activities": []' not in s:
    s = s.replace(d_old, d_new, 1); b += 1

# 2) new route: log activity + optionally set next action
anchor = '@app.route("/api/marketing/delete-deal", methods=["POST"])'
route = '''@app.route("/api/marketing/deal-activity", methods=["POST"])
def astraa_mkt_deal_activity():
    identity = astraa_resolve_session_identity(request)
    if not identity:
        return astraa_json_response({"success": False, "error": "Not authenticated."}, 401)
    email = identity.get("account_email")
    p = astraa_get_request_json() or {}
    did = p.get("id")
    db, key = _astraa_mkt_bucket(email)
    deal = next((d for d in db[key]["deals"] if d.get("id") == did), None)
    if not deal:
        return astraa_json_response({"success": False, "error": "Deal not found."}, 404)
    # log an activity entry (if provided)
    atype = (p.get("activity_type") or "").strip()
    anote = (p.get("activity_note") or "").strip()
    if atype or anote:
        deal.setdefault("activities", [])
        entry = {"id": uuid.uuid4().hex[:8],
                 "type": (atype or "Note"),
                 "note": anote,
                 "at": astraa_now_iso()}
        deal["activities"].append(entry)
        deal["last_activity_at"] = entry["at"]
    # set / update next action (if provided)
    if "next_action" in p:
        deal["next_action"] = (p.get("next_action") or "").strip()
    if "next_action_date" in p:
        deal["next_action_date"] = (p.get("next_action_date") or "").strip()
    deal["updated_at"] = astraa_now_iso()
    _astraa_save_mkt(db)
    return astraa_json_response({"success": True, "deal": deal})

'''
if anchor in s and "astraa_mkt_deal_activity" not in s:
    s = s.replace(anchor, route + anchor, 1); b += 1

ap.write_text(s, encoding="utf-8")
print(f"S2a backend changes: {b} (expected 2)")
