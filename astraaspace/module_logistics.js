// Astraa Logistics - Phase 1+2: Inventory, Suppliers, Purchase Orders
var LogisticsModule = {
  _tab:"inventory", _items:[], _summary:{}, _editId:null, _editItem:null,
  _suppliers:[], _pos:[], _poSummary:{}, _poLines:[],
  apiBase:function(){
    if(typeof ASTRAA_API_BASE!=='undefined' && ASTRAA_API_BASE) return ASTRAA_API_BASE;
    return "http"+"s://"+"family-speed-outcome"+".ngrok-free"+".dev";
  },
  session:function(){try{return JSON.parse(localStorage.getItem('astraa_session')||'{}');}catch(e){return {};}},
  hdr:function(){return {"Content-Type":"application/json","Authorization":"Bearer "+(this.session().token||""),"ngrok-skip-browser-warning":"true"};},
  money:function(n){return "$"+Number(n||0).toLocaleString(undefined,{minimumFractionDigits:2,maximumFractionDigits:2});},
  esc:function(v){return (v!==undefined&&v!==null)?String(v).replace(/"/g,'&quot;'):'';},

  styles:function(){
    return '<style>'
    + '.lg-wrap{font-family:Inter,system-ui,sans-serif;padding:22px 30px;background:#f8fafc;min-height:calc(100vh - 120px);}'
    + '.lg-h{font-size:1.6rem;font-weight:900;color:#0f172a;letter-spacing:-0.03em;margin:0 0 4px;}'
    + '.lg-sub{color:#64748b;margin:0 0 18px;font-size:.95rem;}'
    + '.lg-tabs{display:flex;gap:8px;margin-bottom:20px;border-bottom:2px solid #e2e8f0;}'
    + '.lg-tab{padding:10px 18px;cursor:pointer;font-weight:800;font-size:.92rem;color:#64748b;border-bottom:3px solid transparent;margin-bottom:-2px;}'
    + '.lg-tab.on{color:#1d4ed8;border-bottom-color:#1d4ed8;}'
    + '.lg-kpis{display:grid;grid-template-columns:repeat(auto-fit,minmax(180px,1fr));gap:14px;margin-bottom:22px;}'
    + '.lg-kpi{background:#fff;border:1px solid #e2e8f0;border-radius:14px;padding:18px;box-shadow:0 4px 14px rgba(15,23,42,.04);}'
    + '.lg-kpi .l{color:#64748b;font-size:.75rem;font-weight:800;text-transform:uppercase;letter-spacing:.05em;margin-bottom:6px;}'
    + '.lg-kpi .v{font-size:1.5rem;font-weight:900;color:#0f172a;}'
    + '.lg-kpi.warn .v{color:#dc2626;}'
    + '.lg-card{background:#fff;border:1px solid #e2e8f0;border-radius:16px;padding:22px;box-shadow:0 4px 14px rgba(15,23,42,.04);margin-bottom:18px;}'
    + '.lg-card h3{margin:0 0 16px;font-size:1.05rem;font-weight:800;color:#0f172a;}'
    + '.lg-grid{display:grid;grid-template-columns:1fr 1fr;gap:12px;}'
    + '.lg-grid label,.lg-line label{display:block;font-weight:700;font-size:.8rem;color:#0f172a;margin-bottom:5px;}'
    + '.lg-grid input,.lg-line input,.lg-line select,.lg-card select{width:100%;padding:9px 11px;border:1px solid #cbd5e1;border-radius:9px;font-size:.92rem;box-sizing:border-box;}'
    + '.lg-btn{background:#1d4ed8;color:#fff;border:none;border-radius:10px;padding:11px 18px;font-weight:800;cursor:pointer;font-size:.9rem;}'
    + '.lg-btn.ghost{background:#fff;color:#1d4ed8 !important;border:1px solid #1d4ed8;}'
    + '.lg-btn.sm{padding:6px 12px;font-size:.8rem;border-radius:7px;}'
    + '.lg-btn.danger{background:#fff;color:#dc2626;border:1px solid #fecaca;}'
    + '.lg-btn.ok{background:#16a34a;}'
    + '.lg-bar{display:flex;gap:10px;margin-top:14px;flex-wrap:wrap;}'
    + '.lg-table{width:100%;border-collapse:collapse;font-size:.9rem;}'
    + '.lg-table th{text-align:left;color:#64748b;font-size:.75rem;text-transform:uppercase;letter-spacing:.04em;padding:10px 8px;border-bottom:2px solid #e2e8f0;}'
    + '.lg-table td{padding:11px 8px;border-bottom:1px solid #f1f5f9;color:#334155;}'
    + '.lg-table tr.low td{background:#fef2f2;}'
    + '.lg-lowtag{display:inline-block;background:#fee2e2;color:#b91c1c;font-size:.68rem;font-weight:800;padding:2px 7px;border-radius:6px;margin-left:6px;}'
    + '.lg-badge{display:inline-block;font-size:.7rem;font-weight:800;padding:3px 9px;border-radius:999px;}'
    + '.lg-badge.ordered{background:#fef3c7;color:#b45309;}'
    + '.lg-badge.received{background:#dcfce7;color:#15803d;}'
    + '.lg-qty{display:inline-flex;align-items:center;gap:8px;}'
    + '.lg-qbtn{min-width:30px;height:30px;padding:0 10px;border:1px solid #1d4ed8;background:#fff;border-radius:6px;cursor:pointer;font-weight:900;color:#1d4ed8 !important;font-size:1.1rem;line-height:1;display:inline-flex;align-items:center;justify-content:center;}'
    + '.lg-line{display:grid;grid-template-columns:2fr 1fr 1fr auto;gap:8px;align-items:end;margin-bottom:8px;}'
    + '.lg-muted{color:#94a3b8;font-size:.92rem;}'
    + '.lg-wrap .lg-qbtn{background:#ffffff !important;color:#1d4ed8 !important;border:1px solid #1d4ed8 !important;}'
    + '.lg-wrap button.lg-btn{background:#1d4ed8 !important;color:#ffffff !important;}'
    + '.lg-wrap button.lg-btn.ghost{background:#ffffff !important;color:#1d4ed8 !important;border:1px solid #1d4ed8 !important;}'
    + '.lg-wrap button.lg-btn.danger{background:#ffffff !important;color:#dc2626 !important;border:1px solid #fecaca !important;}'
    + '.lg-wrap button.lg-btn.ok{background:#16a34a !important;color:#ffffff !important;}'
    + '</style>';
  },

  render:function(){
    return this.styles() + '<div class="lg-wrap">'
    + '<h2 class="lg-h">Astraa Logistics</h2>'
    + '<p class="lg-sub">Inventory, suppliers and purchase orders - all in one place.</p>'
    + '<div class="lg-tabs">'
    + '<div class="lg-tab" data-t="inventory" onclick="LogisticsModule.go(\'inventory\')">Inventory</div>'
    + '<div class="lg-tab" data-t="suppliers" onclick="LogisticsModule.go(\'suppliers\')">Suppliers</div>'
    + '<div class="lg-tab" data-t="po" onclick="LogisticsModule.go(\'po\')">Purchase Orders</div>'
    + '</div><div id="lg_body"></div></div>';
  },

  load:function(){ this.go('inventory'); },

  go:function(tab){
    this._tab=tab;
    var tabs=document.querySelectorAll('.lg-tab');
    for(var i=0;i<tabs.length;i++){tabs[i].className='lg-tab'+(tabs[i].getAttribute('data-t')===tab?' on':'');}
    if(tab==='inventory') this.loadInventory();
    else if(tab==='suppliers') this.loadSuppliers();
    else if(tab==='po') this.loadPO();
  },

  // ---------- INVENTORY ----------
  loadInventory:function(){
    document.getElementById('lg_body').innerHTML='<div id="lg_kpis"></div>'
      + '<div class="lg-card"><h3 id="lg_formtitle">Add Item</h3><div id="lg_form"></div></div>'
      + '<div class="lg-card"><h3>Inventory</h3><div id="lg_table"></div></div>';
    this.renderForm(); this.fetchList();
  },
  fetchList:function(){
    var self=this;
    fetch(this.apiBase()+"/api/logistics/list",{headers:this.hdr()})
      .then(function(r){return r.json();})
      .then(function(d){ self._items=(d.success&&d.items)?d.items:[]; self._summary=(d.success&&d.summary)?d.summary:{}; self.renderKpis(); self.renderTable(); })
      .catch(function(){ var t=document.getElementById('lg_table'); if(t)t.innerHTML='<p style="color:#dc2626;">Connection error.</p>'; });
  },
  renderKpis:function(){
    var s=this._summary||{};
    document.getElementById('lg_kpis').innerHTML='<div class="lg-kpis">'
      +'<div class="lg-kpi"><div class="l">Items</div><div class="v">'+(s.item_count||0)+'</div></div>'
      +'<div class="lg-kpi"><div class="l">Total Stock Value</div><div class="v">'+this.money(s.total_value)+'</div></div>'
      +'<div class="lg-kpi'+((s.low_stock_count||0)>0?' warn':'')+'"><div class="l">Low Stock</div><div class="v">'+(s.low_stock_count||0)+'</div></div>'
      +'</div>';
  },
  field:function(id,label,val,type){ return '<div><label>'+label+'</label><input id="lg_'+id+'" type="'+(type||'text')+'" value="'+this.esc(val)+'"></div>'; },
  renderForm:function(){
    var e=this._editItem||{};
    document.getElementById('lg_form').innerHTML='<div class="lg-grid">'
      +this.field('name','Item name',e.name)+this.field('sku','SKU',e.sku)
      +this.field('category','Category',e.category)+this.field('unit','Unit (each, box, sqft)',e.unit)
      +this.field('unit_cost','Unit cost ($)',e.unit_cost,'number')+this.field('quantity','Quantity',e.quantity,'number')
      +this.field('location','Location',e.location)+this.field('reorder_point','Reorder point',e.reorder_point,'number')
      +this.field('supplier','Supplier',e.supplier)+this.field('notes','Notes',e.notes)
      +'</div><div class="lg-bar"><button class="lg-btn" onclick="LogisticsModule.save()">'+(this._editId?'Update Item':'Add Item')+'</button>'
      +(this._editId?'<button class="lg-btn ghost" onclick="LogisticsModule.cancelEdit()">Cancel</button>':'')+'</div>';
    var ft=document.getElementById('lg_formtitle'); if(ft)ft.innerText=this._editId?'Edit Item':'Add Item';
  },
  gather:function(){ function v(id){var el=document.getElementById('lg_'+id);return el?el.value:'';}
    return {name:v('name'),sku:v('sku'),category:v('category'),unit:v('unit'),unit_cost:v('unit_cost'),quantity:v('quantity'),location:v('location'),reorder_point:v('reorder_point'),supplier:v('supplier'),notes:v('notes')}; },
  save:function(){ var body=this.gather(); if(!body.name.trim()){alert('Item name is required.');return;}
    var url=this._editId?"/api/logistics/update":"/api/logistics/add"; if(this._editId)body.id=this._editId; var self=this;
    fetch(this.apiBase()+url,{method:"POST",headers:this.hdr(),body:JSON.stringify(body)}).then(function(r){return r.json();})
      .then(function(d){ if(!d.success){alert(d.error||'Could not save.');return;} self._editId=null; self._editItem=null; self.renderForm(); self.fetchList(); })
      .catch(function(){alert('Connection error.');}); },
  edit:function(id){ for(var i=0;i<this._items.length;i++){if(this._items[i].id===id){this._editItem=this._items[i];this._editId=id;break;}} this.renderForm(); window.scrollTo(0,0); },
  cancelEdit:function(){ this._editId=null; this._editItem=null; this.renderForm(); },
  adjust:function(id,delta){ var self=this; fetch(this.apiBase()+"/api/logistics/adjust",{method:"POST",headers:this.hdr(),body:JSON.stringify({id:id,delta:delta})}).then(function(r){return r.json();}).then(function(d){if(d.success)self.fetchList();}).catch(function(){}); },
  del:function(id){ if(!confirm('Delete this item?'))return; var self=this; fetch(this.apiBase()+"/api/logistics/delete",{method:"POST",headers:this.hdr(),body:JSON.stringify({id:id})}).then(function(r){return r.json();}).then(function(d){if(d.success)self.fetchList();}).catch(function(){}); },
  renderTable:function(){
    if(!this._items.length){document.getElementById('lg_table').innerHTML='<p class="lg-muted">No items yet. Add your first inventory item above.</p>';return;}
    var self=this; var h='<table class="lg-table"><thead><tr><th>Item</th><th>SKU</th><th>Category</th><th>Qty</th><th>Unit cost</th><th>Value</th><th>Location</th><th></th></tr></thead><tbody>';
    this._items.forEach(function(it){ var qty=Number(it.quantity||0),cost=Number(it.unit_cost||0),rp=Number(it.reorder_point||0); var low=(rp>0&&qty<=rp);
      h+='<tr class="'+(low?'low':'')+'"><td><b>'+(it.name||'')+'</b>'+(low?'<span class="lg-lowtag">LOW</span>':'')+'</td><td>'+(it.sku||'')+'</td><td>'+(it.category||'')+'</td>'
        +'<td><span class="lg-qty"><button class="lg-qbtn" onclick="LogisticsModule.adjust(\''+it.id+'\',-1)">-</button>'+qty+'<button class="lg-qbtn" onclick="LogisticsModule.adjust(\''+it.id+'\',1)">+</button></span></td>'
        +'<td>'+self.money(cost)+'</td><td>'+self.money(qty*cost)+'</td><td>'+(it.location||'')+'</td>'
        +'<td><button class="lg-btn sm ghost" onclick="LogisticsModule.edit(\''+it.id+'\')">Edit</button> <button class="lg-btn sm danger" onclick="LogisticsModule.del(\''+it.id+'\')">Delete</button></td></tr>';
    }); h+='</tbody></table>'; document.getElementById('lg_table').innerHTML=h;
  },

  // ---------- SUPPLIERS ----------
  loadSuppliers:function(){
    document.getElementById('lg_body').innerHTML='<div class="lg-card"><h3>Add Supplier</h3>'
      +'<div class="lg-grid">'
      +'<div><label>Supplier name</label><input id="sp_name"></div>'
      +'<div><label>Contact person</label><input id="sp_contact"></div>'
      +'<div><label>Email</label><input id="sp_email"></div>'
      +'<div><label>Phone</label><input id="sp_phone"></div>'
      +'<div><label>Notes</label><input id="sp_notes"></div>'
      +'</div><div class="lg-bar"><button class="lg-btn" onclick="LogisticsModule.saveSupplier()">Add Supplier</button></div></div>'
      +'<div class="lg-card"><h3>Suppliers</h3><div id="sp_table"></div></div>';
    this.fetchSuppliers();
  },
  fetchSuppliers:function(){ var self=this; fetch(this.apiBase()+"/api/logistics/suppliers/list",{headers:this.hdr()}).then(function(r){return r.json();}).then(function(d){self._suppliers=(d.success&&d.suppliers)?d.suppliers:[];self.renderSuppliers();}).catch(function(){}); },
  saveSupplier:function(){ function v(id){var e=document.getElementById(id);return e?e.value:'';} var body={name:v('sp_name'),contact:v('sp_contact'),email:v('sp_email'),phone:v('sp_phone'),notes:v('sp_notes')};
    if(!body.name.trim()){alert('Supplier name is required.');return;} var self=this;
    fetch(this.apiBase()+"/api/logistics/suppliers/add",{method:"POST",headers:this.hdr(),body:JSON.stringify(body)}).then(function(r){return r.json();}).then(function(d){if(!d.success){alert(d.error||'Could not save.');return;}self.fetchSuppliers();document.getElementById('sp_name').value='';document.getElementById('sp_contact').value='';document.getElementById('sp_email').value='';document.getElementById('sp_phone').value='';document.getElementById('sp_notes').value='';}).catch(function(){alert('Connection error.');}); },
  delSupplier:function(id){ if(!confirm('Delete this supplier?'))return; var self=this; fetch(this.apiBase()+"/api/logistics/suppliers/delete",{method:"POST",headers:this.hdr(),body:JSON.stringify({id:id})}).then(function(r){return r.json();}).then(function(d){if(d.success)self.fetchSuppliers();}).catch(function(){}); },
  renderSuppliers:function(){ if(!this._suppliers.length){document.getElementById('sp_table').innerHTML='<p class="lg-muted">No suppliers yet. Add one above.</p>';return;} var self=this;
    var h='<table class="lg-table"><thead><tr><th>Name</th><th>Contact</th><th>Email</th><th>Phone</th><th></th></tr></thead><tbody>';
    this._suppliers.forEach(function(s){h+='<tr><td><b>'+(s.name||'')+'</b></td><td>'+(s.contact||'')+'</td><td>'+(s.email||'')+'</td><td>'+(s.phone||'')+'</td><td><button class="lg-btn sm danger" onclick="LogisticsModule.delSupplier(\''+s.id+'\')">Delete</button></td></tr>';});
    h+='</tbody></table>'; document.getElementById('sp_table').innerHTML=h;
  },

  // ---------- PURCHASE ORDERS ----------
  loadPO:function(){
    this._poLines=[{name:'',quantity:'',unit_cost:'',item_id:''}];
    document.getElementById('lg_body').innerHTML='<div id="po_kpis"></div>'
      +'<div class="lg-card"><h3>Create Purchase Order</h3>'
      +'<div class="lg-grid"><div><label>Supplier</label><input id="po_supplier" placeholder="Supplier name"></div>'
      +'<div><label>Expected date</label><input id="po_date" type="date"></div></div>'
      +'<div style="margin-top:14px;"><label style="font-weight:700;font-size:.8rem;">Items to order</label><div id="po_lines"></div>'
      +'<button class="lg-btn ghost sm" onclick="LogisticsModule.addPoLine()">+ Add line</button></div>'
      +'<div class="lg-bar"><button class="lg-btn" onclick="LogisticsModule.savePO()">Create Order</button></div></div>'
      +'<div class="lg-card"><h3>Purchase Orders</h3><div id="po_table"></div></div>';
    this.renderPoLines(); this.fetchPO();
  },
  addPoLine:function(){ this._poLines.push({name:'',quantity:'',unit_cost:'',item_id:''}); this.renderPoLines(); },
  removePoLine:function(i){ this._poLines.splice(i,1); if(!this._poLines.length)this._poLines=[{name:'',quantity:'',unit_cost:'',item_id:''}]; this.renderPoLines(); },
  renderPoLines:function(){
    var self=this; var opts='<option value="">-- type a name or pick an item --</option>';
    this._items.forEach(function(it){opts+='<option value="'+it.id+'">'+self.esc(it.name)+'</option>';});
    var h='';
    this._poLines.forEach(function(ln,i){
      h+='<div class="lg-line"><div><label>Item</label><input id="pol_name_'+i+'" placeholder="Item name" value="'+self.esc(ln.name)+'" list="pol_items"></div>'
        +'<div><label>Qty</label><input id="pol_qty_'+i+'" type="number" value="'+self.esc(ln.quantity)+'"></div>'
        +'<div><label>Unit cost</label><input id="pol_cost_'+i+'" type="number" value="'+self.esc(ln.unit_cost)+'"></div>'
        +'<div><button class="lg-btn sm danger" onclick="LogisticsModule.removePoLine('+i+')">x</button></div></div>';
    });
    h+='<datalist id="pol_items">'; this._items.forEach(function(it){h+='<option value="'+self.esc(it.name)+'">';}); h+='</datalist>';
    document.getElementById('po_lines').innerHTML=h;
  },
  gatherPoLines:function(){ var lines=[]; for(var i=0;i<this._poLines.length;i++){ var nm=document.getElementById('pol_name_'+i); var q=document.getElementById('pol_qty_'+i); var c=document.getElementById('pol_cost_'+i); if(!nm)continue; var name=nm.value.trim(); if(!name)continue;
    var item_id=''; for(var j=0;j<this._items.length;j++){if(this._items[j].name.toLowerCase()===name.toLowerCase()){item_id=this._items[j].id;break;}}
    lines.push({name:name,quantity:q?q.value:0,unit_cost:c?c.value:0,item_id:item_id}); } return lines; },
  savePO:function(){ var sup=document.getElementById('po_supplier').value.trim(); if(!sup){alert('Supplier is required.');return;}
    var lines=this.gatherPoLines(); if(!lines.length){alert('Add at least one line item.');return;}
    var body={supplier_name:sup,expected_date:document.getElementById('po_date').value,lines:lines}; var self=this;
    fetch(this.apiBase()+"/api/logistics/po/add",{method:"POST",headers:this.hdr(),body:JSON.stringify(body)}).then(function(r){return r.json();}).then(function(d){if(!d.success){alert(d.error||'Could not create order.');return;}self.loadPO();}).catch(function(){alert('Connection error.');}); },
  fetchPO:function(){ var self=this; fetch(this.apiBase()+"/api/logistics/po/list",{headers:this.hdr()}).then(function(r){return r.json();}).then(function(d){self._pos=(d.success&&d.orders)?d.orders:[];self._poSummary=(d.success&&d.summary)?d.summary:{};self.renderPoKpis();self.renderPO();}).catch(function(){}); },
  renderPoKpis:function(){ var s=this._poSummary||{}; var el=document.getElementById('po_kpis'); if(!el)return;
    el.innerHTML='<div class="lg-kpis"><div class="lg-kpi"><div class="l">Open Orders</div><div class="v">'+(s.open_orders||0)+'</div></div>'
      +'<div class="lg-kpi"><div class="l">Open Value</div><div class="v">'+this.money(s.open_value)+'</div></div>'
      +'<div class="lg-kpi"><div class="l">Total Orders</div><div class="v">'+(s.total_orders||0)+'</div></div></div>'; },
  receivePO:function(id){ if(!confirm('Receive this order? Stock will be added to your inventory.'))return; var self=this;
    fetch(this.apiBase()+"/api/logistics/po/receive",{method:"POST",headers:this.hdr(),body:JSON.stringify({id:id})}).then(function(r){return r.json();}).then(function(d){if(!d.success){alert(d.error||'Could not receive.');return;}alert('Received - stock added to inventory.');self.fetchPO();}).catch(function(){alert('Connection error.');}); },
  delPO:function(id){ if(!confirm('Delete this order?'))return; var self=this; fetch(this.apiBase()+"/api/logistics/po/delete",{method:"POST",headers:this.hdr(),body:JSON.stringify({id:id})}).then(function(r){return r.json();}).then(function(d){if(d.success)self.fetchPO();}).catch(function(){}); },
  renderPO:function(){ if(!this._pos.length){document.getElementById('po_table').innerHTML='<p class="lg-muted">No purchase orders yet. Create one above.</p>';return;} var self=this;
    var h='<table class="lg-table"><thead><tr><th>Supplier</th><th>Items</th><th>Total</th><th>Expected</th><th>Status</th><th></th></tr></thead><tbody>';
    this._pos.forEach(function(po){ var items=(po.lines||[]).map(function(l){return l.name+' x'+l.quantity;}).join(', ');
      var badge=po.status==='Received'?'<span class="lg-badge received">Received</span>':'<span class="lg-badge ordered">Ordered</span>';
      h+='<tr><td><b>'+(po.supplier_name||'')+'</b></td><td>'+items+'</td><td>'+self.money(po.total)+'</td><td>'+(po.expected_date||'')+'</td><td>'+badge+'</td><td>'
        +(po.status==='Received'?'':'<button class="lg-btn sm ok" onclick="LogisticsModule.receivePO(\''+po.id+'\')">Receive</button> ')
        +'<button class="lg-btn sm danger" onclick="LogisticsModule.delPO(\''+po.id+'\')">Delete</button></td></tr>';
    }); h+='</tbody></table>'; document.getElementById('po_table').innerHTML=h;
  }
};
