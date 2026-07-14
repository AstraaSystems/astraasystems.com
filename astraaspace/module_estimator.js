// Astraa Estimator — premium, mode-aware (Single Work / Whole Project)
var EstimatorModule = {
  _token:null, _mode:"single_work", _baseline:{},
  tradeCats:["Interior Paint","Flooring","Drywall","Tile","Roofing","Framing","Concrete","Electrical","Plumbing","Insulation","HVAC","General / Other"],
  projectCats:["New Home Build","Home Addition","Full Renovation","Commercial Build-Out","Multi-Unit / Townhouse","Custom Home","Industrial / Warehouse"],
  bcCities:["BC / Vancouver","BC / Burnaby","BC / Richmond","BC / Surrey","BC / Coquitlam","BC / Port Coquitlam","BC / Port Moody","BC / New Westminster","BC / North Vancouver","BC / West Vancouver","BC / Delta","BC / Langley","BC / Maple Ridge","BC / Pitt Meadows","BC / White Rock","BC / Abbotsford","BC / Chilliwack","BC / Mission","BC / Hope","BC / Victoria","BC / Saanich","BC / Langford","BC / Colwood","BC / Nanaimo","BC / Parksville","BC / Qualicum Beach","BC / Duncan","BC / Courtenay","BC / Comox","BC / Campbell River","BC / Port Alberni","BC / Tofino","BC / Ucluelet","BC / Powell River","BC / Squamish","BC / Whistler","BC / Pemberton","BC / Gibsons","BC / Sechelt","BC / Kelowna","BC / West Kelowna","BC / Vernon","BC / Penticton","BC / Kamloops","BC / Merritt","BC / Salmon Arm","BC / Revelstoke","BC / Cranbrook","BC / Kimberley","BC / Fernie","BC / Nelson","BC / Castlegar","BC / Trail","BC / Golden","BC / Prince George","BC / Quesnel","BC / Williams Lake","BC / Fort St. John","BC / Dawson Creek","BC / Terrace","BC / Prince Rupert","BC / Kitimat","BC / Smithers","BC / Fort Nelson","BC / Other City or Town"],

  apiBase:function(){return (typeof ASTRAA_API_BASE!=='undefined')?ASTRAA_API_BASE:"https://family-speed-outcome.ngrok-free.dev";},
  session:function(){try{return JSON.parse(localStorage.getItem('astraa_session')||'{}');}catch(e){return {};}},

  render:function(){
    return ''
      + this.styles()
      + '<div class="ae-wrap">'
      + '  <div class="ae-head">'
      + '    <div><h2 class="ae-title">Astraa Estimator</h2><p class="ae-sub">Calculate free. You only use a credit when you approve.</p></div>'
      + '    <div class="ae-modes">'
      + '      <label class="ae-mode ae-mode-on" id="ae-m-single"><input type="radio" name="est_mode" value="single_work" checked onchange="EstimatorModule.setMode(\'single_work\')"> Single Work</label>'
      + '      <label class="ae-mode" id="ae-m-whole"><input type="radio" name="est_mode" value="whole_project" onchange="EstimatorModule.setMode(\'whole_project\')"> Whole Project</label>'
      + '    </div>'
      + '  <div style="margin-top:10px;"><button onclick="EstimatorModule.showHistory()" style="padding:8px 14px;border:1px solid #1d4ed8;background:#fff;color:#1d4ed8;border-radius:8px;font-weight:700;cursor:pointer;font-size:13px;">📋 My Quotes</button> <button onclick="EstimatorModule.go && EstimatorModule.go()||location.reload()" style="padding:8px 14px;border:1px solid #e2e8f0;background:#fff;color:#475569;border-radius:8px;font-weight:700;cursor:pointer;font-size:13px;">+ New Estimate</button></div>'
      + '  </div>'
      + '  <div class="ae-grid">'
      + '    <div class="ae-card ae-inputs">' + this.inputs() + '</div>'
      + '    <div class="ae-card ae-output"><div id="est_result" class="ae-placeholder">Enter details and calculate to see your estimate.</div></div>'
      + '  </div>'
      + '</div>';
  },

  inputs:function(){
    var cats = (this._mode==="whole_project"?this.projectCats:this.tradeCats).map(function(c){return "<option>"+c+"</option>";}).join("");
    var cityOpts = this.bcCities.map(function(c){return "<option>"+c+"</option>";}).join("");
    var rateFields = this._mode==="single_work" ? (
        '<div class="ae-field"><label>Cost of material ($/sqft)</label><input id="est_material" type="number" step="0.01"><span id="mat_hint" class="ae-hint"></span></div>'
      + '<div class="ae-field"><label>Cost of labour ($/sqft)</label><input id="est_labour" type="number" step="0.01"><span id="lab_hint" class="ae-hint"></span></div>'
      + '<button type="button" class="ae-reset" onclick="EstimatorModule.resetRates()">Reset to BC standard</button>'
    ) : '<p class="ae-note">Whole Project uses Astraa\'s BC building model — all trades, overhead, profit and contingency are calculated automatically.</p>';
    return ''
      + '<div class="ae-field"><label>'+(this._mode==="whole_project"?"Project type":"Category")+'</label><select id="est_category" onchange="EstimatorModule.fillBaseline(true)">'+cats+'</select></div>'
      + '<div class="ae-field"><label>Square footage</label><input id="est_sqft" type="number" placeholder="1000"></div>'
      + '<div class="ae-field"><label>Building / use type</label><select id="est_ptype"><option>Residential</option><option>Commercial</option><option>Industrial</option><option>Renovation</option><option>Service / Repair</option><option>Custom</option></select></div>'
      + '<div class="ae-field"><label>Location / market</label><select id="est_loc">'+cityOpts+'</select></div>'
      + '<div class="ae-field"><label>Quality level</label><select id="est_quality" onchange="EstimatorModule.fillBaseline(true)"><option>Standard</option><option>Premium</option><option>Economy</option></select></div>'
      + rateFields
      + '<button class=\"ae-calc\" onclick=\"EstimatorModule.calculate()\" style=\"width:100%;padding:13px;border:none;border-radius:10px;background:#1d4ed8;color:#ffffff;font-weight:800;font-size:1rem;cursor:pointer;margin-top:6px;\">Calculate (free)</button>';
  },

  setMode:function(m){
    this._mode=m;
    document.getElementById('ae-m-single').className = 'ae-mode' + (m==='single_work'?' ae-mode-on':'');
    document.getElementById('ae-m-whole').className = 'ae-mode' + (m==='whole_project'?' ae-mode-on':'');
    // rebuild inputs for the mode
    var col = document.querySelector('.ae-inputs');
    if(col){ col.innerHTML = this.inputs(); this.loadBaseline(); }
    var out = document.getElementById('est_result');
    if(out){ out.className='ae-placeholder'; out.innerHTML = 'Enter details and calculate to see your estimate.'; }
  },

  loadBaseline:function(){
    var self=this;
    fetch(this.apiBase()+"/api/estimate/baseline",{headers:{"ngrok-skip-browser-warning":"true"}})
      .then(function(r){return r.json();}).then(function(d){if(d.success){self._baseline=d.rates;self.fillBaseline(true);}})
      .catch(function(e){console.log('baseline load failed',e);});
  },

  fillBaseline:function(force){
    if(this._mode!=="single_work")return;
    var cat=(document.getElementById('est_category')||{}).value;
    var q=((document.getElementById('est_quality')||{}).value||"Standard").toLowerCase();
    var qm=q==="premium"?1.15:(q==="economy"?0.9:1.0);
    var b=this._baseline[cat]; if(!b)return;
    var mi=document.getElementById('est_material'),li=document.getElementById('est_labour');
    if(mi&&(force||!mi.value))mi.value=(b.material*qm).toFixed(2);
    if(li&&(force||!li.value))li.value=(b.labour*qm).toFixed(2);
    var mh=document.getElementById('mat_hint'),lh=document.getElementById('lab_hint');
    if(mh&&b.mat_min!=null)mh.innerText="BC typical: $"+(b.mat_min*qm).toFixed(2)+"–$"+(b.mat_max*qm).toFixed(2)+"/sqft";
    if(lh&&b.lab_min!=null)lh.innerText="BC typical: $"+(b.lab_min*qm).toFixed(2)+"–$"+(b.lab_max*qm).toFixed(2)+"/sqft";
  },
  resetRates:function(){this.fillBaseline(true);},

  calculate:function(){
    var self=this,out=document.getElementById('est_result');
    out.className=''; out.innerHTML='<p style="color:#1d4ed8;">Calculating...</p>';
    function val(id){var el=document.getElementById(id);return el?el.value:"";}
    var s=this.session();
    var payload={email:s.email,mode:this._mode,category:val('est_category'),
      sqft:parseFloat(val('est_sqft'))||0,project_type:val('est_ptype'),
      location_market:val('est_loc')||"BC / Vancouver",quality_level:val('est_quality')||"Standard",
      material_cost:parseFloat(val('est_material'))||0,labour_cost:parseFloat(val('est_labour'))||0,
      material:parseFloat(val('est_material'))||1,labor:parseFloat(val('est_labour'))||1,complexity:1};
    fetch(this.apiBase()+"/api/estimate/preview",{method:"POST",
      headers:{"Content-Type":"application/json","Authorization":"Bearer "+(s.token||""),"ngrok-skip-browser-warning":"true"},
      body:JSON.stringify(payload)})
    .then(function(r){return r.json();}).then(function(d){
      if(!d.success){out.innerHTML="<p style='color:#dc2626;'>"+(d.error||'Failed')+"</p>";return;}
      self._token=d.preview_token;
      var total = d.mode==="single_work"?d.total:d.base_estimate;
      var extra = d.mode==="single_work"
        ? "<p class='ae-r-sub'>"+d.category+"</p>"
        : "<p class='ae-r-sub'>Range: $"+Math.round(d.range.low).toLocaleString()+" – $"+Math.round(d.range.high).toLocaleString()+"</p>"
          +"<div class='ae-badges'><span class='ae-badge ae-badge-green'>Confidence "+(d.confidence*100).toFixed(0)+"%</span><span class='ae-badge ae-badge-amber'>Risk "+(d.risk*100).toFixed(0)+"%</span></div>";
      out.innerHTML =
        "<div class='ae-preview'>"
        +"<div class='ae-r-tag'>PREVIEW — NOT APPROVED</div>"
        +"<div class='ae-r-total'>$"+Math.round(total).toLocaleString()+"</div>"
        + extra
        +"<p class='ae-r-note'>Full breakdown unlocks on approval. Uses 1 credit.</p>"
        +"<button class='ae-approve' onclick='EstimatorModule.approve()'>Approve — uses 1 credit</button>"
        +"</div>";
    }).catch(function(e){out.innerHTML="<p style='color:#dc2626;'>Connection error: "+e.message+"</p>";});
  },

  approve:function(){
    var self=this,out=document.getElementById('est_result'),s=this.session();
    if(!this._token){out.innerHTML="<p style='color:#dc2626;'>Please calculate first.</p>";return;}
    out.innerHTML="<p style='color:#16a34a;'>Approving...</p>";
    fetch(this.apiBase()+"/api/estimate/approve",{method:"POST",
      headers:{"Content-Type":"application/json","Authorization":"Bearer "+(s.token||""),"ngrok-skip-browser-warning":"true"},
      body:JSON.stringify({email:s.email,preview_token:this._token})})
    .then(function(r){return r.json();}).then(function(d){
      if(d.error==="limit_reached"){out.innerHTML="<div class='ae-limit'><h4>Approval limit reached</h4><p>"+d.message+"</p></div>";return;}
      if(!d.success){out.innerHTML="<p style='color:#dc2626;'>"+(d.error||'Failed')+"</p>";return;}
      self._token=null;var e=d.estimate,body="";
      if(e.mode==="single_work"){
        function bar(label,amt,tot){var pct=tot?Math.round(amt/tot*100):0;return "<div class='ae-bar-row'><span>"+label+"</span><span>$"+Math.round(amt).toLocaleString()+"</span></div><div class='ae-bar'><div class='ae-bar-fill' style='width:"+pct+"%'></div></div>";}
        var tot=e.materials_cost+e.labour_cost;
        body = bar("Materials ($"+e.material_rate+"/sqft × "+e.sqft+")",e.materials_cost,tot)
             + bar("Labour ($"+e.labour_rate+"/sqft × "+e.sqft+")",e.labour_cost,tot)
             + "<p class='ae-r-note'>"+e.category+" · "+(e.location_market||'')+" · "+(e.quality_level||'')+"</p>";
      } else {
        var bd=e.breakdown||{};var rows=Object.keys(bd).map(function(k){return "<div class='ae-bar-row'><span>"+k+"</span><span>$"+Math.round(bd[k]).toLocaleString()+"</span></div>";}).join("");
        function line(l,v){return "<div class='ae-bar-row'><span>"+l+"</span><span>$"+Math.round(v).toLocaleString()+"</span></div>";}
        body="<p class='ae-r-sub'>Range: $"+Math.round(e.range.low).toLocaleString()+" – $"+Math.round(e.range.high).toLocaleString()+" · Confidence "+(e.confidence*100).toFixed(0)+"%</p>"
          +"<div style='margin-top:8px;font-weight:800;color:#0f172a;'>Trade breakdown</div>"+rows
          +"<div style='margin-top:8px;font-weight:800;color:#0f172a;'>Costs</div>"
          +line("Hard cost",e.hard_cost)+line("Overhead (15%)",e.overhead)+line("Profit (10%)",e.profit)
          +line("Contingency (10%)",e.contingency)+line("Permits/soft (8%)",e.permits)
          +line("GST (5%)",e.gst)+line("PST (7%)",e.pst);
      }
      var total=e.mode==="single_work"?e.total:e.base_estimate;
      out.innerHTML =
        "<div class='ae-approved'>"
        +"<div class='ae-r-tag ae-r-tag-green'>APPROVED — THIS ESTIMATE IS NOW YOURS</div>"
        +"<div class='ae-r-total'>$"+Math.round(total).toLocaleString()+"</div>"
        + body
        +"<p class='ae-credits'>Approved estimates: "+d.approved_used+" / "+d.limit+" · "+d.remaining+" remaining</p>"
        +"</div>";
      if(e.mode==="single_work" && window.QuoteModule){ QuoteModule.offerQuote(e); }
      if(e.mode==="whole_project" && window.ProjectDocModule){ ProjectDocModule.offer(e); }
    }).catch(function(e){out.innerHTML="<p style='color:#dc2626;'>Connection error: "+e.message+"</p>";});
  },

  showHistory:function(){
    var self=this;
    var area=document.getElementById('est_result');
    area.innerHTML='<p style="color:#1d4ed8;">Loading your quotes...</p>';
    fetch(this.apiBase()+"/api/estimate/history",{headers:{"Authorization":"Bearer "+(this.session().token||''),"ngrok-skip-browser-warning":"true"}})
      .then(function(r){return r.json();}).then(function(d){
        if(!d.success){area.innerHTML='<p style="color:#dc2626;">'+(d.error||'Error')+'</p>';return;}
        if(!d.quotes||!d.quotes.length){area.innerHTML='<p style="color:#94a3b8;">No saved quotes yet. Approve an estimate to see it here.</p>';return;}
        var rows=d.quotes.map(function(q){
          var dt=(q.created_at||'').split('T')[0];
          return "<div style='display:flex;justify-content:space-between;align-items:center;border:1px solid #e2e8f0;border-radius:10px;padding:12px;margin-bottom:8px;'><div><b>"+q.title+"</b> <span style='color:#94a3b8;font-size:12px;'>· "+dt+(q.location?' · '+q.location:'')+"</span><br><span style='color:#475569;font-size:13px;'>$"+Math.round(q.total).toLocaleString()+(q.sqft?' · '+q.sqft+' sqft':'')+"</span></div><button onclick='EstimatorModule.viewQuote("+q.index+")' style='padding:6px 12px;border:1px solid #1d4ed8;background:#fff;color:#1d4ed8;border-radius:7px;font-weight:700;cursor:pointer;font-size:12px;'>View</button></div>";
        }).join('');
        area.innerHTML='<h3 style="margin:0 0 12px;">My Quotes ('+d.count+')</h3>'+rows;
        self._history=d.quotes;
      }).catch(function(){area.innerHTML='<p style="color:#dc2626;">Connection error.</p>';});
  },
  viewQuote:function(idx){
    var self=this;
    var q=(this._history||[]).filter(function(x){return x.index===idx;})[0];
    if(!q){return;}
    var e=q.estimate; var area=document.getElementById('est_result');
    var body='';
    if(e.mode==='single_work'){
      body="<p>Materials: $"+Math.round(e.materials_cost||0).toLocaleString()+"</p><p>Labour: $"+Math.round(e.labour_cost||0).toLocaleString()+"</p><p style='font-weight:900;'>Total: $"+Math.round(e.total||0).toLocaleString()+"</p>";
    } else {
      var bd=e.breakdown||{}; var rows=Object.keys(bd).map(function(k){return "<div style='display:flex;justify-content:space-between;'><span>"+k+"</span><span>$"+Math.round(bd[k]).toLocaleString()+"</span></div>";}).join('');
      body=rows+"<p style='font-weight:900;margin-top:8px;'>Grand Total: $"+Math.round(e.grand_total||e.base_estimate||0).toLocaleString()+"</p>";
    }
    area.innerHTML="<div style='padding:20px;border:2px solid #16a34a;border-radius:14px;background:#f0fdf4;'><h3 style='margin:0 0 6px;'>"+q.title+"</h3><p style='color:#94a3b8;font-size:12px;'>"+(q.created_at||'').split('T')[0]+(q.location?' · '+q.location:'')+"</p>"+body+"<button onclick='EstimatorModule.printQuote()' style='margin-top:12px;padding:10px 18px;border:none;border-radius:8px;background:#16a34a;color:#fff;font-weight:800;cursor:pointer;'>Print / Save PDF</button> <button onclick='EstimatorModule.createInvoiceFromQuote()' style='margin-top:12px;padding:10px 18px;border:none;border-radius:8px;background:#1d4ed8;color:#fff;font-weight:800;cursor:pointer;'>Create Invoice (Finance)</button> <button onclick='EstimatorModule.showHistory()' style='margin-top:12px;padding:10px 18px;border:1px solid #e2e8f0;background:#fff;color:#475569;border-radius:8px;font-weight:700;cursor:pointer;'>Back to Quotes</button></div>";
    self._viewing=q;
  },
  printQuote:function(){
    var el=document.getElementById('est_result');
    var w=window.open('','_blank');
    w.document.write("<html><head><title>Astraa Quote</title></head><body style='font-family:Segoe UI,Arial;padding:24px;'>"+el.innerHTML+"</body></html>");
    w.document.close();w.focus();w.print();
  },
  createInvoiceFromQuote:function(){
    var self=this; var q=this._viewing;
    if(!q){alert('Open a quote first.');return;}
    var e=q.estimate||{};
    var amount = (e.mode==='single_work') ? (e.total||0) : (e.grand_total||e.base_estimate||0);
    var client = prompt('Client name for this invoice:', q.title||'Client');
    if(client===null)return;
    fetch(this.apiBase()+"/api/finance/invoice-from-quote",{method:'POST',headers:{"Content-Type":"application/json","Authorization":"Bearer "+(this.session().token||''),"ngrok-skip-browser-warning":"true"},body:JSON.stringify({client:client,description:q.title,amount:amount})})
      .then(function(r){return r.json();}).then(function(d){
        if(d.success){alert('Invoice created in Finance (Pending) for $'+Math.round(amount).toLocaleString()+'. Open Astraa Finance to view/send it.');}
        else{alert(d.error||'Failed to create invoice.');}
      }).catch(function(){alert('Connection error.');});
  },
  styles:function(){
    return "<style>"
    +".ae-wrap{max-width:1000px;}"
    +".ae-head{display:flex;justify-content:space-between;align-items:flex-start;flex-wrap:wrap;gap:16px;margin-bottom:20px;}"
    +".ae-title{margin:0;font-size:1.6rem;font-weight:900;color:#090d16;letter-spacing:-0.02em;}"
    +".ae-sub{margin:4px 0 0;color:#64748b;font-size:0.9rem;}"
    +".ae-modes{display:flex;gap:8px;background:#f1f5f9;border-radius:10px;padding:4px;}"
    +".ae-mode{padding:8px 16px;border-radius:8px;font-weight:700;font-size:0.9rem;color:#475569;cursor:pointer;transition:.15s;}"
    +".ae-mode input{display:none;}"
    +".ae-mode-on{background:#1d4ed8;color:#fff;box-shadow:0 4px 10px rgba(29,78,216,0.25);}"
    +".ae-grid{display:grid;grid-template-columns:1fr 1fr;gap:20px;align-items:start;}"
    +".ae-card{background:#fff;border:1px solid #e2e8f0;border-radius:16px;padding:24px;box-shadow:0 10px 30px rgba(15,23,42,0.05);}"
    +".ae-field{margin-bottom:14px;}"
    +".ae-field label{display:block;font-size:0.8rem;font-weight:800;color:#0f172a;margin-bottom:5px;text-transform:uppercase;letter-spacing:.03em;}"
    +".ae-field input,.ae-field select{width:100%;padding:11px 13px;border:1px solid #e2e8f0;border-radius:9px;background:#f8fafc;color:#0f172a;font-size:0.95rem;font-family:inherit;}"
    +".ae-field input:focus,.ae-field select:focus{outline:none;border-color:#1d4ed8;box-shadow:0 0 0 3px rgba(29,78,216,0.12);}"
    +".ae-hint{display:block;font-size:11px;color:#94a3b8;margin-top:4px;}"
    +".ae-note{color:#475569;font-size:0.85rem;background:#eff6ff;border:1px solid #bfdbfe;border-radius:10px;padding:12px;}"
    +".ae-reset{background:#fff;border:1px solid #e2e8f0;color:#1d4ed8;font-size:12px;font-weight:700;padding:6px 12px;border-radius:7px;cursor:pointer;margin-bottom:8px;}"
    +".ae-calc{width:100% !important;padding:13px !important;border:none !important;border-radius:10px !important;background:#1d4ed8 !important;color:#fff !important;font-weight:800 !important;font-size:1rem !important;cursor:pointer !important;margin-top:6px !important;}"
    +".ae-calc:hover{background:#1e40af;}"
    +".ae-placeholder{color:#94a3b8;text-align:center;padding:40px 10px;font-size:0.9rem;}"
    +".ae-r-tag{font-size:10px;font-weight:800;color:#f59e0b;letter-spacing:.05em;margin-bottom:8px;}"
    +".ae-r-tag-green{color:#16a34a;}"
    +".ae-r-total{font-size:2.4rem;font-weight:900;color:#090d16;letter-spacing:-0.03em;line-height:1;}"
    +".ae-r-sub{color:#475569;margin:8px 0;font-size:0.9rem;}"
    +".ae-r-note{color:#94a3b8;font-size:12px;margin-top:10px;}"
    +".ae-badges{display:flex;gap:8px;margin:10px 0;}"
    +".ae-badge{font-size:12px;font-weight:800;padding:4px 10px;border-radius:999px;}"
    +".ae-badge-green{background:#f0fdf4;color:#16a34a;border:1px solid #bbf7d0;}"
    +".ae-badge-amber{background:#fffbeb;color:#b45309;border:1px solid #fde68a;}"
    +".ae-approve{width:100%;padding:13px;border:none;border-radius:10px;background:#16a34a;color:#fff;font-weight:800;cursor:pointer;margin-top:14px;box-shadow:0 8px 20px rgba(22,163,74,0.25);}"
    +".ae-approve:hover{background:#15803d;}"
    +".ae-bar-row{display:flex;justify-content:space-between;font-size:0.85rem;color:#334155;margin:10px 0 4px;font-weight:700;}"
    +".ae-bar{height:8px;background:#f1f5f9;border-radius:6px;overflow:hidden;}"
    +".ae-bar-fill{height:100%;background:linear-gradient(90deg,#1d4ed8,#06b6d4);}"
    +".ae-credits{color:#166534;font-size:12px;margin-top:14px;font-weight:700;}"
    +".ae-limit{background:#fffbeb;border:1px solid #fde68a;border-radius:12px;padding:16px;color:#92400e;}"
    +"@media(max-width:820px){.ae-grid{grid-template-columns:1fr;}.ae-head{flex-direction:column;}}"
    +"</style>";
  }
};
window.EstimatorModule = EstimatorModule;
