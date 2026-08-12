import shutil
from pathlib import Path
from datetime import datetime
stamp = datetime.now().strftime("%Y%m%d_%H%M%S")

mp = Path("astraaspace/module_logistics.js"); m = mp.read_text(encoding="utf-8")
shutil.copyfile(mp, f"astraaspace/module_logistics.js.bak_5c3_{stamp}")
ch = 0

# 1) state: add _scan array
st_old = "_editItem:null,"
st_new = "_editItem:null, _scan:[],"
if st_old in m and "_scan:[]" not in m:
    m = m.replace(st_old, st_new, 1); ch += 1

# 2) tab button after Deliveries
deliv = r"""    + '<div class="lg-tab" data-t="delivery" onclick="LogisticsModule.go(\'delivery\')">Deliveries</div>'"""
scantab = r"""    + '<div class="lg-tab" data-t="scan" onclick="LogisticsModule.go(\'scan\')">Scan Intake</div>'"""
if deliv in m and 'data-t="scan"' not in m:
    m = m.replace(deliv, deliv + "\n" + scantab, 1); ch += 1

# 3) go() branch
go_old = "    else if(tab==='delivery') this.loadDelivery();"
go_new = go_old + "\n    else if(tab==='scan') this.loadScan();"
if go_old in m and "tab==='scan'" not in m:
    m = m.replace(go_old, go_new, 1); ch += 1

# 4) scan methods inserted before go:function
methods = """  loadScan:function(){
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
"""
go_anchor = "  go:function(tab){"
if go_anchor in m and "loadScan:function" not in m:
    m = m.replace(go_anchor, methods + go_anchor, 1); ch += 1

mp.write_text(m, encoding="utf-8")
print(f"Frontend changes: {ch} (expected 4)")
