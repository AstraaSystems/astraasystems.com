// Astraa Business — full workspace: Dashboard, Projects, Leads/CRM, Marketing, HR
var BusinessModule = {
  _section:"dashboard",
  crmStages:["New","Contacted","Qualified","Won","Lost"],
  crmSources:["Website","Referral","Advertisement","Cold Outreach","Social Media","Other"],
  _crmFilter:"",
  apiBase:function(){return (typeof ASTRAA_API_BASE!=='undefined')?ASTRAA_API_BASE:"https://family-speed-outcome.ngrok-free.dev";},
  session:function(){try{return JSON.parse(localStorage.getItem('astraa_session')||'{}');}catch(e){return {};}},
  hdr:function(){return {"Content-Type":"application/json","Authorization":"Bearer "+(this.session().token||""),"ngrok-skip-browser-warning":"true"};},

  render:function(){
    return this.styles()
      + '<div class="bw-shell">'
      + '  <aside class="bw-menu">'
      + '    <div class="bw-brand">Astraa Business</div>'
      + '    <a class="bw-nav" data-s="dashboard" onclick="BusinessModule.go(\'dashboard\')">📊 Dashboard</a>'
      + '    <a class="bw-nav" data-s="projects" onclick="BusinessModule.go(\'projects\')">📁 Projects</a>'
      + '    <a class="bw-nav" data-s="crm" onclick="BusinessModule.go(\'crm\')">👥 Leads / CRM</a>'
      + '    <a class="bw-nav" data-s="marketing" onclick="BusinessModule.go(\'marketing\')">📣 Marketing</a>'
      + '    <a class="bw-nav" data-s="sales" onclick="BusinessModule.go(\'sales\')">🧾 Sales</a>'
      + '    <a class="bw-nav" data-s="hr" onclick="BusinessModule.go(\'hr\')">🧑‍💼 HR</a>'
      + '  </aside>'
      + '  <main class="bw-main"><div id="bw_body"></div></main>'
      + '</div>';
  },

  load:function(){ this.go('dashboard'); },

  go:function(section){
    this._section=section;
    var navs=document.querySelectorAll('.bw-nav');
    for(var i=0;i<navs.length;i++){navs[i].className='bw-nav'+(navs[i].getAttribute('data-s')===section?' bw-nav-on':'');}
    if(section==='dashboard')this.renderDashboard();
    else if(section==='projects')this.renderProjects();
    else if(section==='crm')this.renderCRM();
    else if(section==='marketing')this.renderMarketing();
    else if(section==='sales')this.renderSales();
    else if(section==='hr')this.renderHR();
  },

  // ---------- DASHBOARD ----------
  renderDashboard:function(){
    var self=this, body=document.getElementById('bw_body');
    body.innerHTML='<h2 class="bw-h2">Dashboard</h2><p class="bw-muted">Loading overview…</p>';
    Promise.all([
      fetch(this.apiBase()+"/api/business/list",{headers:this.hdr()}).then(function(r){return r.json();}).catch(function(){return {};}),
      fetch(this.apiBase()+"/api/crm/list",{headers:this.hdr()}).then(function(r){return r.json();}).catch(function(){return {};})
    ]).then(function(res){
      var b=(res[0]&&res[0].summary)||{}, c=(res[1]&&res[1].summary)||{};
      var money=function(n){return "$"+Number(n||0).toLocaleString();};
      body.innerHTML='<h2 class="bw-h2">Dashboard</h2>'
        +'<div class="bw-stats">'
        +stat("Active Projects",b.active||0)
        +stat("Open Tasks",b.pending_tasks||0)
        +stat("Total Leads",c.total||0)
        +stat("Pipeline Value",money(c.pipeline_value))
        +stat("Project Value",money(b.total_value))
        +stat("Conversion",(c.conversion_rate||0)+"%")
        +'</div>'
        +'<div class="bw-quick"><button class="bw-qbtn" onclick="BusinessModule.go(\'projects\')">+ New Project</button>'
        +'<button class="bw-qbtn" onclick="BusinessModule.go(\'crm\')">+ New Lead</button></div>';
      function stat(l,v){return "<div class='bw-stat'><span class='bw-stat-l'>"+l+"</span><span class='bw-stat-v'>"+v+"</span></div>";}
    });
  },

  // ---------- PROJECTS ----------
  renderProjects:function(){
    var f="width:100%;padding:10px 12px;border:1px solid #e2e8f0;border-radius:8px;background:#f8fafc;font-size:0.9rem;";
    document.getElementById('bw_body').innerHTML=
      '<h2 class="bw-h2">Projects</h2>'
      +'<div class="bw-two">'
      +'<div class="bw-panel"><h3 class="bw-h3">New Project</h3>'
      +'<div class="bw-f"><label>Project name</label><input id="bz_name" style="'+f+'" placeholder="e.g. Q3 Client Onboarding"></div>'
      +'<div class="bw-f"><label>Client / Contact</label><input id="bz_client" style="'+f+'"></div>'
      +'<div class="bw-f"><label>Status</label><select id="bz_status" style="'+f+'"><option>Active</option><option>On Hold</option><option>Complete</option></select></div>'
      +'<div class="bw-f"><label>Due date</label><input id="bz_due" type="date" style="'+f+'"></div>'
      +'<div class="bw-f"><label>Value ($) optional</label><input id="bz_value" type="number" step="0.01" style="'+f+'"></div>'
      +'<button class="bw-add" onclick="BusinessModule.addProject()">Add Project</button></div>'
      +'<div class="bw-panel"><h3 class="bw-h3">Active Projects</h3><div id="bz_list"></div></div>'
      +'</div>';
    this.refreshProjects();
  },
  refreshProjects:function(){
    var self=this;
    fetch(this.apiBase()+"/api/business/list",{headers:this.hdr()}).then(function(r){return r.json();}).then(function(d){
      if(!d.success){document.getElementById('bz_list').innerHTML="<p class='bw-muted'>Error loading.</p>";return;}
      var money=function(n){return "$"+Number(n||0).toLocaleString();};
      var ps=d.projects||[];
      if(!ps.length){document.getElementById('bz_list').innerHTML="<p class='bw-muted'>No projects yet.</p>";return;}
      var col={"Active":"#16a34a","On Hold":"#f59e0b","Complete":"#64748b"};
      document.getElementById('bz_list').innerHTML=ps.map(function(p){
        var tasks=(p.tasks||[]).map(function(t){var done=t.status==="Done";
          return "<div class='bw-task'><label style='display:flex;gap:8px;align-items:center;cursor:pointer;"+(done?"text-decoration:line-through;color:#94a3b8;":"")+"'><input type='checkbox' "+(done?"checked":"")+" onchange=\"BusinessModule.toggleTask('"+p.id+"','"+t.id+"')\">"+t.title+(t.assignee?" · "+t.assignee:"")+"</label></div>";}).join("");
        return "<div class='bw-proj'><div class='bw-proj-top'><div><b>"+p.name+"</b> <span class='bw-badge' style='background:"+(col[p.status]||'#64748b')+"'>"+p.status+"</span></div><button class='bw-del' onclick=\"BusinessModule.delProject('"+p.id+"')\">✕</button></div>"
          +"<div class='bw-muted' style='font-size:12px;margin:4px 0;'>"+(p.client?p.client+" · ":"")+(p.value?money(p.value)+" · ":"")+(p.due_date?"due "+p.due_date:"")+"</div>"
          +tasks
          +"<div class='bw-taskadd'><input id='task_"+p.id+"' placeholder='Add task…' class='bw-ti'><input id='asg_"+p.id+"' placeholder='Assigned to' class='bw-ti' style='max-width:120px;'><button class='bw-tbtn' onclick=\"BusinessModule.addTask('"+p.id+"')\">+</button></div></div>";
      }).join("");
    });
  },
  addProject:function(){var self=this;function v(id){var e=document.getElementById(id);return e?e.value:"";}
    if(!v('bz_name')){alert("Enter a project name.");return;}
    fetch(this.apiBase()+"/api/business/add-project",{method:"POST",headers:this.hdr(),body:JSON.stringify({name:v('bz_name'),client:v('bz_client'),status:v('bz_status'),due_date:v('bz_due'),value:parseFloat(v('bz_value'))||0})})
      .then(function(r){return r.json();}).then(function(){["bz_name","bz_client","bz_value"].forEach(function(i){var e=document.getElementById(i);if(e)e.value="";});self.refreshProjects();});},
  delProject:function(id){var self=this;if(!confirm("Delete project?"))return;fetch(this.apiBase()+"/api/business/delete-project",{method:"POST",headers:this.hdr(),body:JSON.stringify({id:id})}).then(function(r){return r.json();}).then(function(){self.refreshProjects();});},
  addTask:function(pid){var self=this;var t=(document.getElementById('task_'+pid)||{}).value||"";var a=(document.getElementById('asg_'+pid)||{}).value||"";if(!t)return;fetch(this.apiBase()+"/api/business/add-task",{method:"POST",headers:this.hdr(),body:JSON.stringify({project_id:pid,title:t,assignee:a})}).then(function(r){return r.json();}).then(function(){self.refreshProjects();});},
  toggleTask:function(pid,tid){var self=this;fetch(this.apiBase()+"/api/business/toggle-task",{method:"POST",headers:this.hdr(),body:JSON.stringify({project_id:pid,task_id:tid})}).then(function(r){return r.json();}).then(function(){self.refreshProjects();});},

  // ---------- LEADS / CRM ----------
  renderCRM:function(){
    var f="width:100%;padding:10px 12px;border:1px solid #e2e8f0;border-radius:8px;background:#f8fafc;font-size:0.9rem;";
    var src=this.crmSources.map(function(s){return "<option>"+s+"</option>";}).join("");
    var stg=this.crmStages.map(function(s){return "<option>"+s+"</option>";}).join("");
    document.getElementById('bw_body').innerHTML=
      '<h2 class="bw-h2">Leads / CRM</h2>'
      +'<div class="bw-two">'
      +'<div class="bw-panel"><h3 class="bw-h3">Add Lead</h3>'
      +'<div class="bw-f"><label>Name</label><input id="cr_name" style="'+f+'"></div>'
      +'<div class="bw-f"><label>Company</label><input id="cr_company" style="'+f+'"></div>'
      +'<div class="bw-f"><label>Email</label><input id="cr_email" style="'+f+'"></div>'
      +'<div class="bw-f"><label>Phone</label><input id="cr_phone" style="'+f+'"></div>'
      +'<div class="bw-f"><label>Source</label><select id="cr_source" style="'+f+'">'+src+'</select></div>'
      +'<div class="bw-f"><label>Est. value ($)</label><input id="cr_value" type="number" step="0.01" style="'+f+'"></div>'
      +'<div class="bw-f"><label>Next action</label><input id="cr_action" style="'+f+'" placeholder="e.g. Send proposal"></div>'
      +'<button class="bw-add" onclick="BusinessModule.addLead()">Add Lead</button></div>'
      +'<div class="bw-panel"><div class="bw-listhead"><h3 class="bw-h3" style="margin:0;">Pipeline</h3><select id="cr_filter" class="bw-filter" onchange="BusinessModule.setCrmFilter(this.value)"><option value="">All stages</option>'+stg+'</select></div><div id="cr_list"></div></div>'
      +'</div>';
    this.refreshCRM();
  },
  setCrmFilter:function(v){this._crmFilter=v;this.refreshCRM();},
  refreshCRM:function(){
    var self=this;
    fetch(this.apiBase()+"/api/crm/list",{headers:this.hdr()}).then(function(r){return r.json();}).then(function(d){
      if(!d.success){document.getElementById('cr_list').innerHTML="<p class='bw-muted'>Error.</p>";return;}
      var money=function(n){return "$"+Number(n||0).toLocaleString();};
      var leads=(d.leads||[]).filter(function(l){return !self._crmFilter||l.stage===self._crmFilter;});
      if(!leads.length){document.getElementById('cr_list').innerHTML="<p class='bw-muted'>No leads yet.</p>";return;}
      var col={"New":"#3b82f6","Contacted":"#f59e0b","Qualified":"#8b5cf6","Won":"#16a34a","Lost":"#94a3b8"};
      document.getElementById('cr_list').innerHTML=leads.map(function(l){
        var opts=self.crmStages.map(function(st){return "<option "+(st===l.stage?"selected":"")+">"+st+"</option>";}).join("");
        return "<div class='bw-lead'><div class='bw-proj-top'><div><b>"+l.name+"</b>"+(l.company?" <span class='bw-muted'>· "+l.company+"</span>":"")+"</div><button class='bw-del' onclick=\"BusinessModule.delLead('"+l.id+"')\">✕</button></div>"
          +"<div class='bw-muted' style='font-size:12px;'>"+(l.value?money(l.value)+" · ":"")+l.source+(l.email?" · "+l.email:"")+"</div>"
          +(l.next_action?"<div style='color:#1d4ed8;font-size:12px;font-weight:700;margin-top:4px;'>▶ "+l.next_action+"</div>":"")
          +"<div style='display:flex;align-items:center;gap:8px;margin-top:6px;'><span style='width:10px;height:10px;border-radius:50%;background:"+(col[l.stage]||'#94a3b8')+";'></span><select class='bw-stagesel' onchange=\"BusinessModule.setStage('"+l.id+"',this.value)\">"+opts+"</select></div></div>";
      }).join("");
    });
  },
  addLead:function(){var self=this;function v(id){var e=document.getElementById(id);return e?e.value:"";}
    if(!v('cr_name')){alert("Enter a lead name.");return;}
    fetch(this.apiBase()+"/api/crm/add",{method:"POST",headers:this.hdr(),body:JSON.stringify({name:v('cr_name'),company:v('cr_company'),email:v('cr_email'),phone:v('cr_phone'),source:v('cr_source'),value:parseFloat(v('cr_value'))||0,next_action:v('cr_action'),stage:"New"})})
      .then(function(r){return r.json();}).then(function(){["cr_name","cr_company","cr_email","cr_phone","cr_value","cr_action"].forEach(function(i){var e=document.getElementById(i);if(e)e.value="";});self.refreshCRM();});},
  setStage:function(id,stage){var self=this;fetch(this.apiBase()+"/api/crm/update-stage",{method:"POST",headers:this.hdr(),body:JSON.stringify({id:id,stage:stage})}).then(function(r){return r.json();}).then(function(){self.refreshCRM();});},
  delLead:function(id){var self=this;if(!confirm("Delete lead?"))return;fetch(this.apiBase()+"/api/crm/delete",{method:"POST",headers:this.hdr(),body:JSON.stringify({id:id})}).then(function(r){return r.json();}).then(function(){self.refreshCRM();});},

  // ---------- MARKETING & SALES ----------
  dealStages:["Lead","Proposal","Negotiation","Won","Lost"],
  channels:["Email","Social Media","Paid Ads","SEO","Events","Referral","Other"],
  renderSales:function(){
    var f="width:100%;padding:10px 12px;border:1px solid #e2e8f0;border-radius:8px;background:#f8fafc;font-size:0.9rem;";
    var stg=this.dealStages.map(function(x){return "<option>"+x+"</option>";}).join("");
    document.getElementById('bw_body').innerHTML=
      '<h2 class="bw-h2">Sales</h2>'
      +'<div id="sal_summary" class="bw-stats" style="grid-template-columns:repeat(4,1fr);"></div>'
      +'<div class="bw-two" style="margin-top:20px;">'
      +'<div class="bw-panel"><h3 class="bw-h3">New Deal</h3>'
      +'<div class="bw-f"><label>Deal name</label><input id="sd_name" style="'+f+'"></div>'
      +'<div class="bw-f"><label>Client</label><input id="sd_client" style="'+f+'"></div>'
      +'<div class="bw-f"><label>Value ($)</label><input id="sd_value" type="number" step="0.01" style="'+f+'"></div>'
      +'<div class="bw-f"><label>\ud83d\udcce Link Estimator quote (optional)</label><select id="sd_quote" style="'+f+'" onchange="BusinessModule.applyQuoteToDeal()"><option value="">— none —</option></select></div>'
      +'<div class="bw-f"><label>Stage</label><select id="sd_stage" style="'+f+'">'+stg+'</select></div>'
      +'<div class="bw-f"><label>Probability % (optional)</label><input id="sd_prob" type="number" min="0" max="100" placeholder="auto from stage" style="'+f+'"></div>'
      +'<div class="bw-f"><label>Expected close</label><input id="sd_close" type="date" style="'+f+'"></div>'
      +'<div class="bw-f"><label>Owner</label><input id="sd_owner" style="'+f+'"></div>'
      +'<details style="margin:6px 0 10px;"><summary style="cursor:pointer;color:#1d4ed8;font-size:.85rem;">Adding an older deal? Set original dates</summary>'
      +'<div class="bw-f" style="margin-top:8px;"><label>Deal started</label><input id="sd_created" type="date" style="'+f+'"></div>'
      +'<div class="bw-f"><label>Entered current stage</label><input id="sd_stagedate" type="date" style="'+f+'"></div></details>'
      +'<button class="bw-add" onclick="BusinessModule.addSalesDeal()">Add Deal</button></div>'
      +'<div class="bw-panel"><h3 class="bw-h3">Pipeline</h3><div id="sd_list"></div></div>'
      +'</div>';
    this.refreshSales();
    this.loadDealQuotes();
  },
  refreshSales:function(){
    var self=this;
    fetch(this.apiBase()+"/api/marketing/list",{headers:this.hdr()}).then(function(r){return r.json();}).then(function(d){
      if(!d.success)return;
      var s=d.summary||{},money=function(n){return "$"+Number(n||0).toLocaleString();};
      document.getElementById('sal_summary').innerHTML=
        "<div class='bw-stat'><span class='bw-stat-l'>Open Pipeline</span><span class='bw-stat-v'>"+money(s.open_value)+"</span></div>"
        +"<div class='bw-stat'><span class='bw-stat-l'>Weighted Pipeline</span><span class='bw-stat-v' style='color:#1d4ed8;'>"+money(s.weighted_pipeline)+"</span></div>"
        +"<div class='bw-stat'><span class='bw-stat-l'>Won Revenue</span><span class='bw-stat-v'>"+money(s.won_value)+"</span></div>"
        +"<div class='bw-stat'><span class='bw-stat-l'>Total Deals</span><span class='bw-stat-v'>"+(s.total_deals||0)+"</span></div>";
      var col={"Lead":"#3b82f6","Qualified":"#0ea5e9","Proposal":"#f59e0b","Negotiation":"#8b5cf6","Won":"#16a34a","Lost":"#94a3b8"};
      var deals=d.deals||[];
      document.getElementById('sd_list').innerHTML = deals.length? deals.map(function(x){
        var opts=self.dealStages.map(function(st){return "<option "+(st===x.stage?"selected":"")+">"+st+"</option>";}).join("");
        var prob=(x.probability!=null?x.probability:0);
        var weighted=(Number(x.value||0)*Number(prob)/100);
        var meta=[];
        if(x.owner)meta.push("\ud83d\udc64 "+x.owner);
        if(x.expected_close)meta.push("\ud83d\udcc5 "+x.expected_close);
        var _sc=x.stage_changed_at||x.created_at||"";
        if(_sc){var _d=Math.floor((Date.now()-new Date(_sc).getTime())/86400000);if(!isNaN(_d)&&_d>=0){var _c=(_d>30?"#dc2626":(_d>14?"#eab308":"#64748b"));meta.push("<span style=\"color:"+_c+";\">\u23f1 "+_d+"d in "+x.stage+"</span>");}}
        return "<div class='bw-lead'><div class='bw-proj-top'><div><b>"+x.name+"</b>"+(x.client?" <span class='bw-muted'>\u00b7 "+x.client+"</span>":"")+"</div><button class='bw-del' onclick=\"BusinessModule.delSalesDeal('"+x.id+"')\">\u2715</button></div>"
          +"<div class='bw-muted' style='font-size:12px;'>"+money(x.value)+" \u00d7 "+prob+"% = <b style='color:#1d4ed8;'>"+money(weighted)+"</b>"+(meta.length?(" \u00b7 "+meta.join(" \u00b7 ")):"")+"</div>"
          +"<div style='display:flex;align-items:center;gap:8px;margin-top:6px;'><span style='width:10px;height:10px;border-radius:50%;background:"+(col[x.stage]||'#94a3b8')+";'></span><select class='bw-stagesel' onchange=\"BusinessModule.setSalesStage('"+x.id+"',this.value)\">"+opts+"</select></div>"+BusinessModule.salesActivityBlock(x)+"</div>";
      }).join("") : "<p class='bw-muted'>No deals yet. Add your first deal above.</p>";
    });
  },
  salesActivityBlock:function(x){
    var out="";
    if(x.quote_title){ out+="<div style='margin-top:6px;font-size:11px;color:#1d4ed8;'>\ud83d\udcce From quote: "+x.quote_title+"</div>"; }
    // next-action / overdue flag
    var na=(x.next_action||""), nad=(x.next_action_date||"");
    if(na){
      var overdue=false;
      if(nad){var _t=new Date(nad+"T00:00:00");var _n=new Date();_n.setHours(0,0,0,0);overdue=(_t<_n);}
      var c=overdue?"#dc2626":"#0f766e";
      out+="<div style='margin-top:8px;font-size:12px;color:"+c+";font-weight:600;'>"+(overdue?"\ud83d\udd34 OVERDUE: ":"\u27a1 Next: ")+x.next_action+(nad?(" (by "+nad+")"):"")+"</div>";
    } else {
      out+="<div style='margin-top:8px;font-size:12px;color:#94a3b8;'>\u26a0 No next step set</div>";
    }
    // last activity
    if(x.last_activity_at){
      var la=new Date(x.last_activity_at); if(!isNaN(la)){var days=Math.floor((Date.now()-la.getTime())/86400000); out+="<div style='font-size:11px;color:#94a3b8;'>Last activity "+days+"d ago</div>";}
    }
    // expandable log + add form
    var acts=(x.activities||[]);
    var log=acts.length? acts.slice().reverse().map(function(a){var t=new Date(a.at);var ds=isNaN(t)?"":(t.toLocaleDateString());return "<div style='font-size:11px;color:#475569;border-left:2px solid #e2e8f0;padding:2px 0 2px 8px;margin:3px 0;'><b>"+(a.type||"Note")+"</b> "+(a.note||"")+" <span style='color:#94a3b8;'>"+ds+"</span></div>";}).join("") : "<div style='font-size:11px;color:#94a3b8;'>No activity yet.</div>";
    out+="<details style='margin-top:8px;'><summary style='cursor:pointer;color:#1d4ed8;font-size:12px;'>Activity &amp; follow-up</summary>"
      +"<div style='margin-top:8px;'>"+log+"</div>"
      +"<div style='margin-top:8px;display:flex;gap:6px;flex-wrap:wrap;'>"
      +"<select id='act_type_"+x.id+"' style='padding:5px;border:1px solid #e2e8f0;border-radius:6px;font-size:12px;'><option>Call</option><option>Email</option><option>Meeting</option><option>Note</option></select>"
      +"<input id='act_note_"+x.id+"' placeholder='What happened?' style='flex:1;min-width:120px;padding:5px;border:1px solid #e2e8f0;border-radius:6px;font-size:12px;'>"
      +"<button class='bw-btn' style='font-size:12px;padding:5px 10px;' onclick=\"BusinessModule.logActivity('"+x.id+"')\">Log</button></div>"
      +"<div style='margin-top:8px;display:flex;gap:6px;flex-wrap:wrap;align-items:center;'>"
      +"<input id='na_text_"+x.id+"' value=\""+(na.replace(/\"/g,'&quot;'))+"\" placeholder='Next step...' style='flex:1;min-width:120px;padding:5px;border:1px solid #e2e8f0;border-radius:6px;font-size:12px;'>"
      +"<input id='na_date_"+x.id+"' type='date' value='"+nad+"' style='padding:5px;border:1px solid #e2e8f0;border-radius:6px;font-size:12px;'>"
      +"<button class='bw-btn' style='font-size:12px;padding:5px 10px;' onclick=\"BusinessModule.setNextAction('"+x.id+"')\">Set</button></div>"
      +"</details>";
    return out;
  },
  logActivity:function(id){
    var self=this;
    var t=(document.getElementById('act_type_'+id)||{}).value||"Note";
    var n=(document.getElementById('act_note_'+id)||{}).value||"";
    if(!n){alert("Add a short note.");return;}
    fetch(this.apiBase()+"/api/marketing/deal-activity",{method:"POST",headers:this.hdr(),body:JSON.stringify({id:id,activity_type:t,activity_note:n})}).then(function(r){return r.json();}).then(function(){self.refreshSales();});
  },
  setNextAction:function(id){
    var self=this;
    var t=(document.getElementById('na_text_'+id)||{}).value||"";
    var d=(document.getElementById('na_date_'+id)||{}).value||"";
    fetch(this.apiBase()+"/api/marketing/deal-activity",{method:"POST",headers:this.hdr(),body:JSON.stringify({id:id,next_action:t,next_action_date:d})}).then(function(r){return r.json();}).then(function(){self.refreshSales();});
  },
  _dealQuotes:[],
  loadDealQuotes:function(){
    var self=this;
    fetch(this.apiBase()+"/api/estimate/history",{headers:this.hdr()}).then(function(r){return r.json();}).then(function(d){
      self._dealQuotes=(d&&d.quotes)?d.quotes:[];
      var sel=document.getElementById('sd_quote'); if(!sel)return;
      var opts='<option value="">\u2014 none \u2014</option>';
      self._dealQuotes.forEach(function(q){
        var lbl=q.title+" \u00b7 $"+Math.round(q.total||0).toLocaleString()+((q.created_at||'').split('T')[0]?(" \u00b7 "+(q.created_at||'').split('T')[0]):"");
        opts+='<option value="'+q.index+'">'+lbl+'</option>';
      });
      sel.innerHTML=opts;
    }).catch(function(){});
  },
  applyQuoteToDeal:function(){
    var sel=document.getElementById('sd_quote'); if(!sel)return;
    var idx=sel.value; if(idx==='')return;
    var q=(this._dealQuotes||[]).filter(function(x){return String(x.index)===String(idx);})[0];
    if(!q)return;
    var nm=document.getElementById('sd_name'); if(nm && !nm.value){ nm.value=q.title||''; }
    var val=document.getElementById('sd_value'); if(val){ val.value=Math.round(q.total||0); }
  },
  addSalesDeal:function(){var self=this;function v(i){var e=document.getElementById(i);return e?e.value:"";}
    if(!v('sd_name')){alert("Enter a deal name.");return;}
    fetch(this.apiBase()+"/api/marketing/add-deal",{method:"POST",headers:this.hdr(),body:JSON.stringify({name:v('sd_name'),client:v('sd_client'),value:parseFloat(v('sd_value'))||0,stage:v('sd_stage')||"Lead",probability:v('sd_prob'),expected_close:v('sd_close'),owner:v('sd_owner'),created_override:v('sd_created'),stage_changed_override:v('sd_stagedate'),quote_index:v('sd_quote'),quote_title:(function(){var s=document.getElementById('sd_quote');return (s&&s.selectedIndex>0)?s.options[s.selectedIndex].text:'';})()})}).then(function(r){return r.json();}).then(function(){["sd_name","sd_client","sd_value","sd_prob","sd_close","sd_owner","sd_created","sd_stagedate"].forEach(function(i){var e=document.getElementById(i);if(e)e.value="";});self.refreshSales();});},
  setSalesStage:function(id,st){var self=this;fetch(this.apiBase()+"/api/marketing/update-deal",{method:"POST",headers:this.hdr(),body:JSON.stringify({id:id,stage:st})}).then(function(r){return r.json();}).then(function(){self.refreshSales();});},
  delSalesDeal:function(id){var self=this;if(!confirm("Delete deal?"))return;fetch(this.apiBase()+"/api/marketing/delete-deal",{method:"POST",headers:this.hdr(),body:JSON.stringify({id:id})}).then(function(r){return r.json();}).then(function(){self.refreshSales();});},
  renderMarketing:function(){
    var f="width:100%;padding:10px 12px;border:1px solid #e2e8f0;border-radius:8px;background:#f8fafc;font-size:0.9rem;";
    var stg=this.dealStages.map(function(x){return "<option>"+x+"</option>";}).join("");
    var ch=this.channels.map(function(x){return "<option>"+x+"</option>";}).join("");
    document.getElementById('bw_body').innerHTML=
      '<h2 class="bw-h2">Marketing</h2>'
      +'<div id="mkt_summary" class="bw-stats" style="grid-template-columns:repeat(4,1fr);"></div>'
      +'<div class="bw-two" style="margin-top:20px;">'
      +'<div class="bw-panel"><h3 class="bw-h3">New Campaign</h3>'
      +'<div class="bw-f"><label>Campaign name</label><input id="cp_name" style="'+f+'"></div>'
      +'<div class="bw-f"><label>Channel</label><select id="cp_channel" style="'+f+'">'+ch+'</select></div>'
      +'<div class="bw-f"><label>Budget ($)</label><input id="cp_budget" type="number" step="0.01" style="'+f+'"></div>'
      +'<div class="bw-f"><label>Spend so far ($)</label><input id="cp_spend" type="number" step="0.01" style="'+f+'"></div>'
      +'<div class="bw-f"><label>Leads generated</label><input id="cp_leads" type="number" step="1" style="'+f+'"></div>'
      +'<div class="bw-f"><label>Start date</label><input id="cp_start" type="date" style="'+f+'"></div>'
      +'<div class="bw-f"><label>End date</label><input id="cp_end" type="date" style="'+f+'"></div>'
      +'<button class="bw-add" onclick="BusinessModule.addCampaign()">Add Campaign</button></div>'
      +'<div class="bw-panel"><h3 class="bw-h3">Campaigns</h3><div id="cp_list"></div></div>'
      +'</div>';
    this.refreshMarketing();
  },
  refreshMarketing:function(){
    var self=this;
    fetch(this.apiBase()+"/api/marketing/list",{headers:this.hdr()}).then(function(r){return r.json();}).then(function(d){
      if(!d.success)return;
      var s=d.summary||{},money=function(n){return "$"+Number(n||0).toLocaleString();};
      document.getElementById('mkt_summary').innerHTML=
        "<div class='bw-stat'><span class='bw-stat-l'>Total Budget</span><span class='bw-stat-v'>"+money(s.total_budget)+"</span></div>"
        +"<div class='bw-stat'><span class='bw-stat-l'>Total Spend</span><span class='bw-stat-v' style='color:#dc2626;'>"+money(s.total_spend)+"</span></div>"
        +"<div class='bw-stat'><span class='bw-stat-l'>Leads</span><span class='bw-stat-v'>"+(s.total_leads||0)+"</span></div>"
        +"<div class='bw-stat'><span class='bw-stat-l'>Cost / Lead</span><span class='bw-stat-v' style='color:#1d4ed8;'>"+money(s.cost_per_lead)+"</span></div>";
      var col={"Lead":"#3b82f6","Proposal":"#f59e0b","Negotiation":"#8b5cf6","Won":"#16a34a","Lost":"#94a3b8"};
      var deals=d.deals||[];
      document.getElementById('dl_list').innerHTML = deals.length? deals.map(function(x){
        var opts=self.dealStages.map(function(st){return "<option "+(st===x.stage?"selected":"")+">"+st+"</option>";}).join("");
        return "<div class='bw-lead'><div class='bw-proj-top'><div><b>"+x.name+"</b>"+(x.client?" <span class='bw-muted'>· "+x.client+"</span>":"")+"</div><button class='bw-del' onclick=\"BusinessModule.delDeal('"+x.id+"')\">✕</button></div>"
          +"<div class='bw-muted' style='font-size:12px;'>"+money(x.value)+"</div>"
          +"<div style='display:flex;align-items:center;gap:8px;margin-top:6px;'><span style='width:10px;height:10px;border-radius:50%;background:"+(col[x.stage]||'#94a3b8')+";'></span><select class='bw-stagesel' onchange=\"BusinessModule.setDealStage('"+x.id+"',this.value)\">"+opts+"</select></div></div>";
      }).join("") : "<p class='bw-muted'>No deals yet.</p>";
      var camps=d.campaigns||[];
      document.getElementById('cp_list').innerHTML = camps.length? camps.map(function(c){
        return "<div class='bw-lead'><div class='bw-proj-top'><div><b>"+c.name+"</b> <span class='bw-muted'>· "+c.channel+"</span></div><button class='bw-del' onclick=\"BusinessModule.delCampaign('"+c.id+"')\">✕</button></div><div class='bw-muted' style='font-size:12px;margin:2px 0;'>Spent "+money(c.spend||0)+" / "+money(c.budget||0)+" · "+(+c.leads||0)+" leads · CPL "+money((+c.leads>0)?((+(c.spend||0))/(+c.leads)):0)+" · "+c.status+"</div><div style='background:#e5e7eb;border-radius:6px;height:8px;overflow:hidden;margin:2px 0;'><div style='height:8px;width:"+((+c.budget>0)?Math.min(100,Math.round((+(c.spend||0))/(+c.budget)*100)):0)+"%;background:"+(((+(c.spend||0))>(+c.budget)&&(+c.budget>0))?'#dc2626':'#1d4ed8')+";'></div></div><div style='display:flex;gap:6px;margin-top:6px;'><input id='cs_amt_"+c.id+"' type='number' step='0.01' placeholder='Add spend' style='flex:1;padding:4px;font-size:12px;'><button class='bw-del' style='background:#1d4ed8;color:#fff;' onclick=\"BusinessModule.addCampaignSpend('"+c.id+"')\">Log</button></div></div>";
      }).join("") : "<p class='bw-muted'>No campaigns yet.</p>";
    });
  },
  addDeal:function(){var self=this;function v(i){var e=document.getElementById(i);return e?e.value:"";}
    if(!v('dl_name')){alert("Enter a deal name.");return;}
    fetch(this.apiBase()+"/api/marketing/add-deal",{method:"POST",headers:this.hdr(),body:JSON.stringify({name:v('dl_name'),client:v('dl_client'),value:parseFloat(v('dl_value'))||0,stage:"Lead"})}).then(function(r){return r.json();}).then(function(){["dl_name","dl_client","dl_value"].forEach(function(i){var e=document.getElementById(i);if(e)e.value="";});self.refreshMarketing();});},
  setDealStage:function(id,st){var self=this;fetch(this.apiBase()+"/api/marketing/update-deal",{method:"POST",headers:this.hdr(),body:JSON.stringify({id:id,stage:st})}).then(function(r){return r.json();}).then(function(){self.refreshMarketing();});},
  delDeal:function(id){var self=this;if(!confirm("Delete deal?"))return;fetch(this.apiBase()+"/api/marketing/delete-deal",{method:"POST",headers:this.hdr(),body:JSON.stringify({id:id})}).then(function(r){return r.json();}).then(function(){self.refreshMarketing();});},
  updateCampaign:function(id){var self=this;
    var amt=(document.getElementById('cs_amt_'+id)||{}).value||"";
    var lds=(document.getElementById('cl_amt_'+id)||{}).value||"";
    var body={id:id};
    if(amt!=="")body.add_spend=parseFloat(amt)||0;
    if(lds!=="")body.leads=parseInt(lds)||0;
    fetch(this.apiBase()+"/api/marketing/campaign-update",{method:"POST",headers:this.hdr(),body:JSON.stringify(body)}).then(function(r){return r.json();}).then(function(){self.refreshMarketing();});},
  addCampaignSpend:function(id){var self=this;var el=document.getElementById('cs_amt_'+id);var amt=parseFloat(el&&el.value)||0;if(amt<=0){alert('Enter a spend amount.');return;}fetch(this.apiBase()+"/api/marketing/campaign-update",{method:"POST",headers:this.hdr(),body:JSON.stringify({id:id,add_spend:amt})}).then(function(r){return r.json();}).then(function(){if(el)el.value="";self.refreshMarketing();});},
  addCampaign:function(){var self=this;function v(i){var e=document.getElementById(i);return e?e.value:"";}
    if(!v('cp_name')){alert("Enter a campaign name.");return;}
    fetch(this.apiBase()+"/api/marketing/add-campaign",{method:"POST",headers:this.hdr(),body:JSON.stringify({name:v('cp_name'),channel:v('cp_channel'),budget:parseFloat(v('cp_budget'))||0,spend:parseFloat(v('cp_spend'))||0,leads:parseInt(v('cp_leads'))||0,start_date:v('cp_start'),end_date:v('cp_end'),status:"Active"})}).then(function(r){return r.json();}).then(function(){["cp_name","cp_budget","cp_spend","cp_leads","cp_start","cp_end"].forEach(function(i){var e=document.getElementById(i);if(e)e.value="";});self.refreshMarketing();});},
  delCampaign:function(id){var self=this;if(!confirm("Delete campaign?"))return;fetch(this.apiBase()+"/api/marketing/delete-campaign",{method:"POST",headers:this.hdr(),body:JSON.stringify({id:id})}).then(function(r){return r.json();}).then(function(){self.refreshMarketing();});},

  // ---------- HR ----------
  renderHR:function(){
    var f="width:100%;padding:10px 12px;border:1px solid #e2e8f0;border-radius:8px;background:#f8fafc;font-size:0.9rem;";
    document.getElementById('bw_body').innerHTML=
      '<h2 class="bw-h2">HR</h2>'
      +'<div id="hr_summary" class="bw-stats"></div>'
      +'<div class="bw-two" style="margin-top:20px;">'
      +'<div class="bw-panel"><h3 class="bw-h3">Add Team Member</h3>'
      +'<div class="bw-f"><label>Name</label><input id="hr_name" style="'+f+'"></div>'
      +'<div class="bw-f"><label>Role / Title</label><input id="hr_role" style="'+f+'"></div>'
      +'<div class="bw-f"><label>Email</label><input id="hr_email" style="'+f+'"></div>'
      +'<div class="bw-f"><label>Phone</label><input id="hr_phone" style="'+f+'"></div>'
      +'<div class="bw-f"><label>Start date</label><input id="hr_start" type="date" style="'+f+'"></div>'
      +'<button class="bw-add" onclick="BusinessModule.addEmployee()">Add Member</button></div>'
      +'<div class="bw-panel"><h3 class="bw-h3">Team</h3><div id="hr_list"></div></div>'
      +'</div>';
    this.refreshHR();
  },
  refreshHR:function(){
    var self=this;
    fetch(this.apiBase()+"/api/hr/list",{headers:this.hdr()}).then(function(r){return r.json();}).then(function(d){
      if(!d.success)return;
      var s=d.summary||{};
      document.getElementById('hr_summary').innerHTML=
        "<div class='bw-stat'><span class='bw-stat-l'>Team Size</span><span class='bw-stat-v'>"+(s.total||0)+"</span></div>"
        +"<div class='bw-stat'><span class='bw-stat-l'>Active</span><span class='bw-stat-v'>"+(s.active||0)+"</span></div>"
        +"<div class='bw-stat'><span class='bw-stat-l'>On Leave</span><span class='bw-stat-v'>"+(s.on_leave||0)+"</span></div>";
      var emps=d.employees||[];
      var col={"Active":"#16a34a","On Leave":"#f59e0b","Inactive":"#94a3b8"};
      document.getElementById('hr_list').innerHTML = emps.length? emps.map(function(e){
        var opts=["Active","On Leave","Inactive"].map(function(st){return "<option "+(st===e.status?"selected":"")+">"+st+"</option>";}).join("");
        return "<div class='bw-lead'><div class='bw-proj-top'><div><b>"+e.name+"</b>"+(e.role?" <span class='bw-muted'>· "+e.role+"</span>":"")+"</div><button class='bw-del' onclick=\"BusinessModule.delEmployee('"+e.id+"')\">✕</button></div>"
          +"<div class='bw-muted' style='font-size:12px;'>"+(e.email||"")+(e.phone?" · "+e.phone:"")+(e.start_date?" · since "+e.start_date:"")+"</div>"
          +"<div style='display:flex;align-items:center;gap:8px;margin-top:6px;'><span style='width:10px;height:10px;border-radius:50%;background:"+(col[e.status]||'#94a3b8')+";'></span><select class='bw-stagesel' onchange=\"BusinessModule.setEmpStatus('"+e.id+"',this.value)\">"+opts+"</select></div></div>";
      }).join("") : "<p class='bw-muted'>No team members yet.</p>";
    });
  },
  addEmployee:function(){var self=this;function v(i){var e=document.getElementById(i);return e?e.value:"";}
    if(!v('hr_name')){alert("Enter a name.");return;}
    fetch(this.apiBase()+"/api/hr/add",{method:"POST",headers:this.hdr(),body:JSON.stringify({name:v('hr_name'),role:v('hr_role'),email:v('hr_email'),phone:v('hr_phone'),start_date:v('hr_start'),status:"Active"})}).then(function(r){return r.json();}).then(function(){["hr_name","hr_role","hr_email","hr_phone"].forEach(function(i){var e=document.getElementById(i);if(e)e.value="";});self.refreshHR();});},
  setEmpStatus:function(id,st){var self=this;fetch(this.apiBase()+"/api/hr/update-status",{method:"POST",headers:this.hdr(),body:JSON.stringify({id:id,status:st})}).then(function(r){return r.json();}).then(function(){self.refreshHR();});},
  delEmployee:function(id){var self=this;if(!confirm("Remove team member?"))return;fetch(this.apiBase()+"/api/hr/delete",{method:"POST",headers:this.hdr(),body:JSON.stringify({id:id})}).then(function(r){return r.json();}).then(function(){self.refreshHR();});},

  // ---------- PLACEHOLDER (Marketing / HR) ----------
  renderPlaceholder:function(title,desc){
    document.getElementById('bw_body').innerHTML=
      '<h2 class="bw-h2">'+title+'</h2>'
      +'<div class="bw-soon"><div class="bw-soon-badge">COMING SOON</div>'
      +'<p class="bw-muted">'+desc+'</p>'
      +'<p class="bw-muted" style="font-size:13px;">This section is in active development and will be available soon.</p></div>';
  },

  styles:function(){
    return "<style>"
    +".bw-shell{display:grid;grid-template-columns:230px 1fr;gap:0;min-height:calc(100vh - 62px);background:#f8fafc;}"
    +".bw-menu{background:#0b1220;padding:24px 14px;display:flex;flex-direction:column;gap:3px;}"
    +".bw-brand{color:#fff;font-weight:900;font-size:1.05rem;padding:6px 14px 20px;letter-spacing:-0.02em;border-bottom:1px solid rgba(255,255,255,0.08);margin-bottom:10px;}"
    +".bw-nav{display:block;padding:11px 14px;border-radius:9px;color:#cbd5e1;font-weight:700;font-size:0.9rem;cursor:pointer;transition:.15s;}"
    +".bw-nav:hover{background:rgba(255,255,255,0.06);color:#fff;}"
    +".bw-nav-on{background:#1d4ed8 !important;color:#fff !important;}.bw-nav{color:#cbd5e1 !important;background:transparent;}"
    +".bw-main{background:#f8fafc;padding:36px 40px;overflow-y:auto;}"
    +".bw-h2{margin:0 0 24px;font-size:1.7rem;font-weight:900;color:#090d16;letter-spacing:-0.03em;}"
    +".bw-h3{font-size:1rem;font-weight:800;color:#0f172a;margin:0 0 12px;}"
    +".bw-muted{color:#94a3b8;}"
    +".bw-stats{display:grid;grid-template-columns:repeat(3,1fr);gap:12px;}"
    +".bw-stat{background:#f8fafc;border:1px solid #e2e8f0;border-radius:12px;padding:16px;text-align:center;}"
    +".bw-stat-l{display:block;font-size:11px;color:#64748b;font-weight:700;text-transform:uppercase;}"
    +".bw-stat-v{display:block;font-size:1.4rem;font-weight:900;color:#090d16;margin-top:4px;}"
    +".bw-quick{display:flex;gap:10px;margin-top:18px;}"
    +".bw-qbtn{padding:10px 16px !important;border:1px solid #1d4ed8 !important;background:#fff !important;color:#1d4ed8 !important;border-radius:9px !important;font-weight:700 !important;cursor:pointer !important;}"
    +".bw-two{display:grid;grid-template-columns:0.9fr 1.2fr;gap:18px;align-items:start;}"
    +".bw-panel{background:#fff;border:1px solid #e2e8f0;border-radius:12px;padding:18px;}"
    +".bw-f{margin-bottom:10px;}.bw-f label{display:block;font-size:0.72rem;font-weight:800;color:#0f172a;margin-bottom:4px;text-transform:uppercase;}"
    +".bw-add{width:100% !important;padding:11px !important;border:none !important;border-radius:9px !important;background:#1d4ed8 !important;color:#fff !important;font-weight:800 !important;cursor:pointer !important;}"
    +".bw-proj,.bw-lead{border:1px solid #e2e8f0;border-radius:10px;padding:12px;margin-bottom:10px;}"
    +".bw-proj-top{display:flex;justify-content:space-between;align-items:center;}"
    +".bw-badge{color:#fff;font-size:10px;font-weight:800;padding:2px 7px;border-radius:999px;margin-left:6px;}"
    +".bw-task{padding:2px 0;font-size:13px;color:#334155;}"
    +".bw-taskadd{display:flex;gap:6px;margin-top:8px;}"
    +".bw-ti{flex:1;padding:6px 9px;border:1px solid #e2e8f0;border-radius:7px;background:#f8fafc;font-size:12px;}"
    +".bw-tbtn{background:#1d4ed8 !important;color:#fff !important;border:none;border-radius:7px;width:32px;font-weight:900;cursor:pointer;}"
    +".bw-del{background:#fff !important;border:1px solid #fecaca !important;color:#dc2626 !important;border-radius:6px;width:24px;height:24px;cursor:pointer;font-weight:700;}"
    +".bw-listhead{display:flex;justify-content:space-between;align-items:center;margin-bottom:10px;}"
    +".bw-filter{padding:6px 9px;border:1px solid #e2e8f0;border-radius:7px;background:#f8fafc;font-size:12px;}"
    +".bw-stagesel{padding:4px 7px;border:1px solid #e2e8f0;border-radius:6px;background:#f8fafc;font-size:12px;font-weight:700;}"
    +".bw-soon{text-align:center;padding:50px 20px;background:#f8fafc;border:1px dashed #cbd5e1;border-radius:14px;}"
    +".bw-soon-badge{display:inline-block;background:#fffbeb;color:#b45309;border:1px solid #fde68a;font-size:11px;font-weight:800;padding:5px 12px;border-radius:999px;margin-bottom:12px;}"
    +"@media(max-width:820px){.bw-shell{grid-template-columns:1fr;}.bw-two{grid-template-columns:1fr;}.bw-stats{grid-template-columns:repeat(2,1fr);}}"
    +"</style>";
  }
};
window.BusinessModule = BusinessModule;
