#!/usr/bin/env python3
"""
Astraa Patch: Public Finance + Operations Pricing

PATCH SCRIPT.

Purpose:
- Add public-facing Finance and Operations pricing blocks to pricing/tool/package pages.
- Keep backend Moneris/payment enforcement unchanged.
- Keep public language clean: Tools, not Engines; no internal system names.

Targets:
- pricing.html / frontend/pricing.html
- tool-finance.html / frontend/tool-finance.html
- tool-operations.html / frontend/tool-operations.html
- pricing-nonprofit.html / frontend/pricing-nonprofit.html
- pricing-contractor.html / frontend/pricing-contractor.html
- pricing-franchise.html / frontend/pricing-franchise.html

Safety:
- Creates backups under SAFE_SNAPSHOTS/.
- Idempotent marker replacement.
- Does not modify api.py.
- Does not change payment logic.
"""

from __future__ import annotations

from pathlib import Path
from datetime import datetime
import re


ROOT = Path(".")
STAMP = datetime.now().strftime("%Y%m%d_%H%M%S")
BACKUP_DIR = ROOT / "SAFE_SNAPSHOTS" / f"public_finance_operations_pricing_{STAMP}"

START = "<!-- ASTRAA_PUBLIC_FINANCE_OPERATIONS_PRICING_V1_START -->"
END = "<!-- ASTRAA_PUBLIC_FINANCE_OPERATIONS_PRICING_V1_END -->"

TARGETS = [
    "pricing.html",
    "frontend/pricing.html",
    "tool-finance.html",
    "frontend/tool-finance.html",
    "tool-operations.html",
    "frontend/tool-operations.html",
    "pricing-nonprofit.html",
    "frontend/pricing-nonprofit.html",
    "pricing-contractor.html",
    "frontend/pricing-contractor.html",
    "pricing-franchise.html",
    "frontend/pricing-franchise.html",
]


COMMON_STYLE = """
<style>
  .astraa-pricing-insert {
    margin: 48px auto;
    max-width: 1180px;
    padding: 0 20px;
    font-family: inherit;
  }
  .astraa-pricing-insert .pricing-eyebrow {
    color: #1d4ed8;
    font-weight: 800;
    letter-spacing: .08em;
    text-transform: uppercase;
    font-size: .78rem;
    margin-bottom: 10px;
  }
  .astraa-pricing-insert h2 {
    color: #0b1f3a;
    font-size: clamp(1.8rem, 3vw, 2.6rem);
    margin: 0 0 12px;
    line-height: 1.12;
  }
  .astraa-pricing-insert .pricing-note {
    color: #475569;
    max-width: 820px;
    line-height: 1.7;
    margin-bottom: 22px;
  }
  .astraa-pricing-grid {
    display: grid;
    grid-template-columns: repeat(3, minmax(0, 1fr));
    gap: 18px;
  }
  .astraa-pricing-card {
    background: #fff;
    border: 1px solid #e5e7eb;
    border-radius: 18px;
    padding: 22px;
    box-shadow: 0 14px 35px rgba(15, 23, 42, .06);
  }
  .astraa-pricing-card.featured {
    border-color: rgba(29, 78, 216, .35);
    box-shadow: 0 18px 45px rgba(29, 78, 216, .12);
  }
  .astraa-pricing-card h3 {
    margin: 0 0 8px;
    color: #111827;
    font-size: 1.2rem;
  }
  .astraa-price {
    color: #0b1f3a;
    font-size: 1.8rem;
    font-weight: 900;
    margin: 8px 0;
  }
  .astraa-price span {
    color: #64748b;
    font-size: .95rem;
    font-weight: 600;
  }
  .astraa-pricing-card p {
    color: #475569;
    line-height: 1.55;
    margin: 8px 0 12px;
  }
  .astraa-pricing-card ul {
    margin: 0;
    padding-left: 18px;
    color: #334155;
    line-height: 1.6;
  }
  .astraa-bundle-row {
    margin-top: 18px;
    background: #f8fafc;
    border: 1px solid #e2e8f0;
    border-radius: 18px;
    padding: 20px;
  }
  .astraa-bundle-row strong {
    color: #0b1f3a;
  }
  @media (max-width: 900px) {
    .astraa-pricing-grid {
      grid-template-columns: 1fr;
    }
  }
</style>
""".strip()


FINANCE_BLOCK = """
<section class="astraa-pricing-insert" aria-label="Astraa Finance pricing">
  <div class="pricing-eyebrow">Astraa Finance</div>
  <h2>Simple financial control for growing businesses.</h2>
  <p class="pricing-note">
    Astraa Finance helps businesses organize cash flow, invoices, payment tracking, tax-ready records,
    and financial visibility without adding enterprise complexity.
  </p>
  <div class="astraa-pricing-grid">
    <article class="astraa-pricing-card">
      <h3>Finance Basic</h3>
      <div class="astraa-price">$29.99 <span>CAD/month</span></div>
      <p>For small and startup businesses that need clear financial tracking.</p>
      <ul>
        <li>Single user</li>
        <li>Basic finance workspace</li>
        <li>Invoice and payment visibility</li>
        <li>Simple reporting foundation</li>
      </ul>
    </article>
    <article class="astraa-pricing-card featured">
      <h3>Finance Professional</h3>
      <div class="astraa-price">$79.99 <span>CAD/month</span></div>
      <p>For growing businesses that need stronger financial control.</p>
      <ul>
        <li>Includes up to 3 users</li>
        <li>Milestone and payment tracking</li>
        <li>Business finance views</li>
        <li>Designed to connect with other Astraa tools</li>
      </ul>
    </article>
    <article class="astraa-pricing-card">
      <h3>Finance Custom</h3>
      <div class="astraa-price">Custom <span>quote</span></div>
      <p>For franchises, contractors, multi-location teams, or special reporting needs.</p>
      <ul>
        <li>Custom setup</li>
        <li>Multi-location options</li>
        <li>Special workflow support</li>
        <li>Package pricing available</li>
      </ul>
    </article>
  </div>
  <div class="astraa-bundle-row">
    <strong>Personal and non-profit options:</strong>
    Finance Personal is $24.99 CAD/month. Finance Non-Profit is $59.99 CAD/month, with additional startup discounts available by request for eligible new low-budget non-profits.
  </div>
</section>
""".strip()


OPERATIONS_BLOCK = """
<section class="astraa-pricing-insert" aria-label="Astraa Operations pricing">
  <div class="pricing-eyebrow">Astraa Operations</div>
  <h2>Operational coordination for teams, crews, and field workflows.</h2>
  <p class="pricing-note">
    Astraa Operations supports scheduling, job coordination, subcontractor workflows, field updates,
    location-aware work, and operational visibility for growing teams.
  </p>
  <div class="astraa-pricing-grid">
    <article class="astraa-pricing-card">
      <h3>Operations Basic</h3>
      <div class="astraa-price">$59.99 <span>CAD/month</span></div>
      <p>For small teams that need basic scheduling and job coordination.</p>
      <ul>
        <li>Single user</li>
        <li>Basic scheduling support</li>
        <li>Job coordination views</li>
        <li>Internal workflow foundation</li>
      </ul>
    </article>
    <article class="astraa-pricing-card featured">
      <h3>Operations Professional</h3>
      <div class="astraa-price">$149.99 <span>CAD/month</span></div>
      <p>For growing teams managing people, work, and field updates.</p>
      <ul>
        <li>Includes up to 5 users</li>
        <li>Crew and subcontractor coordination</li>
        <li>Certification and field-update workflow concepts</li>
        <li>Designed for operational visibility</li>
      </ul>
    </article>
    <article class="astraa-pricing-card">
      <h3>Operations Plus</h3>
      <div class="astraa-price">$299.99 <span>CAD/month</span></div>
      <p>For larger operations that need deeper coordination and reporting.</p>
      <ul>
        <li>Includes up to 10 users</li>
        <li>Multi-location workflow support</li>
        <li>Staging, SLA, and check-in workflow concepts</li>
        <li>Custom package path available</li>
      </ul>
    </article>
  </div>
  <div class="astraa-bundle-row">
    <strong>Operations Custom:</strong>
    Custom quotes are available for contractors, franchises, non-profits, multi-company setups, high-volume teams, and special packages.
  </div>
</section>
""".strip()


BUNDLE_BLOCK = """
<section class="astraa-pricing-insert" aria-label="Astraa bundle pricing">
  <div class="pricing-eyebrow">Astraa Bundles</div>
  <h2>Package pricing for businesses that want more than one tool.</h2>
  <p class="pricing-note">
    Astraa tools can be used individually or combined into practical packages for business, operations,
    contractor, franchise, and custom setups.
  </p>
  <div class="astraa-pricing-grid">
    <article class="astraa-pricing-card">
      <h3>Business Starter</h3>
      <div class="astraa-price">$59.99 <span>CAD/month</span></div>
      <p>Estimator Basic + Finance Basic.</p>
    </article>
    <article class="astraa-pricing-card">
      <h3>Business Professional</h3>
      <div class="astraa-price">$159.99 <span>CAD/month</span></div>
      <p>Estimator Professional + Finance Professional.</p>
    </article>
    <article class="astraa-pricing-card featured">
      <h3>Contractor Professional</h3>
      <div class="astraa-price">$279.99 <span>CAD/month</span></div>
      <p>Estimator Professional + Finance Professional + Operations Professional.</p>
    </article>
  </div>
  <div class="astraa-bundle-row">
    <strong>Operations Bundle:</strong> Finance Professional + Operations Professional is $199.99 CAD/month.
    <br>
    <strong>Custom Suite:</strong> Custom pricing is available for selected tools, users, contractors, franchise/multi-location setup, and special configurations.
  </div>
</section>
""".strip()


NONPROFIT_BLOCK = """
<section class="astraa-pricing-insert" aria-label="Astraa non-profit pricing">
  <div class="pricing-eyebrow">Non-Profit Pricing</div>
  <h2>Practical pricing for organizations that need structure without heavy overhead.</h2>
  <div class="astraa-pricing-grid">
    <article class="astraa-pricing-card featured">
      <h3>Finance Non-Profit</h3>
      <div class="astraa-price">$59.99 <span>CAD/month</span></div>
      <p>A standard non-profit package between Finance Basic and Finance Professional.</p>
      <ul>
        <li>Designed for simple financial organization</li>
        <li>Useful for small teams and growing programs</li>
        <li>Startup discount requests available by email</li>
      </ul>
    </article>
    <article class="astraa-pricing-card">
      <h3>Operations Custom</h3>
      <div class="astraa-price">Custom <span>quote</span></div>
      <p>For non-profits with staff, volunteers, locations, programs, or field coordination needs.</p>
    </article>
    <article class="astraa-pricing-card">
      <h3>Custom Package</h3>
      <div class="astraa-price">Custom <span>quote</span></div>
      <p>Combine selected Astraa tools based on organization size and budget.</p>
    </article>
  </div>
</section>
""".strip()


CONTRACTOR_BLOCK = """
<section class="astraa-pricing-insert" aria-label="Astraa contractor package pricing">
  <div class="pricing-eyebrow">Contractor Packages</div>
  <h2>Pricing for estimating, finance, and operations in one workflow.</h2>
  <div class="astraa-pricing-grid">
    <article class="astraa-pricing-card">
      <h3>Operations Professional</h3>
      <div class="astraa-price">$149.99 <span>CAD/month</span></div>
      <p>For crews, subcontractors, scheduling, and field-update workflows.</p>
    </article>
    <article class="astraa-pricing-card featured">
      <h3>Contractor Professional</h3>
      <div class="astraa-price">$279.99 <span>CAD/month</span></div>
      <p>Estimator Professional + Finance Professional + Operations Professional.</p>
    </article>
    <article class="astraa-pricing-card">
      <h3>Contractor Custom</h3>
      <div class="astraa-price">Custom <span>quote</span></div>
      <p>For multi-crew, franchise, multi-company, or special contractor setups.</p>
    </article>
  </div>
</section>
""".strip()


FRANCHISE_BLOCK = """
<section class="astraa-pricing-insert" aria-label="Astraa franchise pricing">
  <div class="pricing-eyebrow">Franchise & Multi-Location Packages</div>
  <h2>Custom pricing for multi-location and franchise operations.</h2>
  <div class="astraa-pricing-grid">
    <article class="astraa-pricing-card">
      <h3>Finance Custom</h3>
      <div class="astraa-price">Custom <span>quote</span></div>
      <p>For multi-location financial views, reporting needs, and custom workflows.</p>
    </article>
    <article class="astraa-pricing-card">
      <h3>Operations Custom</h3>
      <div class="astraa-price">Custom <span>quote</span></div>
      <p>For location isolation, team coordination, and operational visibility.</p>
    </article>
    <article class="astraa-pricing-card featured">
      <h3>Custom Suite</h3>
      <div class="astraa-price">Custom <span>quote</span></div>
      <p>Any selected tools, users, contractors, franchise structure, and package setup.</p>
    </article>
  </div>
</section>
""".strip()


def combined_block(kind: str) -> str:
    if kind == "pricing":
        body = "\n\n".join([COMMON_STYLE, FINANCE_BLOCK, OPERATIONS_BLOCK, BUNDLE_BLOCK])
    elif kind == "finance":
        body = "\n\n".join([COMMON_STYLE, FINANCE_BLOCK])
    elif kind == "operations":
        body = "\n\n".join([COMMON_STYLE, OPERATIONS_BLOCK])
    elif kind == "nonprofit":
        body = "\n\n".join([COMMON_STYLE, NONPROFIT_BLOCK])
    elif kind == "contractor":
        body = "\n\n".join([COMMON_STYLE, CONTRACTOR_BLOCK])
    elif kind == "franchise":
        body = "\n\n".join([COMMON_STYLE, FRANCHISE_BLOCK])
    else:
        body = COMMON_STYLE

    return f"{START}\n{body}\n{END}\n"


def classify(path: Path) -> str:
    name = path.name.lower()

    if name == "pricing.html":
        return "pricing"
    if "tool-finance" in name:
        return "finance"
    if "tool-operations" in name or "tool-operation" in name:
        return "operations"
    if "pricing-nonprofit" in name:
        return "nonprofit"
    if "pricing-contractor" in name:
        return "contractor"
    if "pricing-franchise" in name:
        return "franchise"

    return "pricing"


def remove_existing_block(text: str) -> str:
    pattern = re.compile(
        re.escape(START) + r".*?" + re.escape(END) + r"\s*",
        re.DOTALL,
    )
    return pattern.sub("", text)


def insert_block(text: str, block: str) -> str:
    lower = text.lower()

    if "</main>" in lower:
        idx = lower.rfind("</main>")
        return text[:idx] + block + "\n" + text[idx:]

    if "</body>" in lower:
        idx = lower.rfind("</body>")
        return text[:idx] + block + "\n" + text[idx:]

    return text.rstrip() + "\n\n" + block


def patch_file(path: Path) -> bool:
    if not path.exists():
        print(f"SKIP missing: {path}")
        return False

    text = path.read_text(encoding="utf-8", errors="ignore")
    original = text

    kind = classify(path)
    block = combined_block(kind)

    text = remove_existing_block(text)
    text = insert_block(text, block)

    if text == original:
        print(f"UNCHANGED: {path}")
        return False

    backup_path = BACKUP_DIR / path
    backup_path.parent.mkdir(parents=True, exist_ok=True)
    backup_path.write_text(original, encoding="utf-8")

    path.write_text(text, encoding="utf-8")
    print(f"PATCHED: {path} ({kind})")
    return True


def main():
    print("=" * 100)
    print("ASTRAA PUBLIC FINANCE + OPERATIONS PRICING PATCH")
    print("=" * 100)
    print("Mode: PATCH PUBLIC HTML ONLY")
    print("Backend payment enforcement: unchanged")
    print("Backup directory:", BACKUP_DIR)

    changed = 0

    for item in TARGETS:
        if patch_file(Path(item)):
            changed += 1

    print("\nChanged files:", changed)
    print("\nSafety confirmation:")
    print("- This script did not modify api.py.")
    print("- This script did not change Moneris/payment logic.")
    print("- This script did not deploy Astraa.")
    print("- Backups were written under SAFE_SNAPSHOTS/.")


if __name__ == "__main__":
    main()
