function verifySession() {
    const session = localStorage.getItem('astraa_session');
    if (!session) {
        window.location.href = 'login.html';
        return null;
    }
    return JSON.parse(session);
}

function initDashboard() {
    const activeUser = verifySession();
    if (!activeUser) return;

    const data = window.AstraaBlueprint;
    document.getElementById('welcome-title').innerText = `WELCOME TO THE ${data.profile.company_name.toUpperCase()} COMMAND CENTER`;
    document.getElementById('welcome-subtitle').innerText = `OPERATIONAL HUB // ${activeUser.user.toUpperCase()} // ACTIVE`;
    document.getElementById('content-area').innerHTML = Dashboard.render();
    
    const nav = document.getElementById('nav-list');
    nav.innerHTML = '';
    
    Object.keys(data.tools).forEach(key => {
        const tool = data.tools[key];
        const card = document.createElement('div');
        card.className = 'tool-card';
        card.innerHTML = `<div><strong>${tool.name}</strong></div>`;
        card.onclick = () => {
            if (key === 'comm' && typeof CommerceModule !== 'undefined') {
                document.getElementById('content-area').innerHTML = CommerceModule.render();
            } else {
                document.getElementById('content-area').innerHTML = `<h3>${tool.name}</h3><p>Module active and operational.</p>`;
            }
        };
        nav.appendChild(card);
    });
}

window.onload = initDashboard;
