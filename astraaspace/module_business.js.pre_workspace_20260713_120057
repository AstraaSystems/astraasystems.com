// Astraa Business — projects + tasks (industry-agnostic Operations) MVP
var BusinessModule = {
  apiBase:function(){return (typeof ASTRAA_API_BASE!=='undefined')?ASTRAA_API_BASE:"https://family-speed-outcome.ngrok-free.dev";},
  session:function(){try{return JSON.parse(localStorage.getItem('astraa_session')||'{}');}catch(e){return {};}},
  hdr:function(){return {"Content-Type":"application/json","Authorization":"Bearer "+(this.session().token||""),"ngrok-skip-browser-warning":"true"};},

  render:function(){
    var f="width:100%;padding:11px 13px;border:1px solid #e2e8f0;border-radius:8px;background:#f8fafc;color:#0f172a;font-size:0.95rem;";
    return this.styles()
      + '<div class="bz-wrap">'
      + '  <div class="bz-head"><h2 class="bz-title">Astraa Business</h2><p class="bz-sub">Manage projects, teams, and tasks — for any business.</p></div>'
      + '  <div id="bz_summary" class="bz-stats"></div>'
      + '  <div class="bz-grid">'
      + '    <div class="bz-card">'
      + '      <h3 class="bz-h3">New Project</h3>'
      + '      <div class="bz-field"><label>Project name</label><input id="bz_name" style="'+f+'" placeholder="e.g. Q3 Client Onboarding"></div>'
      + '      <div class="bz-field"><label>Client / Contact</label><input id="bz_client" style="'+f+'" placeholder="Client or account name"></div>'
      + '      <div class="bz-field"><label>Status</label><select id="bz_status" style="'+f+'"><option>Active</option><option>On Hold</option><option>Complete</option></select></div>'
      + '      <div class="bz-field"><label>Start date</label><input id="bz_start" type="date" style="'+f+'"></div>'
      + '      <div class="bz-field"><label>Due date</label><input id="bz_due" type="date" style="'+f+'"></div>'
      + '      <div class="bz-field"><label>Value ($) (optional)</label><input id="bz_value" type="number" step="0.01" style="'+f+'" placeholder="0.00"></div>'
      + '      <button class="bz-add" onclick="BusinessModule.addProject()">Add Project</button>'
      + '    </div>'
      + '    <div class="bz-card"><h3 class="bz-h3">Projects</h3><div id="bz_list"></div></div>'
      + '  </div>'
      + '</div>';
  },

  load:function(){
    var s=document.getElementById('bz_start'); if(s)s.value=new Date().toISOString().slice(0,10);
    this.refresh();
  },

  refresh:function(){
    var self=this;
    fetch(this.apiBase()+"/api/business/list",{headers:this.hdr()})
      .then(function(r){return r.json();}).then(function(d){
        if(!d.success){document.getElementById('bz_list').innerHTML="<p style='color:#dc2626;'>"+(d.error||'Error')+"</p>";return;}
        var s=d.summary||{};
        var money=function(n){return "$"+Number(n||0).toLocaleString();};
        document.getElementById('bz_summary').innerHTML=
          "<div class='bz-stat'><span class='bz-stat-l'>Projects</span><span class='bz-stat-v'>"+(s.total_projects||0)+"</span></div>"
          +"<div class='bz-stat'><span class='bz-stat-l'>Active</span><span class='bz-stat-v'>"+(s.active||0)+"</span></div>"
          +"<div class='bz-stat'><span class='bz-stat-l'>Open tasks</span><span class='bz-stat-v'>"+(s.pending_tasks||0)+"</span></div>"
          +"<div class='bz-stat'><span class='bz-stat-l'>Total value</span><span class='bz-stat-v'>"+money(s.total_value)+"</span></div>";
        var projects=d.projects||[];
        if(!projects.length){document.getElementById('bz_list').innerHTML="<p style='color:#94a3b8;'>No projects yet. Create one on the left.</p>";return;}
        document.getElementById('bz_list').innerHTML=projects.map(function(p){
          var badge={"Active":"#16a34a","On Hold":"#f59e0b","Complete":"#64748b"}[p.status]||"#64748b";
          var tasks=(p.tasks||[]).map(function(t){
            var done=t.status==="Done";
            return "<div class='bz-task'><label style='display:flex;gap:8px;align-items:center;cursor:pointer;"+(done?"text-decoration:line-through;color:#94a3b8;":"")+"'>"
              +"<input type='checkbox' "+(done?"checked":"")+" onchange=\"BusinessModule.toggleTask('"+p.id+"','"+t.id+"')\">"
              +t.title+(t.assignee?" · "+t.assignee:"")+(t.due_date?" · due "+t.due_date:"")+"</label></div>";
          }).join("");
          return "<div class='bz-proj'>"
            +"<div class='bz-proj-top'><div><span class='bz-proj-name'>"+p.name+"</span> <span class='bz-badge' style='background:"+badge+"'>"+p.status+"</span></div>"
            +"<button class='bz-del' onclick=\"BusinessModule.delProject('"+p.id+"')\">✕</button></div>"
            +"<div class='bz-proj-sub'>"+(p.client?p.client+" · ":"")+(p.value?money(p.value)+" · ":"")+(p.due_date?"due "+p.due_date:"")+"</div>"
            +"<div class='bz-tasks'>"+tasks+"</div>"
            +"<div class='bz-taskadd'><input id='task_"+p.id+"' placeholder='Add task…' class='bz-taskinput'>"
            +"<input id='asg_"+p.id+"' placeholder='Assigned to' class='bz-taskinput' style='max-width:130px;'>"
            +"<button class='bz-taskbtn' onclick=\"BusinessModule.addTask('"+p.id+"')\">+</button></div>"
            +"</div>";
        }).join("");
      }).catch(function(){document.getElementById('bz_list').innerHTML="<p style='color:#dc2626;'>Connection error.</p>";});
  },

  addProject:function(){
    var self=this;
    function v(id){var e=document.getElementById(id);return e?e.value:"";}
    if(!v('bz_name')){alert("Enter a project name.");return;}
    var body={name:v('bz_name'),client:v('bz_client'),status:v('bz_status'),start_date:v('bz_start'),due_date:v('bz_due'),value:parseFloat(v('bz_value'))||0};
    fetch(this.apiBase()+"/api/business/add-project",{method:"POST",headers:this.hdr(),body:JSON.stringify(body)})
      .then(function(r){return r.json();}).then(function(d){
        if(!d.success){alert(d.error||"Failed.");return;}
        document.getElementById('bz_name').value="";document.getElementById('bz_client').value="";document.getElementById('bz_value').value="";
        self.refresh();
      }).catch(function(){alert("Connection error.");});
  },

  delProject:function(id){
    var self=this; if(!confirm("Delete this project and its tasks?"))return;
    fetch(this.apiBase()+"/api/business/delete-project",{method:"POST",headers:this.hdr(),body:JSON.stringify({id:id})})
      .then(function(r){return r.json();}).then(function(){self.refresh();}).catch(function(){});
  },

  addTask:function(pid){
    var self=this;
    var title=(document.getElementById('task_'+pid)||{}).value||"";
    var asg=(document.getElementById('asg_'+pid)||{}).value||"";
    if(!title){return;}
    fetch(this.apiBase()+"/api/business/add-task",{method:"POST",headers:this.hdr(),body:JSON.stringify({project_id:pid,title:title,assignee:asg})})
      .then(function(r){return r.json();}).then(function(){self.refresh();}).catch(function(){});
  },

  toggleTask:function(pid,tid){
    var self=this;
    fetch(this.apiBase()+"/api/business/toggle-task",{method:"POST",headers:this.hdr(),body:JSON.stringify({project_id:pid,task_id:tid})})
      .then(function(r){return r.json();}).then(function(){self.refresh();}).catch(function(){});
  },

  styles:function(){
    return "<style>"
    +".bz-wrap{max-width:1000px;}"
    +".bz-head{margin-bottom:16px;}.bz-title{margin:0;font-size:1.6rem;font-weight:900;color:#090d16;}.bz-sub{margin:4px 0 0;color:#64748b;font-size:0.9rem;}"
    +".bz-stats{display:flex;gap:12px;margin-bottom:18px;flex-wrap:wrap;}"
    +".bz-stat{flex:1;min-width:120px;background:#fff;border:1px solid #e2e8f0;border-radius:12px;padding:14px;text-align:center;box-shadow:0 6px 18px rgba(15,23,42,0.04);}"
    +".bz-stat-l{display:block;font-size:11px;color:#64748b;font-weight:700;text-transform:uppercase;}"
    +".bz-stat-v{display:block;font-size:1.3rem;font-weight:900;color:#090d16;margin-top:4px;}"
    +".bz-grid{display:grid;grid-template-columns:0.9fr 1.3fr;gap:20px;align-items:start;}"
    +".bz-card{background:#fff;border:1px solid #e2e8f0;border-radius:16px;padding:24px;box-shadow:0 10px 30px rgba(15,23,42,0.05);}"
    +".bz-h3{font-size:1.1rem;font-weight:800;color:#0f172a;margin:0 0 14px;}"
    +".bz-field{margin-bottom:12px;}.bz-field label{display:block;font-size:0.78rem;font-weight:800;color:#0f172a;margin-bottom:5px;text-transform:uppercase;letter-spacing:.03em;}"
    +".bz-add{width:100%;padding:12px;border:none;border-radius:10px;background:#1d4ed8;color:#fff;font-weight:800;cursor:pointer;box-shadow:0 8px 20px rgba(29,78,216,0.25);}"
    +".bz-add:hover{background:#1e40af;}"
    +".bz-proj{border:1px solid #e2e8f0;border-radius:12px;padding:14px;margin-bottom:12px;}"
    +".bz-proj-top{display:flex;justify-content:space-between;align-items:center;}"
    +".bz-proj-name{font-weight:800;color:#0f172a;}"
    +".bz-badge{color:#fff;font-size:11px;font-weight:800;padding:2px 8px;border-radius:999px;margin-left:6px;}"
    +".bz-proj-sub{color:#94a3b8;font-size:12px;margin:4px 0 8px;}"
    +".bz-task{padding:3px 0;font-size:14px;color:#334155;}"
    +".bz-taskadd{display:flex;gap:6px;margin-top:8px;}"
    +".bz-taskinput{flex:1;padding:7px 10px;border:1px solid #e2e8f0;border-radius:7px;background:#f8fafc;font-size:13px;}"
    +".bz-taskbtn{background:#1d4ed8 !important;color:#fff !important;border:none !important;border-radius:7px;width:34px;font-weight:900;cursor:pointer;}"
    +".bz-del{background:#fff !important;border:1px solid #fecaca !important;color:#dc2626 !important;border-radius:6px !important;width:26px;height:26px;cursor:pointer;font-weight:700 !important;}"
    +"@media(max-width:820px){.bz-grid{grid-template-columns:1fr;}}"
    +"</style>";
  }
};
window.BusinessModule = BusinessModule;
