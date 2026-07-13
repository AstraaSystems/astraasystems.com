// Astraa Estimator — calculate (free preview) -> approve (spends 1 credit) -> full breakdown
var EstimatorModule = {
  _token: null,
  bcCities: ["BC / Vancouver","BC / Burnaby","BC / Richmond","BC / Surrey","BC / Coquitlam","BC / Port Coquitlam","BC / Port Moody","BC / New Westminster","BC / North Vancouver","BC / West Vancouver","BC / Delta","BC / Langley","BC / Maple Ridge","BC / Pitt Meadows","BC / White Rock","BC / Abbotsford","BC / Chilliwack","BC / Mission","BC / Hope","BC / Victoria","BC / Saanich","BC / Langford","BC / Colwood","BC / Nanaimo","BC / Parksville","BC / Qualicum Beach","BC / Duncan","BC / Courtenay","BC / Comox","BC / Campbell River","BC / Port Alberni","BC / Tofino","BC / Ucluelet","BC / Powell River","BC / Squamish","BC / Whistler","BC / Pemberton","BC / Gibsons","BC / Sechelt","BC / Kelowna","BC / West Kelowna","BC / Vernon","BC / Penticton","BC / Kamloops","BC / Merritt","BC / Salmon Arm","BC / Revelstoke","BC / Cranbrook","BC / Kimberley","BC / Fernie","BC / Nelson","BC / Castlegar","BC / Trail","BC / Golden","BC / Prince George","BC / Quesnel","BC / Williams Lake","BC / Fort St. John","BC / Dawson Creek","BC / Terrace","BC / Prince Rupert","BC / Kitimat","BC / Smithers","BC / Fort Nelson","BC / Other City or Town"],

  apiBase: function () {
    return (typeof ASTRAA_API_BASE !== 'undefined') ? ASTRAA_API_BASE : "https://family-speed-outcome.ngrok-free.dev";
  },
  session: function () {
    try { return JSON.parse(localStorage.getItem('astraa_session') || '{}'); } catch (e) { return {}; }
  },

  render: function () {
    var f = "width:100%;padding:11px 13px;border:1px solid #e2e8f0;border-radius:8px;background:#f8fafc;color:#0f172a;font-size:0.95rem;";
    var cityOpts = this.bcCities.map(function (c) { return "<option>" + c + "</option>"; }).join("");
    return ''
      + '<h3>Astraa Estimator</h3>'
      + '<p style="color:#64748b;margin-bottom:16px;">Calculate as many times as you like — free. You only use a credit when you <strong>approve</strong> an estimate.</p>'
      + '<div style="max-width:560px;display:flex;flex-direction:column;gap:12px;">'
      + '  <label>Assembly (optional bundle)<select id="est_assembly" style="' + f + '"><option value="">— None —</option></select></label>'
      + '  <label>Square footage<input id="est_sqft" type="number" placeholder="1000" style="' + f + '"></label>'
      + '  <label>Project type<select id="est_ptype" style="' + f + '"><option>Commercial</option><option>Residential</option><option>Industrial</option><option>Renovation</option><option>Service / Repair</option><option>Custom</option></select></label>'
      + '  <label>Location / market<select id="est_loc" style="' + f + '">' + cityOpts + '</select></label>'
      + '  <label>Quality level<select id="est_quality" style="' + f + '"><option>Standard</option><option>Premium</option><option>Economy</option></select></label>'
      + '  <label>Material factor<input id="est_material" type="number" step="0.1" value="1" style="' + f + '"></label>'
      + '  <label>Labor factor<input id="est_labor" type="number" step="0.1" value="1" style="' + f + '"></label>'
      + '  <label>Complexity factor<input id="est_complexity" type="number" step="0.1" value="1" style="' + f + '"></label>'
      + '  <button onclick="EstimatorModule.calculate()" style="padding:12px;border:none;border-radius:8px;background:#1d4ed8;color:#fff;font-weight:700;cursor:pointer;">Calculate (free)</button>'
      + '</div>'
      + '<div id="est_result" style="margin-top:20px;"></div>';
  },

  loadAssemblies: function () {
    fetch(this.apiBase() + "/api/estimate/assemblies", { headers: { "ngrok-skip-browser-warning": "true" } })
      .then(function (r) { return r.json(); })
      .then(function (data) {
        if (!data.success) return;
        var sel = document.getElementById('est_assembly');
        if (!sel) return;
        data.assemblies.forEach(function (a) {
          var o = document.createElement('option');
          o.value = a.key; o.text = a.name; o.title = a.description;
          sel.appendChild(o);
        });
      }).catch(function (e) { console.log('assemblies load failed', e); });
  },

  calculate: function () {
    var self = this;
    var out = document.getElementById('est_result');
    out.innerHTML = '<p style="color:#1d4ed8;">Calculating...</p>';
    function val(id){ var el=document.getElementById(id); return el?el.value:""; }
    var s = this.session();
    var payload = {
      email: s.email,
      sqft: parseFloat(val('est_sqft')) || 0,
      project_type: val('est_ptype') || "Commercial",
      location_market: val('est_loc') || "BC / Vancouver",
      quality_level: val('est_quality') || "Standard",
      material: parseFloat(val('est_material')) || 1,
      labor: parseFloat(val('est_labor')) || 1,
      complexity: parseFloat(val('est_complexity')) || 1,
      assembly: val('est_assembly')
    };
    fetch(this.apiBase() + "/api/estimate/preview", {
      method: "POST",
      headers: { "Content-Type": "application/json", "Authorization": "Bearer " + (s.token||""), "ngrok-skip-browser-warning": "true" },
      body: JSON.stringify(payload)
    })
    .then(function(r){ return r.json(); })
    .then(function(d){
      if (!d.success) { out.innerHTML = "<p style='color:#dc2626;'>" + (d.error||'Failed') + "</p>"; return; }
      self._token = d.preview_token;
      out.innerHTML =
        "<div style='padding:20px;border:1px dashed #94a3b8;border-radius:14px;background:#f8fafc;position:relative;'>"
        + "<div style='position:absolute;top:8px;right:14px;font-size:11px;font-weight:800;color:#f59e0b;'>PREVIEW — NOT APPROVED</div>"
        + "<h4 style='margin:0 0 6px 0;color:#03050a;'>Estimated Cost: $" + Math.round(d.base_estimate).toLocaleString() + "</h4>"
        + "<p style='color:#475569;margin:2px 0;'>Range: $" + Math.round(d.range.low).toLocaleString() + " – $" + Math.round(d.range.high).toLocaleString() + "</p>"
        + "<p style='color:#475569;margin:2px 0;'>Confidence: " + (d.confidence*100).toFixed(1) + "%  &middot;  Risk: " + (d.risk*100).toFixed(0) + "%</p>"
        + "<p style='color:#94a3b8;font-size:12px;margin-top:10px;'>Full trade breakdown unlocks when you approve. Approving uses 1 credit.</p>"
        + "<button onclick='EstimatorModule.approve()' style='margin-top:10px;padding:12px 18px;border:none;border-radius:8px;background:#16a34a;color:#fff;font-weight:800;cursor:pointer;'>Approve — uses 1 credit</button>"
        + "</div>";
    })
    .catch(function(e){ out.innerHTML = "<p style='color:#dc2626;'>Connection error: " + e.message + "</p>"; });
  },

  approve: function () {
    var self = this;
    var out = document.getElementById('est_result');
    var s = this.session();
    if (!this._token) { out.innerHTML = "<p style='color:#dc2626;'>Please calculate first.</p>"; return; }
    out.innerHTML = "<p style='color:#16a34a;'>Approving...</p>";
    fetch(this.apiBase() + "/api/estimate/approve", {
      method: "POST",
      headers: { "Content-Type": "application/json", "Authorization": "Bearer " + (s.token||""), "ngrok-skip-browser-warning": "true" },
      body: JSON.stringify({ email: s.email, preview_token: this._token })
    })
    .then(function(r){ return r.json(); })
    .then(function(d){
      if (d.error === "limit_reached") {
        out.innerHTML = "<div style='padding:18px;border:1px solid #f59e0b;border-radius:12px;background:#fffbeb;'>"
          + "<h4 style='margin:0 0 6px 0;color:#92400e;'>Approval limit reached</h4>"
          + "<p style='color:#92400e;'>" + d.message + "</p>"
          + "<p style='color:#94a3b8;font-size:12px;'>(Overage purchase — $10 for 10 — coming in the next update.)</p></div>";
        return;
      }
      if (!d.success) { out.innerHTML = "<p style='color:#dc2626;'>" + (d.error||'Approval failed') + "</p>"; return; }
      var e = d.estimate, bd = e.breakdown || {};
      var rows = Object.keys(bd).map(function(k){
        return "<tr><td style='padding:4px 10px;color:#475569;text-transform:capitalize;'>"+k+"</td><td style='padding:4px 10px;text-align:right;font-weight:700;'>$"+Math.round(bd[k]).toLocaleString()+"</td></tr>";
      }).join("");
      self._token = null;
      out.innerHTML =
        "<div style='padding:20px;border:2px solid #16a34a;border-radius:14px;background:#f0fdf4;'>"
        + "<div style='font-size:11px;font-weight:800;color:#16a34a;margin-bottom:6px;'>APPROVED — THIS ESTIMATE IS NOW YOURS</div>"
        + "<h4 style='margin:0 0 6px 0;color:#03050a;'>Total: $" + Math.round(e.base_estimate).toLocaleString() + "</h4>"
        + "<p style='color:#475569;margin:2px 0;'>Range: $" + Math.round(e.range.low).toLocaleString() + " – $" + Math.round(e.range.high).toLocaleString() + "  &middot;  Confidence " + (e.confidence*100).toFixed(1) + "%  &middot;  Risk " + (e.risk*100).toFixed(0) + "%</p>"
        + "<table style='margin-top:12px;border-collapse:collapse;width:100%;max-width:360px;'>" + rows + "</table>"
        + "<p style='color:#166534;font-size:12px;margin-top:12px;font-weight:700;'>Approved estimates: " + d.approved_used + " / " + d.limit + (d.extra_credits ? " (+"+d.extra_credits+" extra)" : "") + "  &middot;  " + d.remaining + " remaining</p>"
        + "</div>";
    })
    .catch(function(e){ out.innerHTML = "<p style='color:#dc2626;'>Connection error: " + e.message + "</p>"; });
  }
};
window.EstimatorModule = EstimatorModule;
