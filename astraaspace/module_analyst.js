// Astraa Research Analyst — cross-tool analysis, strategy, roadmap, what-if
var AnalystModule = {
  _r:null, _adj:{mark_paid_ids:[],extra_income:0,extra_expense:0,quotes_convert:0},
  apiBase:function(){
    if(typeof ASTRAA_API_BASE!=='undefined' && ASTRAA_API_BASE) return ASTRAA_API_BASE;
    return "http"+"s://"+"family-speed-outcome"+".ngrok-free"+".dev";
  },
  session:function(){try{return JSON.parse(localStorage.getItem('astraa_session')||'{}');}catch(e){return {};}},
  hdr:function(){return {"Content-Type":"application/json","Authorization":"Bearer "+(this.session().token||""),"ngrok-skip-browser-warning":"true"};},
  money:function(n){return "$"+Number(n||0).toLocaleString(undefined,{minimumFractionDigits:2,maximumFractionDigits:2});},

  styles:function(){
    return '<style>'
    + '.an-shell{display:flex;min-height:calc(100vh - 120px);font-family:Inter,system-ui,sans-serif;}'
    + '.an-menu{width:230px;background:#061a33;padding:22px 14px;flex-shrink:0;}'
    + '.an-brand{color:#fff;font-weight:900;font-size:1.05rem;letter-spacing:-0.02em;margin:0 8px 4px;}'
    + '.an-tag{color:#7ea2e6;font-size:0.72rem;margin:0 8px 18px;font-weight:600;text-transform:uppercase;letter-spacing:0.05em;}'
    + '.an-nav{display:block;color:#c7d2fe;text-decoration:none;padding:11px 14px;border-radius:10px;font-weight:600;font-size:0.92rem;margin-bottom:6px;cursor:pointer;}'
    + '.an-nav:hover{background:rgba(255,255,255,0.08);color:#fff;}.an-nav-on{background:#1d4ed8;color:#fff;}'
    + '.an-main{flex:1;padding:28px 30px;background:#f8fafc;overflow-y:auto;}'
    + '.an-h{font-size:1.5rem;font-weight:900;color:#0f172a;margin:0 0 4px;letter-spacing:-0.03em;}'
    + '.an-sub{color:#64748b;margin:0 0 22px;font-size:0.95rem;line-height:1.6;}'
    + '.an-card{background:#fff;border:1px solid #e2e8f0;border-radius:16px;padding:22px;box-shadow:0 4px 14px rgba(15,23,42,0.04);margin-bottom:18px;}'
    + '.an-card h3{margin:0 0 14px;font-size:1.02rem;font-weight:800;color:#0f172a;}'
    + '.an-score-wrap{display:flex;align-items:center;gap:24px;}'
    + '.an-dial{width:120px;height:120px;flex-shrink:0;}'
    + '.an-focus{display:flex;flex-wrap:wrap;gap:8px;margin-top:8px;}'
    + '.an-chip{background:#eff6ff;color:#1d4ed8;border-radius:999px;padding:6px 12px;font-size:0.82rem;font-weight:700;}'
    + '.an-find{display:flex;gap:12px;padding:12px 0;border-bottom:1px solid #f1f5f9;}'
    + '.an-find:last-child{border-bottom:none;}'
    + '.an-badge{font-size:0.7rem;font-weight:800;padding:3px 8px;border-radius:6px;height:fit-content;white-space:nowrap;}'
    + '.an-badge.active{background:#dcfce7;color:#15803d;}'
    + '.an-find .ft{font-weight:700;color:#0f172a;font-size:0.92rem;}.an-find .fx{color:#475569;font-size:0.9rem;line-height:1.5;}'
    + '.an-li{color:#334155;font-size:0.93rem;line-height:1.6;padding:7px 0 7px 22px;position:relative;}'
    + '.an-li:before{content:"\\2192";position:absolute;left:0;color:#1d4ed8;font-weight:900;}'
    + '.an-road{display:grid;grid-template-columns:repeat(3,1fr);gap:14px;}'
    + '.an-road .col{background:#fff;border:1px solid #e2e8f0;border-radius:14px;padding:18px;}'
    + '.an-road .col h4{margin:0 0 10px;font-size:0.85rem;font-weight:800;color:#1d4ed8;text-transform:uppercase;letter-spacing:0.04em;}'
    + '.an-lock{background:#fffaf0;border:1px dashed #f59e0b;border-radius:14px;padding:16px;margin-bottom:12px;}'
    + '.an-lock .lt{font-weight:800;color:#b45309;font-size:0.92rem;margin-bottom:4px;}'
    + '.an-lock .lx{color:#7c5a1e;font-size:0.88rem;line-height:1.5;margin-bottom:8px;}'
    + '.an-lock a{display:inline-block;background:#f59e0b;color:#fff;text-decoration:none;font-weight:800;font-size:0.82rem;padding:7px 14px;border-radius:8px;}'
    + '.an-wi{display:grid;grid-template-columns:1fr 1fr;gap:14px;}'
    + '.an-wi label{display:block;font-weight:700;font-size:0.82rem;color:#0f172a;margin-bottom:5px;}'
    + '.an-wi input{width:100%;padding:9px 11px;border:1px solid #cbd5e1;border-radius:9px;font-size:0.92rem;box-sizing:border-box;}'
    + '.an-inv-row{display:flex;justify-content:space-between;align-items:center;padding:9px 0;border-bottom:1px solid #f1f5f9;font-size:0.9rem;}'
    + '.an-btn{background:#1d4ed8;color:#fff;border:none;border-radius:10px;padding:11px 18px;font-weight:800;cursor:pointer;font-size:0.9rem;}'
    + '.an-btn.ghost{background:#fff;color:#1d4ed8;border:1px solid #bfdbfe;}'
    + '.an-muted{color:#94a3b8;font-size:0.92rem;}'
    + '.an-bar{display:flex;gap:10px;flex-wrap:wrap;margin-top:14px;}'
    + '</style>';
  },

  render:function(){
    return this.styles()
    + '<div class="an-shell">'
    + '  <aside class="an-menu">'
    + '    <div class="an-brand">Astraa Research Analyst</div>'
    + '    <div class="an-tag">Your business, analyzed</div>'
    + '    <a class="an-nav" data-s="report" onclick="AnalystModule.go(\'report\')">📊 Analysis</a>'
    + '    <a class="an-nav" data-s="roadmap" onclick="AnalystModule.go(\'roadmap\')">🗺️ Roadmap</a>'
    + '    <a class="an-nav" data-s="whatif" onclick="AnalystModule.go(\'whatif\')">✏️ What-if</a>'
    + '  </aside>'
    + '  <main class="an-main"><div id="an_body"></div></main>'
    + '</div>';
  },

  load:function(){ this.go('report'); },

  fetchReport:function(cb){
    var self=this, body=document.getElementById('an_body');
    body.innerHTML='<p class="an-muted">Analyzing your business…</p>';
    fetch(this.apiBase()+"/api/analyst/report",{method:"POST",headers:this.hdr(),body:JSON.stringify(this._adj)})
      .then(function(r){return r.json();})
      .then(function(d){ if(!d.success){body.innerHTML='<p style="color:#dc2626;">'+(d.error||'Could not build report.')+'</p>';return;} self._r=d; cb(); })
      .catch(function(){body.innerHTML='<p style="color:#dc2626;">Connection error.</p>';});
  },

  go:function(section){
    this._section=section;
    var navs=document.querySelectorAll('.an-nav');
    for(var i=0;i<navs.length;i++){navs[i].className='an-nav'+(navs[i].getAttribute('data-s')===section?' an-nav-on':'');}
    var self=this;
    this.fetchReport(function(){
      if(section==='report')self.renderReport();
      else if(section==='roadmap')self.renderRoadmap();
      else if(section==='whatif')self.renderWhatif();
    });
  },

  dial:function(score){
    var c=score>=70?'#16a34a':(score>=40?'#f59e0b':'#dc2626');
    var circ=2*Math.PI*52, off=circ*(1-score/100);
    return '<svg class="an-dial" viewBox="0 0 120 120">'
      +'<circle cx="60" cy="60" r="52" fill="none" stroke="#e2e8f0" stroke-width="12"></circle>'
      +'<circle cx="60" cy="60" r="52" fill="none" stroke="'+c+'" stroke-width="12" stroke-linecap="round" stroke-dasharray="'+circ+'" stroke-dashoffset="'+off+'" transform="rotate(-90 60 60)"></circle>'
      +'<text x="60" y="58" text-anchor="middle" font-size="30" font-weight="900" fill="#0f172a">'+score+'</text>'
      +'<text x="60" y="78" text-anchor="middle" font-size="11" fill="#64748b">Health</text></svg>';
  },

  renderReport:function(){
    var d=this._r, m=d.metrics||{};
    var h='<h2 class="an-h">Business Analysis</h2><p class="an-sub">'+(d.adjusted?'Showing an adjusted "what-if" view. ':'')+'Based on your live data across the tools you use.</p>';
    h+='<div class="an-card"><div class="an-score-wrap">'+this.dial(d.health_score||0)+'<div><h3 style="margin:0 0 6px;">Executive Summary</h3><p class="fx" style="color:#475569;line-height:1.6;">'+d.summary+'</p><div class="an-focus">';
    (d.focus_areas||[]).forEach(function(f){h+='<span class="an-chip">'+f+'</span>';});
    h+='</div></div></div></div>';
    h+='<div class="an-card"><h3>Key Numbers</h3>';
    h+='<div class="an-inv-row"><span>Income</span><b>'+this.money(m.income)+'</b></div>';
    h+='<div class="an-inv-row"><span>Expenses</span><b>'+this.money(m.expense)+'</b></div>';
    h+='<div class="an-inv-row"><span>Net profit</span><b style="color:'+((m.net||0)>=0?'#16a34a':'#dc2626')+'">'+this.money(m.net)+'</b></div>';
    h+='<div class="an-inv-row"><span>Margin</span><b>'+(m.margin||0)+'%</b></div>';
    h+='<div class="an-inv-row"><span>Unpaid invoices</span><b>'+this.money(m.pending)+'</b></div>';
    h+='</div>';
    if((d.findings||[]).length){ h+='<div class="an-card"><h3>What I Found</h3>';
      d.findings.forEach(function(f){h+='<div class="an-find"><span class="an-badge active">'+f.area+'</span><div><div class="fx">'+f.text+'</div></div></div>';}); h+='</div>'; }
    if((d.strategy||[]).length){ h+='<div class="an-card"><h3>Strategy &amp; Improvements</h3>';
      d.strategy.forEach(function(s){h+='<div class="an-li">'+s+'</div>';}); h+='</div>'; }
    if((d.locked||[]).length){ h+='<div class="an-card"><h3>Unlock More Insight</h3><p class="an-muted" style="margin-bottom:12px;">You get full value on what you have. These sections turn on honestly when you add the tool.</p>';
      d.locked.forEach(function(l){h+='<div class="an-lock"><div class="lt">🔒 '+l.area+'</div><div class="lx">'+l.text+'</div>../pricing.html</div>';}); h+='</div>'; }
    h+='<div class="an-bar"><button class="an-btn" onclick="AnalystModule.saveVault()">💾 Save to Vault</button><button class="an-btn ghost" onclick="AnalystModule.go(\'whatif\')">✏️ Try What-if</button></div>';
    document.getElementById('an_body').innerHTML=h;
  },

  renderRoadmap:function(){
    var r=(this._r&&this._r.roadmap)||{d30:[],d60:[],d90:[]};
    var h='<h2 class="an-h">Your Roadmap</h2><p class="an-sub">A simple, prioritized plan based on what your numbers show.</p><div class="an-road">';
    function col(t,items){var s='<div class="col"><h4>'+t+'</h4>';(items||[]).forEach(function(i){s+='<div class="an-li">'+i+'</div>';});return s+'</div>';}
    h+=col('Next 30 days',r.d30)+col('Next 60 days',r.d60)+col('Next 90 days',r.d90)+'</div>';
    document.getElementById('an_body').innerHTML=h;
  },

  renderWhatif:function(){
    var a=this._adj, m=(this._r&&this._r.metrics)||{};
    var h='<h2 class="an-h">What-if Adjustments</h2><p class="an-sub">Test changes without touching your real records — great for invoices you were paid for but haven\'t recorded yet. Watch your health score move.</p>';
    h+='<div class="an-card"><h3>Adjust the numbers</h3><div class="an-wi">';
    h+='<div><label>Extra income to assume ($)</label><input id="wi_inc" type="number" value="'+(a.extra_income||0)+'"></div>';
    h+='<div><label>Extra expense to assume ($)</label><input id="wi_exp" type="number" value="'+(a.extra_expense||0)+'"></div>';
    h+='<div><label>Open quotes you expect to win</label><input id="wi_q" type="number" value="'+(a.quotes_convert||0)+'" min="0" max="'+(m.idle_quotes||0)+'"></div>';
    h+='<div><label>Mark unpaid invoices as paid</label><input id="wi_paid" type="text" placeholder="invoice ids, comma-separated" value="'+((a.mark_paid_ids||[]).join(','))+'"></div>';
    h+='</div><div class="an-bar"><button class="an-btn" onclick="AnalystModule.applyWhatif()">Recalculate</button><button class="an-btn ghost" onclick="AnalystModule.resetWhatif()">Reset to real data</button></div></div>';
    h+='<div class="an-card"><div class="an-score-wrap">'+this.dial((this._r&&this._r.health_score)||0)+'<div><h3 style="margin:0 0 6px;">Projected result</h3><p class="fx" style="color:#475569;line-height:1.6;">'+((this._r&&this._r.summary)||'')+'</p><div class="an-inv-row" style="margin-top:8px;"><span>Projected net</span><b style="color:'+(((m.net||0)>=0)?'#16a34a':'#dc2626')+'">'+this.money(m.net)+'</b></div><div class="an-inv-row"><span>Projected margin</span><b>'+(m.margin||0)+'%</b></div></div></div>';
    h+='<p class="an-muted" style="margin-top:12px;">Tip: if an invoice really is paid, update it in Finance to make it official.</p></div>';
    document.getElementById('an_body').innerHTML=h;
  },

  applyWhatif:function(){
    this._adj={
      extra_income:parseFloat(document.getElementById('wi_inc').value)||0,
      extra_expense:parseFloat(document.getElementById('wi_exp').value)||0,
      quotes_convert:parseInt(document.getElementById('wi_q').value)||0,
      mark_paid_ids:(document.getElementById('wi_paid').value||'').split(',').map(function(x){return x.trim();}).filter(function(x){return x;})
    };
    var self=this; this.fetchReport(function(){ self.renderWhatif(); });
  },

  resetWhatif:function(){
    this._adj={mark_paid_ids:[],extra_income:0,extra_expense:0,quotes_convert:0};
    var self=this; this.fetchReport(function(){ self.renderWhatif(); });
  },

  saveVault:function(){
    var d=this._r; if(!d){return;}
    var lines=["ASTRAA RESEARCH ANALYST REPORT","Generated: "+(d.generated_at||""),"","Health Score: "+d.health_score+"/100","Focus: "+(d.focus_areas||[]).join(", "),"","SUMMARY","  "+d.summary,"","FINDINGS"];
    (d.findings||[]).forEach(function(f){lines.push("  ["+f.area+"] "+f.text);});
    lines.push("","STRATEGY"); (d.strategy||[]).forEach(function(s){lines.push("  - "+s);});
    var r=d.roadmap||{}; lines.push("","ROADMAP","  30 days:"); (r.d30||[]).forEach(function(i){lines.push("    - "+i);});
    lines.push("  60 days:"); (r.d60||[]).forEach(function(i){lines.push("    - "+i);});
    lines.push("  90 days:"); (r.d90||[]).forEach(function(i){lines.push("    - "+i);});
    var text=lines.join("\n");
    fetch(this.apiBase()+"/api/vault/upload",{method:"POST",headers:this.hdr(),body:JSON.stringify({filename:"Research_Analyst_Report.txt",content_base64:btoa(unescape(encodeURIComponent(text))),category:"Reports",note:"Saved from Research Analyst"})})
      .then(function(r){return r.json();}).then(function(x){ alert(x.success?"Saved to Vault.":"Could not save: "+(x.error||"error")); })
      .catch(function(){ alert("Connection error saving to Vault."); });
  }
};
