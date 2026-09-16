// Astraa Users & Access — RBAC admin (Phase 4)
var UsersModule = {
  _data:null,
  esc:function(x){return String(x==null?'':x).replace(/&/g,'&amp;').replace(/</g,'&lt;').replace(/>/g,'&gt;').replace(/"/g,'&quot;').replace(/'/g,'&#39;');},
  apiBase:function(){
    if(typeof ASTRAA_API_BASE!=='undefined' && ASTRAA_API_BASE) return ASTRAA_API_BASE;
    return "http"+"s://"+"family-speed-outcome"+".ngrok-free"+".dev";
  },
  session:function(){try{return JSON.parse(localStorage.getItem('astraa_session')||'{}');}catch(e){return {};}},
  hdr:function(){return {"Content-Type":"application/json","Authorization":"Bearer "+(this.session().token||""),"ngrok-skip-browser-warning":"true"};},
  TOOLS:["estimator","business","finance","expense","vault","reports","research_analyst","logistics"],

  styles:function(){
    return '<style>'
    +'.um-shell{padding:26px 30px;font-family:Inter,system-ui,sans-serif;background:#f8fafc;min-height:calc(100vh - 120px);}'
    +'.um-h{font-size:1.5rem;font-weight:900;color:#0f172a;margin:0 0 4px;}'
    +'.um-sub{color:#64748b;margin:0 0 20px;font-size:.95rem;}'
    +'.um-seats{display:inline-block;background:#eff6ff;color:#1d4ed8;font-weight:800;font-size:.85rem;padding:6px 14px;border-radius:999px;margin-bottom:18px;}'
    +'.um-card{background:#fff;border:1px solid #e2e8f0;border-radius:16px;padding:22px;box-shadow:0 4px 14px rgba(15,23,42,.04);margin-bottom:20px;}'
    +'.um-tbl{width:100%;border-collapse:collapse;}'
    +'.um-tbl th{text-align:left;font-size:.72rem;text-transform:uppercase;letter-spacing:.04em;color:#64748b;padding:8px 10px;border-bottom:2px solid #e2e8f0;}'
    +'.um-tbl td{padding:10px;border-bottom:1px solid #f1f5f9;font-size:.9rem;color:#334155;vertical-align:top;}'
    +'.um-pill{display:inline-block;font-size:.72rem;font-weight:800;padding:3px 9px;border-radius:999px;}'
    +'.um-owner{background:#fef3c7;color:#92400e;}.um-admin{background:#dbeafe;color:#1e40af;}.um-basic{background:#f1f5f9;color:#475569;}'
    +'.um-in{padding:8px 10px;border:1px solid #cbd5e1;border-radius:8px;font-size:.88rem;width:100%;box-sizing:border-box;}'
    +'.um-btn{background:#1d4ed8;color:#fff;border:none;padding:9px 16px;border-radius:9px;font-weight:800;cursor:pointer;font-size:.88rem;}'
    +'.um-btn.ghost{background:#fff;color:#dc2626;border:1px solid #fecaca;}'
    +'.um-grid{display:grid;grid-template-columns:1fr 1fr;gap:12px;}'
    +'.um-lbl{font-size:.75rem;font-weight:700;color:#475569;margin:0 0 4px;display:block;}'
    +'.um-tools{display:flex;flex-wrap:wrap;gap:6px;}'
    +'.um-tool{font-size:.72rem;background:#f1f5f9;color:#475569;padding:2px 7px;border-radius:6px;}'
    +'.um-msg{padding:10px 14px;border-radius:9px;font-size:.88rem;margin-bottom:14px;}'
    +'.um-ok{background:#dcfce7;color:#166534;}.um-err{background:#fee2e2;color:#991b1b;}'
    +'</style>';
  },

  render:function(){
    return this.styles()
    +'<div class="um-shell">'
    +'<div class="um-h">Users & Access</div>'
    +'<div class="um-sub">Manage your team, roles, departments, and tool access.</div>'
    +'<div id="um_body"><p style="color:#94a3b8;">Loading…</p></div>'
    +'</div>';
  },

  load:function(){ this.refresh(); },

  refresh:function(){
    var self=this;
    fetch(this.apiBase()+"/api/rbac/users",{headers:this.hdr()})
      .then(function(r){return r.json();})
      .then(function(d){ self._data=d; self.paint(); })
      .catch(function(){ document.getElementById('um_body').innerHTML='<p class="um-err um-msg">Could not load users.</p>'; });
  },

  paint:function(){
    var self=this; var d=this._data||{}; var b=document.getElementById('um_body');
    if(!d.ok){ b.innerHTML='<p class="um-err um-msg">'+(d.error||'Error')+'</p>'; return; }
    var depts=d.departments||[];
    var h='';
    h+='<span class="um-seats">Seats: '+(d.seats_used||0)+' / '+(d.seats_total||0)+' \u00b7 Admins: '+(d.admins_used||0)+' / '+(d.max_admins||0)+'</span>';
    h+='<div id="um_flash"></div>';
    // users table
    h+='<div class="um-card"><table class="um-tbl"><thead><tr><th>Name</th><th>Email</th><th>Role</th><th>Departments</th><th>Tools</th><th></th></tr></thead><tbody>';
    (d.users||[]).forEach(function(u){
      var rc=u.role==='owner'?'um-owner':(u.role==='admin'?'um-admin':'um-basic');
      var tools=(u.tools||[]).map(function(t){return '<span class="um-tool">'+self.esc(t)+'</span>';}).join(' ')||'<span class="um-tool">none</span>';
      var deps=self.esc((u.departments||[]).join(', '))||'\u2014';
      h+='<tr><td><b>'+self.esc(u.name)+'</b></td><td>'+self.esc(u.email)+'</td>'
        +'<td><span class="um-pill '+rc+'">'+u.role+'</span></td>'
        +'<td>'+deps+'</td><td><div class="um-tools">'+tools+'</div></td>'
        +'<td>'+(u.role==='owner'?'':'<button class="um-btn ghost" onclick="UsersModule.remove(\''+self.esc(u.email)+'\')">Remove</button>')+'</td></tr>';
    });
    h+='</tbody></table></div>';
    // add-user form
    h+='<div class="um-card"><h3 style="margin:0 0 14px;font-size:1.05rem;font-weight:800;">Add a user</h3>';
    h+='<div class="um-grid">';
    h+='<div><label class="um-lbl">Name</label><input id="um_name" class="um-in" placeholder="Jane Doe"></div>';
    h+='<div><label class="um-lbl">Email</label><input id="um_email" class="um-in" placeholder="jane@company.com"></div>';
    h+='</div><div class="um-grid" style="margin-top:12px;">';
    h+='<div><label class="um-lbl">Role</label><select id="um_role" class="um-in"><option value="basic">Basic user</option><option value="admin">Admin</option></select></div>';
    h+='<div><label class="um-lbl">Department</label><select id="um_dept" class="um-in">'+depts.map(function(x){return '<option>'+x+'</option>';}).join('')+'</select></div>';
    h+='</div>';
    h+='<div style="margin-top:12px;"><label class="um-lbl">Tool access</label><div class="um-tools">';
    this.TOOLS.forEach(function(t){ h+='<label style="font-size:.78rem;margin-right:10px;"><input type="checkbox" class="um_tool_cb" value="'+t+'"> '+t+'</label>'; });
    h+='</div></div>';
    h+='<div style="margin-top:16px;"><button class="um-btn" onclick="UsersModule.add()">+ Add user</button></div>';
    h+='</div>';
    b.innerHTML=h;
  },

  flash:function(cls,msg){
    var f=document.getElementById('um_flash');
    if(f) f.innerHTML='<div class="um-msg '+cls+'">'+msg+'</div>';
  },

  add:function(){
    var self=this;
    var tools=[];
    document.querySelectorAll('.um_tool_cb').forEach(function(cb){ if(cb.checked) tools.push(cb.value); });
    var body={ name:(document.getElementById('um_name')||{}).value||'',
      email:(document.getElementById('um_email')||{}).value||'',
      role:(document.getElementById('um_role')||{}).value||'basic',
      departments:[(document.getElementById('um_dept')||{}).value||''],
      tools:tools };
    if(!body.email){ this.flash('um-err','Email is required.'); return; }
    fetch(this.apiBase()+"/api/rbac/users/add",{method:"POST",headers:this.hdr(),body:JSON.stringify(body)})
      .then(function(r){return r.json();}).then(function(d){
        if(d.ok){ self.flash('um-ok','User added.'); self.refresh(); }
        else self.flash('um-err','Could not add: '+(d.result||d.error));
      });
  },

  remove:function(email){
    if(!confirm('Remove '+email+'?')) return;
    var self=this;
    fetch(this.apiBase()+"/api/rbac/users/remove",{method:"POST",headers:this.hdr(),body:JSON.stringify({email:email})})
      .then(function(r){return r.json();}).then(function(d){
        if(d.ok){ self.refresh(); } else self.flash('um-err','Could not remove: '+(d.result||d.error));
      });
  }
};
