// Astraa Space core — entitlement-gated portal
const ASTRAA_API_BASE = window.ASTRAA_API_BASE || "https://family-speed-outcome.ngrok-free.dev";

// Which tools have a REAL, usable module today. Others show "Coming soon".
const ASTRAA_LIVE_MODULES = ["estimator", "finance", "operations", "expense"];

function verifySession() {
    const session = localStorage.getItem('astraa_session');
    if (!session) {
        window.location.href = 'login.html';
        return null;
    }
    try { return JSON.parse(session); }
    catch (e) { window.location.href = 'login.html'; return null; }
}

// Does the logged-in customer's entitlements include this tool?
function astraaIsEntitled(toolName, entitlements) {
    if (!Array.isArray(entitlements)) return false;
    const n = (toolName || "").toLowerCase();
    return entitlements.some(ent => {
        const e = (ent || "").toLowerCase();
        // match on the tool's core word, e.g. "estimator", "finance", "expense", "operations"
        return e.includes(n) || n.includes(e.split(" ")[0]);
    });
}

async function initDashboard() {
    const activeUser = verifySession();
    if (!activeUser) return;

    // Prefer backend truth; fall back to stored session entitlements
    let entitlements = activeUser.entitlements || [];
    try {
        const res = await fetch(ASTRAA_API_BASE + "/api/auth/login-check", {
            method: "GET",
            headers: { "Authorization": "Bearer " + activeUser.token, "ngrok-skip-browser-warning": "true" }
        });
        if (res.ok) {
            const me = await res.json();
            if (Array.isArray(me.entitlements)) entitlements = me.entitlements;
        }
    } catch (e) { /* offline fallback: use stored entitlements */ }

    const data = window.AstraaBlueprint;
    document.getElementById('welcome-title').innerText =
        `WELCOME TO THE ${data.profile.company_name.toUpperCase()} COMMAND CENTER`;
    document.getElementById('welcome-subtitle').innerText =
        `OPERATIONAL HUB // ${(activeUser.user||'').toUpperCase()} // ACTIVE`;

    document.getElementById('content-area').innerHTML = Dashboard.render();

    const nav = document.getElementById('nav-list');
    nav.innerHTML = '';

    let shown = 0;
    Object.keys(data.tools).forEach(key => {
        const tool = data.tools[key];
        if (!astraaIsEntitled(tool.name, entitlements)) return;   // gate by entitlement
        shown++;

        const card = document.createElement('div');
        card.className = 'tool-card';
        card.innerHTML = `<div><strong>${tool.name}</strong></div>`;

        const live = ASTRAA_LIVE_MODULES.some(m => (tool.name||'').toLowerCase().includes(m));
        card.onclick = () => {
            if (key === 'comm' && typeof CommerceModule !== 'undefined') {
                document.getElementById('content-area').innerHTML = CommerceModule.render();
            } else if (live) {
                document.getElementById('content-area').innerHTML =
                    `<h3>${tool.name}</h3><p>Welcome to ${tool.name}. Select an action to begin.</p>`;
            } else {
                document.getElementById('content-area').innerHTML =
                    `<h3>${tool.name}</h3><p>This module is coming soon.</p>`;
            }
        };
        nav.appendChild(card);
    });

    if (shown === 0) {
        nav.innerHTML = '<div class="tool-card"><strong>No active tools</strong></div>';
        document.getElementById('content-area').innerHTML =
            '<h3>No active subscriptions</h3><p>Your account has no active tools yet. Visit pricing to subscribe.</p>';
    }
}

window.onload = initDashboard;
