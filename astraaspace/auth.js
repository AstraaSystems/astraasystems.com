document.addEventListener('DOMContentLoaded', () => {
    const loginForm = document.getElementById('login-form');
    
    if (loginForm) {
        loginForm.addEventListener('submit', (e) => {
            e.preventDefault();
            const username = document.getElementById('username').value.trim();
            const password = document.getElementById('password').value.trim();
            const statusEl = document.getElementById('auth-status');

            // Hardcoded credentials for your private test environment
            const VALID_USER = "keshanth@astraasystems.com";
            const VALID_PASS = "AstraaSovereign2026!"; // Change this to whatever password you want

            if (username === VALID_USER && password === VALID_PASS) {
                statusEl.style.color = "#22c55e";
                statusEl.innerText = "AUTHENTICATING OPERATOR...";
                
                setTimeout(() => {
                    const sessionData = {
                        user: username.split('@')[0],
                        role: "Administrator",
                        token: "ASTRAA-SESSION-" + Date.now()
                    };
                    localStorage.setItem('astraa_session', JSON.stringify(sessionData));
                    window.location.href = 'index.html';
                }, 800);
            } else {
                statusEl.style.color = "#ef4444";
                statusEl.innerText = "CRITICAL ERROR: INVALID OPERATOR CREDENTIALS";
            }
        });
    }
});

function logoutAstraa() {
    localStorage.removeItem('astraa_session');
    window.location.href = 'login.html';
}
