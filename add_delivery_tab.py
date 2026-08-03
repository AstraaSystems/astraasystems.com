from pathlib import Path
import shutil
from datetime import datetime

p = Path("astraaspace/module_logistics.js")
s = p.read_text(encoding="utf-8")
stamp = datetime.now().strftime("%Y%m%d_%H%M%S")
shutil.copyfile(p, f"astraaspace/module_logistics.js.bak_deliv_{stamp}")

changes = 0

# 1. Add the Deliveries tab button after the Purchase Orders tab
tab_anchor = "'<div class=\"lg-tab\" data-t=\"po\" onclick=\"LogisticsModule.go(\\'po\\')\">Purchase Orders</div>'"
tab_new = tab_anchor + "\n    + '<div class=\"lg-tab\" data-t=\"delivery\" onclick=\"LogisticsModule.go(\\'delivery\\')\">Deliveries</div>'"
if tab_anchor in s and "data-t=\"delivery\"" not in s:
    s = s.replace(tab_anchor, tab_new, 1); changes += 1

# 2. Route the delivery tab in go()
go_anchor = "    else if(tab==='po') this.loadPO();"
go_new = go_anchor + "\n    else if(tab==='delivery') this.loadDelivery();"
if go_anchor in s and "this.loadDelivery()" not in s:
    s = s.replace(go_anchor, go_new, 1); changes += 1

# 3. Inject delivery methods before the final "};" that closes the module object.
# The file ends with "  }\n};" (last method then object close). Insert before the closing.
methods = r'''
  ,
  // ---------- DELIVERIES ----------
  _dvLines:[],
  loadDelivery:function(){
    var self=this;
    // ensure inventory is loaded for item picking
    fetch(this.apiBase()+"/api/logistics/list",{headers:this.hdr()}).then(function(r){return r.json();}).then(function(d){
      self._items=(d.success&&d.items)?d.items:[];
      self._dvLines=[{name:'',quantity:'',item_id:''}];
      document.getElementById('lg_body').innerHTML='<div id="dv_kpis"></div>'
        +'<div class="lg-card"><h3>Create Delivery</h3>'
        +'<div class="lg-grid"><div><label>Destination</label><input id="dv_dest" placeholder="Job site / address"></div>'
        +'<div><label>Project (optional)</label><input id="dv_project" placeholder="Project name"></div>'
        +'<div><label>ETA</label><input id="dv_eta" type="date"></div>'
        +'<div><label>Notes</label><input id="dv_notes"></div></div>'
        +'<div style="margin-top:14px;"><label style="font-weight:700;font-size:.8rem;">Items to send</label><div id="dv_lines"></div>'
        +'<button class="lg-btn ghost sm" onclick="LogisticsModule.addDvLine()">+ Add line</button></div>'
        +'<div class="lg-bar"><button class="lg-btn" onclick="LogisticsModule.saveDelivery()">Create Delivery</button></div></div>'
        +'<div class="lg-card"><h3>Deliveries</h3><div id="dv_table"></div></div>';
      self.renderDvLines(); self.fetchDeliveries();
    }).catch(function(){});
  },
  addDvLine:function(){ this._dvLines.push({name:'',quantity:'',item_id:''}); this.renderDvLines(); },
  removeDvLine:function(i){ this._dvLines.splice(i,1); if(!this._dvLines.length)this._dvLines=[{name:'',quantity:'',item_id:''}]; this.renderDvLines(); },
  renderDvLines:function(){
    var self=this; var h='';
    this._dvLines.forEach(function(ln,i){
      h+='<div class="lg-line" style="grid-template-columns:2fr 1fr auto;"><div><label>Item</label><input id="dvl_name_'+i+'" placeholder="Item name" value="'+self.esc(ln.name)+'" list="dvl_items"></div>'
        +'<div><label>Qty</label><input id="dvl_qty_'+i+'" type="number" value="'+self.esc(ln.quantity)+'"></div>'
        +'<div><button class="lg-btn sm danger" onclick="LogisticsModule.removeDvLine('+i+')">x</button></div></div>';
    });
    h+='<datalist id="dvl_items">'; this._items.forEach(function(it){h+='<option value="'+self.esc(it.name)+'">';}); h+='</datalist>';
    document.getElementById('dv_lines').innerHTML=h;
  },
  gatherDvLines:function(){ var lines=[]; for(var i=0;i<this._dvLines.length;i++){ var nm=document.getElementById('dvl_name_'+i); var q=document.getElementById('dvl_qty_'+i); if(!nm)continue; var name=nm.value.trim(); if(!name)continue;
    var item_id=''; for(var j=0;j<this._items.length;j++){if(this._items[j].name.toLowerCase()===name.toLowerCase()){item_id=this._items[j].id;break;}}
    lines.push({name:name,quantity:q?q.value:0,item_id:item_id}); } return lines; },
  saveDelivery:function(){ var dest=document.getElementById('dv_dest').value.trim(); if(!dest){alert('Destination is required.');return;}
    var lines=this.gatherDvLines(); if(!lines.length){alert('Add at least one item.');return;}
    var body={destination:dest,project:document.getElementById('dv_project').value,eta:document.getElementById('dv_eta').value,notes:document.getElementById('dv_notes').value,lines:lines};
    var self=this;
    fetch(this.apiBase()+"/api/logistics/delivery/add",{method:"POST",headers:this.hdr(),body:JSON.stringify(body)}).then(function(r){return r.json();}).then(function(d){if(!d.success){alert(d.error||'Could not create.');return;}self.loadDelivery();}).catch(function(){alert('Connection error.');}); },
  fetchDeliveries:function(){ var self=this; fetch(this.apiBase()+"/api/logistics/delivery/list",{headers:this.hdr()}).then(function(r){return r.json();}).then(function(d){self._dvs=(d.success&&d.deliveries)?d.deliveries:[];self._dvSummary=(d.success&&d.summary)?d.summary:{};self.renderDvKpis();self.renderDeliveries();}).catch(function(){}); },
  renderDvKpis:function(){ var s=this._dvSummary||{}; var el=document.getElementById('dv_kpis'); if(!el)return;
    el.innerHTML='<div class="lg-kpis"><div class="lg-kpi"><div class="l">Pending</div><div class="v">'+(s.pending||0)+'</div></div>'
      +'<div class="lg-kpi"><div class="l">In Transit</div><div class="v">'+(s.in_transit||0)+'</div></div>'
      +'<div class="lg-kpi"><div class="l">Delivered</div><div class="v">'+(s.delivered||0)+'</div></div></div>'; },
  dispatchDelivery:function(id){ if(!confirm('Dispatch this delivery? Stock will be deducted from inventory.'))return; var self=this;
    fetch(this.apiBase()+"/api/logistics/delivery/dispatch",{method:"POST",headers:this.hdr(),body:JSON.stringify({id:id})}).then(function(r){return r.json();}).then(function(d){if(!d.success){alert(d.error||'Could not dispatch.');return;}alert('Dispatched - stock deducted from inventory.');self.fetchDeliveries();}).catch(function(){alert('Connection error.');}); },
  completeDelivery:function(id){ var self=this; fetch(this.apiBase()+"/api/logistics/delivery/complete",{method:"POST",headers:this.hdr(),body:JSON.stringify({id:id})}).then(function(r){return r.json();}).then(function(d){if(!d.success){alert(d.error||'Could not complete.');return;}self.fetchDeliveries();}).catch(function(){}); },
  delDelivery:function(id){ if(!confirm('Delete this delivery?'))return; var self=this; fetch(this.apiBase()+"/api/logistics/delivery/delete",{method:"POST",headers:this.hdr(),body:JSON.stringify({id:id})}).then(function(r){return r.json();}).then(function(d){if(d.success)self.fetchDeliveries();}).catch(function(){}); },
  renderDeliveries:function(){ if(!this._dvs||!this._dvs.length){document.getElementById('dv_table').innerHTML='<p class="lg-muted">No deliveries yet. Create one above.</p>';return;} var self=this;
    var h='<table class="lg-table"><thead><tr><th>Destination</th><th>Project</th><th>Items</th><th>ETA</th><th>Status</th><th></th></tr></thead><tbody>';
    this._dvs.forEach(function(dv){ var items=(dv.lines||[]).map(function(l){return l.name+' x'+l.quantity;}).join(', ');
      var st=dv.status; var badge=st==='Delivered'?'<span class="lg-badge received">Delivered</span>':(st==='In Transit'?'<span class="lg-badge" style="background:#dbeafe;color:#1d4ed8;">In Transit</span>':'<span class="lg-badge ordered">Pending</span>');
      var actions='';
      if(st==='Pending') actions+='<button class="lg-btn sm ok" onclick="LogisticsModule.dispatchDelivery(\''+dv.id+'\')">Dispatch</button> ';
      if(st==='In Transit') actions+='<button class="lg-btn sm ok" onclick="LogisticsModule.completeDelivery(\''+dv.id+'\')">Mark Delivered</button> ';
      actions+='<button class="lg-btn sm danger" onclick="LogisticsModule.delDelivery(\''+dv.id+'\')">Delete</button>';
      h+='<tr><td><b>'+(dv.destination||'')+'</b></td><td>'+(dv.project||'')+'</td><td>'+items+'</td><td>'+(dv.eta||'')+'</td><td>'+badge+'</td><td>'+actions+'</td></tr>';
    }); h+='</tbody></table>'; document.getElementById('dv_table').innerHTML=h;
  }
'''

# Insert methods before the final closing "};" of the object.
# The file's last two chars structure is "  }\n};\n" — inject before "\n};"
close_idx = s.rstrip().rfind("\n};")
if close_idx == -1:
    print("ABORT: object close not found"); raise SystemExit
s = s[:close_idx] + methods + s[close_idx:]
changes += 1

p.write_text(s, encoding="utf-8")
print("Changes applied:", changes, "(expected 3)")
