#!/usr/bin/env python3
"""
Astraa Patch: Support Concierge Widget

PATCH SCRIPT.

Purpose:
- Add a floating non-bot support/contact widget to public Astraa pages.
- Let customers ask questions, request onboarding help, or request a call.
- Prepare future digital phone support without claiming it is live yet.

Does NOT:
- modify api.py
- change auth behavior
- change payment behavior
- deploy Astraa
- connect external chat/phone providers
"""

from __future__ import annotations

from pathlib import Path
from datetime import datetime
import re


ROOT = Path(".")
STAMP = datetime.now().strftime("%Y%m%d_%H%M%S")
BACKUP_DIR = ROOT / "SAFE_SNAPSHOTS" / f"support_concierge_widget_{STAMP}"

START = "<!-- ASTRAA_SUPPORT_CONCIERGE_V1_START -->"
END = "<!-- ASTRAA_SUPPORT_CONCIERGE_V1_END -->"

TARGETS = [
    Path("index.html"),
    Path("tools.html"),
    Path("pricing.html"),
    Path("support.html"),
    Path("contact.html"),
    Path("login.html"),
    Path("register.html"),
    Path("frontend/index.html"),
    Path("frontend/tools.html"),
    Path("frontend/pricing.html"),
    Path("frontend/support.html"),
    Path("frontend/contact.html"),
    Path("frontend/login.html"),
    Path("frontend/register.html"),
]

WIDGET = r"""
<!-- ASTRAA_SUPPORT_CONCIERGE_V1_START -->
<style>
  .astraa-concierge-button {
    position: fixed;
    right: 22px;
    bottom: 22px;
    z-index: 99998;
    border: none;
    border-radius: 999px;
    background: #0b1f3a;
    color: #ffffff;
    padding: 14px 18px;
    font-weight: 800;
    box-shadow: 0 18px 45px rgba(15, 23, 42, .22);
    cursor: pointer;
    font-family: inherit;
  }

  .astraa-concierge-button span {
    display: inline-block;
    margin-left: 6px;
    color: #bfdbfe;
  }

  .astraa-concierge-panel {
    position: fixed;
    right: 22px;
    bottom: 82px;
    width: min(390px, calc(100vw - 32px));
    z-index: 99999;
    background: #ffffff;
    border: 1px solid #dbe4f0;
    border-radius: 22px;
    box-shadow: 0 26px 70px rgba(15, 23, 42, .22);
    overflow: hidden;
    font-family: inherit;
    display: none;
  }

  .astraa-concierge-panel.open {
    display: block;
  }

  .astraa-concierge-head {
    background: linear-gradient(135deg, #0b1f3a, #1d4ed8);
    color: #ffffff;
    padding: 18px 20px;
  }

  .astraa-concierge-head strong {
    display: block;
    font-size: 1.05rem;
  }

  .astraa-concierge-head span {
    display: block;
    color: #dbeafe;
    margin-top: 4px;
    font-size: .9rem;
    line-height: 1.4;
  }

  .astraa-concierge-body {
    padding: 18px 20px 20px;
  }

  .astraa-concierge-note {
    color: #475569;
    line-height: 1.55;
    margin: 0 0 14px;
    font-size: .95rem;
  }

  .astraa-concierge-field {
    margin-bottom: 10px;
  }

  .astraa-concierge-field label {
    display: block;
    font-size: .82rem;
    color: #334155;
    font-weight: 800;
    margin-bottom: 5px;
  }

  .astraa-concierge-field input,
  .astraa-concierge-field select,
  .astraa-concierge-field textarea {
    width: 100%;
    box-sizing: border-box;
    border: 1px solid #dbe4f0;
    border-radius: 12px;
    padding: 10px 11px;
    font-family: inherit;
    font-size: .95rem;
    color: #111827;
    background: #ffffff;
  }

  .astraa-concierge-field textarea {
    min-height: 84px;
    resize: vertical;
  }

  .astraa-concierge-actions {
    display: grid;
    gap: 9px;
    margin-top: 12px;
  }

  .astraa-concierge-actions button,
  .astraa-concierge-actions a {
    text-align: center;
    text-decoration: none;
    border-radius: 12px;
    padding: 11px 12px;
    font-weight: 800;
    font-family: inherit;
  }

  .astraa-concierge-send {
    border: none;
    background: #1d4ed8;
    color: #ffffff;
    cursor: pointer;
  }

  .astraa-concierge-call {
    border: 1px solid #cbd5e1;
    background: #f8fafc;
    color: #0b1f3a;
  }

  .astraa-concierge-small {
    color: #64748b;
    font-size: .78rem;
    line-height: 1.45;
    margin-top: 10px;
  }

  @media (max-width: 520px) {
    .astraa-concierge-button {
      right: 16px;
      bottom: 16px;
    }

    .astraa-concierge-panel {
      right: 16px;
      bottom: 74px;
    }
  }
</style>

<button class="astraa-concierge-button" type="button" onclick="astraaToggleConcierge()" aria-label="Ask Astraa support">
  Ask Astraa <span>Support</span>
</button>

<section class="astraa-concierge-panel" id="astraaConciergePanel" aria-label="Astraa support concierge">
  <div class="astraa-concierge-head">
    <strong>Astraa Support Concierge</strong>
    <span>This is not a bot. Send your question to Astraa support or request onboarding help.</span>
  </div>

  <div class="astraa-concierge-body">
    <p class="astraa-concierge-note">
      Ask about tools, pricing, packages, onboarding, or controlled access. Please do not send passwords or payment card details here.
    </p>

    <div class="astraa-concierge-field">
      <label for="astraaSupportName">Name</label>
      <input id="astraaSupportName" type="text" placeholder="Your name">
    </div>

    <div class="astraa-concierge-field">
      <label for="astraaSupportEmail">Email</label>
      <input id="astraaSupportEmail" type="email" placeholder="you@example.com">
    </div>

    <div class="astraa-concierge-field">
      <label for="astraaSupportTopic">Topic</label>
      <select id="astraaSupportTopic">
        <option>Pricing or package question</option>
        <option>Estimator help</option>
        <option>Finance help</option>
        <option>Operations help</option>
        <option>Onboarding request</option>
        <option>Request a call</option>
        <option>Other support question</option>
      </select>
    </div>

    <div class="astraa-concierge-field">
      <label for="astraaSupportMessage">Question</label>
      <textarea id="astraaSupportMessage" placeholder="Tell Astraa what you need help with..."></textarea>
    </div>

    <div class="astraa-concierge-actions">
      <button class="astraa-concierge-send" type="button" onclick="astraaSendSupportEmail()">Send support request</button>
      <a class="astraa-concierge-call" href="mailto:support@astraasystems.com?subject=Astraa%20call%20request&body=Hi%20Astraa%20Support%2C%0A%0AI%20would%20like%20to%20request%20a%20call%20for%20onboarding%20or%20package%20guidance.%0A%0AName%3A%0APhone%3A%0ABusiness%2Forganization%3A%0ATools%20I%20am%20interested%20in%3A%0A%0AThank%20you.">Request a call</a>
    </div>

    <div class="astraa-concierge-small">
      Digital phone support is being prepared. Until a support number is connected, use the request form or call request option.
    </div>
  </div>
</section>

<script>
  function astraaToggleConcierge() {
    var panel = document.getElementById("astraaConciergePanel");
    if (!panel) return;
    panel.classList.toggle("open");
  }

  function astraaSendSupportEmail() {
    var name = document.getElementById("astraaSupportName")?.value || "";
    var email = document.getElementById("astraaSupportEmail")?.value || "";
    var topic = document.getElementById("astraaSupportTopic")?.value || "Support question";
    var message = document.getElementById("astraaSupportMessage")?.value || "";

    var subject = "Astraa support request - " + topic;
    var body = [
      "Hi Astraa Support,",
      "",
      "I have a question/request from the Astraa website.",
      "",
      "Name: " + name,
      "Email: " + email,
      "Topic: " + topic,
      "",
      "Question:",
      message,
      "",
      "Please follow up when available.",
      "",
      "Note: I understand this is not an automated bot and customer access remains controlled during launch hardening."
    ].join("\n");

    var mailto = "mailto:support@astraasystems.com"
      + "?subject=" + encodeURIComponent(subject)
      + "&body=" + encodeURIComponent(body);

    window.location.href = mailto;
  }
</script>
<!-- ASTRAA_SUPPORT_CONCIERGE_V1_END -->
""".strip() + "\n"


def remove_existing_block(text: str) -> str:
    pattern = re.compile(
        re.escape(START) + r".*?" + re.escape(END) + r"\s*",
        re.DOTALL,
    )
    return pattern.sub("", text)


def insert_before_body(text: str) -> str:
    lower = text.lower()
    if "</body>" in lower:
        idx = lower.rfind("</body>")
        return text[:idx] + WIDGET + "\n" + text[idx:]
    return text.rstrip() + "\n\n" + WIDGET


def patch_file(path: Path) -> bool:
    if not path.exists():
        print(f"SKIP missing: {path}")
        return False

    original = path.read_text(encoding="utf-8", errors="ignore")
    text = remove_existing_block(original)
    text = insert_before_body(text)

    if text == original:
        print(f"UNCHANGED: {path}")
        return False

    backup_path = BACKUP_DIR / path
    backup_path.parent.mkdir(parents=True, exist_ok=True)
    backup_path.write_text(original, encoding="utf-8")

    path.write_text(text, encoding="utf-8")
    print(f"PATCHED: {path}")
    return True


def main():
    print("=" * 100)
    print("ASTRAA SUPPORT CONCIERGE WIDGET PATCH")
    print("=" * 100)
    print("Mode: PATCH PUBLIC HTML ONLY")
    print("Backup directory:", BACKUP_DIR)

    changed = 0

    for path in TARGETS:
        if patch_file(path):
            changed += 1

    print("")
    print("Changed files:", changed)
    print("")
    print("Safety confirmation:")
    print("- This script did not modify api.py.")
    print("- This script did not change auth behavior.")
    print("- This script did not change payment behavior.")
    print("- This script did not deploy Astraa.")
    print("- This script did not connect external chat/phone providers.")


if __name__ == "__main__":
    main()
