import shutil
from pathlib import Path
from datetime import datetime
stamp = datetime.now().strftime("%Y%m%d_%H%M%S")
mp = Path("astraaspace/module_business.js"); m = mp.read_text(encoding="utf-8")
shutil.copyfile(mp, f"astraaspace/module_business.js.bak_s2b_{stamp}")
ch = 0

# 1) In refreshSales deal row: append a next-action flag + expandable activity panel.
# Anchor on the closing of the stage-select div in the sales row (end of the deal card).
anchor = ("\"<div style='display:flex;align-items:center;gap:8px;margin-top:6px;'><span style='width:10px;height:10px;border-radius:50%;background:\"+(col[x.stage]||'#94a3b8')+\";'></span><select class='bw-stagesel' onchange=\\\"BusinessModule.setSalesStage('\"+x.id+\"',this.value)\\\">\"+opts+\"</select></div></div>\";")

addon = ("\"<div style='display:flex;align-items:center;gap:8px;margin-top:6px;'><span style='width:10px;height:10px;border-radius:50%;background:\"+(col[x.stage]||'#94a3b8')+\";'></span><select class='bw-stagesel' onchange=\\\"BusinessModule.setSalesStage('\"+x.id+\"',this.value)\\\">\"+opts+\"</select></div>\""
    "+BusinessModule.salesActivityBlock(x)+\"</div>\";")

if anchor in m and "salesActivityBlock" not in m:
    m = m.replace(anchor, addon, 1); ch += 1

# 2) Add the helper methods after refreshSales (anchor on addSalesDeal)
anchor2 = "  addSalesDeal:function(){"
methods = r"""  salesActivityBlock:function(x){
    var out="";
    // next-action / overdue flag
    var na=(x.next_action||""), nad=(x.next_action_date||"");
    if(na){
      var overdue=false;
      if(nad){var _t=new Date(nad+"T00:00:00");var _n=new Date();_n.setHours(0,0,0,0);overdue=(_t<_n);}
      var c=overdue?"#dc2626":"#0f766e";
      out+="<div style='margin-top:8px;font-size:12px;color:"+c+";font-weight:600;'>"+(overdue?"\ud83d\udd34 OVERDUE: ":"\u27a1 Next: ")+x.next_action+(nad?(" (by "+nad+")"):"")+"</div>";
    } else {
      out+="<div style='margin-top:8px;font-size:12px;color:#94a3b8;'>\u26a0 No next step set</div>";
    }
    // last activity
    if(x.last_activity_at){
      var la=new Date(x.last_activity_at); if(!isNaN(la)){var days=Math.floor((Date.now()-la.getTime())/86400000); out+="<div style='font-size:11px;color:#94a3b8;'>Last activity "+days+"d ago</div>";}
    }
    // expandable log + add form
    var acts=(x.activities||[]);
    var log=acts.length? acts.slice().reverse().map(function(a){var t=new Date(a.at);var ds=isNaN(t)?"":(t.toLocaleDateString());return "<div style='font-size:11px;color:#475569;border-left:2px solid #e2e8f0;padding:2px 0 2px 8px;margin:3px 0;'><b>"+(a.type||"Note")+"</b> "+(a.note||"")+" <span style='color:#94a3b8;'>"+ds+"</span></div>";}).join("") : "<div style='font-size:11px;color:#94a3b8;'>No activity yet.</div>";
    out+="<details style='margin-top:8px;'><summary style='cursor:pointer;color:#1d4ed8;font-size:12px;'>Activity &amp; follow-up</summary>"
      +"<div style='margin-top:8px;'>"+log+"</div>"
      +"<div style='margin-top:8px;display:flex;gap:6px;flex-wrap:wrap;'>"
      +"<select id='act_type_"+x.id+"' style='padding:5px;border:1px solid #e2e8f0;border-radius:6px;font-size:12px;'><option>Call</option><option>Email</option><option>Meeting</option><option>Note</option></select>"
      +"<input id='act_note_"+x.id+"' placeholder='What happened?' style='flex:1;min-width:120px;padding:5px;border:1px solid #e2e8f0;border-radius:6px;font-size:12px;'>"
      +"<button class='bw-btn' style='font-size:12px;padding:5px 10px;' onclick=\"BusinessModule.logActivity('"+x.id+"')\">Log</button></div>"
      +"<div style='margin-top:8px;display:flex;gap:6px;flex-wrap:wrap;align-items:center;'>"
      +"<input id='na_text_"+x.id+"' value=\""+(na.replace(/\"/g,'&quot;'))+"\" placeholder='Next step...' style='flex:1;min-width:120px;padding:5px;border:1px solid #e2e8f0;border-radius:6px;font-size:12px;'>"
      +"<input id='na_date_"+x.id+"' type='date' value='"+nad+"' style='padding:5px;border:1px solid #e2e8f0;border-radius:6px;font-size:12px;'>"
      +"<button class='bw-btn' style='font-size:12px;padding:5px 10px;' onclick=\"BusinessModule.setNextAction('"+x.id+"')\">Set</button></div>"
      +"</details>";
    return out;
  },
  logActivity:function(id){
    var self=this;
    var t=(document.getElementById('act_type_'+id)||{}).value||"Note";
    var n=(document.getElementById('act_note_'+id)||{}).value||"";
    if(!n){alert("Add a short note.");return;}
    fetch(this.apiBase()+"/api/marketing/deal-activity",{method:"POST",headers:this.hdr(),body:JSON.stringify({id:id,activity_type:t,activity_note:n})}).then(function(r){return r.json();}).then(function(){self.refreshSales();});
  },
  setNextAction:function(id){
    var self=this;
    var t=(document.getElementById('na_text_'+id)||{}).value||"";
    var d=(document.getElementById('na_date_'+id)||{}).value||"";
    fetch(this.apiBase()+"/api/marketing/deal-activity",{method:"POST",headers:this.hdr(),body:JSON.stringify({id:id,next_action:t,next_action_date:d})}).then(function(r){return r.json();}).then(function(){self.refreshSales();});
  },
"""
if anchor2 in m and "salesActivityBlock:function" not in m:
    m = m.replace(anchor2, methods + anchor2, 1); ch += 1

mp.write_text(m, encoding="utf-8")
print(f"S2b frontend changes: {ch} (expected 2)")
