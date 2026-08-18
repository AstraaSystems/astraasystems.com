import shutil
from pathlib import Path
from datetime import datetime
stamp = datetime.now().strftime("%Y%m%d_%H%M%S")
mp = Path("astraaspace/module_business.js"); m = mp.read_text(encoding="utf-8")
shutil.copyfile(mp, f"astraaspace/module_business.js.bak_s3b_{stamp}")
ch = 0

# 1) Add a quote-picker field into the Sales New Deal form (after Value field)
v_anchor = "+'<div class=\"bw-f\"><label>Value ($)</label><input id=\"sd_value\" type=\"number\" step=\"0.01\" style=\"'+f+'\"></div>'"
v_new = (v_anchor + "\n"
    "      +'<div class=\"bw-f\"><label>\\ud83d\\udcce Link Estimator quote (optional)</label><select id=\"sd_quote\" style=\"'+f+'\" onchange=\"BusinessModule.applyQuoteToDeal()\"><option value=\"\">\u2014 none \u2014</option></select></div>'")
if v_anchor in m and 'sd_quote' not in m:
    m = m.replace(v_anchor, v_new, 1); ch += 1

# 2) In renderSales, after this.refreshSales(); also load quotes into the picker
r_anchor = "    this.refreshSales();\n  },\n  refreshSales:function(){"
r_new = "    this.refreshSales();\n    this.loadDealQuotes();\n  },\n  refreshSales:function(){"
if r_anchor in m and "loadDealQuotes" not in m:
    m = m.replace(r_anchor, r_new, 1); ch += 1

# 3) Add loadDealQuotes + applyQuoteToDeal helpers before addSalesDeal
a2 = "  addSalesDeal:function(){"
methods = r"""  _dealQuotes:[],
  loadDealQuotes:function(){
    var self=this;
    fetch(this.apiBase()+"/api/estimate/history",{headers:this.hdr()}).then(function(r){return r.json();}).then(function(d){
      self._dealQuotes=(d&&d.quotes)?d.quotes:[];
      var sel=document.getElementById('sd_quote'); if(!sel)return;
      var opts='<option value="">\u2014 none \u2014</option>';
      self._dealQuotes.forEach(function(q){
        var lbl=q.title+" \u00b7 $"+Math.round(q.total||0).toLocaleString()+((q.created_at||'').split('T')[0]?(" \u00b7 "+(q.created_at||'').split('T')[0]):"");
        opts+='<option value="'+q.index+'">'+lbl+'</option>';
      });
      sel.innerHTML=opts;
    }).catch(function(){});
  },
  applyQuoteToDeal:function(){
    var sel=document.getElementById('sd_quote'); if(!sel)return;
    var idx=sel.value; if(idx==='')return;
    var q=(this._dealQuotes||[]).filter(function(x){return String(x.index)===String(idx);})[0];
    if(!q)return;
    var nm=document.getElementById('sd_name'); if(nm && !nm.value){ nm.value=q.title||''; }
    var val=document.getElementById('sd_value'); if(val){ val.value=Math.round(q.total||0); }
  },
"""
if a2 in m and "loadDealQuotes:function" not in m:
    m = m.replace(a2, methods + a2, 1); ch += 1

# 4) addSalesDeal: send quote_index + quote_title
add_anchor = "created_override:v('sd_created'),stage_changed_override:v('sd_stagedate')})"
add_new = ("created_override:v('sd_created'),stage_changed_override:v('sd_stagedate'),"
           "quote_index:v('sd_quote'),quote_title:(function(){var s=document.getElementById('sd_quote');return (s&&s.selectedIndex>0)?s.options[s.selectedIndex].text:'';})()})")
if add_anchor in m and "quote_index:v('sd_quote')" not in m:
    m = m.replace(add_anchor, add_new, 1); ch += 1

# 5) show linked quote on the deal card (in salesActivityBlock, at top of out)
b_anchor = "  salesActivityBlock:function(x){\n    var out=\"\";"
b_new = ("  salesActivityBlock:function(x){\n    var out=\"\";\n"
         "    if(x.quote_title){ out+=\"<div style='margin-top:6px;font-size:11px;color:#1d4ed8;'>\\ud83d\\udcce From quote: \"+x.quote_title+\"</div>\"; }")
if b_anchor in m and "From quote:" not in m:
    m = m.replace(b_anchor, b_new, 1); ch += 1

mp.write_text(m, encoding="utf-8")
print(f"S3b frontend changes: {ch} (expected 5)")
