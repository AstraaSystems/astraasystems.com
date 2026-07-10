// Astraa Space core — all 9 tools; 4 live, 5 coming soon
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

function initDashboard() {
    var activeUser = verifySession();
    if (!activeUser) return;

    var data = window.AstraaBlueprint;

    document.getElementById('welcome-title').innerText =
        "WELCOME TO THE " + data.profile.company_name.toUpperCase() + " COMMAND CENTER";
    document.getElementById('welcome-subtitle').innerText =
        "OPERATIONAL HUB // " + ((activeUser.user || '').toUpperCase()) + " // ACTIVE";

    document.getElementById('content-area').innerHTML = Dashboard.render();

    var nav = document.getElementById('nav-list');
    nav.innerHTML = '';

    Object.keys(data.tools).forEach(function (key) {
        var tool = data.tools[key];
        var live = astraaIsLive(tool.name);

        var card = document.createElement('div');
        card.className = 'tool-card';
        card.innerHTML = live
            ? "<div><strong>" + tool.name + "</strong></div>"
            : "<div><strong>" + tool.name + "</strong> <span style='font-size:0.7rem;color:#f59e0b;font-weight:700;'>COMING SOON</span></div>";

        card.onclick = function () {
            var area = document.getElementById('content-area');
            if (live) {
                if (key === 'comm' && typeof CommerceModule !== 'undefined') {
                    area.innerHTML = CommerceModule.render();
                } else {
                    area.innerHTML = "<h3>" + tool.name + "</h3><p>Welcome to " + tool.name + ". This tool is active on your account.</p>";
                }
            } else {
                var link = "mailto:" + ASTRAA_REQUEST_EMAIL + "?subject=Request access to " + tool.name;
                area.innerHTML = "<h3>" + tool.name + " - Coming Soon</h3>" +
                    "<p>" + tool.name + " is in active development and not yet available.</p>" +
                    "<p>" + link + "Email us to request access</a></p>";
            }
        };
        nav.appendChild(card);
    });
}

window.onload = initDashboard;
