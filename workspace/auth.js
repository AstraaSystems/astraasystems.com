document.addEventListener('DOMContentLoaded', () => {
    const loginForm = document.getElementById('login-form');
    
    if (loginForm) {
        loginForm.addEventListener('submit', (e) => {
            e.preventDefault();
            const username = document.getElementById('username').value.trim();
            const password = document.getElementById('password').value.trim();
            const statusEl = document.getElementById('auth-status');

            if (username && password) {
                statusEl.style.color = "#22c55e";
                statusEl.innerText = "AUTHENTICATING OPERATOR...";
                
                setTimeout(() => {
                    const sessionData = {
                        user: username,
                        role: "Administrator",
                        token: "ASTRAA-SESSION-" + Date.now()
                    };
                    localStorage.setItem('astraa_session', JSON.stringify(sessionData));
                    window.location.href = 'index.html';
                }, 800);
            } else {
                statusEl.innerText = "Error: Please provide valid credentials.";
            }
        });
    }
});

function logoutAstraa() {
    localStorage.removeItem('astraa_session');
    window.location.href = 'login.html';
}
