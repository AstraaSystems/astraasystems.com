// Astraa Space core — dropdown selector + full-page tool workspace
var ASTRAA_LIVE_MODULES = ["estimator", "finance", "operations", "expense", "business", "lead gen", "crm", "vault", "reports", "data", "research analyst", "analyst", "research", "inference"];
var ASTRAA_REQUEST_EMAIL = "sales@astraasystems.com";

function verifySession() {
    var session = localStorage.getItem('astraa_session');
    if (!session) { window.location.href = 'login.html'; return null; }
    try { return JSON.parse(session); }
    catch (e) { window.location.href = 'login.html'; return null; }
}

function astraaIsLive(toolName) {
    var n = (toolName || "").toLowerCase();
    for (var i = 0; i < ASTRAA_LIVE_MODULES.length; i++) {
        if (n.indexOf(ASTRAA_LIVE_MODULES[i]) !== -1) return true;
    }
    return false;
}

function astraaRenderTool(key, tool) {
    var area = document.getElementById('content-area');
    var nameLower = (tool.name || "").toLowerCase();

    if (astraaIsLive(tool.name)) {
        if ((nameLower.indexOf("lead")!==-1||nameLower.indexOf("crm")!==-1) && typeof CRMModule !== "undefined") {
                    area.innerHTML = CRMModule.render(); if(CRMModule.load)CRMModule.load();
                } else if (nameLower.indexOf("vault") !== -1 && typeof VaultModule !== "undefined") {
                    area.innerHTML = VaultModule.render(); if(VaultModule.load)VaultModule.load();
                } else if (nameLower.indexOf("finance") !== -1 && typeof FinanceModule !== "undefined") {
                    document.body.classList.add("astraa-workspace-active"); area.innerHTML = FinanceModule.render(); if(FinanceModule.load)FinanceModule.load();
                } else if ((nameLower.indexOf("business")!==-1||nameLower.indexOf("operations")!==-1) && typeof BusinessModule !== "undefined") {
                    document.body.classList.add("astraa-workspace-active"); area.innerHTML = BusinessModule.render(); if(BusinessModule.load)BusinessModule.load();
                } else if (nameLower.indexOf("expense") !== -1 && typeof ExpenseModule !== "undefined") {
                    area.innerHTML = ExpenseModule.render(); if(ExpenseModule.load)ExpenseModule.load();
                } else if (nameLower.indexOf("estimator") !== -1 && typeof EstimatorModule !== "undefined") {
            area.innerHTML = EstimatorModule.render(); if (EstimatorModule.loadBaseline) EstimatorModule.loadBaseline();
        } else if ((nameLower.indexOf("report") !== -1 || nameLower.indexOf("data") !== -1) && typeof ReportsModule !== "undefined") {
            document.body.classList.add("astraa-workspace-active"); area.innerHTML = ReportsModule.render(); if(ReportsModule.load)ReportsModule.load();
        } else if ((nameLower.indexOf("analyst") !== -1 || nameLower.indexOf("research") !== -1 || nameLower.indexOf("inference") !== -1) && typeof AnalystModule !== "undefined") {
            document.body.classList.add("astraa-workspace-active"); area.innerHTML = AnalystModule.render(); if(AnalystModule.load)AnalystModule.load();
        } else if ((nameLower.indexOf("logistics") !== -1 || nameLower.indexOf("distribution") !== -1) && typeof LogisticsModule !== "undefined") {
            document.body.classList.add("astraa-workspace-active"); area.innerHTML = LogisticsModule.render(); if(LogisticsModule.load)LogisticsModule.load();
        } else if (key === 'comm' && typeof CommerceModule !== 'undefined') {
            area.innerHTML = CommerceModule.render();
        } else {
            area.innerHTML = "<h3>" + tool.name + "</h3>" +
                "<p style='color:#94a3b8;'>This tool is active on your account. Full module interface coming online.</p>";
        }
    } else {
        var mail = "mailto:" + ASTRAA_REQUEST_EMAIL + "?subject=Request access to " + encodeURIComponent(tool.name);
        area.innerHTML = "<h3>" + tool.name + " — Coming Soon</h3>" +
            "<p style='color:#94a3b8;'>" + tool.name + " is in active development and not yet available.</p>" +
            "<p>" + mail + "'>Email us to request early access</a></p>";
    }
}

function initDashboard() {
    var activeUser = verifySession();
    if (!activeUser) return;

    var data = window.AstraaBlueprint;

    var who = (activeUser.company || activeUser.user || "there");
    who = who.charAt(0).toUpperCase() + who.slice(1);
    document.getElementById('welcome-title').innerText = "Welcome " + who + " to Astraa Space";
    document.getElementById('welcome-subtitle').innerText = "Your tools are ready. Select one from the menu above.";

    var select = document.getElementById('tool-select');
    var keys = Object.keys(data.tools);

    // Fetch the user's entitlements, then show ONLY the tools they purchased
    var apiBase = (typeof ASTRAA_API_BASE !== 'undefined') ? ASTRAA_API_BASE : "https://family-speed-outcome.ngrok-free.dev";
    var sess = {};
    try { sess = JSON.parse(localStorage.getItem('astraa_session')||'{}'); } catch(e){}

    function toolAllowed(toolName, ents){
        if(!ents || !ents.length) return false;
        var n = (toolName||'').toLowerCase();
        for(var i=0;i<ents.length;i++){
            var e = (ents[i]||'').toLowerCase();
            // "Astraa Finance" matches entitlement "Astraa Finance"
            if(e.indexOf(n.replace('astraa ','')) !== -1) return true;
            if(n.indexOf('expense')!==-1 && e.indexOf('expense')!==-1) return true;
            if(n.indexOf('estimator')!==-1 && e.indexOf('estimator')!==-1) return true;
            if(n.indexOf('business')!==-1 && e.indexOf('business')!==-1) return true;
            if(n.indexOf('finance')!==-1 && e.indexOf('finance')!==-1) return true;
            if(n.indexOf('vault')!==-1 && e.indexOf('vault')!==-1) return true;
            if((n.indexOf('report')!==-1||n.indexOf('data')!==-1) && (e.indexOf('report')!==-1||e.indexOf('data')!==-1||e.indexOf('professional')!==-1||e.indexOf('suite')!==-1)) return true;
            if((n.indexOf('analyst')!==-1||n.indexOf('research')!==-1||n.indexOf('inference')!==-1) && (e.indexOf('analyst')!==-1||e.indexOf('research')!==-1||e.indexOf('professional')!==-1||e.indexOf('suite')!==-1)) return true;
        }
        return false;
    }

    function buildDropdown(entitlements){
        select.innerHTML = '<option value="">Select a tool...</option>';
        keys.forEach(function (key) {
            var tool = data.tools[key];
            var live = astraaIsLive(tool.name);
            if(!live) return;                          // skip coming-soon
            if(!toolAllowed(tool.name, entitlements)) return;  // skip not-purchased
            var opt = document.createElement('option');
            opt.value = key;
            opt.text = tool.name;
            select.appendChild(opt);
        });
        if(select.options.length <= 1){
            document.getElementById('welcome-subtitle').innerText = "No tools on your plan yet. Visit Pricing to add tools.";
        }
    }

    fetch(apiBase + "/api/auth/login-check", {headers:{"Authorization":"Bearer "+(sess.token||""),"ngrok-skip-browser-warning":"true"}})
      .then(function(r){return r.json();})
      .then(function(d){ buildDropdown((d && d.entitlements) || []); })
      .catch(function(){ buildDropdown([]); });

    select.onchange = function () {
        var key = select.value; document.body.classList.remove("astraa-workspace-active"); /* astraa-clear-styles */ var _ca=document.getElementById("content-area"); if(_ca){_ca.innerHTML="";}
        if (!key) {
            document.getElementById('content-area').innerHTML =
                "<p style='color:#94a3b8;'>Select a tool from the menu above to begin.</p>";
            return;
        }
        astraaRenderTool(key, data.tools[key]);
    };

    // Landing content before a tool is chosen
    document.getElementById('content-area').innerHTML =
        "<p style='color:#94a3b8;'>Select a tool from the menu above to begin.</p>";
}

window.onload = initDashboard;
