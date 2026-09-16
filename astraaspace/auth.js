// Astraa Space — real passkey login (Path 1)
const ASTRAA_API_BASE = window.ASTRAA_API_BASE || "https://family-speed-outcome.ngrok-free.dev";

var ASTRAA_LOGIN_MODE = "account";
function astraaSetLoginMode(mode){
  ASTRAA_LOGIN_MODE = mode;
  var a=document.getElementById('tab-account'), u=document.getElementById('tab-user');
  var on="flex:1;padding:9px;border-radius:8px;border:1px solid #1d4ed8;background:#1d4ed8;color:#fff;font-weight:700;cursor:pointer;font-size:.82rem;";
  var off="flex:1;padding:9px;border-radius:8px;border:1px solid #334155;background:transparent;color:#94a3b8;font-weight:700;cursor:pointer;font-size:.82rem;";
  if(a&&u){ a.style.cssText=(mode==='account'?on:off); u.style.cssText=(mode==='user'?on:off); }
  var lbl=document.querySelector('label[for="username"]');
  if(lbl) lbl.innerText = (mode==='user') ? "Your Email" : "Operator ID / Email";
}

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
      var _ep = (ASTRAA_LOGIN_MODE === "user") ? "/api/auth/user-login" : "/api/auth/dev-login";
      const res = await fetch(ASTRAA_API_BASE + _ep, {
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
          entitlements: data.entitlements || [],
          login_mode: ASTRAA_LOGIN_MODE,
          role: data.role || null,
          departments: data.departments || [],
          tools: data.tools || []
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
