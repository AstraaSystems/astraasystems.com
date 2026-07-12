// Astraa Estimator — real portal module calling /api/estimate
var EstimatorModule = {
  render: function () {
    var f = "";
    return ''
      + '<h3>Astraa Estimator</h3>'
      + '<p style="color:#94a3b8;margin-bottom:16px;">Enter project details to generate a calibrated estimate.</p>'+ '<label>Assembly (optional bundle)<select id="est_assembly"><option value="">— None —</option></select></label>'
      + '<div style="max-width:560px;display:flex;flex-direction:column;gap:12px;">'
      + '  <label>Square footage<input id="est_sqft" type="number" placeholder="1000" style="' + f + '"></label>'
      + '  <label>Project type'
      + '    <select id="est_ptype" style="' + f + '">'
      + '      <option>Commercial</option><option>Residential</option><option>Industrial</option><option>Institutional</option>'
      + '    </select></label>'
      + '  <label>Location / market<input id="est_loc" type="text" value="BC / Vancouver" style="' + f + '"></label>'
      + '  <label>Quality level'
      + '    <select id="est_quality" style="' + f + '">'
      + '      <option>Standard</option><option>Premium</option><option>Economy</option>'
      + '    </select></label>'
      + '  <label>Material factor (1 = baseline)<input id="est_material" type="number" step="0.1" value="1" style="' + f + '"></label>'
      + '  <label>Labor factor (1 = baseline)<input id="est_labor" type="number" step="0.1" value="1" style="' + f + '"></label>'
      + '  <label>Complexity factor (1 = baseline)<input id="est_complexity" type="number" step="0.1" value="1" style="' + f + '"></label>'
      + '  <button onclick="EstimatorModule.run()" style="padding:12px;border:none;border-radius:8px;background:#2563eb;color:#fff;font-weight:700;cursor:pointer;">Generate Estimate</button>'
      + '</div>'
      + '<div id="est_result" style="margin-top:20px;"></div>';
  },


  ,loadAssemblies: function () {
    var base = (typeof ASTRAA_API_BASE !== 'undefined') ? ASTRAA_API_BASE : "https://family-speed-outcome.ngrok-free.dev";
    fetch(base + "/api/estimate/assemblies", { headers: { "ngrok-skip-browser-warning": "true" } })
      .then(function(r){ return r.json(); })
      .then(function(data){
        if (!data.success) return;
        var sel = document.getElementById('est_assembly');
        if (!sel) return;
        data.assemblies.forEach(function(a){
          var o = document.createElement('option');
          o.value = a.key;
          o.text = a.name;
          o.title = a.description;
          sel.appendChild(o);
        });
      }).catch(function(e){ console.log('assemblies load failed', e); });
  }
  ,run: function () {
    var session = {};
    try { session = JSON.parse(localStorage.getItem('astraa_session') || '{}'); } catch (e) {}
    var out = document.getElementById('est_result');
    out.innerHTML = '<p style="color:#38bdf8;">Calculating...</p>';

    function val(id) { var el = document.getElementById(id); return el ? el.value : ""; }

    var payload = {
      email: session.email,
      selected_tool: "Astraa Estimator",
      selected_plan: session.plan || "Professional",
      sqft: parseFloat(val('est_sqft')) || 0,
      project_type: val('est_ptype') || "Commercial",
      location_market: val('est_loc') || "BC / Vancouver",
      quality_level: val('est_quality') || "Standard",
      material: parseFloat(val('est_material')) || 1,
      labor: parseFloat(val('est_labor')) || 1,
      complexity: parseFloat(val('est_complexity')) || 1,
      assembly: val('est_assembly')
    };

    var base = (typeof ASTRAA_API_BASE !== 'undefined') ? ASTRAA_API_BASE : "https://family-speed-outcome.ngrok-free.dev";

    fetch(base + "/api/estimate/enterprise", {
      method: "POST",
      headers: {
        "Content-Type": "application/json",
        "Authorization": "Bearer " + (session.token || ""),
        "ngrok-skip-browser-warning": "true"
      },
      body: JSON.stringify(payload)
    })
    .then(function (r) { return r.json(); })
    .then(function (data) {
      if (data.success && data.estimate) {
        var e = data.estimate;
        var u = data.usage || {};
        var bd = e.breakdown || {};
        var rows = Object.keys(bd).map(function(k){
          return "<tr><td style='padding:4px 10px;color:#475569;text-transform:capitalize;'>"+k+"</td><td style='padding:4px 10px;text-align:right;font-weight:700;'>$"+Math.round(bd[k]).toLocaleString()+"</td></tr>";
        }).join("");
        out.innerHTML =
          "<div style='padding:20px;border:1px solid #1d4ed8;border-radius:14px;background:#f8fafc;'>"
          + "<h4 style='margin:0 0 6px 0;color:#03050a;'>Base Estimate: $"+Math.round(e.base_estimate).toLocaleString()+"</h4>"
          + "<p style='color:#475569;margin:2px 0;'>Range: $"+Math.round(e.range.low).toLocaleString()+" – $"+Math.round(e.range.high).toLocaleString()+"</p>"
          + "<p style='color:#475569;margin:2px 0;'>Confidence: "+(e.confidence*100).toFixed(1)+"%  &middot;  Risk: "+(e.risk*100).toFixed(0)+"%  &middot;  Recommended: "+(e.recommended_plan||"")+"</p>"
          + "<table style='margin-top:12px;border-collapse:collapse;width:100%;max-width:360px;'>"+rows+"</table>"
          + "<p style='color:#94a3b8;font-size:12px;margin-top:12px;'>Estimates used: "+(u.estimate_used!=null?u.estimate_used:"?")+" / "+(u.estimate_limit!=null?u.estimate_limit:"?")+"</p>"
          + "</div>";
        return;
      }
      if (false) {
        var e = data.estimate;
        var u = data.usage || {};
        out.innerHTML =
          '<div style="padding:18px;border:1px solid #1d4ed8;border-radius:12px;background:#0b1220;">'
          + '<h4 style="margin:0 0 10px 0;color:#22c55e;">Estimated Cost: $' + (e.estimate != null ? e.estimate.toLocaleString() : "?") + '</h4>'
          + '<p style="color:#e2e8f0;font-size:13px;margin:4px 0;">Base rate: $' + e.base_rate + '/sqft &middot; ' + e.project_type + ' &middot; ' + e.location_market + ' &middot; ' + e.quality_level + '</p>'
          + '<p style="color:#94a3b8;font-size:12px;">Basis: ' + (e.calibration_basis || '') + '</p>'
          + '<p style="color:#94a3b8;font-size:12px;margin-top:10px;">Estimates used: ' + (u.estimate_used != null ? u.estimate_used : '?') + ' / ' + (u.estimate_limit != null ? u.estimate_limit : '?') + '</p>'
          + '</div>';
      } else {
        out.innerHTML = '<p style="color:#ef4444;">' + (data.error || 'Estimate failed.') + '</p>';
      }
    })
    .catch(function (e) {
      out.innerHTML = '<p style="color:#ef4444;">Connection error: ' + e.message + '</p>';
    });
  }
};
window.EstimatorModule = EstimatorModule;
