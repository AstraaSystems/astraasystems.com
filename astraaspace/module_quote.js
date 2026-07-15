// Astraa Quote/Invoice generator — Single Work
var QuoteModule = {
  GST: 0, PST: 0,  // default OFF — set via toggle
  apiBase: function(){ return (typeof ASTRAA_API_BASE!=='undefined')?ASTRAA_API_BASE:"https://family-speed-outcome.ngrok-free.dev"; },
  session: function(){ try{return JSON.parse(localStorage.getItem('astraa_session')||'{}');}catch(e){return {};} },
  _profile: null, _estimate: null,

  // Called from estimator after an approved single-work estimate
  offerQuote: function(estimate){
    this._estimate = estimate;
    var host = document.getElementById('est_result');
    var btn = document.createElement('button');
    btn.textContent = "Create Quote / Invoice";
    btn.style.cssText = "margin-top:12px;padding:12px 18px;border:none;border-radius:8px;background:#0f172a;color:#fff;font-weight:800;cursor:pointer;";
    btn.onclick = function(){ QuoteModule.start(); };
    host.appendChild(btn);
  },

  start: function(){
    var self = this;
    fetch(this.apiBase()+"/api/account/business-profile", {
      headers:{ "Authorization":"Bearer "+(this.session().token||""), "ngrok-skip-browser-warning":"true" }
    }).then(function(r){return r.json();}).then(function(d){
      self._profile = (d.success && d.profile) ? d.profile : {};
      if (self._profile && self._profile.company_name) {
        self.renderQuote();               // profile exists -> branded quote
      } else {
        self.askProfile();                // first time -> ask to set up
      }
    }).catch(function(){ self._profile={}; self.askProfile(); });
  },

  askProfile: function(){
    var out = document.getElementById('est_result');
    out.innerHTML =
      "<div style='padding:20px;border:1px solid #e2e8f0;border-radius:14px;background:#fff;max-width:560px;'>"
      + "<h4 style='margin:0 0 8px 0;'>Set up your business profile?</h4>"
      + "<p style='color:#64748b;font-size:14px;'>Add your company details for professional, branded quotes. Or skip for a generic quote.</p>"
      + field('q_company','Company name') + field('q_phone','Phone') + field('q_email','Email')
      + field('q_address','Address') + field('q_license','Business license #')
      + field('q_worksafe','WorkSafeBC #') + field('q_gst','GST #')
      + "<div style='display:flex;gap:10px;margin-top:12px;'>"
      + "<button onclick='QuoteModule.saveProfile()' style='padding:10px 16px;border:none;border-radius:8px;background:#1d4ed8;color:#fff;font-weight:700;cursor:pointer;'>Save & Create Quote</button>"
      + "<button onclick='QuoteModule.skipProfile()' style='padding:10px 16px;border:1px solid #e2e8f0;border-radius:8px;background:#fff;color:#475569;font-weight:700;cursor:pointer;'>Skip — generic quote</button>"
      + "</div></div>";
    function field(id,label){ var f="width:100%;padding:9px 11px;border:1px solid #e2e8f0;border-radius:7px;background:#f8fafc;margin-bottom:8px;"; return "<label style='font-size:13px;font-weight:700;color:#0f172a;'>"+label+"<input id='"+id+"' style='"+f+"'></label>"; }
  },

  saveProfile: function(){
    var self=this;
    function v(id){var e=document.getElementById(id);return e?e.value:"";}
    var prof={ company_name:v('q_company'), phone:v('q_phone'), email:v('q_email'), address:v('q_address'), license_no:v('q_license'), worksafe_no:v('q_worksafe'), gst_no:v('q_gst') };
    fetch(this.apiBase()+"/api/account/business-profile",{
      method:"POST",
      headers:{ "Content-Type":"application/json","Authorization":"Bearer "+(this.session().token||""),"ngrok-skip-browser-warning":"true" },
      body:JSON.stringify(prof)
    }).then(function(r){return r.json();}).then(function(d){
      self._profile = d.profile || prof; self.renderQuote();
    }).catch(function(){ self._profile=prof; self.renderQuote(); });
  },

  skipProfile: function(){ this._profile = {}; this.renderQuote(); },

  renderQuote: function(){
    var e=this._estimate, p=this._profile||{};
    var sub = e.total;
    var gst = sub*this.GST, pst = sub*this.PST, grand = sub+gst+pst;
    var today = new Date().toLocaleDateString();
    var qno = "Q-" + Date.now().toString().slice(-8);
    var head = p.company_name
      ? "<h2 style='margin:0;'>"+p.company_name+"</h2>"
        + "<p style='color:#64748b;font-size:13px;margin:2px 0;'>"+[p.phone,p.email,p.address].filter(Boolean).join(" · ")+"</p>"
        + "<p style='color:#94a3b8;font-size:12px;margin:2px 0;'>"+[p.license_no&&("Lic# "+p.license_no),p.worksafe_no&&("WorkSafeBC# "+p.worksafe_no),p.gst_no&&("GST# "+p.gst_no)].filter(Boolean).join(" · ")+"</p>"
      : "<h2 style='margin:0;'>Quote / Invoice</h2>";

    var money=function(n){return "$"+Math.round(n).toLocaleString();};
    document.getElementById('est_result').innerHTML =
      "<div id='quote_doc' style='padding:28px;border:1px solid #e2e8f0;border-radius:14px;background:#fff;max-width:640px;'>"
      + head
      + "<hr style='border:none;border-top:1px solid #e2e8f0;margin:14px 0;'>"
      + "<div style='display:flex;justify-content:space-between;font-size:13px;color:#475569;'><span><strong>Quote #</strong> "+qno+"</span><span><strong>Date:</strong> "+today+"</span></div>"
      + "<p style='font-size:13px;color:#475569;margin:6px 0;'><strong>Client:</strong> <span contenteditable='true' style='border-bottom:1px dashed #cbd5e1;padding:0 40px;'>&nbsp;</span></p>"
      + "<table style='width:100%;border-collapse:collapse;margin-top:14px;'>"
      + "<tr><td style='padding:6px 0;color:#475569;'>"+e.category+" — "+e.sqft+" sqft ("+(e.location_market||'')+", "+(e.quality_level||'')+")</td><td></td></tr>"
      + "<tr><td style='padding:6px 0;color:#475569;'>Materials ($"+e.material_rate+"/sqft)</td><td style='text-align:right;font-weight:700;'>"+money(e.materials_cost)+"</td></tr>"
      + "<tr><td style='padding:6px 0;color:#475569;'>Labour ($"+e.labour_rate+"/sqft)</td><td style='text-align:right;font-weight:700;'>"+money(e.labour_cost)+"</td></tr>"
      + "<tr><td style='padding:6px 0;'>Subtotal</td><td style='text-align:right;font-weight:700;'>"+money(sub)+"</td></tr>"
      + (gst>0 ? "<tr><td style='padding:6px 0;color:#475569;'>GST</td><td style='text-align:right;'>"+money(gst)+"</td></tr>" : "")
      + (pst>0 ? "<tr><td style='padding:6px 0;color:#475569;'>PST</td><td style='text-align:right;'>"+money(pst)+"</td></tr>" : "")
      + "<tr style='border-top:2px solid #0f172a;'><td style='padding:8px 0;font-weight:900;'>TOTAL</td><td style='text-align:right;font-weight:900;font-size:18px;'>"+money(grand)+"</td></tr>"
      + "</table>"
      + "<p style='font-size:12px;color:#94a3b8;margin-top:16px;'>This quote is an estimate valid for 30 days. Final costs may vary with site conditions and supplier pricing.</p>"
      + "<div contenteditable='true' style='margin-top:10px;font-size:13px;color:#475569;border:1px dashed #e2e8f0;border-radius:8px;padding:10px;'>Notes / terms (click to edit)…</div>"
      + "</div>"
      + "<div style='margin-top:14px;padding:10px;background:#f8fafc;border:1px solid #e2e8f0;border-radius:8px;font-size:13px;'>"+ "<label style='cursor:pointer;'><input type='checkbox' "+(this.GST>0?'checked':'')+" onchange='QuoteModule.toggleTax(this.checked)'> Charge GST (5%) + PST (7%) — only if you are tax-registered</label></div>"+ "<button onclick='QuoteModule.print()' style='margin-top:14px;padding:12px 20px;border:none;border-radius:8px;background:#16a34a;color:#fff;font-weight:800;cursor:pointer;'>Print / Save PDF</button>";
  },

  toggleTax: function(on){
    this.GST = on ? 0.05 : 0;
    this.PST = on ? 0.07 : 0;
    this.renderQuote();
  },
  print: function(){
    var doc = document.getElementById('quote_doc').outerHTML;
    var w = window.open('', '_blank');
    w.document.write("<html><head><title>Astraa Quote</title></head><body style='font-family:Segoe UI,Arial,sans-serif;padding:20px;'>"+doc+"</body></html>");
    w.document.close(); w.focus(); w.print();
  }
};
window.QuoteModule = QuoteModule;
