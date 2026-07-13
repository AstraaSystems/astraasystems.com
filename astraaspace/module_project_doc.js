// Astraa Whole Project Document — bank/client/bid-ready written estimate
var ProjectDocModule = {
  apiBase:function(){return (typeof ASTRAA_API_BASE!=='undefined')?ASTRAA_API_BASE:"https://family-speed-outcome.ngrok-free.dev";},
  session:function(){try{return JSON.parse(localStorage.getItem('astraa_session')||'{}');}catch(e){return {};}},
  _e:null, _profile:null,

  offer:function(estimate){
    this._e = estimate;
    var host = document.getElementById('est_result');
    var btn = document.createElement('button');
    btn.textContent = "Generate Project Document";
    btn.style.cssText="margin-top:12px;padding:12px 18px;border:none;border-radius:8px;background:#0f172a;color:#fff;font-weight:800;cursor:pointer;";
    btn.onclick=function(){ ProjectDocModule.start(); };
    host.appendChild(btn);
  },

  start:function(){
    var self=this;
    fetch(this.apiBase()+"/api/account/business-profile",{headers:{"Authorization":"Bearer "+(this.session().token||""),"ngrok-skip-browser-warning":"true"}})
      .then(function(r){return r.json();}).then(function(d){self._profile=(d.success&&d.profile)?d.profile:{};self.render();})
      .catch(function(){self._profile={};self.render();});
  },

  render:function(){
    var e=this._e, p=this._profile||{};
    var money=function(n){return "$"+Math.round(n).toLocaleString();};
    var today=new Date().toLocaleDateString();
    var docno="PROJ-"+Date.now().toString().slice(-8);
    var bd=e.breakdown||{};
    var tradeRows=Object.keys(bd).map(function(k){return "<tr><td style='padding:5px 10px;color:#475569;'>"+k+"</td><td style='padding:5px 10px;text-align:right;'>"+money(bd[k])+"</td></tr>";}).join("");
    var header = p.company_name
      ? "<h2 style='margin:0;'>"+p.company_name+"</h2><p style='color:#64748b;font-size:13px;margin:2px 0;'>"+[p.phone,p.email,p.address].filter(Boolean).join(" · ")+"</p><p style='color:#94a3b8;font-size:12px;margin:2px 0;'>"+[p.license_no&&("Lic# "+p.license_no),p.worksafe_no&&("WorkSafeBC# "+p.worksafe_no),p.gst_no&&("GST# "+p.gst_no)].filter(Boolean).join(" · ")+"</p>"
      : "<h2 style='margin:0;'>Project Estimate</h2>";

    document.getElementById('est_result').innerHTML =
      "<div id='proj_doc' style='padding:30px;border:1px solid #e2e8f0;border-radius:14px;background:#fff;max-width:720px;'>"
      + header
      + "<hr style='border:none;border-top:2px solid #1d4ed8;margin:14px 0;'>"
      + "<h3 style='margin:0 0 4px;'>PROJECT ESTIMATE</h3>"
      + "<div style='display:flex;justify-content:space-between;font-size:13px;color:#475569;'><span><strong>Doc #</strong> "+docno+"</span><span><strong>Date:</strong> "+today+"</span></div>"
      + "<p style='font-size:13px;color:#475569;margin:6px 0;'><strong>Prepared for:</strong> <span contenteditable='true' style='border-bottom:1px dashed #cbd5e1;padding:0 60px;'>&nbsp;</span></p>"
      + "<h4 style='margin:16px 0 6px;'>Project Overview</h4>"
      + "<p style='font-size:14px;color:#334155;'>"+e.project_type+" · "+e.sqft+" sqft · "+(e.location_market||'')+" · "+(e.quality_level||'')+" quality</p>"
      + "<h4 style='margin:16px 0 6px;'>Trade Breakdown</h4>"
      + "<table style='width:100%;border-collapse:collapse;font-size:14px;'>"+tradeRows
      + "<tr style='border-top:1px solid #e2e8f0;'><td style='padding:6px 10px;font-weight:800;'>Hard Cost Subtotal</td><td style='padding:6px 10px;text-align:right;font-weight:800;'>"+money(e.hard_cost)+"</td></tr></table>"
      + "<h4 style='margin:16px 0 6px;'>Cost Summary</h4>"
      + "<table style='width:100%;border-collapse:collapse;font-size:14px;'>"
      + "<tr><td style='padding:5px 10px;color:#475569;'>Overhead (15%)</td><td style='padding:5px 10px;text-align:right;'>"+money(e.overhead)+"</td></tr>"
      + "<tr><td style='padding:5px 10px;color:#475569;'>Profit (10%)</td><td style='padding:5px 10px;text-align:right;'>"+money(e.profit)+"</td></tr>"
      + "<tr><td style='padding:5px 10px;color:#475569;'>Contingency (10%)</td><td style='padding:5px 10px;text-align:right;'>"+money(e.contingency)+"</td></tr>"
      + "<tr><td style='padding:5px 10px;color:#475569;'>Permits / Soft Costs (8%)</td><td style='padding:5px 10px;text-align:right;'>"+money(e.permits)+"</td></tr>"
      + "<tr style='border-top:1px solid #e2e8f0;'><td style='padding:6px 10px;font-weight:700;'>Subtotal</td><td style='padding:6px 10px;text-align:right;font-weight:700;'>"+money(e.subtotal)+"</td></tr>"
      + "<tr><td style='padding:5px 10px;color:#475569;'>GST (5%)</td><td style='padding:5px 10px;text-align:right;'>"+money(e.gst)+"</td></tr>"
      + "<tr><td style='padding:5px 10px;color:#475569;'>PST (7%)</td><td style='padding:5px 10px;text-align:right;'>"+money(e.pst)+"</td></tr>"
      + "<tr style='border-top:2px solid #0f172a;'><td style='padding:8px 10px;font-weight:900;font-size:16px;'>GRAND TOTAL</td><td style='padding:8px 10px;text-align:right;font-weight:900;font-size:18px;'>"+money(e.grand_total)+"</td></tr></table>"
      + "<h4 style='margin:16px 0 6px;'>Scope &amp; Notes</h4>"
      + "<div contenteditable='true' style='font-size:13px;color:#475569;border:1px dashed #e2e8f0;border-radius:8px;padding:12px;min-height:60px;'>Add scope, inclusions, exclusions, assumptions, payment schedule, and timeline here (click to edit)…</div>"
      + "<div style='margin-top:16px;padding:12px;background:#fffbeb;border:1px solid #fde68a;border-radius:8px;font-size:12px;color:#92400e;'>"
      + "<strong>Disclaimer:</strong> YOUR NEW DISCLAIMER TEXT HERE."
      + "</div>"
      + "<p style='margin-top:14px;font-size:13px;color:#475569;'>Authorized signature: <span style='border-bottom:1px solid #0f172a;padding:0 80px;'>&nbsp;</span></p>"
      + "</div>"
      + "<button onclick='ProjectDocModule.print()' style='margin-top:14px;padding:12px 20px;border:none;border-radius:8px;background:#16a34a;color:#fff;font-weight:800;cursor:pointer;'>Print / Save PDF</button>";
  },

  print:function(){
    var doc=document.getElementById('proj_doc').outerHTML;
    var w=window.open('','_blank');
    w.document.write("<html><head><title>Astraa Project Estimate</title></head><body style='font-family:Segoe UI,Arial,sans-serif;padding:20px;'>"+doc+"</body></html>");
    w.document.close();w.focus();w.print();
  }
};
window.ProjectDocModule = ProjectDocModule;
