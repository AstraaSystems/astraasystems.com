// Astraa Expense — per-account expense tracking MVP
var ExpenseModule = {
  _cats: [],
  apiBase:function(){return (typeof ASTRAA_API_BASE!=='undefined')?ASTRAA_API_BASE:"https://family-speed-outcome.ngrok-free.dev";},
  session:function(){try{return JSON.parse(localStorage.getItem('astraa_session')||'{}');}catch(e){return {};}},
  hdr:function(){return {"Content-Type":"application/json","Authorization":"Bearer "+(this.session().token||""),"ngrok-skip-browser-warning":"true"};},

  render:function(){
    var f="width:100%;padding:11px 13px;border:1px solid #e2e8f0;border-radius:8px;background:#f8fafc;color:#0f172a;font-size:0.95rem;";
    return this.styles()
      + '<div class="ex-wrap">'
      + '  <div class="ex-head"><h2 class="ex-title">Astraa Expense</h2><p class="ex-sub">Track and categorize your business expenses.</p></div>'
      + '  <div class="ex-grid">'
      + '    <div class="ex-card">'
      + '      <h3 class="ex-h3">Add Expense</h3>'
      + '      <div class="ex-field"><label>Date</label><input id="ex_date" type="date" style="'+f+'"></div>'
      + '      <div class="ex-field"><label>Category</label><select id="ex_cat" style="'+f+'"></select></div>'
      + '      <div class="ex-field"><label>Amount ($)</label><input id="ex_amount" type="number" step="0.01" placeholder="0.00" style="'+f+'"></div>'
      + '      <div class="ex-field"><label>Vendor / Supplier</label><input id="ex_vendor" type="text" placeholder="e.g. Home Depot" style="'+f+'"></div>'
      + '      <div class="ex-field"><label>Project / Job (optional)</label><input id="ex_project" type="text" placeholder="e.g. Smith Reno" style="'+f+'"></div>'
      + '      <div class="ex-field"><label>Notes</label><input id="ex_notes" type="text" placeholder="optional" style="'+f+'"></div>'
      + '      <button class="ex-add" onclick="ExpenseModule.add()">Add Expense</button>'
      + '    </div>'
      + '    <div class="ex-card">'
      + '      <div id="ex_summary"></div>'
      + '      <div style="display:flex;justify-content:space-between;align-items:center;margin:14px 0 6px;">'
      + '        <h3 class="ex-h3" style="margin:0;">Expenses</h3>'
      + '        <button class="ex-print" onclick="ExpenseModule.printReport()">Print Report</button>'
      + '      </div>'
      + '      <div id="ex_list"></div>'
      + '    </div>'
      + '  </div>'
      + '</div>';
  },

  load:function(){
    var self=this;
    // set today's date
    var d=document.getElementById('ex_date'); if(d) d.value=new Date().toISOString().slice(0,10);
    // categories
    fetch(this.apiBase()+"/api/expense/categories",{headers:{"ngrok-skip-browser-warning":"true"}})
      .then(function(r){return r.json();}).then(function(x){
        if(x.success){self._cats=x.categories;var sel=document.getElementById('ex_cat');
          if(sel)sel.innerHTML=x.categories.map(function(c){return "<option>"+c+"</option>";}).join("");}
      }).catch(function(){});
    this.refresh();
  },

  refresh:function(){
    var self=this;
    fetch(this.apiBase()+"/api/expense/list",{headers:this.hdr()})
      .then(function(r){return r.json();}).then(function(d){
        if(!d.success){document.getElementById('ex_list').innerHTML="<p style='color:#dc2626;'>"+(d.error||'Error')+"</p>";return;}
        var s=d.summary||{};
        var money=function(n){return "$"+Number(n||0).toLocaleString(undefined,{minimumFractionDigits:2,maximumFractionDigits:2});};
        var catRows=Object.keys(s.by_category||{}).map(function(k){return "<div class='ex-catrow'><span>"+k+"</span><span>"+money(s.by_category[k])+"</span></div>";}).join("");
        document.getElementById('ex_summary').innerHTML=
          "<div class='ex-stats'>"
          +"<div class='ex-stat'><span class='ex-stat-l'>Total spent</span><span class='ex-stat-v'>"+money(s.total)+"</span></div>"
          +"<div class='ex-stat'><span class='ex-stat-l'>This month</span><span class='ex-stat-v'>"+money(s.month_total)+"</span></div>"
          +"<div class='ex-stat'><span class='ex-stat-l'>Entries</span><span class='ex-stat-v'>"+(s.count||0)+"</span></div>"
          +"</div>"
          +(catRows?"<div class='ex-catbox'>"+catRows+"</div>":"");
        var items=d.expenses||[];
        if(!items.length){document.getElementById('ex_list').innerHTML="<p style='color:#94a3b8;'>No expenses yet. Add your first above.</p>";return;}
        document.getElementById('ex_list').innerHTML=items.map(function(x){
          return "<div class='ex-item'>"
            +"<div><div class='ex-item-top'>"+money(x.amount)+" · "+x.category+"</div>"
            +"<div class='ex-item-sub'>"+x.date+(x.vendor?" · "+x.vendor:"")+(x.project?" · "+x.project:"")+(x.notes?" · "+x.notes:"")+"</div></div>"
            +"<button class='ex-del' onclick=\"ExpenseModule.del('"+x.id+"')\">✕</button></div>";
        }).join("");
      }).catch(function(e){document.getElementById('ex_list').innerHTML="<p style='color:#dc2626;'>Connection error.</p>";});
  },

  add:function(){
    var self=this;
    function v(id){var e=document.getElementById(id);return e?e.value:"";}
    var amount=parseFloat(v('ex_amount'))||0;
    if(amount<=0){alert("Enter a valid amount.");return;}
    var body={date:v('ex_date'),category:v('ex_cat'),amount:amount,vendor:v('ex_vendor'),project:v('ex_project'),notes:v('ex_notes')};
    fetch(this.apiBase()+"/api/expense/add",{method:"POST",headers:this.hdr(),body:JSON.stringify(body)})
      .then(function(r){return r.json();}).then(function(d){
        if(!d.success){alert(d.error||"Failed to add.");return;}
        document.getElementById('ex_amount').value="";document.getElementById('ex_vendor').value="";
        document.getElementById('ex_project').value="";document.getElementById('ex_notes').value="";
        self.refresh();
      }).catch(function(){alert("Connection error.");});
  },

  del:function(id){
    var self=this;
    if(!confirm("Delete this expense?"))return;
    fetch(this.apiBase()+"/api/expense/delete",{method:"POST",headers:this.hdr(),body:JSON.stringify({id:id})})
      .then(function(r){return r.json();}).then(function(){self.refresh();}).catch(function(){});
  },

  printReport:function(){
    var el=document.getElementById('ex_summary').parentNode;
    var w=window.open('','_blank');
    w.document.write("<html><head><title>Astraa Expense Report</title></head><body style='font-family:Segoe UI,Arial,sans-serif;padding:24px;'><h1>Expense Report</h1><p>Generated "+new Date().toLocaleDateString()+"</p>"+el.innerHTML+"</body></html>");
    w.document.close();w.focus();w.print();
  },

  styles:function(){
    return "<style>"
    +".ex-wrap{max-width:1000px;}"
    +".ex-head{margin-bottom:18px;}.ex-title{margin:0;font-size:1.6rem;font-weight:900;color:#090d16;}.ex-sub{margin:4px 0 0;color:#64748b;font-size:0.9rem;}"
    +".ex-grid{display:grid;grid-template-columns:1fr 1.2fr;gap:20px;align-items:start;}"
    +".ex-card{background:#fff;border:1px solid #e2e8f0;border-radius:16px;padding:24px;box-shadow:0 10px 30px rgba(15,23,42,0.05);}"
    +".ex-h3{font-size:1.1rem;font-weight:800;color:#0f172a;margin:0 0 14px;}"
    +".ex-field{margin-bottom:12px;}.ex-field label{display:block;font-size:0.78rem;font-weight:800;color:#0f172a;margin-bottom:5px;text-transform:uppercase;letter-spacing:.03em;}"
    +".ex-add{width:100%;padding:12px;border:none;border-radius:10px;background:#1d4ed8;color:#fff;font-weight:800;cursor:pointer;box-shadow:0 8px 20px rgba(29,78,216,0.25);}"
    +".ex-add:hover{background:#1e40af;}"
    +".ex-print{padding:7px 12px;border:1px solid #e2e8f0;border-radius:8px;background:#fff;color:#1d4ed8;font-size:12px;font-weight:700;cursor:pointer;}"
    +".ex-stats{display:flex;gap:12px;margin-bottom:12px;}"
    +".ex-stat{flex:1;background:#f8fafc;border:1px solid #e2e8f0;border-radius:12px;padding:12px;text-align:center;}"
    +".ex-stat-l{display:block;font-size:11px;color:#64748b;font-weight:700;text-transform:uppercase;}"
    +".ex-stat-v{display:block;font-size:1.2rem;font-weight:900;color:#090d16;margin-top:4px;}"
    +".ex-catbox{background:#f8fafc;border:1px solid #e2e8f0;border-radius:10px;padding:12px;margin-bottom:6px;}"
    +".ex-catrow{display:flex;justify-content:space-between;font-size:13px;color:#475569;padding:3px 0;}"
    +".ex-item{display:flex;justify-content:space-between;align-items:center;border-bottom:1px solid #f1f5f9;padding:10px 0;}"
    +".ex-item-top{font-weight:800;color:#0f172a;font-size:0.95rem;}.ex-item-sub{color:#94a3b8;font-size:12px;margin-top:2px;}"
    +".ex-del{background:#fff;border:1px solid #fecaca;color:#dc2626;border-radius:6px;width:26px;height:26px;cursor:pointer;font-weight:700;}"
    +"@media(max-width:820px){.ex-grid{grid-template-columns:1fr;}.ex-stats{flex-direction:column;}}"
    +"</style>";
  }
};
window.ExpenseModule = ExpenseModule;
