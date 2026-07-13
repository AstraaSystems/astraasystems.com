// Astraa Vault — per-account file storage (upload/list/download/delete)
var VaultModule = {
  cats:["Documents","Estimates & Quotes","Invoices","Receipts","Contracts","Images","Other"],
  _filter:"",
  apiBase:function(){return (typeof ASTRAA_API_BASE!=='undefined')?ASTRAA_API_BASE:"https://family-speed-outcome.ngrok-free.dev";},
  session:function(){try{return JSON.parse(localStorage.getItem('astraa_session')||'{}');}catch(e){return {};}},
  hdr:function(){return {"Content-Type":"application/json","Authorization":"Bearer "+(this.session().token||""),"ngrok-skip-browser-warning":"true"};},
  fmtSize:function(b){b=Number(b||0);if(b<1024)return b+" B";if(b<1048576)return (b/1024).toFixed(1)+" KB";return (b/1048576).toFixed(1)+" MB";},

  render:function(){
    var f="width:100%;padding:11px 13px;border:1px solid #e2e8f0;border-radius:8px;background:#f8fafc;font-size:0.95rem;";
    var catOpts=this.cats.map(function(c){return "<option>"+c+"</option>";}).join("");
    var filtOpts=this.cats.map(function(c){return "<option>"+c+"</option>";}).join("");
    return this.styles()
      + '<div class="vt-wrap">'
      + '  <div class="vt-head"><h2 class="vt-title">Astraa Vault</h2><p class="vt-sub">Securely save and retrieve your files — documents, quotes, invoices, receipts.</p></div>'
      + '  <div id="vt_summary" class="vt-stats"></div>'
      + '  <div class="vt-grid">'
      + '    <div class="vt-card">'
      + '      <h3 class="vt-h3">Upload File</h3>'
      + '      <div class="vt-f"><label>Category</label><select id="vt_cat" style="'+f+'">'+catOpts+'</select></div>'
      + '      <div class="vt-f"><label>Note (optional)</label><input id="vt_note" style="'+f+'" placeholder="e.g. Smith project quote"></div>'
      + '      <div class="vt-f"><label>Choose file (max 10 MB)</label><input id="vt_file" type="file" style="'+f+'"></div>'
      + '      <button class="vt-add" onclick="VaultModule.upload()">Upload to Vault</button>'
      + '      <div id="vt_status" style="margin-top:10px;font-size:13px;"></div>'
      + '    </div>'
      + '    <div class="vt-card">'
      + '      <div class="vt-listhead"><h3 class="vt-h3" style="margin:0;">Your Files</h3>'
      + '        <select id="vt_filter" class="vt-filter" onchange="VaultModule.setFilter(this.value)"><option value="">All categories</option>'+filtOpts+'</select></div>'
      + '      <div id="vt_list"></div>'
      + '    </div>'
      + '  </div>'
      + '</div>';
  },

  load:function(){ this.refresh(); },
  setFilter:function(v){ this._filter=v; this.refresh(); },

  refresh:function(){
    var self=this;
    fetch(this.apiBase()+"/api/vault/list",{headers:this.hdr()}).then(function(r){return r.json();}).then(function(d){
      if(!d.success){document.getElementById('vt_list').innerHTML="<p class='vt-muted'>"+(d.error||'Error')+"</p>";return;}
      var s=d.summary||{};
      document.getElementById('vt_summary').innerHTML=
        "<div class='vt-stat'><span class='vt-stat-l'>Files</span><span class='vt-stat-v'>"+(s.count||0)+"</span></div>"
        +"<div class='vt-stat'><span class='vt-stat-l'>Storage Used</span><span class='vt-stat-v'>"+self.fmtSize(s.total_bytes)+"</span></div>";
      var files=(d.files||[]).filter(function(f){return !self._filter||f.category===self._filter;});
      if(!files.length){document.getElementById('vt_list').innerHTML="<p class='vt-muted'>No files yet. Upload one on the left.</p>";return;}
      document.getElementById('vt_list').innerHTML=files.map(function(f){
        return "<div class='vt-item'><div class='vt-item-main'>"
          +"<div class='vt-fname'>📄 "+f.filename+"</div>"
          +"<div class='vt-fmeta'>"+f.category+" · "+self.fmtSize(f.size)+(f.note?" · "+f.note:"")+"</div></div>"
          +"<div class='vt-actions'><button class='vt-dl' onclick=\"VaultModule.download('"+f.id+"')\">Download</button>"
          +"<button class='vt-del' onclick=\"VaultModule.del('"+f.id+"')\">✕</button></div></div>";
      }).join("");
    }).catch(function(){document.getElementById('vt_list').innerHTML="<p class='vt-muted'>Connection error.</p>";});
  },

  upload:function(){
    var self=this;
    var fileInput=document.getElementById('vt_file');
    var status=document.getElementById('vt_status');
    if(!fileInput||!fileInput.files||!fileInput.files[0]){status.innerHTML="<span style='color:#dc2626;'>Choose a file first.</span>";return;}
    var file=fileInput.files[0];
    if(file.size>10*1024*1024){status.innerHTML="<span style='color:#dc2626;'>File exceeds 10 MB.</span>";return;}
    status.innerHTML="<span style='color:#1d4ed8;'>Uploading…</span>";
    var reader=new FileReader();
    reader.onload=function(e){
      var b64=e.target.result;
      fetch(self.apiBase()+"/api/vault/upload",{method:"POST",headers:self.hdr(),
        body:JSON.stringify({filename:file.name,data:b64,category:(document.getElementById('vt_cat')||{}).value,note:(document.getElementById('vt_note')||{}).value})})
        .then(function(r){return r.json();}).then(function(d){
          if(!d.success){status.innerHTML="<span style='color:#dc2626;'>"+(d.error||'Upload failed')+"</span>";return;}
          status.innerHTML="<span style='color:#16a34a;'>Uploaded ✓</span>";
          fileInput.value="";var n=document.getElementById('vt_note');if(n)n.value="";
          self.refresh();
        }).catch(function(){status.innerHTML="<span style='color:#dc2626;'>Connection error.</span>";});
    };
    reader.readAsDataURL(file);
  },

  download:function(id){
    var self=this;
    fetch(this.apiBase()+"/api/vault/download?id="+encodeURIComponent(id),{headers:this.hdr()})
      .then(function(r){return r.json();}).then(function(d){
        if(!d.success){alert(d.error||"Download failed");return;}
        var a=document.createElement("a");
        a.href="data:application/octet-stream;base64,"+d.data;
        a.download=d.filename;a.click();
      }).catch(function(){alert("Connection error.");});
  },

  del:function(id){
    var self=this; if(!confirm("Delete this file permanently?"))return;
    fetch(this.apiBase()+"/api/vault/delete",{method:"POST",headers:this.hdr(),body:JSON.stringify({id:id})})
      .then(function(r){return r.json();}).then(function(){self.refresh();}).catch(function(){});
  },

  styles:function(){
    return "<style>"
    +".vt-wrap{max-width:1000px;}"
    +".vt-head{margin-bottom:16px;}.vt-title{margin:0;font-size:1.6rem;font-weight:900;color:#090d16;}.vt-sub{margin:4px 0 0;color:#64748b;font-size:0.9rem;}"
    +".vt-stats{display:flex;gap:12px;margin-bottom:18px;flex-wrap:wrap;}"
    +".vt-stat{flex:1;min-width:120px;background:#fff;border:1px solid #e2e8f0;border-radius:12px;padding:14px;text-align:center;box-shadow:0 6px 18px rgba(15,23,42,0.04);}"
    +".vt-stat-l{display:block;font-size:11px;color:#64748b;font-weight:700;text-transform:uppercase;}"
    +".vt-stat-v{display:block;font-size:1.3rem;font-weight:900;color:#090d16;margin-top:4px;}"
    +".vt-grid{display:grid;grid-template-columns:0.9fr 1.3fr;gap:20px;align-items:start;}"
    +".vt-card{background:#fff;border:1px solid #e2e8f0;border-radius:16px;padding:24px;box-shadow:0 10px 30px rgba(15,23,42,0.05);}"
    +".vt-h3{font-size:1.1rem;font-weight:800;color:#0f172a;margin:0 0 14px;}"
    +".vt-f{margin-bottom:12px;}.vt-f label{display:block;font-size:0.76rem;font-weight:800;color:#0f172a;margin-bottom:4px;text-transform:uppercase;}"
    +".vt-add{width:100%;padding:12px;border:none;border-radius:10px;background:#1d4ed8 !important;color:#fff !important;font-weight:800;cursor:pointer;}"
    +".vt-listhead{display:flex;justify-content:space-between;align-items:center;margin-bottom:12px;}"
    +".vt-filter{padding:7px 10px;border:1px solid #e2e8f0;border-radius:8px;background:#f8fafc;font-size:12px;}"
    +".vt-item{display:flex;justify-content:space-between;align-items:center;border:1px solid #e2e8f0;border-radius:10px;padding:12px;margin-bottom:10px;}"
    +".vt-fname{font-weight:700;color:#0f172a;font-size:0.95rem;}"
    +".vt-fmeta{color:#94a3b8;font-size:12px;margin-top:2px;}"
    +".vt-actions{display:flex;gap:6px;}"
    +".vt-dl{padding:6px 12px;border:1px solid #1d4ed8 !important;background:#fff !important;color:#1d4ed8 !important;border-radius:7px;font-size:12px;font-weight:700;cursor:pointer;}"
    +".vt-del{background:#fff !important;border:1px solid #fecaca !important;color:#dc2626 !important;border-radius:6px;width:28px;cursor:pointer;font-weight:700;}"
    +".vt-muted{color:#94a3b8;}"
    +"@media(max-width:820px){.vt-grid{grid-template-columns:1fr;}}"
    +"</style>";
  }
};
window.VaultModule = VaultModule;
