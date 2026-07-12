// Astraa Space core — dropdown selector + full-page tool workspace
var ASTRAA_LIVE_MODULES = ["estimator", "finance", "operations", "expense"];
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
        if (nameLower.indexOf("estimator") !== -1 && typeof EstimatorModule !== "undefined") {
            area.innerHTML = EstimatorModule.render();
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

    keys.forEach(function (key) {
        var tool = data.tools[key];
        var live = astraaIsLive(tool.name);
        var opt = document.createElement('option');
        opt.value = key;
        opt.text = tool.name + (live ? "" : "  (Coming Soon)");
        select.appendChild(opt);
    });

    select.onchange = function () {
        var key = select.value;
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
