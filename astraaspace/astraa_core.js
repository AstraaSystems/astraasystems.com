// Astraa Space core — all 9 tools; 4 live, 5 coming soon
const ASTRAA_API_BASE = window.ASTRAA_API_BASE || "https://family-speed-outcome.ngrok-free.dev";

// Tools that are fully built and usable today
const ASTRAA_LIVE_MODULES = ["estimator", "finance", "operations", "expense"];
// Where "coming soon" tools route requests
const ASTRAA_REQUEST_EMAIL = "sales@astraasystems.com";

function verifySession() {
    const session = localStorage.getItem('astraa_session');
    if (!session) { window.location.href = 'login.html'; return null; }
    try { return JSON.parse(session); }
    catch (e) { window.location.href = 'login.html'; return null; }
}

function astraaIsLive(toolName) {
    const n = (toolName || "").toLowerCase();
    return ASTRAA_LIVE_MODULES.some(m => n.includes(m));
}

function initDashboard() {
    const activeUser = verifySession();
    if (!activeUser) return;

    const data = window.AstraaBlueprint;

    document.getElementById('welcome-title').innerText =
        `WELCOME TO THE ${data.profile.company_name.toUpperCase()} COMMAND CENTER`;
    document.getElementById('welcome-subtitle').innerText =
        `OPERATIONAL HUB // ${(activeUser.user || '').toUpperCase()} // ACTIVE`;

    document.getElementById('content-area').innerHTML = Dashboard.render();

    const nav = document.getElementById('nav-list');
    nav.innerHTML = '';

    Object.keys(data.tools).forEach(key => {
        const tool = data.tools[key];
        const live = astraaIsLive(tool.name);

        const card = document.createElement('div');
        card.className = 'tool-card';
        card.innerHTML = live
            ? `<div><strong>${tool.name}</strong></div>`
            : `<div><strong>${tool.name}</strong> <span style="font-size:0.7rem;color:#f59e0b;font-weight:700;">• COMING SOON</span></div>`;

        card.onclick = () => {
            const area = document.getElementById('content-area');
            if (live) {
                if (key === 'comm' && typeof CommerceModule !== 'undefined') {
                    area.innerHTML = CommerceModule.render();
                } else {
                    area.innerHTML =
                        `<h3>${tool.name}</h3>` +
                        `<p>Welcome to ${tool.name}. This tool is active on your account. Select an action to begin.</p>`;
                }
            } else {
                area.innerHTML =
                    `<h3>${tool.name} <span style="font-size:0.9rem;color:#f59e0b;">— Coming Soon</span></h3>` +
                    `<p>${tool.name} is in active development and not yet available.</p>` +
                    `<p>Interested in early access or a custom deployment? ` +
                    `<a href="mailto:${ASTRAA_REQUEST_EMAIL}?subject=Request access to ${encodeURIComponent(tool.name)}f6/a></p>`;
            }
        };
        nav.appendChild(card);
    });
}

window.onload = initDashboard;
