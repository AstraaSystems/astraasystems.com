#!/usr/bin/env python3
"""
Astraa Patch: Paid Conversion CTAs

PATCH SCRIPT.

Purpose:
- Add paid-first customer conversion CTAs to public pages.
- Make clear that trial is available, but paid onboarding/plans are the primary path.
- Route customer interest to support@astraasystems.com via mailto for controlled onboarding.

Does NOT:
- modify api.py
- change Moneris/payment enforcement
- change backend/auth/payment behavior
- deploy Astraa
"""

from __future__ import annotations

from pathlib import Path
from datetime import datetime
import re


ROOT = Path(".")
STAMP = datetime.now().strftime("%Y%m%d_%H%M%S")
BACKUP_DIR = ROOT / "SAFE_SNAPSHOTS" / f"paid_conversion_ctas_{STAMP}"

START = "<!-- ASTRAA_PAID_CONVERSION_CTA_V1_START -->"
END = "<!-- ASTRAA_PAID_CONVERSION_CTA_V1_END -->"

TARGETS = [
    Path("index.html"),
    Path("pricing.html"),
    Path("support.html"),
    Path("contact.html"),
    Path("tools.html"),
    Path("frontend/index.html"),
    Path("frontend/pricing.html"),
    Path("frontend/support.html"),
    Path("frontend/contact.html"),
    Path("frontend/tools.html"),
]

CTA_BLOCK = r"""
<!-- ASTRAA_PAID_CONVERSION_CTA_V1_START -->
<style>
  .astraa-paid-cta {
    max-width: 1180px;
    margin: 44px auto;
    padding: 0 20px;
    font-family: inherit;
  }

  .astraa-paid-cta-inner {
    background: linear-gradient(135deg, #0b1f3a, #1d4ed8);
    color: #ffffff;
    border-radius: 24px;
    padding: clamp(24px, 4vw, 42px);
    box-shadow: 0 24px 70px rgba(15, 23, 42, .22);
  }

  .astraa-paid-cta .eyebrow {
    color: #bfdbfe;
    font-size: .78rem;
    font-weight: 900;
    letter-spacing: .08em;
    text-transform: uppercase;
    margin-bottom: 10px;
  }

  .astraa-paid-cta h2 {
    margin: 0 0 12px;
    font-size: clamp(1.8rem, 3vw, 2.7rem);
    line-height: 1.1;
  }

  .astraa-paid-cta p {
    color: #e0ecff;
    line-height: 1.7;
    max-width: 860px;
    margin: 0 0 18px;
  }

  .astraa-paid-cta-actions {
    display: flex;
    flex-wrap: wrap;
    gap: 12px;
    margin-top: 18px;
  }

  .astraa-paid-cta-actions a {
    display: inline-flex;
    align-items: center;
    justify-content: center;
    text-decoration: none;
    border-radius: 999px;
    padding: 12px 18px;
    font-weight: 900;
  }

  .astraa-paid-primary {
    background: #ffffff;
    color: #0b1f3a;
  }

  .astraa-paid-secondary {
    background: rgba(255, 255, 255, .12);
    color: #ffffff;
    border: 1px solid rgba(255, 255, 255, .35);
  }

  .astraa-paid-cta-grid {
    display: grid;
    grid-template-columns: repeat(3, minmax(0, 1fr));
    gap: 12px;
    margin-top: 22px;
  }

  .astraa-paid-mini {
    background: rgba(255, 255, 255, .1);
    border: 1px solid rgba(255, 255, 255, .22);
    border-radius: 16px;
    padding: 14px;
    color: #eff6ff;
  }

  .astraa-paid-mini strong {
    display: block;
    color: #ffffff;
    margin-bottom: 5px;
  }

  @media (max-width: 900px) {
    .astraa-paid-cta-grid {
      grid-template-columns: 1fr;
    }
  }
</style>

<section class="astraa-paid-cta" aria-label="Astraa paid onboarding">
  <div class="astraa-paid-cta-inner">
    <div class="eyebrow">Start with a paid plan</div>
    <h2>Trial is available — but paid onboarding gets Astraa working for your business faster.</h2>
    <p>
      Astraa is built for businesses that want practical tools for estimating, finance, operations,
      and workspace coordination. You can request trial access for evaluation, or ask Astraa to help
      choose the right paid plan or package for your business.
    </p>

    <div class="astraa-paid-cta-actions">
      <a class="astraa-paid-primary" href="mailto:support@astraasystems.com?subject=Astraa paid onboarding request&body=Hi Astraa Support,

I am interested in starting with a paid Astraa plan or package.

Business/organization:
Tools I am interested in:
Preferred package:
Team size:
Phone number:
Questions:

Thank you.">Request paid onboarding</a>

      <a class="astraa-paid-secondary" href="pricing.html">View pricing</a>

      <a class="astraa-paid-secondary" href="mailto:support@astraasystems.com?subject=Astraa trial or package question&body=Hi Astraa Support,

I would like help choosing between trial access and a paid Astraa plan.

Business/organization:
Tools I am interested in:
Questions:

Thank you.">Ask Astraa first</a>
    </div>

    <div class="astraa-paid-cta-grid">
      <div class="astraa-paid-mini">
        <strong>Paid plan request</strong>
        Choose Estimator, Finance, Operations, or a package and request setup guidance.
      </div>
      <div class="astraa-paid-mini">
        <strong>Controlled trial</strong>
        Trial access is available for evaluation, but customer access is introduced carefully.
      </div>
      <div class="astraa-paid-mini">
        <strong>Custom packages</strong>
        Contractors, franchises, non-profits, and multi-location teams can request a custom setup.
      </div>
    </div>
  </div>
</section>
<!-- ASTRAA_PAID_CONVERSION_CTA_V1_END -->
""".strip() + "\n"


def remove_existing_block(text: str) -> str:
    pattern = re.compile(
        re.escape(START) + r".*?" + re.escape(END) + r"\s*",
        re.DOTALL,
    )
    return pattern.sub("", text)


def insert_block(text: str) -> str:
    lower = text.lower()

    # Prefer before support concierge if present, so paid CTA stays in content flow.
    concierge_marker = "<!-- astraa_support_concierge_v1_start -->"
    idx = lower.find(concierge_marker)
    if idx != -1:
        return text[:idx] + CTA_BLOCK + "\n" + text[idx:]

    if "</main>" in lower:
        idx = lower.rfind("</main>")
        return text[:idx] + CTA_BLOCK + "\n" + text[idx:]

    if "</body>" in lower:
        idx = lower.rfind("</body>")
        return text[:idx] + CTA_BLOCK + "\n" + text[idx:]

    return text.rstrip() + "\n\n" + CTA_BLOCK


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
    print("ASTRAA PAID CONVERSION CTA PATCH")
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
    print("- This script did not change Moneris/payment enforcement.")
    print("- This script did not change backend/auth/payment behavior.")
    print("- This script did not deploy Astraa.")


if __name__ == "__main__":
    main()
