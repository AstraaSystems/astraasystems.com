import shutil
from pathlib import Path
from datetime import datetime
stamp = datetime.now().strftime("%Y%m%d_%H%M%S")

mp = Path("astraaspace/module_logistics.js"); m = mp.read_text(encoding="utf-8")
shutil.copyfile(mp, f"astraaspace/module_logistics.js.bak_6f_{stamp}")
ch = 0

# 1) state: add _orders + _orderLines + _ordSummary
st_old = "_editItem:null, _scan:[],"
st_new = "_editItem:null, _scan:[], _orders:[], _ordSummary:{}, _orderLines:[],"
if st_old in m and "_orders:[]" not in m:
    m = m.replace(st_old, st_new, 1); ch += 1

# 2) tab button after Scan Intake
scantab = r"""    + '<div class="lg-tab" data-t="scan" onclick="LogisticsModule.go(\'scan\')">Scan Intake</div>'"""
ordtab = r"""    + '<div class="lg-tab" data-t="orders" onclick="LogisticsModule.go(\'orders\')">Sales Orders</div>'"""
if scantab in m and 'data-t="orders"' not in m:
    m = m.replace(scantab, scantab + "\n" + ordtab, 1); ch += 1

# 3) go() branch
go_old = "    else if(tab==='scan') this.loadScan();"
go_new = go_old + "\n    else if(tab==='orders') this.loadOrders();"
if go_old in m and "tab==='orders'" not in m:
    m = m.replace(go_old, go_new, 1); ch += 1

# 4) methods before go:function
methods = r"""  loadOrders:function(){
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
"""
go_anchor = "  go:function(tab){"
if go_anchor in m and "loadOrders:function" not in m:
    m = m.replace(go_anchor, methods + go_anchor, 1); ch += 1

mp.write_text(m, encoding="utf-8")
print(f"6f frontend changes: {ch} (expected 4)")
