import shutil
from pathlib import Path
from datetime import datetime
stamp = datetime.now().strftime("%Y%m%d_%H%M%S")
ap = Path("api.py"); s = ap.read_text(encoding="utf-8")
shutil.copyfile("api.py", f"api.py.before_s1a_{stamp}")
b = 0

# 1) extend the deal record on add (probability, expected_close, owner)
d_old = 'deal = {"id": uuid.uuid4().hex[:12], "name": name, "client": (p.get("client") or "").strip(),'
d_new = ('deal = {"id": uuid.uuid4().hex[:12], "name": name, "client": (p.get("client") or "").strip(),\n'
         '            "probability": _astraa_deal_prob(p.get("stage") or "Lead", p.get("probability")),\n'
         '            "expected_close": (p.get("expected_close") or "").strip(),\n'
         '            "owner": (p.get("owner") or "").strip(),')
if d_old in s and '"probability":' not in s:
    s = s.replace(d_old, d_new, 1); b += 1

# 2) helper: stage->default probability (so weighted works even without manual entry)
anchor = '@app.route("/api/marketing/add-deal", methods=["POST"])'
helper = '''ASTRAA_STAGE_PROB = {"Lead":10,"Qualified":30,"Proposal":50,"Negotiation":75,"Won":100,"Lost":0}
def _astraa_deal_prob(stage, override):
    try:
        if override is not None and str(override).strip() != "":
            v = float(override)
            return max(0.0, min(100.0, v))
    except Exception:
        pass
    return float(ASTRAA_STAGE_PROB.get(stage, 10))

'''
if anchor in s and "_astraa_deal_prob" not in s:
    s = s.replace(anchor, helper + anchor, 1); b += 1

# 3) update-deal: recompute probability if stage changes
u_old = '    for d in db[key]["deals"]:'
u_new = ('    for d in db[key]["deals"]:\n'
         '        if d.get("id")==p.get("id"):\n'
         '            if p.get("stage"): d["probability"]=_astraa_deal_prob(p["stage"], p.get("probability"))\n'
         '            if "expected_close" in p: d["expected_close"]=(p.get("expected_close") or "").strip()\n'
         '            if "owner" in p: d["owner"]=(p.get("owner") or "").strip()')
if u_old in s and 'd["probability"]=_astraa_deal_prob' not in s:
    s = s.replace(u_old, u_new, 1); b += 1

# 4) summary: add weighted_pipeline
w_old = '"total_deals": len(deals),'
w_new = ('"total_deals": len(deals),\n'
         '            "weighted_pipeline": round(sum(float(d.get("value",0) or 0)*float(d.get("probability", _astraa_deal_prob(d.get("stage","Lead"), None)))/100.0 for d in deals if d.get("stage") not in ("Won","Lost")), 2),')
if w_old in s and '"weighted_pipeline":' not in s:
    s = s.replace(w_old, w_new, 1); b += 1

ap.write_text(s, encoding="utf-8")
print(f"S1a backend changes: {b} (expected 4)")
