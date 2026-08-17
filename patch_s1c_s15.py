import shutil, re
from pathlib import Path
from datetime import datetime
stamp = datetime.now().strftime("%Y%m%d_%H%M%S")

# ================= BACKEND (S1.5) =================
ap = Path("api.py"); s = ap.read_text(encoding="utf-8")
shutil.copyfile("api.py", f"api.py.before_s15_{stamp}")
b = 0

# 1) add-deal: created override + stage_changed_at
d_old = '"notes": (p.get("notes") or "").strip(), "created_at": astraa_now_iso()}'
d_new = ('"notes": (p.get("notes") or "").strip(),\n'
         '            "created_at": ((p.get("created_override") or "").strip() or astraa_now_iso()),\n'
         '            "stage_changed_at": ((p.get("stage_changed_override") or "").strip() or (p.get("created_override") or "").strip() or astraa_now_iso())}')
if d_old in s and '"stage_changed_at"' not in s:
    s = s.replace(d_old, d_new, 1); b += 1

# 2) update-deal: stamp stage_changed_at when stage actually changes
u_old = '        if d.get("id") == p.get("id") and p.get("stage") in ASTRAA_DEAL_STAGES:\n            d["stage"] = p["stage"]'
u_new = ('        if d.get("id") == p.get("id") and p.get("stage") in ASTRAA_DEAL_STAGES:\n'
         '            if d.get("stage") != p["stage"]:\n'
         '                d["stage_changed_at"] = astraa_now_iso()\n'
         '            d["stage"] = p["stage"]')
if u_old in s and 'd["stage_changed_at"] = astraa_now_iso()' not in s:
    s = s.replace(u_old, u_new, 1); b += 1

ap.write_text(s, encoding="utf-8")
print(f"S1.5 backend changes: {b} (expected 2)")

# ================= FRONTEND (S1c + S1.5) =================
mp = Path("astraaspace/module_business.js"); m = mp.read_text(encoding="utf-8")
shutil.copyfile(mp, f"astraaspace/module_business.js.bak_s1c15_{stamp}")
c = 0

# S1c-1: rename nav label
n_old = "\U0001f4e3 Marketing &amp; Sales</a>"
n_new = "\U0001f4e3 Marketing</a>"
if n_old in m and n_new not in m:
    m = m.replace(n_old, n_new, 1); c += 1

# S1c-2: rename section heading
h_old = "'<h2 class=\"bw-h2\">Marketing & Sales</h2>'"
h_new = "'<h2 class=\"bw-h2\">Marketing</h2>'"
if h_old in m:
    m = m.replace(h_old, h_new, 1); c += 1

# S1c-3: remove the New Deal form block from renderMarketing (keep campaigns)
deal_block = ("'<div class=\"bw-panel\"><h3 class=\"bw-h3\">New Deal</h3>'\n"
    "      +'<div class=\"bw-f\"><label>Deal name</label><input id=\"dl_name\" style=\"'+f+'\"></div>'\n"
    "      +'<div class=\"bw-f\"><label>Client</label><input id=\"dl_client\" style=\"'+f+'\"></div>'\n"
    "      +'<div class=\"bw-f\"><label>Value ($)</label><input id=\"dl_value\" type=\"number\" step=\"0.01\" style=\"'+f+'\"></div>'\n"
    "      +'<button class=\"bw-add\" onclick=\"BusinessModule.addDeal()\">Add Deal</button>'\n"
    "      +'<h3 class=\"bw-h3\" style=\"margin-top:20px;\">New Campaign</h3>'")
deal_block_new = "'<div class=\"bw-panel\"><h3 class=\"bw-h3\">New Campaign</h3>'"
if deal_block in m:
    m = m.replace(deal_block, deal_block_new, 1); c += 1

# S1c-4: remove Deal Pipeline from the right panel (keep Campaigns list)
pipe_old = ("+'<div class=\"bw-panel\"><h3 class=\"bw-h3\">Deal Pipeline</h3><div id=\"dl_list\"></div>'\n"
    "      +'<h3 class=\"bw-h3\" style=\"margin-top:20px;\">Campaigns</h3><div id=\"cp_list\"></div></div>'")
pipe_new = "+'<div class=\"bw-panel\"><h3 class=\"bw-h3\">Campaigns</h3><div id=\"cp_list\"></div></div>'"
if pipe_old in m:
    m = m.replace(pipe_old, pipe_new, 1); c += 1

# S1.5-1: add "days in stage" badge into the Sales pipeline row (in refreshSales)
badge_anchor = 'if(x.expected_close)meta.push("\\ud83d\\udcc5 "+x.expected_close);'
badge_add = (badge_anchor + '\n'
    '        var _sc=x.stage_changed_at||x.created_at||"";\n'
    '        if(_sc){var _d=Math.floor((Date.now()-new Date(_sc).getTime())/86400000);'
    'if(!isNaN(_d)&&_d>=0){var _c=(_d>30?"#dc2626":(_d>14?"#eab308":"#64748b"));'
    'meta.push("<span style=\\"color:"+_c+";\\">\\u23f1 "+_d+"d in "+x.stage+"</span>");}}')
if badge_anchor in m and "d in "+"" not in m and "u23f1" not in m:
    m = m.replace(badge_anchor, badge_add, 1); c += 1

# S1.5-2: add collapsible "older deal" date override to the Sales New Deal form
form_anchor = "+'<div class=\"bw-f\"><label>Owner</label><input id=\"sd_owner\" style=\"'+f+'\"></div>'"
form_add = (form_anchor + '\n'
    "      +'<details style=\"margin:6px 0 10px;\"><summary style=\"cursor:pointer;color:#1d4ed8;font-size:.85rem;\">Adding an older deal? Set original dates</summary>'\n"
    "      +'<div class=\"bw-f\" style=\"margin-top:8px;\"><label>Deal started</label><input id=\"sd_created\" type=\"date\" style=\"'+f+'\"></div>'\n"
    "      +'<div class=\"bw-f\"><label>Entered current stage</label><input id=\"sd_stagedate\" type=\"date\" style=\"'+f+'\"></div></details>'")
if form_anchor in m and "sd_created" not in m:
    m = m.replace(form_anchor, form_add, 1); c += 1

# S1.5-3: pass the override dates in addSalesDeal
add_anchor = "owner:v('sd_owner')})"
add_new = "owner:v('sd_owner'),created_override:v('sd_created'),stage_changed_override:v('sd_stagedate')})"
if add_anchor in m and "created_override" not in m:
    m = m.replace(add_anchor, add_new, 1); c += 1
# also clear the new fields after add
clear_anchor = '["sd_name","sd_client","sd_value","sd_prob","sd_close","sd_owner"]'
clear_new = '["sd_name","sd_client","sd_value","sd_prob","sd_close","sd_owner","sd_created","sd_stagedate"]'
if clear_anchor in m:
    m = m.replace(clear_anchor, clear_new, 1); c += 1

mp.write_text(m, encoding="utf-8")
print(f"S1c + S1.5 frontend changes: {c} (expected 8)")
