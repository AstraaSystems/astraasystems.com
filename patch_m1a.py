import shutil
from pathlib import Path
from datetime import datetime
stamp = datetime.now().strftime("%Y%m%d_%H%M%S")
ap = Path("api.py"); s = ap.read_text(encoding="utf-8")
shutil.copyfile("api.py", f"api.py.before_m1a_{stamp}")
b = 0

# 1) extend campaign record: spend, start/end dates, leads
c_old = ('    camp = {"id": uuid.uuid4().hex[:12], "name": name, "channel": (p.get("channel") or "Other").strip(),\n'
         '            "budget": round(budget,2), "status": (p.get("status") or "Active").strip(),\n'
         '            "results": (p.get("results") or "").strip(), "created_at": astraa_now_iso()}')
c_new = ('    try: spend = float(p.get("spend") or 0)\n'
         '    except Exception: spend = 0\n'
         '    try: leads = int(float(p.get("leads") or 0))\n'
         '    except Exception: leads = 0\n'
         '    camp = {"id": uuid.uuid4().hex[:12], "name": name, "channel": (p.get("channel") or "Other").strip(),\n'
         '            "budget": round(budget,2), "spend": round(spend,2), "leads": leads,\n'
         '            "start_date": (p.get("start_date") or "").strip(), "end_date": (p.get("end_date") or "").strip(),\n'
         '            "status": (p.get("status") or "Active").strip(),\n'
         '            "results": (p.get("results") or "").strip(), "created_at": astraa_now_iso()}')
if c_old in s and '"spend": round(spend,2)' not in s:
    s = s.replace(c_old, c_new, 1); b += 1

# 2) new route: log spend / update leads on a campaign
anchor = '@app.route("/api/marketing/delete-campaign", methods=["POST"])'
route = '''@app.route("/api/marketing/campaign-update", methods=["POST"])
def astraa_mkt_campaign_update():
    identity = astraa_resolve_session_identity(request)
    if not identity:
        return astraa_json_response({"success": False, "error": "Not authenticated."}, 401)
    email = identity.get("account_email")
    p = astraa_get_request_json() or {}
    cid = p.get("id")
    db, key = _astraa_mkt_bucket(email)
    camp = next((c for c in db[key]["campaigns"] if c.get("id") == cid), None)
    if not camp:
        return astraa_json_response({"success": False, "error": "Campaign not found."}, 404)
    # add spend (incremental) if provided
    if p.get("add_spend") not in (None, ""):
        try:
            camp["spend"] = round(float(camp.get("spend", 0) or 0) + float(p.get("add_spend")), 2)
        except Exception:
            pass
    # set absolute fields if provided
    for fld in ("budget", "spend"):
        if p.get(fld) not in (None, ""):
            try: camp[fld] = round(float(p.get(fld)), 2)
            except Exception: pass
    if p.get("leads") not in (None, ""):
        try: camp["leads"] = int(float(p.get("leads")))
        except Exception: pass
    for fld in ("status", "start_date", "end_date"):
        if fld in p:
            camp[fld] = (p.get(fld) or "").strip()
    camp["updated_at"] = astraa_now_iso()
    _astraa_save_mkt(db)
    return astraa_json_response({"success": True, "campaign": camp})

'''
if anchor in s and "astraa_mkt_campaign_update" not in s:
    s = s.replace(anchor, route + anchor, 1); b += 1

# 3) enrich summary: total spend, total budget, remaining, cost-per-lead
sum_old = '            "active_campaigns": active_campaigns'
sum_new = ('            "active_campaigns": active_campaigns,\n'
    '            "total_budget": round(sum(float(c.get("budget",0) or 0) for c in campaigns), 2),\n'
    '            "total_spend": round(sum(float(c.get("spend",0) or 0) for c in campaigns), 2),\n'
    '            "budget_remaining": round(sum(float(c.get("budget",0) or 0) for c in campaigns) - sum(float(c.get("spend",0) or 0) for c in campaigns), 2),\n'
    '            "total_leads": int(sum(int(c.get("leads",0) or 0) for c in campaigns)),\n'
    '            "cost_per_lead": (round(sum(float(c.get("spend",0) or 0) for c in campaigns) / sum(int(c.get("leads",0) or 0) for c in campaigns), 2) if sum(int(c.get("leads",0) or 0) for c in campaigns) > 0 else 0)')
if sum_old in s and '"total_spend"' not in s:
    s = s.replace(sum_old, sum_new, 1); b += 1

ap.write_text(s, encoding="utf-8")
print(f"M1a backend changes: {b} (expected 3)")
