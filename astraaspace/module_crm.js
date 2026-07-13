// Astraa Lead Gen / CRM — pipeline, sources, follow-ups (industry-agnostic)
var CRMModule = {
  stages:["New","Contacted","Qualified","Won","Lost"],
  sources:["Website","Referral","Advertisement","Cold Outreach","Social Media","Other"],
  _filter:"",
  apiBase:function(){return (typeof ASTRAA_API_BASE!=='undefined')?ASTRAA_API_BASE:"https://family-speed-outcome.ngrok-free.dev";},
  session:function(){try{return JSON.parse(localStorage.getItem('astraa_session')||'{}');}catch(e){return {};}},
  hdr:function(){return {"Content-Type":"application/json","Authorization":"Bearer "+(this.session().token||""),"ngrok-skip-browser-warning":"true"};},

  render:function(){
    var f="width:100%;padding:11px 13px;border:1px solid #e2e8f0;border-radius:8px;background:#f8fafc;color:#0f172a;font-size:0.95rem;";
    var srcOpts=this.sources.map(function(s){return "<option>"+s+"</option>";}).join("");
    var stgOpts=this.stages.map(function(s){return "<option>"+s+"</option>";}).join("");
    return this.styles()
      + '<div class="cr-wrap">'
      + '  <div class="cr-head"><h2 class="cr-title">Astraa Lead Gen / CRM</h2><p class="cr-sub">Capture leads, manage your pipeline, and close more deals.</p></div>'
      + '  <div id="cr_summary" class="cr-stats"></div>'
      + '  <div class="cr-grid">'
      + '    <div class="cr-card">'
      + '      <h3 class="cr-h3">Add Lead</h3>'
      + '      <div class="cr-field"><label>Name</label><input id="cr_name" style="'+f+'" placeholder="Contact name"></div>'
      + '      <div class="cr-field"><label>Company</label><input id="cr_company" style="'+f+'" placeholder="Company / account"></div>'
      + '      <div class="cr-field"><label>Email</label><input id="cr_email" type="email" style="'+f+'" placeholder="name@example.com"></div>'
      + '      <div class="cr-field"><label>Phone</label><input id="cr_phone" style="'+f+'" placeholder="(xxx) xxx-xxxx"></div>'
      + '      <div class="cr-field"><label>Source</label><select id="cr_source" style="'+f+'">'+srcOpts+'</select></div>'
      + '      <div class="cr-field"><label>Estimated value ($)</label><input id="cr_value" type="number" step="0.01" style="'+f+'" placeholder="0.00"></div>'
      + '      <div class="cr-field"><label>Next action</label><input id="cr_action" style="'+f+'" placeholder="e.g. Send proposal"></div>'
      + '      <div class="cr-field"><label>Follow-up date</label><input id="cr_actiondate" type="date" style="'+f+'"></div>'
      + '      <div class="cr-field"><label>Notes</label><input id="cr_notes" style="'+f+'" placeholder="optional"></div>'
      + '      <button class="cr-add" onclick="CRMModule.add()">Add Lead</button>'
      + '    </div>'
      + '    <div class="cr-card">'
      + '      <div class="cr-listhead"><h3 class="cr-h3" style="margin:0;">Pipeline</h3>'
      + '        <select id="cr_filter" class="cr-filter" onchange="CRMModule.setFilter(this.value)"><option value="">All stages</option>'+stgOpts+'</select></div>'
      + '      <div id="cr_list"></div>'
      + '    </div>'
      + '  </div>'
      + '</div>';
  },

  load:function(){ var d=document.getElementById('cr_actiondate'); this.refresh(); },
  setFilter:function(v){ this._filter=v; this.refresh(); },

  refresh:function(){
    var self=this;
    fetch(this.apiBase()+"/api/crm/list",{headers:this.hdr()})
      .then(function(r){return r.json();}).then(function(d){
        if(!d.success){document.getElementById('cr_list').innerHTML="<p style='color:#dc2626;'>"+(d.error||'Error')+"</p>";return;}
        var s=d.summary||{}; var money=function(n){return "$"+Number(n||0).toLocaleString();};
        var bs=s.by_stage||{};
        document.getElementById('cr_summary').innerHTML=
          "<div class='cr-stat'><span class='cr-stat-l'>Total leads</span><span class='cr-stat-v'>"+(s.total||0)+"</span></div>"
          +"<div class='cr-stat'><span class='cr-stat-l'>Pipeline value</span><span class='cr-stat-v'>"+money(s.pipeline_value)+"</span></div>"
          +"<div class='cr-stat'><span class='cr-stat-l'>Won</span><span class='cr-stat-v'>"+(bs.Won||0)+"</span></div>"
          +"<div class='cr-stat'><span class='cr-stat-l'>Conversion</span><span class='cr-stat-v'>"+(s.conversion_rate||0)+"%</span></div>";
        var leads=(d.leads||[]).filter(function(l){return !self._filter||l.stage===self._filter;});
        if(!leads.length){document.getElementById('cr_list').innerHTML="<p style='color:#94a3b8;'>No leads yet. Add one on the left.</p>";return;}
        var stageColor={"New":"#3b82f6","Contacted":"#f59e0b","Qualified":"#8b5cf6","Won":"#16a34a","Lost":"#94a3b8"};
        document.getElementById('cr_list').innerHTML=leads.map(function(l){
          var opts=self.stages.map(function(st){return "<option "+(st===l.stage?"selected":"")+">"+st+"</option>";}).join("");
          return "<div class='cr-lead'>"
            +"<div class='cr-lead-top'>"
            +"<div><span class='cr-lead-name'>"+l.name+"</span>"+(l.company?" <span class='cr-lead-co'>· "+l.company+"</span>":"")+"</div>"
            +"<button class='cr-del' onclick=\"CRMModule.del('"+l.id+"')\">✕</button></div>"
            +"<div class='cr-lead-meta'>"+(l.value?money(l.value)+" · ":"")+l.source+(l.email?" · "+l.email:"")+(l.phone?" · "+l.phone:"")+"</div>"
            +(l.next_action?"<div class='cr-lead-next'>▶ "+l.next_action+(l.next_action_date?" (by "+l.next_action_date+")":"")+"</div>":"")
            +(l.notes?"<div class='cr-lead-notes'>"+l.notes+"</div>":"")
            +"<div class='cr-lead-stage'><span class='cr-dot' style='background:"+(stageColor[l.stage]||'#94a3b8')+"'></span>"
            +"<select class='cr-stagesel' onchange=\"CRMModule.setStage('"+l.id+"',this.value)\">"+opts+"</select></div>"
            +"</div>";
        }).join("");
      }).catch(function(){document.getElementById('cr_list').innerHTML="<p style='color:#dc2626;'>Connection error.</p>";});
  },

  add:function(){
    var self=this; function v(id){var e=document.getElementById(id);return e?e.value:"";}
    if(!v('cr_name')){alert("Enter a lead name.");return;}
    var body={name:v('cr_name'),company:v('cr_company'),email:v('cr_email'),phone:v('cr_phone'),
      source:v('cr_source'),value:parseFloat(v('cr_value'))||0,next_action:v('cr_action'),
      next_action_date:v('cr_actiondate'),notes:v('cr_notes'),stage:"New"};
    fetch(this.apiBase()+"/api/crm/add",{method:"POST",headers:this.hdr(),body:JSON.stringify(body)})
      .then(function(r){return r.json();}).then(function(d){
        if(!d.success){alert(d.error||"Failed.");return;}
        ["cr_name","cr_company","cr_email","cr_phone","cr_value","cr_action","cr_notes"].forEach(function(id){var e=document.getElementById(id);if(e)e.value="";});
        self.refresh();
      }).catch(function(){alert("Connection error.");});
  },

  setStage:function(id,stage){
    var self=this;
    fetch(this.apiBase()+"/api/crm/update-stage",{method:"POST",headers:this.hdr(),body:JSON.stringify({id:id,stage:stage})})
      .then(function(r){return r.json();}).then(function(){self.refresh();}).catch(function(){});
  },

  del:function(id){
    var self=this; if(!confirm("Delete this lead?"))return;
    fetch(this.apiBase()+"/api/crm/delete",{method:"POST",headers:this.hdr(),body:JSON.stringify({id:id})})
      .then(function(r){return r.json();}).then(function(){self.refresh();}).catch(function(){});
  },

  styles:function(){
    return "<style>"
    +".cr-wrap{max-width:1000px;}"
    +".cr-head{margin-bottom:16px;}.cr-title{margin:0;font-size:1.6rem;font-weight:900;color:#090d16;}.cr-sub{margin:4px 0 0;color:#64748b;font-size:0.9rem;}"
    +".cr-stats{display:flex;gap:12px;margin-bottom:18px;flex-wrap:wrap;}"
    +".cr-stat{flex:1;min-width:120px;background:#fff;border:1px solid #e2e8f0;border-radius:12px;padding:14px;text-align:center;box-shadow:0 6px 18px rgba(15,23,42,0.04);}"
    +".cr-stat-l{display:block;font-size:11px;color:#64748b;font-weight:700;text-transform:uppercase;}"
    +".cr-stat-v{display:block;font-size:1.3rem;font-weight:900;color:#090d16;margin-top:4px;}"
    +".cr-grid{display:grid;grid-template-columns:0.9fr 1.3fr;gap:20px;align-items:start;}"
    +".cr-card{background:#fff;border:1px solid #e2e8f0;border-radius:16px;padding:24px;box-shadow:0 10px 30px rgba(15,23,42,0.05);}"
    +".cr-h3{font-size:1.1rem;font-weight:800;color:#0f172a;margin:0 0 14px;}"
    +".cr-field{margin-bottom:11px;}.cr-field label{display:block;font-size:0.76rem;font-weight:800;color:#0f172a;margin-bottom:4px;text-transform:uppercase;letter-spacing:.03em;}"
    +".cr-add{width:100%;padding:12px;border:none;border-radius:10px;background:#1d4ed8;color:#fff;font-weight:800;cursor:pointer;box-shadow:0 8px 20px rgba(29,78,216,0.25);}"
    +".cr-add:hover{background:#1e40af;}"
    +".cr-listhead{display:flex;justify-content:space-between;align-items:center;margin-bottom:12px;}"
    +".cr-filter{padding:7px 10px;border:1px solid #e2e8f0;border-radius:8px;background:#f8fafc;font-size:13px;}"
    +".cr-lead{border:1px solid #e2e8f0;border-radius:12px;padding:14px;margin-bottom:10px;}"
    +".cr-lead-top{display:flex;justify-content:space-between;align-items:center;}"
    +".cr-lead-name{font-weight:800;color:#0f172a;}.cr-lead-co{color:#64748b;font-weight:600;font-size:0.9rem;}"
    +".cr-lead-meta{color:#94a3b8;font-size:12px;margin-top:3px;}"
    +".cr-lead-next{color:#1d4ed8;font-size:12px;margin-top:5px;font-weight:700;}"
    +".cr-lead-notes{color:#475569;font-size:12px;margin-top:4px;}"
    +".cr-lead-stage{display:flex;align-items:center;gap:8px;margin-top:8px;}"
    +".cr-dot{width:10px;height:10px;border-radius:50%;display:inline-block;}"
    +".cr-stagesel{padding:5px 8px;border:1px solid #e2e8f0;border-radius:7px;background:#f8fafc;font-size:12px;font-weight:700;}"
    +".cr-del{background:#fff !important;border:1px solid #fecaca !important;color:#dc2626 !important;border-radius:6px !important;width:26px;height:26px;cursor:pointer;font-weight:700 !important;}"
    +"@media(max-width:820px){.cr-grid{grid-template-columns:1fr;}}"
    +"</style>";
  }
};
window.CRMModule = CRMModule;
