// Astraa Reports — read-only analytics over Finance + Expense
var ReportsModule = {
  _section:"overview", _sum:null, _months:null, _top:null,
  apiBase:function(){
    if(typeof ASTRAA_API_BASE!=='undefined' && ASTRAA_API_BASE) return ASTRAA_API_BASE;
    return "http"+"s://"+"family-speed-outcome"+".ngrok-free"+".dev";
  },
  session:function(){try{return JSON.parse(localStorage.getItem('astraa_session')||'{}');}catch(e){return {};}},
  hdr:function(){return {"Content-Type":"application/json","Authorization":"Bearer "+(this.session().token||""),"ngrok-skip-browser-warning":"true"};},
  money:function(n){return "$"+Number(n||0).toLocaleString(undefined,{minimumFractionDigits:2,maximumFractionDigits:2});},

  styles:function(){
    return '<style>'
    + '.rp-shell{display:flex;min-height:calc(100vh - 120px);font-family:Inter,system-ui,sans-serif;}'
    + '.rp-menu{width:230px;background:#061a33;padding:22px 14px;flex-shrink:0;}'
    + '.rp-brand{color:#fff;font-weight:900;font-size:1.1rem;letter-spacing:-0.02em;margin:0 8px 18px;}'
    + '.rp-nav{display:block;color:#c7d2fe;text-decoration:none;padding:11px 14px;border-radius:10px;font-weight:600;font-size:0.92rem;margin-bottom:6px;cursor:pointer;}'
    + '.rp-nav:hover{background:rgba(255,255,255,0.08);color:#fff;}'
    + '.rp-nav-on{background:#1d4ed8;color:#fff;}'
    + '.rp-main{flex:1;padding:28px 30px;background:#f8fafc;}'
    + '.rp-h{font-size:1.5rem;font-weight:900;color:#0f172a;margin:0 0 4px;letter-spacing:-0.03em;}'
    + '.rp-sub{color:#64748b;margin:0 0 22px;font-size:0.95rem;}'
    + '.rp-kpis{display:grid;grid-template-columns:repeat(auto-fit,minmax(200px,1fr));gap:16px;margin-bottom:24px;}'
    + '.rp-kpi{background:#fff;border:1px solid #e2e8f0;border-radius:16px;padding:22px;box-shadow:0 4px 14px rgba(15,23,42,0.04);}'
    + '.rp-kpi .lbl{color:#64748b;font-size:0.8rem;font-weight:700;text-transform:uppercase;letter-spacing:0.04em;margin:0 0 8px;}'
    + '.rp-kpi .val{font-size:1.7rem;font-weight:900;color:#0f172a;letter-spacing:-0.02em;}'
    + '.rp-kpi.pos .val{color:#16a34a;}.rp-kpi.neg .val{color:#dc2626;}'
    + '.rp-card{background:#fff;border:1px solid #e2e8f0;border-radius:16px;padding:24px;box-shadow:0 4px 14px rgba(15,23,42,0.04);margin-bottom:22px;}'
    + '.rp-card h3{margin:0 0 18px;font-size:1.05rem;font-weight:800;color:#0f172a;}'
    + '.rp-row{display:flex;justify-content:space-between;align-items:center;padding:11px 0;border-bottom:1px solid #f1f5f9;}'
    + '.rp-row:last-child{border-bottom:none;}'
    + '.rp-row .nm{font-weight:600;color:#334155;}.rp-row .am{font-weight:800;color:#0f172a;}'
    + '.rp-muted{color:#94a3b8;font-size:0.92rem;}'
    + '.rp-legend{display:flex;gap:18px;margin-bottom:14px;font-size:0.85rem;color:#475569;font-weight:600;}'
    + '.rp-dot{display:inline-block;width:11px;height:11px;border-radius:3px;margin-right:6px;vertical-align:middle;}'
    + '</style>';
  },

  render:function(){
    return this.styles()
    + '<div class="rp-shell">'
    + '  <aside class="rp-menu">'
    + '    <div class="rp-brand">Astraa Reports</div>'
    + '    <a class="rp-nav" data-s="overview" onclick="ReportsModule.go(\'overview\')">📊 Overview</a>'
    + '    <a class="rp-nav" data-s="monthly" onclick="ReportsModule.go(\'monthly\')">📈 Monthly Trend</a>'
    + '    <a class="rp-nav" data-s="clients" onclick="ReportsModule.go(\'clients\')">🏆 Top Clients</a>'
    + '  </aside>'
    + '  <main class="rp-main"><div id="rp_body"></div></main>'
    + '</div>';
  },

  load:function(){ this.go('overview'); },

  go:function(section){
    this._section=section;
    var navs=document.querySelectorAll('.rp-nav');
    for(var i=0;i<navs.length;i++){navs[i].className='rp-nav'+(navs[i].getAttribute('data-s')===section?' rp-nav-on':'');}
    var body=document.getElementById('rp_body'); body.innerHTML='<p class="rp-muted">Loading…</p>';
    var self=this;
    if(section==='overview'){
      fetch(this.apiBase()+"/api/reports/summary",{headers:this.hdr()}).then(function(r){return r.json();}).then(function(d){
        self._sum=d.success?d.summary:{}; self.renderOverview();
      }).catch(function(){body.innerHTML='<p style="color:#dc2626;">Connection error.</p>';});
    } else if(section==='monthly'){
      fetch(this.apiBase()+"/api/reports/monthly",{headers:this.hdr()}).then(function(r){return r.json();}).then(function(d){
        self._months=d.success?d.months:[]; self.renderMonthly();
      }).catch(function(){body.innerHTML='<p style="color:#dc2626;">Connection error.</p>';});
    } else if(section==='clients'){
      fetch(this.apiBase()+"/api/reports/top-clients",{headers:this.hdr()}).then(function(r){return r.json();}).then(function(d){
        self._top=d.success?d.top:[]; self.renderClients();
      }).catch(function(){body.innerHTML='<p style="color:#dc2626;">Connection error.</p>';});
    }
  },

  renderOverview:function(){
    var s=this._sum||{}; var net=Number(s.net_profit||0);
    var h='<h2 class="rp-h">Business Overview</h2><p class="rp-sub">A quick snapshot of your income, expenses, and profit.</p>';
    h+='<div class="rp-kpis">';
    h+='<div class="rp-kpi pos"><p class="lbl">Total Income</p><div class="val">'+this.money(s.total_income)+'</div></div>';
    h+='<div class="rp-kpi neg"><p class="lbl">Total Expenses</p><div class="val">'+this.money(s.total_expense)+'</div></div>';
    h+='<div class="rp-kpi '+(net>=0?'pos':'neg')+'"><p class="lbl">Net Profit</p><div class="val">'+this.money(net)+'</div></div>';
    h+='</div>';
    h+='<div class="rp-card"><h3>Invoices</h3>';
    h+='<div class="rp-row"><span class="nm">Paid invoices</span><span class="am">'+(s.paid_invoices||0)+'</span></div>';
    h+='<div class="rp-row"><span class="nm">Pending / overdue</span><span class="am">'+(s.pending_invoices||0)+'</span></div>';
    h+='<div class="rp-row"><span class="nm">Money still owed to you</span><span class="am">'+this.money(s.invoice_pending)+'</span></div>';
    h+='</div>';
    document.getElementById('rp_body').innerHTML=h;
  },

  renderMonthly:function(){
    var m=this._months||[];
    var h='<h2 class="rp-h">Monthly Trend</h2><p class="rp-sub">Income vs expenses over the last 12 months.</p>';
    if(!m.length){ h+='<div class="rp-card"><p class="rp-muted">No dated income or expense records yet. Add some in Finance or Expense to see your trend here.</p></div>'; document.getElementById('rp_body').innerHTML=h; return; }
    var max=0; for(var i=0;i<m.length;i++){ max=Math.max(max,m[i].income,m[i].expense); } if(max<=0)max=1;
    var W=Math.max(560, m.length*70), H=260, pad=30, bw=18, gap=6, gw=(W-pad*2)/m.length;
    var svg='<svg width="100%" viewBox="0 0 '+W+' '+(H+40)+'" preserveAspectRatio="xMidYMid meet">';
    for(var i=0;i<m.length;i++){
      var x=pad+i*gw+ (gw-(bw*2+gap))/2;
      var ih=(m[i].income/max)*H, eh=(m[i].expense/max)*H;
      svg+='<rect x="'+x+'" y="'+(H-ih)+'" width="'+bw+'" height="'+ih+'" rx="3" fill="#1d4ed8"></rect>';
      svg+='<rect x="'+(x+bw+gap)+'" y="'+(H-eh)+'" width="'+bw+'" height="'+eh+'" rx="3" fill="#f59e0b"></rect>';
      svg+='<text x="'+(pad+i*gw+gw/2)+'" y="'+(H+16)+'" font-size="10" fill="#64748b" text-anchor="middle">'+m[i].month.slice(2)+'</text>';
    }
    svg+='</svg>';
    h+='<div class="rp-card"><div class="rp-legend"><span><span class="rp-dot" style="background:#1d4ed8"></span>Income</span><span><span class="rp-dot" style="background:#f59e0b"></span>Expenses</span></div>'+svg+'</div>';
    h+='<div class="rp-card"><h3>Profit by month</h3>';
    for(var i=m.length-1;i>=0;i--){ var p=m[i].profit; h+='<div class="rp-row"><span class="nm">'+m[i].month+'</span><span class="am" style="color:'+(p>=0?'#16a34a':'#dc2626')+'">'+this.money(p)+'</span></div>'; }
    h+='</div>';
    document.getElementById('rp_body').innerHTML=h;
  },

  renderClients:function(){
    var t=this._top||[];
    var h='<h2 class="rp-h">Top Clients</h2><p class="rp-sub">Your biggest clients by total invoiced value.</p>';
    if(!t.length){ h+='<div class="rp-card"><p class="rp-muted">No invoices yet. Create invoices in Finance to see your top clients here.</p></div>'; document.getElementById('rp_body').innerHTML=h; return; }
    h+='<div class="rp-card">';
    for(var i=0;i<t.length;i++){ h+='<div class="rp-row"><span class="nm">'+(i+1)+'. '+t[i].name+'</span><span class="am">'+this.money(t[i].amount)+'</span></div>'; }
    h+='</div>';
    document.getElementById('rp_body').innerHTML=h;
  }
};
