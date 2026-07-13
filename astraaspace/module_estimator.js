// Astraa Estimator — Single Work / Whole Project modes
var EstimatorModule = {
  _token:null, _mode:"single_work", _baseline:{},
  bcCities:["BC / Vancouver","BC / Burnaby","BC / Richmond","BC / Surrey","BC / Coquitlam","BC / Port Coquitlam","BC / Port Moody","BC / New Westminster","BC / North Vancouver","BC / West Vancouver","BC / Delta","BC / Langley","BC / Maple Ridge","BC / Pitt Meadows","BC / White Rock","BC / Abbotsford","BC / Chilliwack","BC / Mission","BC / Hope","BC / Victoria","BC / Saanich","BC / Langford","BC / Colwood","BC / Nanaimo","BC / Parksville","BC / Qualicum Beach","BC / Duncan","BC / Courtenay","BC / Comox","BC / Campbell River","BC / Port Alberni","BC / Tofino","BC / Ucluelet","BC / Powell River","BC / Squamish","BC / Whistler","BC / Pemberton","BC / Gibsons","BC / Sechelt","BC / Kelowna","BC / West Kelowna","BC / Vernon","BC / Penticton","BC / Kamloops","BC / Merritt","BC / Salmon Arm","BC / Revelstoke","BC / Cranbrook","BC / Kimberley","BC / Fernie","BC / Nelson","BC / Castlegar","BC / Trail","BC / Golden","BC / Prince George","BC / Quesnel","BC / Williams Lake","BC / Fort St. John","BC / Dawson Creek","BC / Terrace","BC / Prince Rupert","BC / Kitimat","BC / Smithers","BC / Fort Nelson","BC / Other City or Town"],

  apiBase:function(){return (typeof ASTRAA_API_BASE!=='undefined')?ASTRAA_API_BASE:"https://family-speed-outcome.ngrok-free.dev";},
  session:function(){try{return JSON.parse(localStorage.getItem('astraa_session')||'{}');}catch(e){return {};}},

  render:function(){
    var f="width:100%;padding:11px 13px;border:1px solid #e2e8f0;border-radius:8px;background:#f8fafc;color:#0f172a;font-size:0.95rem;";
    var defaults=["Interior Paint","Flooring","Drywall","Tile","Roofing","Framing","Concrete","Electrical","Plumbing","Insulation","HVAC","General / Other"];
    var cats=Object.keys(this._baseline); if(!cats.length)cats=defaults;
    var catOpts=cats.map(function(c){return "<option>"+c+"</option>";}).join("");
    var cityOpts=this.bcCities.map(function(c){return "<option>"+c+"</option>";}).join("");
    return ''
      +'<h3>Astraa Estimator</h3>'
      +'<p style="color:#64748b;margin-bottom:14px;">Calculate free. You only use a credit when you <strong>approve</strong>.</p>'
      +'<div style="display:flex;gap:24px;margin-bottom:16px;font-weight:700;">'
      +'  <label style="cursor:pointer;"><input type="radio" name="est_mode" value="single_work" checked onchange="EstimatorModule.setMode(this.value)"> Single Work</label>'
      +'  <label style="cursor:pointer;"><input type="radio" name="est_mode" value="whole_project" onchange="EstimatorModule.setMode(this.value)"> Whole Project</label>'
      +'</div>'
      +'<div style="max-width:560px;display:flex;flex-direction:column;gap:12px;">'
      +'  <label>Category<select id="est_category" style="'+f+'" onchange="EstimatorModule.fillBaseline(true)">'+catOpts+'</select></label>'
      +'  <label>Square footage<input id="est_sqft" type="number" placeholder="100" style="'+f+'"></label>'
      +'  <label>Project type<select id="est_ptype" style="'+f+'"><option>Residential</option><option>Commercial</option><option>Industrial</option><option>Renovation</option><option>Service / Repair</option><option>Custom</option></select></label>'
      +'  <label>Location / market<select id="est_loc" style="'+f+'">'+cityOpts+'</select></label>'
      +'  <label>Quality level<select id="est_quality" style="'+f+'" onchange="EstimatorModule.fillBaseline(true)"><option>Standard</option><option>Premium</option><option>Economy</option></select></label>'
      +'  <label>Cost of material ($/sqft)<input id="est_material" type="number" step="0.01" style="'+f+'"></label>'
      +'  <label>Cost of labour ($/sqft)<input id="est_labour" type="number" step="0.01" style="'+f+'"></label>'
      +'  <p style="color:#94a3b8;font-size:12px;margin:0;">Rates pre-filled from BC industry standard — edit to match your pricing.</p>'
      +'  <button onclick="EstimatorModule.calculate()" style="padding:12px;border:none;border-radius:8px;background:#1d4ed8;color:#fff;font-weight:700;cursor:pointer;">Calculate (free)</button>'
      +'</div>'
      +'<div id="est_result" style="margin-top:20px;"></div>';
  },

  setMode:function(m){this._mode=m;},

  loadBaseline:function(){
    var self=this;
    fetch(this.apiBase()+"/api/estimate/baseline",{headers:{"ngrok-skip-browser-warning":"true"}})
      .then(function(r){return r.json();})
      .then(function(d){if(d.success){self._baseline=d.rates;self.fillBaseline();}})
      .catch(function(e){console.log('baseline load failed',e);});
  },

  fillBaseline:function(force){
    var cat=(document.getElementById('est_category')||{}).value;
    var q=((document.getElementById('est_quality')||{}).value||"Standard").toLowerCase();
    var qm=q==="premium"?1.15:(q==="economy"?0.9:1.0);
    var b=this._baseline[cat];
    if(!b)return;
    var mi=document.getElementById('est_material'),li=document.getElementById('est_labour');
    // Always pre-fill if empty, or when forced (reset / category change)
    if(mi&&(force||!mi.value))mi.value=(b.material*qm).toFixed(2);
    if(li&&(force||!li.value))li.value=(b.labour*qm).toFixed(2);
    // Show BC typical range hints
    var mh=document.getElementById('mat_hint'),lh=document.getElementById('lab_hint');
    if(mh&&b.mat_min!=null)mh.innerText=" BC typical: $"+(b.mat_min*qm).toFixed(2)+"–$"+(b.mat_max*qm).toFixed(2)+"/sqft";
    if(lh&&b.lab_min!=null)lh.innerText=" BC typical: $"+(b.lab_min*qm).toFixed(2)+"–$"+(b.lab_max*qm).toFixed(2)+"/sqft";
  },
  resetRates:function(){ this.fillBaseline(true); },

  calculate:function(){
    var self=this,out=document.getElementById('est_result');
    out.innerHTML='<p style="color:#1d4ed8;">Calculating...</p>';
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
      var head;
      if(d.mode==="single_work"){head="<h4 style='margin:0 0 6px 0;color:#03050a;'>"+d.category+" — Total: $"+Math.round(d.total).toLocaleString()+"</h4>";}
      else{head="<h4 style='margin:0 0 6px 0;color:#03050a;'>Estimated Cost: $"+Math.round(d.base_estimate).toLocaleString()+"</h4><p style='color:#475569;margin:2px 0;'>Range: $"+Math.round(d.range.low).toLocaleString()+" – $"+Math.round(d.range.high).toLocaleString()+" · Confidence "+(d.confidence*100).toFixed(1)+"%</p>";}
      out.innerHTML="<div style='padding:20px;border:1px dashed #94a3b8;border-radius:14px;background:#f8fafc;position:relative;'>"
        +"<div style='position:absolute;top:8px;right:14px;font-size:11px;font-weight:800;color:#f59e0b;'>PREVIEW — NOT APPROVED</div>"
        +head
        +"<p style='color:#94a3b8;font-size:12px;margin-top:8px;'>Full breakdown unlocks on approval. Uses 1 credit.</p>"
        +"<button onclick='EstimatorModule.approve()' style='margin-top:10px;padding:12px 18px;border:none;border-radius:8px;background:#16a34a;color:#fff;font-weight:800;cursor:pointer;'>Approve — uses 1 credit</button></div>";
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
      if(d.error==="limit_reached"){out.innerHTML="<div style='padding:18px;border:1px solid #f59e0b;border-radius:12px;background:#fffbeb;'><h4 style='margin:0 0 6px 0;color:#92400e;'>Limit reached</h4><p style='color:#92400e;'>"+d.message+"</p></div>";return;}
      if(!d.success){out.innerHTML="<p style='color:#dc2626;'>"+(d.error||'Failed')+"</p>";return;}
      self._token=null;var e=d.estimate,body="";
      if(e.mode==="single_work"){
        body="<table style='margin-top:12px;border-collapse:collapse;width:100%;max-width:400px;'>"
          +"<tr><td style='padding:6px 10px;color:#475569;'>Materials ($"+e.material_rate+"/sqft × "+e.sqft+")</td><td style='padding:6px 10px;text-align:right;font-weight:700;'>$"+Math.round(e.materials_cost).toLocaleString()+"</td></tr>"
          +"<tr><td style='padding:6px 10px;color:#475569;'>Labour ($"+e.labour_rate+"/sqft × "+e.sqft+")</td><td style='padding:6px 10px;text-align:right;font-weight:700;'>$"+Math.round(e.labour_cost).toLocaleString()+"</td></tr>"
          +"<tr style='border-top:2px solid #16a34a;'><td style='padding:8px 10px;font-weight:900;'>Total</td><td style='padding:8px 10px;text-align:right;font-weight:900;'>$"+Math.round(e.total).toLocaleString()+"</td></tr></table>"
          +"<p style='color:#94a3b8;font-size:12px;margin-top:8px;'>"+e.category+" · "+(e.location_market||'')+" · "+(e.quality_level||'')+"</p>";
      }else{
        var bd=e.breakdown||{};var rows=Object.keys(bd).map(function(k){return "<tr><td style='padding:4px 10px;color:#475569;text-transform:capitalize;'>"+k+"</td><td style='padding:4px 10px;text-align:right;font-weight:700;'>$"+Math.round(bd[k]).toLocaleString()+"</td></tr>";}).join("");
        body="<p style='color:#475569;'>Range: $"+Math.round(e.range.low).toLocaleString()+" – $"+Math.round(e.range.high).toLocaleString()+" · Confidence "+(e.confidence*100).toFixed(1)+"%</p><table style='margin-top:10px;border-collapse:collapse;width:100%;max-width:400px;'>"+rows+"</table>";
      }
      var total=e.mode==="single_work"?e.total:e.base_estimate;
      out.innerHTML="<div style='padding:20px;border:2px solid #16a34a;border-radius:14px;background:#f0fdf4;'>"
        +"<div style='font-size:11px;font-weight:800;color:#16a34a;margin-bottom:6px;'>APPROVED — THIS ESTIMATE IS NOW YOURS</div>"
        +"<h4 style='margin:0 0 6px 0;color:#03050a;'>Total: $"+Math.round(total).toLocaleString()+"</h4>"+body
        +"<p style='color:#166534;font-size:12px;margin-top:12px;font-weight:700;'>Approved estimates: "+d.approved_used+" / "+d.limit+" · "+d.remaining+" remaining</p></div>";
      if (e.mode === "single_work" && window.QuoteModule) { QuoteModule.offerQuote(e); }
    }).catch(function(e){out.innerHTML="<p style='color:#dc2626;'>Connection error: "+e.message+"</p>";});
  }
};
window.EstimatorModule = EstimatorModule;
