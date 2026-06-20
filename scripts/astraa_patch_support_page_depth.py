#!/usr/bin/env python3
"""
Astraa Patch: Support Page Depth

PATCH SCRIPT.

Purpose:
- Add stronger public-facing support information to support.html and frontend/support.html.
- Improve marketing-launch support readiness.
- Explain support topics, tool questions, pricing/package help, controlled access, and contact guidance.

Does NOT:
- modify api.py
- change auth behavior
- change payment behavior
- deploy Astraa
"""

from __future__ import annotations

from pathlib import Path
from datetime import datetime
import re


ROOT = Path(".")
STAMP = datetime.now().strftime("%Y%m%d_%H%M%S")
BACKUP_DIR = ROOT / "SAFE_SNAPSHOTS" / f"support_page_depth_{STAMP}"

TARGETS = [
    Path("support.html"),
    Path("frontend/support.html"),
]

START = "<!-- ASTRAA_SUPPORT_PAGE_DEPTH_V1_START -->"
END = "<!-- ASTRAA_SUPPORT_PAGE_DEPTH_V1_END -->"

SUPPORT_BLOCK = r"""
<!-- ASTRAA_SUPPORT_PAGE_DEPTH_V1_START -->
<style>
  .astraa-support-depth {
    max-width: 1180px;
    margin: 48px auto;
    padding: 0 20px;
    font-family: inherit;
  }

  .astraa-support-depth .support-eyebrow {
    color: #1d4ed8;
    font-size: .78rem;
    font-weight: 800;
    letter-spacing: .08em;
    text-transform: uppercase;
    margin-bottom: 10px;
  }

  .astraa-support-depth h2 {
    color: #0b1f3a;
    font-size: clamp(1.8rem, 3vw, 2.55rem);
    line-height: 1.12;
    margin: 0 0 12px;
  }

  .astraa-support-depth .support-note {
    color: #475569;
    max-width: 850px;
    line-height: 1.7;
    margin: 0 0 24px;
  }

  .astraa-support-grid {
    display: grid;
    grid-template-columns: repeat(3, minmax(0, 1fr));
    gap: 18px;
    margin: 24px 0;
  }

  .astraa-support-card {
    background: #ffffff;
    border: 1px solid #e5e7eb;
    border-radius: 18px;
    padding: 22px;
    box-shadow: 0 14px 35px rgba(15, 23, 42, .06);
  }

  .astraa-support-card.featured {
    border-color: rgba(29, 78, 216, .35);
    box-shadow: 0 18px 45px rgba(29, 78, 216, .12);
  }

  .astraa-support-card h3 {
    margin: 0 0 8px;
    color: #111827;
    font-size: 1.15rem;
  }

  .astraa-support-card p,
  .astraa-support-card li {
    color: #475569;
    line-height: 1.6;
  }

  .astraa-support-card ul {
    margin: 10px 0 0;
    padding-left: 18px;
  }

  .astraa-support-band {
    background: #f8fafc;
    border: 1px solid #e2e8f0;
    border-radius: 18px;
    padding: 22px;
    margin: 22px 0;
  }

  .astraa-support-band h3 {
    color: #0b1f3a;
    margin: 0 0 10px;
  }

  .astraa-support-faq {
    display: grid;
    grid-template-columns: 1fr 1fr;
    gap: 16px;
    margin-top: 20px;
  }

  .astraa-support-faq .faq-item {
    border: 1px solid #e5e7eb;
    border-radius: 16px;
    padding: 18px;
    background: #fff;
  }

  .astraa-support-faq strong {
    display: block;
    color: #111827;
    margin-bottom: 8px;
  }

  .astraa-support-faq span {
    color: #475569;
    line-height: 1.6;
  }

  @media (max-width: 900px) {
    .astraa-support-grid,
    .astraa-support-faq {
      grid-template-columns: 1fr;
    }
  }
</style>

<section class="astraa-support-depth" aria-label="Astraa support information">
  <div class="support-eyebrow">Support</div>
  <h2>How Astraa support can help</h2>
  <p class="support-note">
    Astraa support is here to help businesses understand tools, pricing, packages, trial access,
    and controlled Workspace setup. Public marketing access is moving forward carefully while paid
    customer SaaS access remains controlled until production authentication, managed database,
    deployment secrets, and deployed payment regression are complete.
  </p>

  <div class="astraa-support-grid">
    <article class="astraa-support-card featured">
      <h3>Tool and package questions</h3>
      <p>Ask which Astraa tools fit your business stage, team size, or workflow.</p>
      <ul>
        <li>Estimator, Finance, and Operations guidance</li>
        <li>Business, contractor, franchise, and non-profit packages</li>
        <li>Custom package discussions</li>
      </ul>
    </article>

    <article class="astraa-support-card">
      <h3>Pricing and plan help</h3>
      <p>Use support to clarify launch pricing, package fit, and upgrade paths.</p>
      <ul>
        <li>Estimator Basic and Professional</li>
        <li>Finance Basic, Professional, Personal, and Non-Profit</li>
        <li>Operations Basic, Professional, Plus, and Custom</li>
      </ul>
    </article>

    <article class="astraa-support-card">
      <h3>Access and trial questions</h3>
      <p>Customer access is introduced carefully while the production foundation is completed.</p>
      <ul>
        <li>Trial/access interest</li>
        <li>Workspace account questions</li>
        <li>Controlled onboarding and package requests</li>
      </ul>
    </article>
  </div>

  <div class="astraa-support-band">
    <h3>Current access status</h3>
    <p>
      Astraa’s public website can move through marketing visibility, but broad paid customer SaaS
      onboarding is not open yet. Production authentication, managed database setup, secure deployment
      secrets, host/TLS configuration, and deployed Moneris regression remain required before broad
      paid access.
    </p>
  </div>

  <div class="astraa-support-grid">
    <article class="astraa-support-card">
      <h3>What to include when contacting support</h3>
      <ul>
        <li>Your business or organization type</li>
        <li>Which tools you are interested in</li>
        <li>Team size or number of users</li>
        <li>Whether you need a standard plan or custom package</li>
        <li>Any contractor, franchise, non-profit, or multi-location needs</li>
      </ul>
    </article>

    <article class="astraa-support-card">
      <h3>Best fit examples</h3>
      <ul>
        <li>Small business: Estimator or Finance Basic</li>
        <li>Growing team: Professional plans or Business Professional bundle</li>
        <li>Contractor team: Contractor Professional package</li>
        <li>Franchise or multi-location team: Custom Suite</li>
      </ul>
    </article>

    <article class="astraa-support-card">
      <h3>Responsible launch approach</h3>
      <p>
        Astraa is being launched carefully: public website first, controlled access next,
        and broad paid SaaS onboarding only after production systems are fully proven.
      </p>
    </article>
  </div>

  <div class="astraa-support-faq">
    <div class="faq-item">
      <strong>Can I use Astraa right now?</strong>
      <span>
        You can review the public website, pricing, and tools. Customer tool access is controlled
        while production systems continue through final hardening.
      </span>
    </div>

    <div class="faq-item">
      <strong>Which tools are available in pricing?</strong>
      <span>
        Estimator, Finance, and Operations now have visible launch pricing. Custom packages are
        available for contractors, franchises, non-profits, and special setups.
      </span>
    </div>

    <div class="faq-item">
      <strong>Is paid SaaS onboarding fully open?</strong>
      <span>
        Not yet. Broad paid SaaS access remains blocked until production auth, managed database,
        deployed secrets, host/TLS, and deployed payment regression are complete.
      </span>
    </div>

    <div class="faq-item">
      <strong>How do I ask for a custom package?</strong>
      <span>
        Contact Astraa with your business type, team size, desired tools, and any contractor,
        franchise, non-profit, or multi-location requirements.
      </span>
    </div>

    <div class="faq-item">
      <strong>Does Astraa support non-profits?</strong>
      <span>
        Yes. Finance Non-Profit pricing is available, and very new low-budget non-profits can
        request additional startup discount review.
      </span>
    </div>

    <div class="faq-item">
      <strong>Does Astraa support contractors and field teams?</strong>
      <span>
        Yes. Operations and Contractor Professional packages are designed for teams that need
        estimating, finance, scheduling, coordination, and field workflow visibility.
      </span>
    </div>
  </div>
</section>
<!-- ASTRAA_SUPPORT_PAGE_DEPTH_V1_END -->
""".strip() + "\n"


def remove_existing_block(text: str) -> str:
    pattern = re.compile(
        re.escape(START) + r".*?" + re.escape(END) + r"\s*",
        re.DOTALL,
    )
    return pattern.sub("", text)


def insert_block(text: str) -> str:
    lower = text.lower()

    if "</main>" in lower:
        idx = lower.rfind("</main>")
        return text[:idx] + SUPPORT_BLOCK + "\n" + text[idx:]

    if "</body>" in lower:
        idx = lower.rfind("</body>")
        return text[:idx] + SUPPORT_BLOCK + "\n" + text[idx:]

    return text.rstrip() + "\n\n" + SUPPORT_BLOCK


def patch_file(path: Path) -> bool:
    if not path.exists():
        print(f"SKIP missing: {path}")
        return False

    original = path.read_text(encoding="utf-8", errors="ignore")
    text = remove_existing_block(original)
    text = insert_block(text)

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
    print("ASTRAA SUPPORT PAGE DEPTH PATCH")
    print("=" * 100)
    print("Mode: PATCH PUBLIC SUPPORT HTML ONLY")
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


if __name__ == "__main__":
    main()
