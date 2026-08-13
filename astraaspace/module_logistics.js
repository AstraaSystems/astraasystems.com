// Astraa Logistics - Phase 1+2: Inventory, Suppliers, Purchase Orders
var LogisticsModule = {
  _tab:"inventory", _items:[], _summary:{}, _editId:null, _editItem:null, _scan:[], _orders:[], _ordSummary:{}, _orderLines:[],
  _suppliers:[], _pos:[], _poSummary:{}, _poLines:[],
  apiBase:function(){
    if(typeof ASTRAA_API_BASE!=='undefined' && ASTRAA_API_BASE) return ASTRAA_API_BASE;
    return "http"+"s://"+"family-speed-outcome"+".ngrok-free"+".dev";
  },
  session:function(){try{return JSON.parse(localStorage.getItem('astraa_session')||'{}');}catch(e){return {};}},
  hdr:function(){return {"Content-Type":"application/json","Authorization":"Bearer "+(this.session().token||""),"ngrok-skip-browser-warning":"true"};},
  money:function(n){return "$"+Number(n||0).toLocaleString(undefined,{minimumFractionDigits:2,maximumFractionDigits:2});},
  esc:function(v){return (v!==undefined&&v!==null)?String(v).replace(/"/g,'&quot;'):'';},
  nsLabel:function(it){var sp=(it.specification||'').trim();return it.name+(sp?(' \u2014 '+sp):'');},

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
    + '<div class="lg-tab" data-t="delivery" onclick="LogisticsModule.go(\'delivery\')">Deliveries</div>'
    + '<div class="lg-tab" data-t="scan" onclick="LogisticsModule.go(\'scan\')">Scan Intake</div>'
    + '<div class="lg-tab" data-t="orders" onclick="LogisticsModule.go(\'orders\')">Sales Orders</div>'
    + '</div><div id="lg_body"></div></div>';
  },

  load:function(){ this.go('inventory'); },

  loadScan:function(){
    var self=this;
    document.getElementById('lg_body').innerHTML=
      '<div class="lg-card"><h3>Scan Intake</h3>'
      +'<p class="lg-muted">Set the shared details once, then scan SKUs. Each new SKU adds a row. Scanning the same SKU again is ignored — edit its quantity on the row. Nothing touches inventory until you press Commit.</p>'
      +'<div class="lg-grid">'
      +this.field('scan_name','Product name','','text')
      +this.field('scan_category','Category','General','text')
      +this.field('scan_spec','Spec / Size','','text')
      +this.field('scan_unit','Unit','each','text')
      +this.field('scan_location','Location','','text')
      +this.field('scan_supplier','Supplier','','text')
      +this.field('scan_unit_cost','Unit cost ($)','','number')
      +this.field('scan_sale_price','Sale price ($)','','number')
      +'</div>'
      +'<div style="margin:14px 0;"><label style="font-weight:800;display:block;margin-bottom:6px;">Scan box</label>'
      +'<input id="lg_scanbox" type="text" placeholder="Click here, then scan a barcode..." autocomplete="off" style="width:100%;padding:12px;font-size:1.1rem;border:2px solid #1d4ed8;border-radius:8px;"></div>'
      +'<div id="scan_toast" style="min-height:22px;font-weight:700;margin-bottom:8px;"></div>'
      +'<div id="scan_table"></div>'
      +'<div style="margin-top:16px;display:flex;gap:12px;align-items:center;">'
      +'<button class="lg-btn" onclick="LogisticsModule.commitScan()">Commit to Inventory</button>'
      +'<button class="lg-btn ghost" onclick="LogisticsModule.clearScan()">Clear sheet</button>'
      +'</div></div>';
    this.renderScan();
    var box=document.getElementById('lg_scanbox');
    box.addEventListener('keydown',function(e){ if(e.key==='Enter'){e.preventDefault();self.onScan(box.value);box.value='';box.focus();} });
    box.focus();
  },
  onScan:function(code){
    code=(code||'').trim(); if(!code)return;
    for(var i=0;i<this._scan.length;i++){ if((this._scan[i].sku||'').toLowerCase()===code.toLowerCase()){ this.scanToast('Duplicate scan ignored: "'+code+'" is already on the sheet — edit its qty.','#dc2626'); return; } }
    var g=function(id){var el=document.getElementById('lg_'+id);return el?el.value:'';};
    this._scan.push({sku:code,name:g('scan_name'),specification:g('scan_spec'),category:g('scan_category'),unit:g('scan_unit'),location:g('scan_location'),supplier:g('scan_supplier'),unit_cost:g('scan_unit_cost'),sale_price:g('scan_sale_price'),quantity:1});
    this.scanToast('Added "'+code+'"','#16a34a');
    this.renderScan();
  },
  renderScan:function(){
    var el=document.getElementById('scan_table'); if(!el)return;
    if(!this._scan.length){el.innerHTML='<p class="lg-muted">No rows yet. Click the scan box and scan a SKU to begin.</p>';return;}
    var h='<table class="lg-table"><thead><tr><th>SKU</th><th>Name</th><th>Spec</th><th>Qty</th><th></th></tr></thead><tbody>';
    for(var i=0;i<this._scan.length;i++){ var r=this._scan[i];
      h+='<tr><td><b>'+this.esc(r.sku)+'</b></td><td>'+this.esc(r.name)+'</td><td>'+this.esc(r.specification)+'</td>'
        +'<td><input type="number" value="'+r.quantity+'" style="width:72px;" onchange="LogisticsModule.scanQty('+i+',this.value)"></td>'
        +'<td><button class="lg-btn sm danger" onclick="LogisticsModule.scanRemove('+i+')">Remove</button></td></tr>';
    }
    h+='</tbody></table><p class="lg-muted" style="margin-top:8px;">'+this._scan.length+' row(s) staged.</p>'; el.innerHTML=h;
  },
  scanQty:function(i,val){ if(this._scan[i]){ this._scan[i].quantity=Number(val)||0; } },
  scanRemove:function(i){ this._scan.splice(i,1); this.renderScan(); },
  clearScan:function(){ if(!this._scan.length)return; if(!confirm('Clear all scanned rows?'))return; this._scan=[]; this.renderScan(); this.scanToast('Sheet cleared.','#334155'); },
  scanToast:function(msg,color){ var t=document.getElementById('scan_toast'); if(t){ t.style.color=color||'#334155'; t.textContent=msg; } },
  commitScan:function(){
    if(!this._scan.length){ this.scanToast('Nothing to commit.','#dc2626'); return; }
    if(!confirm('Commit '+this._scan.length+' item(s) to inventory?'))return;
    var self=this; var rows=this._scan.slice(); var done=0, fail=0;
    var post=function(idx){
      if(idx>=rows.length){ self.scanToast('Committed '+done+' item(s)'+(fail?', '+fail+' failed':'')+'.', fail?'#dc2626':'#16a34a'); self._scan=[]; self.renderScan(); return; }
      var r=rows[idx];
      fetch(self.apiBase()+"/api/logistics/add",{method:"POST",headers:self.hdr(),body:JSON.stringify(r)})
        .then(function(x){return x.json();}).then(function(d){ if(d&&d.success)done++; else fail++; post(idx+1); })
        .catch(function(){ fail++; post(idx+1); });
    };
    post(0);
  },
  loadOrders:function(){
    document.getElementById('lg_body').innerHTML=
      '<div id="ord_kpis"></div>'
      +'<div class="lg-card"><h3>New Sales Order</h3>'
      +'<div class="lg-grid">'
      +this.field('ord_customer','Customer','','text')
      +this.field('ord_notes','Notes','','text')
      +'</div>'
      +'<div style="margin-top:12px;"><label style="font-weight:800;display:block;margin-bottom:6px;">Add line item</label>'
      +'<div class="lg-grid">'
      +this.field('ol_name','Item name','','text')
      +this.field('ol_spec','Spec / Size','','text')
      +this.field('ol_qty','Quantity','1','number')
      +this.field('ol_price','Sale price ($)','','number')
      +'</div>'
      +'<div style="margin-top:8px;"><button class="lg-btn ghost" onclick="LogisticsModule.addOrderLine()">+ Add line</button></div>'
      +'<div id="ord_lines"></div></div>'
      +'<div style="margin-top:14px;"><button class="lg-btn" onclick="LogisticsModule.saveOrder()">Create Order (Draft)</button></div>'
      +'</div>'
      +'<div class="lg-card"><h3>Orders</h3><div id="ord_table"></div></div>';
    this._orderLines=[];
    this.renderOrderLines();
    this.fetchOrders();
    var self=this;
    var nm=document.getElementById('lg_ol_name');
    if(nm) nm.addEventListener('blur',function(){ self.autofillPrice(); });
  },
  autofillPrice:function(){
    var nm=(document.getElementById('lg_ol_name')||{}).value||'';
    var sp=(document.getElementById('lg_ol_spec')||{}).value||'';
    if(!nm)return;
    var match=null;
    for(var i=0;i<this._items.length;i++){ var it=this._items[i];
      if((it.name||'').toLowerCase()===nm.toLowerCase() && (it.specification||'').toLowerCase()===sp.toLowerCase()){ match=it; break; } }
    if(!match){ for(var j=0;j<this._items.length;j++){ if((this._items[j].name||'').toLowerCase()===nm.toLowerCase()){ match=this._items[j]; break; } } }
    if(match){ var pf=document.getElementById('lg_ol_price'); if(pf && !pf.value){ pf.value=Number(match.sale_price||0)||''; } }
  },
  addOrderLine:function(){
    var g=function(id){var el=document.getElementById('lg_'+id);return el?el.value:'';};
    var nm=g('ol_name').trim(); if(!nm){ alert('Item name required.'); return; }
    this._orderLines.push({name:nm,specification:g('ol_spec').trim(),quantity:Number(g('ol_qty'))||0,sale_price:Number(g('ol_price'))||0});
    document.getElementById('lg_ol_name').value='';document.getElementById('lg_ol_spec').value='';
    document.getElementById('lg_ol_qty').value='1';document.getElementById('lg_ol_price').value='';
    this.renderOrderLines();
    document.getElementById('lg_ol_name').focus();
  },
  renderOrderLines:function(){
    var el=document.getElementById('ord_lines'); if(!el)return;
    if(!this._orderLines.length){el.innerHTML='<p class="lg-muted" style="margin-top:8px;">No lines yet.</p>';return;}
    var self=this,tot=0;
    var h='<table class="lg-table" style="margin-top:8px;"><thead><tr><th>Item</th><th>Spec</th><th>Qty</th><th>Price</th><th>Line</th><th></th></tr></thead><tbody>';
    for(var i=0;i<this._orderLines.length;i++){ var r=this._orderLines[i]; var lt=(r.quantity*r.sale_price); tot+=lt;
      h+='<tr><td><b>'+this.esc(r.name)+'</b></td><td>'+this.esc(r.specification)+'</td><td>'+r.quantity+'</td><td>'+this.money(r.sale_price)+'</td><td>'+this.money(lt)+'</td>'
        +'<td><button class="lg-btn sm danger" onclick="LogisticsModule.removeOrderLine('+i+')">Remove</button></td></tr>';
    }
    h+='</tbody></table><p style="margin-top:8px;font-weight:800;">Order total: '+this.money(tot)+'</p>'; el.innerHTML=h;
  },
  removeOrderLine:function(i){ this._orderLines.splice(i,1); this.renderOrderLines(); },
  saveOrder:function(){
    if(!this._orderLines.length){ alert('Add at least one line item.'); return; }
    var g=function(id){var el=document.getElementById('lg_'+id);return el?el.value:'';};
    var self=this;
    var body={customer:g('ord_customer').trim(),notes:g('ord_notes').trim(),lines:this._orderLines};
    fetch(this.apiBase()+"/api/logistics/orders/add",{method:"POST",headers:this.hdr(),body:JSON.stringify(body)})
      .then(function(r){return r.json();}).then(function(d){ if(d&&d.success){ self._orderLines=[]; self.loadOrders(); } else { alert('Could not create order.'); } })
      .catch(function(){ alert('Connection error.'); });
  },
  fetchOrders:function(){
    var self=this;
    fetch(this.apiBase()+"/api/logistics/orders/list",{headers:this.hdr()})
      .then(function(r){return r.json();}).then(function(d){ self._orders=(d.success&&d.orders)?d.orders:[]; self._ordSummary=(d.success&&d.summary)?d.summary:{}; self.renderOrdKpis(); self.renderOrders(); })
      .catch(function(){ var t=document.getElementById('ord_table'); if(t)t.innerHTML='<p style="color:#dc2626;">Connection error.</p>'; });
  },
  renderOrdKpis:function(){
    var s=this._ordSummary||{}; var el=document.getElementById('ord_kpis'); if(!el)return;
    el.innerHTML='<div class="lg-kpis">'
      +'<div class="lg-kpi"><div class="l">Draft</div><div class="v">'+(s.draft||0)+'</div></div>'
      +'<div class="lg-kpi"><div class="l">Pending</div><div class="v">'+(s.pending||0)+'</div></div>'
      +'<div class="lg-kpi"><div class="l">Fulfilled</div><div class="v">'+(s.fulfilled||0)+'</div></div>'
      +'<div class="lg-kpi"><div class="l">Pending Value</div><div class="v">'+this.money(s.pending_value)+'</div></div>'
      +'</div>';
  },
  ordBadge:function(st){
    var c={'Draft':'#64748b','Pending':'#eab308','Fulfilled':'#16a34a','Cancelled':'#dc2626'}[st]||'#64748b';
    return '<span style="background:'+c+';color:#fff;padding:2px 9px;border-radius:10px;font-size:.72rem;font-weight:800;">'+st+'</span>';
  },
  renderOrders:function(){
    var el=document.getElementById('ord_table'); if(!el)return;
    if(!this._orders.length){ el.innerHTML='<p class="lg-muted">No orders yet. Create one above.</p>'; return; }
    var self=this;
    var h='<table class="lg-table"><thead><tr><th>Customer</th><th>Items</th><th>Total</th><th>Status</th><th>Actions</th></tr></thead><tbody>';
    for(var i=0;i<this._orders.length;i++){ var o=this._orders[i];
      var lines=(o.lines||[]).map(function(l){ var w=(l.shortfall&&l.shortfall>0)?(' <span style="color:#dc2626;font-weight:700;">(short '+l.shortfall+')</span>'):''; return self.esc(l.name)+(l.specification?(' ('+self.esc(l.specification)+')'):'')+' x'+l.quantity+w; }).join('<br>');
      var acts='';
      if(o.status==='Draft'){ acts+='<button class="lg-btn sm" onclick="LogisticsModule.confirmOrder(\''+o.id+'\')">Confirm</button> '; }
      if(o.status==='Draft'||o.status==='Pending'){ acts+='<button class="lg-btn sm" onclick="LogisticsModule.fulfillOrder(\''+o.id+'\')">Fulfill &amp; Ship</button> '; acts+='<button class="lg-btn sm ghost" onclick="LogisticsModule.cancelOrder(\''+o.id+'\')">Cancel</button> '; }
      acts+='<button class="lg-btn sm danger" onclick="LogisticsModule.deleteOrder(\''+o.id+'\')">Delete</button>';
      h+='<tr><td><b>'+(this.esc(o.customer)||'<span class="lg-muted">Walk-in</span>')+'</b></td><td style="font-size:.82rem;">'+lines+'</td><td>'+this.money(o.total)+'</td><td>'+this.ordBadge(o.status)+'</td><td>'+acts+'</td></tr>';
    }
    h+='</tbody></table>'; el.innerHTML=h;
  },
  confirmOrder:function(id){
    if(!confirm('Confirm this order? This will reserve stock.'))return;
    var self=this;
    fetch(this.apiBase()+"/api/logistics/orders/confirm",{method:"POST",headers:this.hdr(),body:JSON.stringify({id:id})})
      .then(function(r){return r.json();}).then(function(d){ if(d&&d.success){ self.fetchOrders(); } else { alert((d&&d.error)||'Could not confirm.'); } })
      .catch(function(){ alert('Connection error.'); });
  },
  fulfillOrder:function(id){
    if(!confirm('Ship this order and log the invoice to Finance?'))return;
    var self=this;
    fetch(this.apiBase()+"/api/logistics/orders/fulfill",{method:"POST",headers:this.hdr(),body:JSON.stringify({id:id})})
      .then(function(r){return r.json();}).then(function(d){
        if(d&&d.success){
          var msg='Shipped.'+(d.invoice_logged?' Invoice logged to Finance.':'');
          if(d.shortfalls&&d.shortfalls.length){ msg+=' Backorder: '+d.shortfalls.map(function(x){return x.name+' short '+x.short;}).join(', ')+'.'; }
          alert(msg); self.fetchOrders();
        } else { alert((d&&d.error)||'Could not fulfill.'); }
      })
      .catch(function(){ alert('Connection error.'); });
  },
  cancelOrder:function(id){
    if(!confirm('Cancel this order? Any reserved stock will be released.'))return;
    var self=this;
    fetch(this.apiBase()+"/api/logistics/orders/cancel",{method:"POST",headers:this.hdr(),body:JSON.stringify({id:id})})
      .then(function(r){return r.json();}).then(function(d){ if(d&&d.success){ self.fetchOrders(); } else { alert((d&&d.error)||'Could not cancel.'); } })
      .catch(function(){ alert('Connection error.'); });
  },
  deleteOrder:function(id){
    if(!confirm('Delete this order record?'))return;
    var self=this;
    fetch(this.apiBase()+"/api/logistics/orders/delete",{method:"POST",headers:this.hdr(),body:JSON.stringify({id:id})})
      .then(function(r){return r.json();}).then(function(d){ if(d&&d.success){ self.fetchOrders(); } else { alert((d&&d.error)||'Could not delete.'); } })
      .catch(function(){ alert('Connection error.'); });
  },
  go:function(tab){
    this._tab=tab;
    var tabs=document.querySelectorAll('.lg-tab');
    for(var i=0;i<tabs.length;i++){tabs[i].className='lg-tab'+(tabs[i].getAttribute('data-t')===tab?' on':'');}
    if(tab==='inventory') this.loadInventory();
    else if(tab==='suppliers') this.loadSuppliers();
    else if(tab==='po') this.loadPO();
    else if(tab==='delivery') this.loadDelivery();
    else if(tab==='scan') this.loadScan();
    else if(tab==='orders') this.loadOrders();
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
      +this.field('specification','Specification / Size',e.specification)
      +this.field('category','Category',e.category)+this.field('unit','Unit (each, box, sqft)',e.unit)
      +this.field('unit_cost','Unit cost ($)',e.unit_cost,'number')+this.field('sale_price','Sale price ($)',e.sale_price,'number')
      +this.field('markup_percent','Markup %',e.markup_percent,'number')+this.field('quantity','Quantity',e.quantity,'number')
      +this.field('location','Location',e.location)+this.field('reorder_point','Reorder point',e.reorder_point,'number')+this.field('reserved','Reserved (committed)',e.reserved,'number')
      +this.field('supplier','Supplier',e.supplier)+this.field('notes','Notes',e.notes)
      +'</div><div class="lg-bar"><button class="lg-btn" onclick="LogisticsModule.save()">'+(this._editId?'Update Item':'Add Item')+'</button>'
      +(this._editId?'<button class="lg-btn ghost" onclick="LogisticsModule.cancelEdit()">Cancel</button>':'')+'</div>';
    var ft=document.getElementById('lg_formtitle'); if(ft)ft.innerText=this._editId?'Edit Item':'Add Item';
  },
  gather:function(){ function v(id){var el=document.getElementById('lg_'+id);return el?el.value:'';}
    return {name:v('name'),sku:v('sku'),specification:v('specification'),category:v('category'),unit:v('unit'),unit_cost:v('unit_cost'),sale_price:v('sale_price'),markup_percent:v('markup_percent'),quantity:v('quantity'),location:v('location'),reorder_point:v('reorder_point'),reserved:v('reserved'),supplier:v('supplier'),notes:v('notes')}; },
  applyMarkup:function(){var c=parseFloat(document.getElementById('lg_unit_cost').value)||0;var mk=parseFloat(document.getElementById('lg_markup_percent').value)||0;if(c>0&&mk>0){document.getElementById('lg_sale_price').value=(c*(1+mk/100)).toFixed(2);}},
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
    var self=this; var h='<table class="lg-table"><thead><tr><th>Item</th><th>SKU</th><th>Spec</th><th>Category</th><th>Qty</th><th>Reserved</th><th>Available</th><th>On-Order</th><th>ETA</th><th>Unit cost</th><th>Sale</th><th>Margin</th><th>Value</th><th>Location</th><th></th></tr></thead><tbody>';
    this._items.forEach(function(it){ var qty=Number(it.quantity||0),cost=Number(it.unit_cost||0),sale=Number(it.sale_price||0),rp=Number(it.reorder_point||0),reserved=Number(it.reserved||0),available=(qty-reserved); var marginPct=(sale>0?((sale-cost)/sale*100):0); var marginTxt=(sale>0?marginPct.toFixed(0)+'%':'-'); var marginColor=(sale<=0?'#94a3b8':(marginPct>=30?'#16a34a':(marginPct>=10?'#eab308':'#dc2626'))); var availColor=(available<=0?'#dc2626':(rp>0&&available<=rp?'#eab308':'#16a34a'));var low=(rp>0&&available<=rp);var onOrder=Number(it.on_order||0);var eta=(it.on_order_eta||'');var onOrderTxt=(onOrder>0?'+'+onOrder:'—');var onOrderColor=(onOrder>0?'#2563eb':'#94a3b8');var etaTxt=(eta?eta:'—');var etaOverdue=false;if(eta){var _t=new Date(eta+'T00:00:00');var _n=new Date();_n.setHours(0,0,0,0);etaOverdue=(_t<_n);}var etaColor=(etaOverdue?'#dc2626':'#334155');
      h+='<tr class="'+(low?'low':'')+'"><td><b>'+(it.name||'')+'</b>'+(low?'<span class="lg-lowtag">LOW</span>':'')+'</td><td>'+(it.sku||'')+'</td><td>'+(it.specification||'')+'</td><td>'+(it.category||'')+'</td>'
        +'<td><span class="lg-qty"><button class="lg-qbtn" onclick="LogisticsModule.adjust(\''+it.id+'\',-1)">-</button>'+qty+'<button class="lg-qbtn" onclick="LogisticsModule.adjust(\''+it.id+'\',1)">+</button></span></td>'
        +'<td>'+reserved+'</td>'+'<td style="color:'+availColor+';font-weight:600">'+available+'</td>'
        +'<td style="color:'+onOrderColor+';font-weight:600">'+onOrderTxt+'</td>'+'<td style="color:'+etaColor+'">'+etaTxt+'</td>'
        +'<td>'+self.money(cost)+'</td>'+'<td>'+self.money(sale)+'</td>'+'<td style="color:'+marginColor+';font-weight:600">'+marginTxt+'</td>'+'<td>'+self.money(qty*cost)+'</td><td>'+(it.location||'')+'</td>'
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
    this._poLines=[{name:'',specification:'',quantity:'',unit_cost:'',item_id:''}];
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
  addPoLine:function(){ this._poLines.push({name:'',specification:'',quantity:'',unit_cost:'',item_id:''}); this.renderPoLines(); },
  removePoLine:function(i){ this._poLines.splice(i,1); if(!this._poLines.length)this._poLines=[{name:'',specification:'',quantity:'',unit_cost:'',item_id:''}]; this.renderPoLines(); },
  renderPoLines:function(){
    var self=this; var opts='<option value="">-- type a name or pick an item --</option>';
    this._items.forEach(function(it){opts+='<option value="'+it.id+'">'+self.esc(it.name)+'</option>';});
    var h='';
    this._poLines.forEach(function(ln,i){
      h+='<div class="lg-line" style="grid-template-columns:2fr 1fr 1fr 1fr auto;"><div><label>Item</label><input id="pol_name_'+i+'" placeholder="Item name" value="'+self.esc(ln.name)+'" list="pol_items"></div>'
        +'<div><label>Spec</label><input id="pol_spec_'+i+'" placeholder="e.g. 10ft" value="'+self.esc(ln.specification)+'"></div>'
        +'<div><label>Qty</label><input id="pol_qty_'+i+'" type="number" value="'+self.esc(ln.quantity)+'"></div>'
        +'<div><label>Unit cost</label><input id="pol_cost_'+i+'" type="number" value="'+self.esc(ln.unit_cost)+'"></div>'
        +'<div><button class="lg-btn sm danger" onclick="LogisticsModule.removePoLine('+i+')">x</button></div></div>';
    });
    h+='<datalist id="pol_items">'; this._items.forEach(function(it){h+='<option value="'+self.esc(self.nsLabel(it))+'">';}); h+='</datalist>';
    document.getElementById('po_lines').innerHTML=h;
  },
  gatherPoLines:function(){ var lines=[]; for(var i=0;i<this._poLines.length;i++){ var nm=document.getElementById('pol_name_'+i); var sp=document.getElementById('pol_spec_'+i); var q=document.getElementById('pol_qty_'+i); var c=document.getElementById('pol_cost_'+i); if(!nm)continue; var raw=nm.value.trim(); if(!raw)continue;
    var name=raw; var spec=sp?sp.value.trim():''; var dash=raw.indexOf(' \u2014 '); if(dash!==-1){ name=raw.substring(0,dash).trim(); if(!spec)spec=raw.substring(dash+3).trim(); }
    var item_id=''; for(var j=0;j<this._items.length;j++){if(this._items[j].name.toLowerCase()===name.toLowerCase() && (this._items[j].specification||'').toLowerCase()===spec.toLowerCase()){item_id=this._items[j].id;break;}}
    lines.push({name:name,specification:spec,quantity:q?q.value:0,unit_cost:c?c.value:0,item_id:item_id}); } return lines; },
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
  ,
  // ---------- DELIVERIES ----------
  _dvLines:[],
  loadDelivery:function(){
    var self=this;
    // ensure inventory is loaded for item picking
    fetch(this.apiBase()+"/api/logistics/list",{headers:this.hdr()}).then(function(r){return r.json();}).then(function(d){
      self._items=(d.success&&d.items)?d.items:[];
      self._dvLines=[{name:'',specification:'',quantity:'',item_id:''}];
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
  addDvLine:function(){ this._dvLines.push({name:'',specification:'',quantity:'',item_id:''}); this.renderDvLines(); },
  removeDvLine:function(i){ this._dvLines.splice(i,1); if(!this._dvLines.length)this._dvLines=[{name:'',specification:'',quantity:'',item_id:''}]; this.renderDvLines(); },
  renderDvLines:function(){
    var self=this; var h='';
    this._dvLines.forEach(function(ln,i){
      h+='<div class="lg-line" style="grid-template-columns:2fr 1fr 1fr auto;"><div><label>Item</label><input id="dvl_name_'+i+'" placeholder="Item name" value="'+self.esc(ln.name)+'" list="dvl_items"></div>'
        +'<div><label>Spec</label><input id="dvl_spec_'+i+'" placeholder="e.g. 10ft" value="'+self.esc(ln.specification)+'"></div>'
        +'<div><label>Qty</label><input id="dvl_qty_'+i+'" type="number" value="'+self.esc(ln.quantity)+'"></div>'
        +'<div><button class="lg-btn sm danger" onclick="LogisticsModule.removeDvLine('+i+')">x</button></div></div>';
    });
    h+='<datalist id="dvl_items">'; this._items.forEach(function(it){h+='<option value="'+self.esc(self.nsLabel(it))+'">';}); h+='</datalist>';
    document.getElementById('dv_lines').innerHTML=h;
  },
  gatherDvLines:function(){ var lines=[]; for(var i=0;i<this._dvLines.length;i++){ var nm=document.getElementById('dvl_name_'+i); var sp=document.getElementById('dvl_spec_'+i); var q=document.getElementById('dvl_qty_'+i); if(!nm)continue; var raw=nm.value.trim(); if(!raw)continue;
    var name=raw; var spec=sp?sp.value.trim():''; var dash=raw.indexOf(' \u2014 '); if(dash!==-1){ name=raw.substring(0,dash).trim(); if(!spec)spec=raw.substring(dash+3).trim(); }
    var item_id=''; for(var j=0;j<this._items.length;j++){if(this._items[j].name.toLowerCase()===name.toLowerCase() && (this._items[j].specification||'').toLowerCase()===spec.toLowerCase()){item_id=this._items[j].id;break;}}
    lines.push({name:name,specification:spec,quantity:q?q.value:0,item_id:item_id}); } return lines; },
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

};
