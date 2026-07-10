// Astraa Space — real passkey login (Path 1)
const ASTRAA_API_BASE = window.ASTRAA_API_BASE || "https://family-speed-outcome.ngrok-free.dev";

document.addEventListener('DOMContentLoaded', () => {
  const loginForm = document.getElementById('login-form');
  if (!loginForm) return;

  loginForm.addEventListener('submit', async (e) => {
    e.preventDefault();
    const email = document.getElementById('username').value.trim();
    const passkey = document.getElementById('password').value.trim();
    const statusEl = document.getElementById('auth-status');

    statusEl.style.color = "#38bdf8";
    statusEl.innerText = "AUTHENTICATING OPERATOR...";

    try {
      const res = await fetch(ASTRAA_API_BASE + "/api/auth/login", {
        method: "POST",
        headers: {
          "Content-Type": "application/json",
          "ngrok-skip-browser-warning": "true"
        },
        body: JSON.stringify({ email, passkey })
      });
      const data = await res.json();

      if (res.ok && data.status === "ok" && data.token) {
        statusEl.style.color = "#22c55e";
        statusEl.innerText = "SESSION INITIALIZED";
        localStorage.setItem('astraa_session', JSON.stringify({
          user: email.split('@')[0],
          email: email,
          token: data.token,
          plan: data.selected_plan,
          entitlements: data.entitlements || []
        }));
        setTimeout(() => { window.location.href = 'index.html'; }, 600);
      } else {
        statusEl.style.color = "#ef4444";
        statusEl.innerText = (data.reason || "INVALID CREDENTIALS").toUpperCase();
      }
    } catch (err) {
      statusEl.style.color = "#ef4444";
      statusEl.innerText = "CONNECTION ERROR — TRY AGAIN";
      console.error(err);
    }
  });
});

function logoutAstraa() {
  localStorage.removeItem('astraa_session');
  window.location.href = 'login.html';
}
