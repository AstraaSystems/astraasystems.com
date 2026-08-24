import shutil
from pathlib import Path
from datetime import datetime
stamp = datetime.now().strftime("%Y%m%d_%H%M%S")
mp = Path("astraaspace/module_business.js"); m = mp.read_text(encoding="utf-8")
shutil.copyfile(mp, f"astraaspace/module_business.js.bak_m1b_{stamp}")
ch = 0

# 1) Add spend / leads / dates fields to the New Campaign form (after Budget field)
f_old = "+'<div class=\"bw-f\"><label>Budget ($)</label><input id=\"cp_budget\" type=\"number\" step=\"0.01\" style=\"'+f+'\"></div>'"
f_new = (f_old + "\n"
    "      +'<div class=\"bw-f\"><label>Spend so far ($)</label><input id=\"cp_spend\" type=\"number\" step=\"0.01\" style=\"'+f+'\"></div>'\n"
    "      +'<div class=\"bw-f\"><label>Leads generated</label><input id=\"cp_leads\" type=\"number\" step=\"1\" style=\"'+f+'\"></div>'\n"
    "      +'<div class=\"bw-f\"><label>Start date</label><input id=\"cp_start\" type=\"date\" style=\"'+f+'\"></div>'\n"
    "      +'<div class=\"bw-f\"><label>End date</label><input id=\"cp_end\" type=\"date\" style=\"'+f+'\"></div>'")
if f_old in m and 'cp_spend' not in m:
    m = m.replace(f_old, f_new, 1); ch += 1

# 2) Marketing KPI summary -> spend-focused (replace the 4 stat cards)
k_old = ('"<div class=\'bw-stat\'><span class=\'bw-stat-l\'>Open Pipeline</span><span class=\'bw-stat-v\'>"+money(s.open_value)+"</span></div>"\n'
    '        +"<div class=\'bw-stat\'><span class=\'bw-stat-l\'>Won Revenue</span><span class=\'bw-stat-v\'>"+money(s.won_value)+"</span></div>"\n'
    '        +"<div class=\'bw-stat\'><span class=\'bw-stat-l\'>Total Deals</span><span class=\'bw-stat-v\'>"+(s.total_deals||0)+"</span></div>"\n'
    '        +"<div class=\'bw-stat\'><span class=\'bw-stat-l\'>Active Campaigns</span><span class=\'bw-stat-v\'>"+(s.active_campaigns||0)+"</span></div>";')
k_new = ('"<div class=\'bw-stat\'><span class=\'bw-stat-l\'>Total Budget</span><span class=\'bw-stat-v\'>"+money(s.total_budget)+"</span></div>"\n'
    '        +"<div class=\'bw-stat\'><span class=\'bw-stat-l\'>Total Spend</span><span class=\'bw-stat-v\' style=\'color:#dc2626;\'>"+money(s.total_spend)+"</span></div>"\n'
    '        +"<div class=\'bw-stat\'><span class=\'bw-stat-l\'>Leads</span><span class=\'bw-stat-v\'>"+(s.total_leads||0)+"</span></div>"\n'
    '        +"<div class=\'bw-stat\'><span class=\'bw-stat-l\'>Cost / Lead</span><span class=\'bw-stat-v\' style=\'color:#1d4ed8;\'>"+money(s.cost_per_lead)+"</span></div>";')
if k_old in m and "Cost / Lead" not in m:
    m = m.replace(k_old, k_new, 1); ch += 1

# 3) Campaign card -> budget-vs-spend bar + leads + CPL + inline log-spend
c_old = ("return \"<div class='bw-lead'><div class='bw-proj-top'><div><b>\"+c.name+\"</b> <span class='bw-muted'>\\u00b7 \"+c.channel+\"</span></div><button class='bw-del' onclick=\\\"BusinessModule.delCampaign('\"+c.id+\"')\\\">\\u2715</button></div><div class='bw-muted' style='font-size:12px;'>Budget \"+money(c.budget)+\" \\u00b7 \"+c.status+\"</div></div>\";")
c_new = ("var _b=Number(c.budget||0),_sp=Number(c.spend||0),_ld=Number(c.leads||0);"
    "var _pct=(_b>0?Math.min(100,Math.round(_sp/_b*100)):0);"
    "var _barc=(_pct>=100?'#dc2626':(_pct>=80?'#eab308':'#16a34a'));"
    "var _cpl=(_ld>0?(_sp/_ld):0);"
    "return \"<div class='bw-lead'><div class='bw-proj-top'><div><b>\"+c.name+\"</b> <span class='bw-muted'>\\u00b7 \"+c.channel+\"</span></div><button class='bw-del' onclick=\\\"BusinessModule.delCampaign('\"+c.id+\"')\\\">\\u2715</button></div>\""
    "+\"<div class='bw-muted' style='font-size:12px;margin-top:4px;'>\"+money(_sp)+\" of \"+money(_b)+\" spent \\u00b7 \"+_ld+\" leads \\u00b7 \"+(_ld>0?money(_cpl)+\"/lead\":\"no leads yet\")+\"</div>\""
    "+\"<div style='height:7px;background:#f1f5f9;border-radius:4px;margin:6px 0;overflow:hidden;'><div style='height:100%;width:\"+_pct+\"%;background:\"+_barc+\";'></div></div>\""
    "+\"<div style='display:flex;gap:6px;flex-wrap:wrap;margin-top:4px;'>\""
    "+\"<input id='cs_amt_'+c.id placeholder='+ spend' style='width:80px;padding:4px;border:1px solid #e2e8f0;border-radius:6px;font-size:12px;'>\""
    "+\"<input id='cl_amt_'+c.id placeholder='set leads' style='width:80px;padding:4px;border:1px solid #e2e8f0;border-radius:6px;font-size:12px;'>\""
    "+\"<button class='bw-btn' style='font-size:12px;padding:4px 10px;' onclick=\\\"BusinessModule.updateCampaign('\"+c.id+\"')\\\">Update</button>\""
    "+\"<span class='bw-muted' style='font-size:11px;align-self:center;'>\"+(c.status||'')+(c.end_date?(' \\u00b7 ends '+c.end_date):'')+\"</span></div></div>\";")
if c_old in m and "updateCampaign" not in m:
    m = m.replace(c_old, c_new, 1); ch += 1

# 4) addCampaign: send spend/leads/dates
a_old = "body:JSON.stringify({name:v('cp_name'),channel:v('cp_channel'),budget:parseFloat(v('cp_budget'))||0,status:\"Active\"})"
a_new = ("body:JSON.stringify({name:v('cp_name'),channel:v('cp_channel'),budget:parseFloat(v('cp_budget'))||0,"
         "spend:parseFloat(v('cp_spend'))||0,leads:parseInt(v('cp_leads'))||0,start_date:v('cp_start'),end_date:v('cp_end'),status:\"Active\"})")
if a_old in m and "spend:parseFloat(v('cp_spend'))" not in m:
    m = m.replace(a_old, a_new, 1); ch += 1

# 5) clear the new fields after add
cl_old = '["cp_name","cp_budget"].forEach'
cl_new = '["cp_name","cp_budget","cp_spend","cp_leads","cp_start","cp_end"].forEach'
if cl_old in m:
    m = m.replace(cl_old, cl_new, 1); ch += 1

# 6) add updateCampaign handler after addCampaign
ac_anchor = "  addCampaign:function(){var self=this;function v(i){var e=document.getElementById(i);return e?e.value:\"\";}"
uc = ("""  updateCampaign:function(id){var self=this;
    var amt=(document.getElementById('cs_amt_'+id)||{}).value||"";
    var lds=(document.getElementById('cl_amt_'+id)||{}).value||"";
    var body={id:id};
    if(amt!=="")body.add_spend=parseFloat(amt)||0;
    if(lds!=="")body.leads=parseInt(lds)||0;
    fetch(this.apiBase()+"/api/marketing/campaign-update",{method:"POST",headers:this.hdr(),body:JSON.stringify(body)}).then(function(r){return r.json();}).then(function(){self.refreshMarketing();});},
""" + ac_anchor)
if ac_anchor in m and "updateCampaign:function" not in m:
    m = m.replace(ac_anchor, uc, 1); ch += 1

mp.write_text(m, encoding="utf-8")
print(f"M1b frontend changes: {ch} (expected 6)")
