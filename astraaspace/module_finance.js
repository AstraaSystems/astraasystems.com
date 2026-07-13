// Astraa Finance — standalone workspace: Statement, Invoices, Income/Expenses, Payroll, Export
var FinanceModule = {
  _section:"statement", _data:null,
  apiBase:function(){return (typeof ASTRAA_API_BASE!=='undefined')?ASTRAA_API_BASE:"https://family-speed-outcome.ngrok-free.dev";},
  session:function(){try{return JSON.parse(localStorage.getItem('astraa_session')||'{}');}catch(e){return {};}},
  hdr:function(){return {"Content-Type":"application/json","Authorization":"Bearer "+(this.session().token||""),"ngrok-skip-browser-warning":"true"};},
  money:function(n){return "$"+Number(n||0).toLocaleString(undefined,{minimumFractionDigits:2,maximumFractionDigits:2});},

  render:function(){
    return this.styles()
      + '<div class="fn-shell">'
      + '  <aside class="fn-menu">'
      + '    <div class="fn-brand">Astraa Finance</div>'
      + '    <a class="fn-nav" data-s="statement" onclick="FinanceModule.go(\'statement\')">📊 Financial Statement</a>'
      + '    <a class="fn-nav" data-s="invoices" onclick="FinanceModule.go(\'invoices\')">🧾 Invoices</a>'
      + '    <a class="fn-nav" data-s="entries" onclick="FinanceModule.go(\'entries\')">💵 Income &amp; Expenses</a>'
      + '    <a class="fn-nav" data-s="payroll" onclick="FinanceModule.go(\'payroll\')">🧑‍💼 Payroll Template</a>'
      + '    <a class="fn-nav" data-s="export" onclick="FinanceModule.go(\'export\')">📤 Export</a>'
      + '  </aside>'
      + '  <main class="fn-main"><div id="fn_body"></div></main>'
      + '</div>';
  },

  load:function(){ this.go('statement'); },

  go:function(section){
    this._section=section;
    var navs=document.querySelectorAll('.fn-nav');
    for(var i=0;i<navs.length;i++){navs[i].className='fn-nav'+(navs[i].getAttribute('data-s')===section?' fn-nav-on':'');}
    var body=document.getElementById('fn_body'); body.innerHTML='<p class="fn-muted">Loading…</p>';
    var self=this;
    fetch(this.apiBase()+"/api/finance/list",{headers:this.hdr()}).then(function(r){return r.json();}).then(function(d){
      self._data = d.success? d : {invoices:[],income:[],expenses:[],payroll:[],summary:{}};
      if(section==='statement')self.renderStatement();
      else if(section==='invoices')self.renderInvoices();
      else if(section==='entries')self.renderEntries();
      else if(section==='payroll')self.renderPayroll();
      else if(section==='export')self.renderExport();
    }).catch(function(){body.innerHTML='<p style="color:#dc2626;">Connection error.</p>';});
  },

  // ---- STATEMENT (P&L) ----
  renderStatement:function(){
    var s=this._data.summary||{}, m=this.money;
    document.getElementById('fn_body').innerHTML=
      '<h2 class="fn-h2">Financial Statement (P&amp;L)</h2>'
      +'<div class="fn-stats">'
      +stat("Total Income",m(s.total_income),"#16a34a")
      +stat("Total Expenses",m(s.total_expense),"#dc2626")
      +stat("Net Profit",m(s.net_profit),(s.net_profit>=0?"#16a34a":"#dc2626"))
      +stat("Pending Invoices",m(s.invoice_pending),"#f59e0b")
      +'</div>'
      +'<div class="fn-panel" style="margin-top:20px;max-width:560px;">'
      +'<h3 class="fn-h3">Profit &amp; Loss Summary</h3>'
      +row("Income — Paid invoices",m(s.invoice_income))
      +row("Income — Manual entries",m(s.manual_income))
      +row("Expenses — Finance entries",m(s.manual_expense))
      +row("Expenses — Expense tool",m(s.expense_tool_total))
      +'<div class="fn-total"><span>NET PROFIT</span><span>'+m(s.net_profit)+'</span></div>'
      +'<button class="fn-print" onclick="FinanceModule.printStatement()">Print Statement</button>'
      +'</div>';
    function stat(l,v,c){return "<div class='fn-stat'><span class='fn-stat-l'>"+l+"</span><span class='fn-stat-v' style='color:"+c+"'>"+v+"</span></div>";}
    function row(l,v){return "<div class='fn-row'><span>"+l+"</span><span>"+v+"</span></div>";}
  },
  printStatement:function(){
    var s=this._data.summary||{},m=this.money;
    var w=window.open('','_blank');
    w.document.write("<html><head><title>Astraa Financial Statement</title><style>body{font-family:Segoe UI,Arial;padding:30px;}h1{margin:0;}table{width:100%;max-width:500px;border-collapse:collapse;margin-top:16px;}td{padding:8px 0;border-bottom:1px solid #eee;}td:last-child{text-align:right;font-weight:700;}</style></head><body><h1>Profit &amp; Loss Statement</h1><p>Generated "+new Date().toLocaleDateString()+"</p><table>"
      +"<tr><td>Total Income</td><td>"+m(s.total_income)+"</td></tr>"
      +"<tr><td>Total Expenses</td><td>"+m(s.total_expense)+"</td></tr>"
      +"<tr style='border-top:2px solid #000;'><td><b>NET PROFIT</b></td><td><b>"+m(s.net_profit)+"</b></td></tr>"
      +"</table><p style='margin-top:20px;font-size:12px;color:#888;'>Estimate for informational purposes. Verify with a qualified accountant.</p></body></html>");
    w.document.close();w.focus();w.print();
  },

  // ---- INVOICES ----
  renderInvoices:function(){
    var f="width:100%;padding:10px 12px;border:1px solid #e2e8f0;border-radius:8px;background:#f8fafc;font-size:0.9rem;";
    document.getElementById('fn_body').innerHTML=
      '<h2 class="fn-h2">Invoices</h2>'
      +'<div class="fn-two">'
      +'<div class="fn-panel"><h3 class="fn-h3">New Invoice</h3>'
      +'<div class="fn-f"><label>Client</label><input id="in_client" style="'+f+'"></div>'
      +'<div class="fn-f"><label>Description</label><input id="in_desc" style="'+f+'"></div>'
      +'<div class="fn-f"><label>Amount ($)</label><input id="in_amount" type="number" step="0.01" style="'+f+'"></div>'
      +'<div class="fn-f"><label>Status</label><select id="in_status" style="'+f+'"><option>Pending</option><option>Paid</option><option>Overdue</option></select></div>'
      +'<div class="fn-f"><label>Comment</label><input id="in_comment" style="'+f+'"></div>'
      +'<button class="fn-add" onclick="FinanceModule.addInvoice()">Add Invoice</button></div>'
      +'<div class="fn-panel"><h3 class="fn-h3">Invoice List</h3><div id="in_list"></div></div>'
      +'</div>';
    this.refreshInvoices();
  },
  refreshInvoices:function(){
    var self=this,m=this.money;
    var invs=(this._data.invoices||[]);
    var col={"Paid":"#16a34a","Pending":"#f59e0b","Overdue":"#dc2626"};
    document.getElementById('in_list').innerHTML = invs.length? invs.map(function(i){
      var opts=["Pending","Paid","Overdue"].map(function(st){return "<option "+(st===i.status?"selected":"")+">"+st+"</option>";}).join("");
      return "<div class='fn-item'><div class='fn-item-top'><div><b>"+i.client+"</b> <span class='fn-muted'>"+(i.description||"")+"</span></div><button class='fn-del' onclick=\"FinanceModule.delInvoice('"+i.id+"')\">✕</button></div>"
        +"<div class='fn-item-sub'>"+m(i.amount)+(i.comment?" · "+i.comment:"")+"</div>"
        +"<div style='display:flex;align-items:center;gap:8px;margin-top:6px;'><span style='width:10px;height:10px;border-radius:50%;background:"+(col[i.status]||'#94a3b8')+";'></span><select class='fn-sel' onchange=\"FinanceModule.setInvoiceStatus('"+i.id+"',this.value)\">"+opts+"</select></div></div>";
    }).join("") : "<p class='fn-muted'>No invoices yet.</p>";
  },
  addInvoice:function(){var self=this;function v(i){var e=document.getElementById(i);return e?e.value:"";}
    if(!v('in_client')){alert("Enter a client.");return;}
    fetch(this.apiBase()+"/api/finance/add-invoice",{method:"POST",headers:this.hdr(),body:JSON.stringify({client:v('in_client'),description:v('in_desc'),amount:parseFloat(v('in_amount'))||0,status:v('in_status'),comment:v('in_comment')})}).then(function(r){return r.json();}).then(function(){self.go('invoices');});},
  setInvoiceStatus:function(id,st){var self=this;fetch(this.apiBase()+"/api/finance/update-invoice",{method:"POST",headers:this.hdr(),body:JSON.stringify({id:id,status:st})}).then(function(r){return r.json();}).then(function(){self.go('invoices');});},
  delInvoice:function(id){var self=this;if(!confirm("Delete invoice?"))return;fetch(this.apiBase()+"/api/finance/delete-invoice",{method:"POST",headers:this.hdr(),body:JSON.stringify({id:id})}).then(function(r){return r.json();}).then(function(){self.go('invoices');});},

  // ---- INCOME & EXPENSES ----
  renderEntries:function(){
    var f="width:100%;padding:10px 12px;border:1px solid #e2e8f0;border-radius:8px;background:#f8fafc;font-size:0.9rem;";
    document.getElementById('fn_body').innerHTML=
      '<h2 class="fn-h2">Income &amp; Expenses</h2>'
      +'<div class="fn-two">'
      +'<div class="fn-panel"><h3 class="fn-h3">Add Entry</h3>'
      +'<div class="fn-f"><label>Type</label><select id="en_kind" style="'+f+'"><option value="income">Income</option><option value="expense">Expense</option></select></div>'
      +'<div class="fn-f"><label>Date</label><input id="en_date" type="date" style="'+f+'"></div>'
      +'<div class="fn-f"><label>Category</label><input id="en_cat" style="'+f+'" placeholder="e.g. Sales, Supplies"></div>'
      +'<div class="fn-f"><label>Amount ($)</label><input id="en_amount" type="number" step="0.01" style="'+f+'"></div>'
      +'<div class="fn-f"><label>Note</label><input id="en_note" style="'+f+'"></div>'
      +'<button class="fn-add" onclick="FinanceModule.addEntry()">Add Entry</button></div>'
      +'<div class="fn-panel"><h3 class="fn-h3">Recent Entries</h3><div id="en_list"></div></div>'
      +'</div>';
    var d=document.getElementById('en_date'); if(d)d.value=new Date().toISOString().slice(0,10);
    this.refreshEntries();
  },
  refreshEntries:function(){
    var self=this,m=this.money;
    var inc=(this._data.income||[]).map(function(x){x._k="income";return x;});
    var exp=(this._data.expenses||[]).map(function(x){x._k="expense";return x;});
    var all=inc.concat(exp).sort(function(a,b){return (b.date||"").localeCompare(a.date||"");});
    document.getElementById('en_list').innerHTML = all.length? all.map(function(x){
      var isInc=x._k==="income";
      return "<div class='fn-item'><div class='fn-item-top'><div><b style='color:"+(isInc?"#16a34a":"#dc2626")+"'>"+(isInc?"+":"−")+m(x.amount)+"</b> <span class='fn-muted'>"+x.category+"</span></div><button class='fn-del' onclick=\"FinanceModule.delEntry('"+x._k+"','"+x.id+"')\">✕</button></div><div class='fn-item-sub'>"+x.date+(x.note?" · "+x.note:"")+"</div></div>";
    }).join("") : "<p class='fn-muted'>No entries yet.</p>";
  },
  addEntry:function(){var self=this;function v(i){var e=document.getElementById(i);return e?e.value:"";}
    if(!(parseFloat(v('en_amount'))>0)){alert("Enter a valid amount.");return;}
    fetch(this.apiBase()+"/api/finance/add-entry",{method:"POST",headers:this.hdr(),body:JSON.stringify({kind:v('en_kind'),date:v('en_date'),category:v('en_cat'),amount:parseFloat(v('en_amount'))||0,note:v('en_note')})}).then(function(r){return r.json();}).then(function(){self.go('entries');});},
  delEntry:function(kind,id){var self=this;fetch(this.apiBase()+"/api/finance/delete-entry",{method:"POST",headers:this.hdr(),body:JSON.stringify({kind:kind,id:id})}).then(function(r){return r.json();}).then(function(){self.go('entries');});},

  // ---- PAYROLL TEMPLATE ----
  renderPayroll:function(){
    var f="width:100%;padding:10px 12px;border:1px solid #e2e8f0;border-radius:8px;background:#f8fafc;font-size:0.9rem;";
    document.getElementById('fn_body').innerHTML=
      '<h2 class="fn-h2">Payroll Template</h2>'
      +'<div class="fn-disc">⚠️ Template only. You enter and verify all figures. Astraa does not calculate or remit taxes — consult a payroll professional or CRA for deductions (CPP/EI/tax).</div>'
      +'<div class="fn-two" style="margin-top:14px;">'
      +'<div class="fn-panel"><h3 class="fn-h3">Add Payroll Row</h3>'
      +'<div class="fn-f"><label>Employee</label><input id="pr_emp" style="'+f+'"></div>'
      +'<div class="fn-f"><label>Hours</label><input id="pr_hours" type="number" step="0.01" style="'+f+'"></div>'
      +'<div class="fn-f"><label>Rate ($/hr)</label><input id="pr_rate" type="number" step="0.01" style="'+f+'"></div>'
      +'<div class="fn-f"><label>Deductions ($) — you enter</label><input id="pr_ded" type="number" step="0.01" style="'+f+'"></div>'
      +'<button class="fn-add" onclick="FinanceModule.addPayroll()">Add Row</button></div>'
      +'<div class="fn-panel"><div class="fn-listhead"><h3 class="fn-h3" style="margin:0;">Payroll</h3><button class="fn-print" onclick="FinanceModule.exportPayroll()">Export CSV</button></div><div id="pr_list"></div></div>'
      +'</div>';
    this.refreshPayroll();
  },
  refreshPayroll:function(){
    var self=this,m=this.money;
    var rows=(this._data.payroll||[]);
    var col={"Paid":"#16a34a","Pending":"#f59e0b"};
    document.getElementById('pr_list').innerHTML = rows.length? rows.map(function(r){
      var opts=["Pending","Paid"].map(function(st){return "<option "+(st===r.status?"selected":"")+">"+st+"</option>";}).join("");
      return "<div class='fn-item'><div class='fn-item-top'><div><b>"+r.employee+"</b></div><button class='fn-del' onclick=\"FinanceModule.delPayroll('"+r.id+"')\">✕</button></div>"
        +"<div class='fn-item-sub'>"+r.hours+"h × "+m(r.rate)+" = Gross "+m(r.gross)+" · Ded "+m(r.deductions)+" · <b>Net "+m(r.net)+"</b></div>"
        +"<div style='display:flex;align-items:center;gap:8px;margin-top:6px;'><span style='width:10px;height:10px;border-radius:50%;background:"+(col[r.status]||'#94a3b8')+";'></span><select class='fn-sel' onchange=\"FinanceModule.setPayrollStatus('"+r.id+"',this.value)\">"+opts+"</select></div></div>";
    }).join("") : "<p class='fn-muted'>No payroll rows yet.</p>";
  },
  addPayroll:function(){var self=this;function v(i){var e=document.getElementById(i);return e?e.value:"";}
    if(!v('pr_emp')){alert("Enter employee name.");return;}
    fetch(this.apiBase()+"/api/finance/add-payroll",{method:"POST",headers:this.hdr(),body:JSON.stringify({employee:v('pr_emp'),hours:parseFloat(v('pr_hours'))||0,rate:parseFloat(v('pr_rate'))||0,deductions:parseFloat(v('pr_ded'))||0,status:"Pending"})}).then(function(r){return r.json();}).then(function(){self.go('payroll');});},
  setPayrollStatus:function(id,st){var self=this;fetch(this.apiBase()+"/api/finance/update-payroll",{method:"POST",headers:this.hdr(),body:JSON.stringify({id:id,status:st})}).then(function(r){return r.json();}).then(function(){self.go('payroll');});},
  delPayroll:function(id){var self=this;if(!confirm("Delete row?"))return;fetch(this.apiBase()+"/api/finance/delete-payroll",{method:"POST",headers:this.hdr(),body:JSON.stringify({id:id})}).then(function(r){return r.json();}).then(function(){self.go('payroll');});},
  exportPayroll:function(){
    var rows=(this._data.payroll||[]);
    var csv="Employee,Hours,Rate,Gross,Deductions,Net,Status\n"+rows.map(function(r){return [r.employee,r.hours,r.rate,r.gross,r.deductions,r.net,r.status].join(",");}).join("\n");
    this.download("astraa_payroll.csv",csv);
  },

  // ---- EXPORT ----
  renderExport:function(){
    document.getElementById('fn_body').innerHTML=
      '<h2 class="fn-h2">Export</h2>'
      +'<div class="fn-panel" style="max-width:520px;"><p class="fn-muted">Download your financial data as spreadsheets (CSV — opens in Excel, Google Sheets, Numbers).</p>'
      +'<button class="fn-add" style="margin-bottom:10px;" onclick="FinanceModule.exportAll(\'income\')">Export Income CSV</button>'
      +'<button class="fn-add" style="margin-bottom:10px;" onclick="FinanceModule.exportAll(\'expenses\')">Export Expenses CSV</button>'
      +'<button class="fn-add" style="margin-bottom:10px;" onclick="FinanceModule.exportAll(\'invoices\')">Export Invoices CSV</button>'
      +'<button class="fn-add" onclick="FinanceModule.exportPayroll()">Export Payroll CSV</button></div>';
  },
  exportAll:function(kind){
    var self=this,rows=(this._data[kind]||[]);
    var csv="";
    if(kind==="invoices")csv="Client,Description,Amount,Status,Comment,Date\n"+rows.map(function(r){return [r.client,r.description,r.amount,r.status,r.comment,r.date].join(",");}).join("\n");
    else csv="Date,Category,Amount,Note\n"+rows.map(function(r){return [r.date,r.category,r.amount,r.note].join(",");}).join("\n");
    this.download("astraa_"+kind+".csv",csv);
  },
  download:function(fname,text){
    var blob=new Blob([text],{type:"text/csv"});var url=URL.createObjectURL(blob);
    var a=document.createElement("a");a.href=url;a.download=fname;a.click();URL.revokeObjectURL(url);
  },

  styles:function(){
    return "<style>"
    +".fn-shell{display:grid;grid-template-columns:230px 1fr;min-height:calc(100vh - 62px);background:#f8fafc;}"
    +".fn-menu{background:#0b1220;padding:24px 14px;display:flex;flex-direction:column;gap:3px;}"
    +".fn-brand{color:#fff;font-weight:900;font-size:1.05rem;padding:6px 14px 20px;border-bottom:1px solid rgba(255,255,255,0.08);margin-bottom:10px;}"
    +".fn-nav{display:block;padding:11px 14px;border-radius:9px;color:#cbd5e1 !important;font-weight:700;font-size:0.9rem;cursor:pointer;background:transparent;}"
    +".fn-nav:hover{background:rgba(255,255,255,0.06);color:#fff !important;}"
    +".fn-nav-on{background:#1d4ed8 !important;color:#fff !important;}"
    +".fn-main{background:#f8fafc;padding:36px 40px;overflow-y:auto;}"
    +".fn-h2{margin:0 0 24px;font-size:1.7rem;font-weight:900;color:#090d16;letter-spacing:-0.03em;}"
    +".fn-h3{font-size:1rem;font-weight:800;color:#0f172a;margin:0 0 12px;}"
    +".fn-muted{color:#94a3b8;}"
    +".fn-stats{display:grid;grid-template-columns:repeat(4,1fr);gap:12px;}"
    +".fn-stat{background:#fff;border:1px solid #e2e8f0;border-radius:12px;padding:16px;text-align:center;}"
    +".fn-stat-l{display:block;font-size:11px;color:#64748b;font-weight:700;text-transform:uppercase;}"
    +".fn-stat-v{display:block;font-size:1.3rem;font-weight:900;margin-top:4px;}"
    +".fn-two{display:grid;grid-template-columns:0.9fr 1.2fr;gap:18px;align-items:start;}"
    +".fn-panel{background:#fff;border:1px solid #e2e8f0;border-radius:12px;padding:18px;}"
    +".fn-f{margin-bottom:10px;}.fn-f label{display:block;font-size:0.72rem;font-weight:800;color:#0f172a;margin-bottom:4px;text-transform:uppercase;}"
    +".fn-add{width:100%;padding:11px;border:none;border-radius:9px;background:#1d4ed8 !important;color:#fff !important;font-weight:800;cursor:pointer;}"
    +".fn-print{padding:7px 12px;border:1px solid #1d4ed8 !important;border-radius:8px;background:#fff !important;color:#1d4ed8 !important;font-size:12px;font-weight:700;cursor:pointer;}"
    +".fn-row{display:flex;justify-content:space-between;padding:8px 0;border-bottom:1px solid #f1f5f9;color:#475569;font-size:0.9rem;}"
    +".fn-total{display:flex;justify-content:space-between;padding:12px 0 4px;font-weight:900;font-size:1.1rem;color:#090d16;border-top:2px solid #0f172a;margin-top:4px;}"
    +".fn-item{border:1px solid #e2e8f0;border-radius:10px;padding:12px;margin-bottom:10px;}"
    +".fn-item-top{display:flex;justify-content:space-between;align-items:center;}"
    +".fn-item-sub{color:#94a3b8;font-size:12px;margin-top:3px;}"
    +".fn-listhead{display:flex;justify-content:space-between;align-items:center;margin-bottom:12px;}"
    +".fn-sel{padding:4px 7px;border:1px solid #e2e8f0;border-radius:6px;background:#f8fafc;font-size:12px;font-weight:700;}"
    +".fn-del{background:#fff !important;border:1px solid #fecaca !important;color:#dc2626 !important;border-radius:6px;width:24px;height:24px;cursor:pointer;font-weight:700;}"
    +".fn-disc{background:#fffbeb;border:1px solid #fde68a;border-radius:10px;padding:12px;color:#92400e;font-size:13px;}"
    +"@media(max-width:820px){.fn-shell{grid-template-columns:1fr;}.fn-two{grid-template-columns:1fr;}.fn-stats{grid-template-columns:repeat(2,1fr);}}"
    +"</style>";
  }
};
window.FinanceModule = FinanceModule;
