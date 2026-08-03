// Astraa Logistics - Phase 1: Inventory Core
var LogisticsModule = {
  _items:[], _summary:{}, _editId:null,
  apiBase:function(){
    if(typeof ASTRAA_API_BASE!=='undefined' && ASTRAA_API_BASE) return ASTRAA_API_BASE;
    return "http"+"s://"+"family-speed-outcome"+".ngrok-free"+".dev";
  },
  session:function(){try{return JSON.parse(localStorage.getItem('astraa_session')||'{}');}catch(e){return {};}},
  hdr:function(){return {"Content-Type":"application/json","Authorization":"Bearer "+(this.session().token||""),"ngrok-skip-browser-warning":"true"};},
  money:function(n){return "$"+Number(n||0).toLocaleString(undefined,{minimumFractionDigits:2,maximumFractionDigits:2});},

  styles:function(){
    return '<style>'
    + '.lg-wrap{font-family:Inter,system-ui,sans-serif;padding:26px 30px;background:#f8fafc;min-height:calc(100vh - 120px);}'
    + '.lg-h{font-size:1.6rem;font-weight:900;color:#0f172a;letter-spacing:-0.03em;margin:0 0 4px;}'
    + '.lg-sub{color:#64748b;margin:0 0 22px;font-size:.95rem;}'
    + '.lg-kpis{display:grid;grid-template-columns:repeat(auto-fit,minmax(180px,1fr));gap:14px;margin-bottom:22px;}'
    + '.lg-kpi{background:#fff;border:1px solid #e2e8f0;border-radius:14px;padding:18px;box-shadow:0 4px 14px rgba(15,23,42,.04);}'
    + '.lg-kpi .l{color:#64748b;font-size:.75rem;font-weight:800;text-transform:uppercase;letter-spacing:.05em;margin-bottom:6px;}'
    + '.lg-kpi .v{font-size:1.5rem;font-weight:900;color:#0f172a;}'
    + '.lg-kpi.warn .v{color:#dc2626;}'
    + '.lg-card{background:#fff;border:1px solid #e2e8f0;border-radius:16px;padding:22px;box-shadow:0 4px 14px rgba(15,23,42,.04);margin-bottom:18px;}'
    + '.lg-card h3{margin:0 0 16px;font-size:1.05rem;font-weight:800;color:#0f172a;}'
    + '.lg-grid{display:grid;grid-template-columns:1fr 1fr;gap:12px;}'
    + '.lg-grid label{display:block;font-weight:700;font-size:.8rem;color:#0f172a;margin-bottom:5px;}'
    + '.lg-grid input{width:100%;padding:9px 11px;border:1px solid #cbd5e1;border-radius:9px;font-size:.92rem;box-sizing:border-box;}'
    + '.lg-btn{background:#1d4ed8;color:#fff;border:none;border-radius:10px;padding:11px 18px;font-weight:800;cursor:pointer;font-size:.9rem;}'
    + '.lg-btn.ghost{background:#fff;color:#1d4ed8;border:1px solid #bfdbfe;}'
    + '.lg-btn.sm{padding:5px 10px;font-size:.8rem;border-radius:7px;}'
    + '.lg-btn.danger{background:#fff;color:#dc2626;border:1px solid #fecaca;}'
    + '.lg-bar{display:flex;gap:10px;margin-top:14px;flex-wrap:wrap;}'
    + '.lg-table{width:100%;border-collapse:collapse;font-size:.9rem;}'
    + '.lg-table th{text-align:left;color:#64748b;font-size:.75rem;text-transform:uppercase;letter-spacing:.04em;padding:10px 8px;border-bottom:2px solid #e2e8f0;}'
    + '.lg-table td{padding:11px 8px;border-bottom:1px solid #f1f5f9;color:#334155;}'
    + '.lg-table tr.low td{background:#fef2f2;}'
    + '.lg-lowtag{display:inline-block;background:#fee2e2;color:#b91c1c;font-size:.68rem;font-weight:800;padding:2px 7px;border-radius:6px;margin-left:6px;}'
    + '.lg-qty{display:inline-flex;align-items:center;gap:6px;}'
    + '.lg-qbtn{width:26px;height:26px;border:1px solid #cbd5e1;background:#fff;border-radius:6px;cursor:pointer;font-weight:900;color:#1d4ed8;line-height:1;}'
    + '.lg-muted{color:#94a3b8;font-size:.92rem;}'
    + '</style>';
  },

  render:function(){
    return this.styles() + '<div class="lg-wrap">'
    + '<h2 class="lg-h">Astraa Logistics</h2>'
    + '<p class="lg-sub">Inventory Core - track your materials, stock levels and value.</p>'
    + '<div id="lg_kpis"></div>'
    + '<div class="lg-card"><h3 id="lg_formtitle">Add Item</h3><div id="lg_form"></div></div>'
    + '<div class="lg-card"><h3>Inventory</h3><div id="lg_table"></div></div>'
    + '</div>';
  },

  load:function(){ this.renderForm(); this.fetchList(); },

  fetchList:function(){
    var self=this;
    fetch(this.apiBase()+"/api/logistics/list",{headers:this.hdr()})
      .then(function(r){return r.json();})
      .then(function(d){
        self._items = (d.success && d.items) ? d.items : [];
        self._summary = (d.success && d.summary) ? d.summary : {};
        self.renderKpis(); self.renderTable();
      })
      .catch(function(){ document.getElementById('lg_table').innerHTML='<p style="color:#dc2626;">Connection error.</p>'; });
  },

  renderKpis:function(){
    var s=this._summary||{};
    var h='<div class="lg-kpis">'
      + '<div class="lg-kpi"><div class="l">Items</div><div class="v">'+(s.item_count||0)+'</div></div>'
      + '<div class="lg-kpi"><div class="l">Total Stock Value</div><div class="v">'+this.money(s.total_value)+'</div></div>'
      + '<div class="lg-kpi'+((s.low_stock_count||0)>0?' warn':'')+'"><div class="l">Low Stock</div><div class="v">'+(s.low_stock_count||0)+'</div></div>'
      + '</div>';
    document.getElementById('lg_kpis').innerHTML=h;
  },

  field:function(id,label,val,type){
    return '<div><label>'+label+'</label><input id="lg_'+id+'" type="'+(type||'text')+'" value="'+(val!==undefined&&val!==null?String(val).replace(/"/g,'&quot;'):'')+'"></div>';
  },

  renderForm:function(){
    var e=this._editItem||{};
    var h='<div class="lg-grid">'
      + this.field('name','Item name',e.name)
      + this.field('sku','SKU',e.sku)
      + this.field('category','Category',e.category)
      + this.field('unit','Unit (each, box, sqft)',e.unit)
      + this.field('unit_cost','Unit cost ($)',e.unit_cost,'number')
      + this.field('quantity','Quantity',e.quantity,'number')
      + this.field('location','Location',e.location)
      + this.field('reorder_point','Reorder point',e.reorder_point,'number')
      + this.field('supplier','Supplier',e.supplier)
      + this.field('notes','Notes',e.notes)
      + '</div><div class="lg-bar">'
      + '<button class="lg-btn" onclick="LogisticsModule.save()">'+(this._editId?'Update Item':'Add Item')+'</button>'
      + (this._editId?'<button class="lg-btn ghost" onclick="LogisticsModule.cancelEdit()">Cancel</button>':'')
      + '</div>';
    document.getElementById('lg_form').innerHTML=h;
    document.getElementById('lg_formtitle').innerText=this._editId?'Edit Item':'Add Item';
  },

  gather:function(){
    function v(id){var el=document.getElementById('lg_'+id);return el?el.value:'';}
    return {name:v('name'),sku:v('sku'),category:v('category'),unit:v('unit'),
      unit_cost:v('unit_cost'),quantity:v('quantity'),location:v('location'),
      reorder_point:v('reorder_point'),supplier:v('supplier'),notes:v('notes')};
  },

  save:function(){
    var body=this.gather();
    if(!body.name.trim()){ alert('Item name is required.'); return; }
    var url=this._editId?"/api/logistics/update":"/api/logistics/add";
    if(this._editId){ body.id=this._editId; }
    var self=this;
    fetch(this.apiBase()+url,{method:"POST",headers:this.hdr(),body:JSON.stringify(body)})
      .then(function(r){return r.json();})
      .then(function(d){
        if(!d.success){ alert(d.error||'Could not save.'); return; }
        self._editId=null; self._editItem=null; self.renderForm(); self.fetchList();
      })
      .catch(function(){ alert('Connection error.'); });
  },

  edit:function(id){
    for(var i=0;i<this._items.length;i++){ if(this._items[i].id===id){ this._editItem=this._items[i]; this._editId=id; break; } }
    this.renderForm();
    window.scrollTo(0,0);
  },

  cancelEdit:function(){ this._editId=null; this._editItem=null; this.renderForm(); },

  adjust:function(id,delta){
    var self=this;
    fetch(this.apiBase()+"/api/logistics/adjust",{method:"POST",headers:this.hdr(),body:JSON.stringify({id:id,delta:delta})})
      .then(function(r){return r.json();}).then(function(d){ if(d.success) self.fetchList(); })
      .catch(function(){});
  },

  del:function(id){
    if(!confirm('Delete this item?')) return;
    var self=this;
    fetch(this.apiBase()+"/api/logistics/delete",{method:"POST",headers:this.hdr(),body:JSON.stringify({id:id})})
      .then(function(r){return r.json();}).then(function(d){ if(d.success) self.fetchList(); })
      .catch(function(){});
  },

  renderTable:function(){
    if(!this._items.length){ document.getElementById('lg_table').innerHTML='<p class="lg-muted">No items yet. Add your first inventory item above.</p>'; return; }
    var self=this;
    var h='<table class="lg-table"><thead><tr><th>Item</th><th>SKU</th><th>Category</th><th>Qty</th><th>Unit cost</th><th>Value</th><th>Location</th><th></th></tr></thead><tbody>';
    this._items.forEach(function(it){
      var qty=Number(it.quantity||0), cost=Number(it.unit_cost||0), rp=Number(it.reorder_point||0);
      var low=(rp>0 && qty<=rp);
      h+='<tr class="'+(low?'low':'')+'">'
        +'<td><b>'+(it.name||'')+'</b>'+(low?'<span class="lg-lowtag">LOW</span>':'')+'</td>'
        +'<td>'+(it.sku||'')+'</td>'
        +'<td>'+(it.category||'')+'</td>'
        +'<td><span class="lg-qty"><button class="lg-qbtn" onclick="LogisticsModule.adjust(\''+it.id+'\',-1)">-</button>'+qty+'<button class="lg-qbtn" onclick="LogisticsModule.adjust(\''+it.id+'\',1)">+</button></span></td>'
        +'<td>'+self.money(cost)+'</td>'
        +'<td>'+self.money(qty*cost)+'</td>'
        +'<td>'+(it.location||'')+'</td>'
        +'<td><button class="lg-btn sm ghost" onclick="LogisticsModule.edit(\''+it.id+'\')">Edit</button> <button class="lg-btn sm danger" onclick="LogisticsModule.del(\''+it.id+'\')">Delete</button></td>'
        +'</tr>';
    });
    h+='</tbody></table>';
    document.getElementById('lg_table').innerHTML=h;
  }
};
