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
      + '    <a class="bw-nav" data-s="marketing" onclick="BusinessModule.go(\'marketing\')">📣 Marketing &amp; Sales</a>'
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
  renderMarketing:function(){
    var f="width:100%;padding:10px 12px;border:1px solid #e2e8f0;border-radius:8px;background:#f8fafc;font-size:0.9rem;";
    var stg=this.dealStages.map(function(x){return "<option>"+x+"</option>";}).join("");
    var ch=this.channels.map(function(x){return "<option>"+x+"</option>";}).join("");
    document.getElementById('bw_body').innerHTML=
      '<h2 class="bw-h2">Marketing & Sales</h2>'
      +'<div id="mkt_summary" class="bw-stats" style="grid-template-columns:repeat(4,1fr);"></div>'
      +'<div class="bw-two" style="margin-top:20px;">'
      +'<div class="bw-panel"><h3 class="bw-h3">New Deal</h3>'
      +'<div class="bw-f"><label>Deal name</label><input id="dl_name" style="'+f+'"></div>'
      +'<div class="bw-f"><label>Client</label><input id="dl_client" style="'+f+'"></div>'
      +'<div class="bw-f"><label>Value ($)</label><input id="dl_value" type="number" step="0.01" style="'+f+'"></div>'
      +'<button class="bw-add" onclick="BusinessModule.addDeal()">Add Deal</button>'
      +'<h3 class="bw-h3" style="margin-top:20px;">New Campaign</h3>'
      +'<div class="bw-f"><label>Campaign name</label><input id="cp_name" style="'+f+'"></div>'
      +'<div class="bw-f"><label>Channel</label><select id="cp_channel" style="'+f+'">'+ch+'</select></div>'
      +'<div class="bw-f"><label>Budget ($)</label><input id="cp_budget" type="number" step="0.01" style="'+f+'"></div>'
      +'<button class="bw-add" onclick="BusinessModule.addCampaign()">Add Campaign</button></div>'
      +'<div class="bw-panel"><h3 class="bw-h3">Deal Pipeline</h3><div id="dl_list"></div>'
      +'<h3 class="bw-h3" style="margin-top:20px;">Campaigns</h3><div id="cp_list"></div></div>'
      +'</div>';
    this.refreshMarketing();
  },
  refreshMarketing:function(){
    var self=this;
    fetch(this.apiBase()+"/api/marketing/list",{headers:this.hdr()}).then(function(r){return r.json();}).then(function(d){
      if(!d.success)return;
      var s=d.summary||{},money=function(n){return "$"+Number(n||0).toLocaleString();};
      document.getElementById('mkt_summary').innerHTML=
        "<div class='bw-stat'><span class='bw-stat-l'>Open Pipeline</span><span class='bw-stat-v'>"+money(s.open_value)+"</span></div>"
        +"<div class='bw-stat'><span class='bw-stat-l'>Won Revenue</span><span class='bw-stat-v'>"+money(s.won_value)+"</span></div>"
        +"<div class='bw-stat'><span class='bw-stat-l'>Total Deals</span><span class='bw-stat-v'>"+(s.total_deals||0)+"</span></div>"
        +"<div class='bw-stat'><span class='bw-stat-l'>Active Campaigns</span><span class='bw-stat-v'>"+(s.active_campaigns||0)+"</span></div>";
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
        return "<div class='bw-lead'><div class='bw-proj-top'><div><b>"+c.name+"</b> <span class='bw-muted'>· "+c.channel+"</span></div><button class='bw-del' onclick=\"BusinessModule.delCampaign('"+c.id+"')\">✕</button></div><div class='bw-muted' style='font-size:12px;'>Budget "+money(c.budget)+" · "+c.status+"</div></div>";
      }).join("") : "<p class='bw-muted'>No campaigns yet.</p>";
    });
  },
  addDeal:function(){var self=this;function v(i){var e=document.getElementById(i);return e?e.value:"";}
    if(!v('dl_name')){alert("Enter a deal name.");return;}
    fetch(this.apiBase()+"/api/marketing/add-deal",{method:"POST",headers:this.hdr(),body:JSON.stringify({name:v('dl_name'),client:v('dl_client'),value:parseFloat(v('dl_value'))||0,stage:"Lead"})}).then(function(r){return r.json();}).then(function(){["dl_name","dl_client","dl_value"].forEach(function(i){var e=document.getElementById(i);if(e)e.value="";});self.refreshMarketing();});},
  setDealStage:function(id,st){var self=this;fetch(this.apiBase()+"/api/marketing/update-deal",{method:"POST",headers:this.hdr(),body:JSON.stringify({id:id,stage:st})}).then(function(r){return r.json();}).then(function(){self.refreshMarketing();});},
  delDeal:function(id){var self=this;if(!confirm("Delete deal?"))return;fetch(this.apiBase()+"/api/marketing/delete-deal",{method:"POST",headers:this.hdr(),body:JSON.stringify({id:id})}).then(function(r){return r.json();}).then(function(){self.refreshMarketing();});},
  addCampaign:function(){var self=this;function v(i){var e=document.getElementById(i);return e?e.value:"";}
    if(!v('cp_name')){alert("Enter a campaign name.");return;}
    fetch(this.apiBase()+"/api/marketing/add-campaign",{method:"POST",headers:this.hdr(),body:JSON.stringify({name:v('cp_name'),channel:v('cp_channel'),budget:parseFloat(v('cp_budget'))||0,status:"Active"})}).then(function(r){return r.json();}).then(function(){["cp_name","cp_budget"].forEach(function(i){var e=document.getElementById(i);if(e)e.value="";});self.refreshMarketing();});},
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
