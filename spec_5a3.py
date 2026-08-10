import shutil
from pathlib import Path
from datetime import datetime

mp = Path("astraaspace/module_logistics.js")
m = mp.read_text(encoding="utf-8")
stamp = datetime.now().strftime("%Y%m%d_%H%M%S")
shutil.copyfile(mp, f"astraaspace/module_logistics.js.bak_spec5a3_{stamp}")

changes = 0

# Helper: a JS function to format "name — spec" label, added once to the module.
# Insert esc-adjacent. We'll add a labelNS helper after the esc: line.
esc_anchor = "  esc:function(v){return (v!==undefined&&v!==null)?String(v).replace(/\"/g,'&quot;'):'';},"
helper = esc_anchor + "\n  nsLabel:function(it){var sp=(it.specification||'').trim();return it.name+(sp?(' \\u2014 '+sp):'');},"
if esc_anchor in m and "nsLabel:function" not in m:
    m = m.replace(esc_anchor, helper, 1); changes += 1

# ---- PO line state: include specification ----
m2 = m.replace("this._poLines.push({name:'',quantity:'',unit_cost:'',item_id:''})",
               "this._poLines.push({name:'',specification:'',quantity:'',unit_cost:'',item_id:''})")
if m2 != m: m = m2; changes += 1
m2 = m.replace("this._poLines=[{name:'',quantity:'',unit_cost:'',item_id:''}]",
               "this._poLines=[{name:'',specification:'',quantity:'',unit_cost:'',item_id:''}]")
if m2 != m: m = m2; changes += 1

# ---- PO renderPoLines: add Spec input + datalist with name-spec labels ----
po_line_old = ("h+='<div class=\"lg-line\"><div><label>Item</label><input id=\"pol_name_'+i+'\" placeholder=\"Item name\" value=\"'+self.esc(ln.name)+'\" list=\"pol_items\"></div>'\n"
               "        +'<div><label>Qty</label><input id=\"pol_qty_'+i+'\" type=\"number\" value=\"'+self.esc(ln.quantity)+'\"></div>'\n"
               "        +'<div><label>Unit cost</label><input id=\"pol_cost_'+i+'\" type=\"number\" value=\"'+self.esc(ln.unit_cost)+'\"></div>'")
po_line_new = ("h+='<div class=\"lg-line\" style=\"grid-template-columns:2fr 1fr 1fr 1fr auto;\"><div><label>Item</label><input id=\"pol_name_'+i+'\" placeholder=\"Item name\" value=\"'+self.esc(ln.name)+'\" list=\"pol_items\"></div>'\n"
               "        +'<div><label>Spec</label><input id=\"pol_spec_'+i+'\" placeholder=\"e.g. 10ft\" value=\"'+self.esc(ln.specification)+'\"></div>'\n"
               "        +'<div><label>Qty</label><input id=\"pol_qty_'+i+'\" type=\"number\" value=\"'+self.esc(ln.quantity)+'\"></div>'\n"
               "        +'<div><label>Unit cost</label><input id=\"pol_cost_'+i+'\" type=\"number\" value=\"'+self.esc(ln.unit_cost)+'\"></div>'")
if po_line_old in m:
    m = m.replace(po_line_old, po_line_new, 1); changes += 1

# PO datalist: use name-spec labels
po_dl_old = "h+='<datalist id=\"pol_items\">'; this._items.forEach(function(it){h+='<option value=\"'+self.esc(it.name)+'\">';}); h+='</datalist>';"
po_dl_new = "h+='<datalist id=\"pol_items\">'; this._items.forEach(function(it){h+='<option value=\"'+self.esc(self.nsLabel(it))+'\">';}); h+='</datalist>';"
if po_dl_old in m:
    m = m.replace(po_dl_old, po_dl_new, 1); changes += 1

# ---- PO gatherPoLines: parse name/spec, match item_id on name+spec ----
po_gather_old = ("gatherPoLines:function(){ var lines=[]; for(var i=0;i<this._poLines.length;i++){ var nm=document.getElementById('pol_name_'+i); var q=document.getElementById('pol_qty_'+i); var c=document.getElementById('pol_cost_'+i); if(!nm)continue; var name=nm.value.trim(); if(!name)continue;\n"
                 "    var item_id=''; for(var j=0;j<this._items.length;j++){if(this._items[j].name.toLowerCase()===name.toLowerCase()){item_id=this._items[j].id;break;}}\n"
                 "    lines.push({name:name,quantity:q?q.value:0,unit_cost:c?c.value:0,item_id:item_id}); } return lines; },")
po_gather_new = ("gatherPoLines:function(){ var lines=[]; for(var i=0;i<this._poLines.length;i++){ var nm=document.getElementById('pol_name_'+i); var sp=document.getElementById('pol_spec_'+i); var q=document.getElementById('pol_qty_'+i); var c=document.getElementById('pol_cost_'+i); if(!nm)continue; var raw=nm.value.trim(); if(!raw)continue;\n"
                 "    var name=raw; var spec=sp?sp.value.trim():''; var dash=raw.indexOf(' \\u2014 '); if(dash!==-1){ name=raw.substring(0,dash).trim(); if(!spec)spec=raw.substring(dash+3).trim(); }\n"
                 "    var item_id=''; for(var j=0;j<this._items.length;j++){if(this._items[j].name.toLowerCase()===name.toLowerCase() && (this._items[j].specification||'').toLowerCase()===spec.toLowerCase()){item_id=this._items[j].id;break;}}\n"
                 "    lines.push({name:name,specification:spec,quantity:q?q.value:0,unit_cost:c?c.value:0,item_id:item_id}); } return lines; },")
if po_gather_old in m:
    m = m.replace(po_gather_old, po_gather_new, 1); changes += 1

# ---- DELIVERY line state: include specification ----
m2 = m.replace("this._dvLines.push({name:'',quantity:'',item_id:''})",
               "this._dvLines.push({name:'',specification:'',quantity:'',item_id:''})")
if m2 != m: m = m2; changes += 1
m2 = m.replace("this._dvLines=[{name:'',quantity:'',item_id:''}]",
               "this._dvLines=[{name:'',specification:'',quantity:'',item_id:''}]")
if m2 != m: m = m2; changes += 1
# also the initial set in loadDelivery
m2 = m.replace("self._dvLines=[{name:'',quantity:'',item_id:''}]",
               "self._dvLines=[{name:'',specification:'',quantity:'',item_id:''}]")
if m2 != m: m = m2; changes += 1

# ---- DELIVERY renderDvLines: add Spec input + datalist labels ----
dv_line_old = ("h+='<div class=\"lg-line\" style=\"grid-template-columns:2fr 1fr auto;\"><div><label>Item</label><input id=\"dvl_name_'+i+'\" placeholder=\"Item name\" value=\"'+self.esc(ln.name)+'\" list=\"dvl_items\"></div>'\n"
               "        +'<div><label>Qty</label><input id=\"dvl_qty_'+i+'\" type=\"number\" value=\"'+self.esc(ln.quantity)+'\"></div>'")
dv_line_new = ("h+='<div class=\"lg-line\" style=\"grid-template-columns:2fr 1fr 1fr auto;\"><div><label>Item</label><input id=\"dvl_name_'+i+'\" placeholder=\"Item name\" value=\"'+self.esc(ln.name)+'\" list=\"dvl_items\"></div>'\n"
               "        +'<div><label>Spec</label><input id=\"dvl_spec_'+i+'\" placeholder=\"e.g. 10ft\" value=\"'+self.esc(ln.specification)+'\"></div>'\n"
               "        +'<div><label>Qty</label><input id=\"dvl_qty_'+i+'\" type=\"number\" value=\"'+self.esc(ln.quantity)+'\"></div>'")
if dv_line_old in m:
    m = m.replace(dv_line_old, dv_line_new, 1); changes += 1

# DELIVERY datalist labels
dv_dl_old = "h+='<datalist id=\"dvl_items\">'; this._items.forEach(function(it){h+='<option value=\"'+self.esc(it.name)+'\">';}); h+='</datalist>';"
dv_dl_new = "h+='<datalist id=\"dvl_items\">'; this._items.forEach(function(it){h+='<option value=\"'+self.esc(self.nsLabel(it))+'\">';}); h+='</datalist>';"
if dv_dl_old in m:
    m = m.replace(dv_dl_old, dv_dl_new, 1); changes += 1

# ---- DELIVERY gatherDvLines: parse name/spec, match item_id on name+spec ----
dv_gather_old = ("gatherDvLines:function(){ var lines=[]; for(var i=0;i<this._dvLines.length;i++){ var nm=document.getElementById('dvl_name_'+i); var q=document.getElementById('dvl_qty_'+i); if(!nm)continue; var name=nm.value.trim(); if(!name)continue;\n"
                 "    var item_id=''; for(var j=0;j<this._items.length;j++){if(this._items[j].name.toLowerCase()===name.toLowerCase()){item_id=this._items[j].id;break;}}\n"
                 "    lines.push({name:name,quantity:q?q.value:0,item_id:item_id}); } return lines; },")
dv_gather_new = ("gatherDvLines:function(){ var lines=[]; for(var i=0;i<this._dvLines.length;i++){ var nm=document.getElementById('dvl_name_'+i); var sp=document.getElementById('dvl_spec_'+i); var q=document.getElementById('dvl_qty_'+i); if(!nm)continue; var raw=nm.value.trim(); if(!raw)continue;\n"
                 "    var name=raw; var spec=sp?sp.value.trim():''; var dash=raw.indexOf(' \\u2014 '); if(dash!==-1){ name=raw.substring(0,dash).trim(); if(!spec)spec=raw.substring(dash+3).trim(); }\n"
                 "    var item_id=''; for(var j=0;j<this._items.length;j++){if(this._items[j].name.toLowerCase()===name.toLowerCase() && (this._items[j].specification||'').toLowerCase()===spec.toLowerCase()){item_id=this._items[j].id;break;}}\n"
                 "    lines.push({name:name,specification:spec,quantity:q?q.value:0,item_id:item_id}); } return lines; },")
if dv_gather_old in m:
    m = m.replace(dv_gather_old, dv_gather_new, 1); changes += 1

mp.write_text(m, encoding="utf-8")
print("Total changes applied:", changes)
