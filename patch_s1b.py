import shutil
from pathlib import Path
from datetime import datetime
stamp = datetime.now().strftime("%Y%m%d_%H%M%S")
mp = Path("astraaspace/module_business.js"); m = mp.read_text(encoding="utf-8")
shutil.copyfile(mp, f"astraaspace/module_business.js.bak_s1b_{stamp}")
ch = 0

# 1) add "Qualified" stage + stage colors used by Sales
st_old = 'dealStages:["Lead","Proposal","Negotiation","Won","Lost"],'
st_new = 'dealStages:["Lead","Qualified","Proposal","Negotiation","Won","Lost"],'
if st_old in m and "Qualified" not in m:
    m = m.replace(st_old, st_new, 1); ch += 1

# 2) Sales nav item after Marketing
nav_old = r"""      + '    <a class="bw-nav" data-s="marketing" onclick="BusinessModule.go(\'marketing\')">\ud83d\udce3 Marketing &amp; Sales</a>'"""
# fallback plain (in case of emoji escaping differences)
nav_anchor = '''data-s="marketing" onclick="BusinessModule.go(\\'marketing\\')">'''
sales_nav = "\n      + '    <a class=\"bw-nav\" data-s=\"sales\" onclick=\"BusinessModule.go(\\'sales\\')\">\U0001f9fe Sales</a>'"
# insert after the whole marketing nav line
import re
mkt_line_pat = re.compile(r"(\+ '    <a class=\"bw-nav\" data-s=\"marketing\"[^\n]*</a>')")
mm = mkt_line_pat.search(m)
if mm and 'data-s="sales"' not in m:
    m = m[:mm.end()] + sales_nav + m[mm.end():]; ch += 1

# 3) go() branch for sales
go_old = "    else if(section==='marketing')this.renderMarketing();"
go_new = go_old + "\n    else if(section==='sales')this.renderSales();"
if go_old in m and "section==='sales'" not in m:
    m = m.replace(go_old, go_new, 1); ch += 1

# 4) renderSales + refreshSales + sales deal handlers, inserted before renderMarketing
methods = r"""  renderSales:function(){
    var f="width:100%;padding:10px 12px;border:1px solid #e2e8f0;border-radius:8px;background:#f8fafc;font-size:0.9rem;";
    var stg=this.dealStages.map(function(x){return "<option>"+x+"</option>";}).join("");
    document.getElementById('bw_body').innerHTML=
      '<h2 class="bw-h2">Sales</h2>'
      +'<div id="sal_summary" class="bw-stats" style="grid-template-columns:repeat(4,1fr);"></div>'
      +'<div class="bw-two" style="margin-top:20px;">'
      +'<div class="bw-panel"><h3 class="bw-h3">New Deal</h3>'
      +'<div class="bw-f"><label>Deal name</label><input id="sd_name" style="'+f+'"></div>'
      +'<div class="bw-f"><label>Client</label><input id="sd_client" style="'+f+'"></div>'
      +'<div class="bw-f"><label>Value ($)</label><input id="sd_value" type="number" step="0.01" style="'+f+'"></div>'
      +'<div class="bw-f"><label>Stage</label><select id="sd_stage" style="'+f+'">'+stg+'</select></div>'
      +'<div class="bw-f"><label>Probability % (optional)</label><input id="sd_prob" type="number" min="0" max="100" placeholder="auto from stage" style="'+f+'"></div>'
      +'<div class="bw-f"><label>Expected close</label><input id="sd_close" type="date" style="'+f+'"></div>'
      +'<div class="bw-f"><label>Owner</label><input id="sd_owner" style="'+f+'"></div>'
      +'<button class="bw-add" onclick="BusinessModule.addSalesDeal()">Add Deal</button></div>'
      +'<div class="bw-panel"><h3 class="bw-h3">Pipeline</h3><div id="sd_list"></div></div>'
      +'</div>';
    this.refreshSales();
  },
  refreshSales:function(){
    var self=this;
    fetch(this.apiBase()+"/api/marketing/list",{headers:this.hdr()}).then(function(r){return r.json();}).then(function(d){
      if(!d.success)return;
      var s=d.summary||{},money=function(n){return "$"+Number(n||0).toLocaleString();};
      document.getElementById('sal_summary').innerHTML=
        "<div class='bw-stat'><span class='bw-stat-l'>Open Pipeline</span><span class='bw-stat-v'>"+money(s.open_value)+"</span></div>"
        +"<div class='bw-stat'><span class='bw-stat-l'>Weighted Pipeline</span><span class='bw-stat-v' style='color:#1d4ed8;'>"+money(s.weighted_pipeline)+"</span></div>"
        +"<div class='bw-stat'><span class='bw-stat-l'>Won Revenue</span><span class='bw-stat-v'>"+money(s.won_value)+"</span></div>"
        +"<div class='bw-stat'><span class='bw-stat-l'>Total Deals</span><span class='bw-stat-v'>"+(s.total_deals||0)+"</span></div>";
      var col={"Lead":"#3b82f6","Qualified":"#0ea5e9","Proposal":"#f59e0b","Negotiation":"#8b5cf6","Won":"#16a34a","Lost":"#94a3b8"};
      var deals=d.deals||[];
      document.getElementById('sd_list').innerHTML = deals.length? deals.map(function(x){
        var opts=self.dealStages.map(function(st){return "<option "+(st===x.stage?"selected":"")+">"+st+"</option>";}).join("");
        var prob=(x.probability!=null?x.probability:0);
        var weighted=(Number(x.value||0)*Number(prob)/100);
        var meta=[];
        if(x.owner)meta.push("\ud83d\udc64 "+x.owner);
        if(x.expected_close)meta.push("\ud83d\udcc5 "+x.expected_close);
        return "<div class='bw-lead'><div class='bw-proj-top'><div><b>"+x.name+"</b>"+(x.client?" <span class='bw-muted'>\u00b7 "+x.client+"</span>":"")+"</div><button class='bw-del' onclick=\"BusinessModule.delSalesDeal('"+x.id+"')\">\u2715</button></div>"
          +"<div class='bw-muted' style='font-size:12px;'>"+money(x.value)+" \u00d7 "+prob+"% = <b style='color:#1d4ed8;'>"+money(weighted)+"</b>"+(meta.length?(" \u00b7 "+meta.join(" \u00b7 ")):"")+"</div>"
          +"<div style='display:flex;align-items:center;gap:8px;margin-top:6px;'><span style='width:10px;height:10px;border-radius:50%;background:"+(col[x.stage]||'#94a3b8')+";'></span><select class='bw-stagesel' onchange=\"BusinessModule.setSalesStage('"+x.id+"',this.value)\">"+opts+"</select></div></div>";
      }).join("") : "<p class='bw-muted'>No deals yet. Add your first deal above.</p>";
    });
  },
  addSalesDeal:function(){var self=this;function v(i){var e=document.getElementById(i);return e?e.value:"";}
    if(!v('sd_name')){alert("Enter a deal name.");return;}
    fetch(this.apiBase()+"/api/marketing/add-deal",{method:"POST",headers:this.hdr(),body:JSON.stringify({name:v('sd_name'),client:v('sd_client'),value:parseFloat(v('sd_value'))||0,stage:v('sd_stage')||"Lead",probability:v('sd_prob'),expected_close:v('sd_close'),owner:v('sd_owner')})}).then(function(r){return r.json();}).then(function(){["sd_name","sd_client","sd_value","sd_prob","sd_close","sd_owner"].forEach(function(i){var e=document.getElementById(i);if(e)e.value="";});self.refreshSales();});},
  setSalesStage:function(id,st){var self=this;fetch(this.apiBase()+"/api/marketing/update-deal",{method:"POST",headers:this.hdr(),body:JSON.stringify({id:id,stage:st})}).then(function(r){return r.json();}).then(function(){self.refreshSales();});},
  delSalesDeal:function(id){var self=this;if(!confirm("Delete deal?"))return;fetch(this.apiBase()+"/api/marketing/delete-deal",{method:"POST",headers:this.hdr(),body:JSON.stringify({id:id})}).then(function(r){return r.json();}).then(function(){self.refreshSales();});},
"""
anchor2 = "  renderMarketing:function(){"
if anchor2 in m and "renderSales:function" not in m:
    m = m.replace(anchor2, methods + anchor2, 1); ch += 1

mp.write_text(m, encoding="utf-8")
print(f"S1b frontend changes: {ch} (expected 5)")
