#!/usr/bin/env python3
"""
Astraa Patch: Public Marketing Metadata

PATCH SCRIPT.

Purpose:
- Add/refresh safe SEO and social-share metadata on key public pages.
- Help Astraa public pages describe themselves clearly for search and sharing.
- Keep public language clean and professional.

Does NOT:
- modify backend/auth/payment logic
- send emails
- post to social media
- deploy Astraa
"""

from __future__ import annotations

from pathlib import Path
from datetime import datetime
import re


ROOT = Path(".")
STAMP = datetime.now().strftime("%Y%m%d_%H%M%S")
BACKUP_DIR = ROOT / "SAFE_SNAPSHOTS" / f"public_marketing_metadata_{STAMP}"

START = "<!-- ASTRAA_PUBLIC_MARKETING_METADATA_V1_START -->"
END = "<!-- ASTRAA_PUBLIC_MARKETING_METADATA_V1_END -->"

PAGE_META = {
    "index.html": {
        "title": "Astraa Systems | Business Tools for Estimating, Finance, Operations, and Growth",
        "description": "Astraa Systems provides clean, modular business tools for estimating, finance, operations, workspace access, and practical business growth.",
    },
    "tools.html": {
        "title": "Astraa Tools | Modular Business Software for Teams and Operations",
        "description": "Explore Astraa tools for estimating, finance, operations, expense tracking, commerce, data, inference, distribution, and secure workspace workflows.",
    },
    "pricing.html": {
        "title": "Astraa Pricing | Estimator, Finance, Operations, and Business Packages",
        "description": "Review Astraa launch pricing for Estimator, Finance, Operations, and practical business packages for contractors, franchises, non-profits, and growing teams.",
    },
    "tool-finance.html": {
        "title": "Astraa Finance | Simple Financial Control for Growing Businesses",
        "description": "Astraa Finance helps businesses organize cash flow, invoices, payment tracking, tax-ready records, and practical financial visibility.",
    },
    "tool-operations.html": {
        "title": "Astraa Operations | Scheduling, Coordination, and Field Workflow Tools",
        "description": "Astraa Operations supports scheduling, crew coordination, subcontractor workflows, field updates, and operational visibility for teams.",
    },
    "pricing-contractor.html": {
        "title": "Astraa Contractor Pricing | Estimator, Finance, and Operations Packages",
        "description": "Astraa contractor packages combine estimating, finance, and operations tools for teams that need practical business coordination.",
    },
    "pricing-nonprofit.html": {
        "title": "Astraa Non-Profit Pricing | Practical Tools for Lean Organizations",
        "description": "Astraa offers practical pricing paths for non-profits that need financial organization, operations support, and controlled workspace access.",
    },
    "pricing-franchise.html": {
        "title": "Astraa Franchise Pricing | Multi-Location and Custom Business Packages",
        "description": "Astraa supports franchise and multi-location teams with custom tool packages for finance, operations, workspace access, and business workflows.",
    },
    "contact.html": {
        "title": "Contact Astraa Systems | Request Access or Ask About Packages",
        "description": "Contact Astraa Systems to ask about tools, pricing, custom packages, demos, and controlled access for your business or organization.",
    },
    "trial.html": {
        "title": "Astraa Trial | Explore Astraa Tools with Controlled Access",
        "description": "Explore Astraa trial access for selected tools while customer access remains controlled during launch hardening.",
    },
}


def meta_block(title: str, description: str, file_name: str) -> str:
    url_path = "/" if file_name == "index.html" else f"/{file_name}"

    return f"""{START}
<title>{title}</title>
<meta name="description" content="{description}">
<meta property="og:title" content="{title}">
<meta property="og:description" content="{description}">
<meta property="og:type" content="website">
<meta property="og:site_name" content="Astraa Systems">
<meta property="og:url" content="https://astraasystems.com{url_path}">
<meta name="twitter:card" content="summary_large_image">
<meta name="twitter:title" content="{title}">
<meta name="twitter:description" content="{description}">
<link rel="canonical" href="https://astraasystems.com{url_path}">
{END}
"""


def remove_existing_marketing_block(text: str) -> str:
    pattern = re.compile(
        re.escape(START) + r".*?" + re.escape(END) + r"\s*",
        re.DOTALL,
    )
    return pattern.sub("", text)


def remove_basic_title_description(text: str) -> str:
    # Remove simple existing title/description to reduce duplicate search snippets.
    text = re.sub(r"<title>.*?</title>\s*", "", text, count=1, flags=re.IGNORECASE | re.DOTALL)
    text = re.sub(r'<meta\s+name=["\']description["\']\s+content=["\'].*?["\']\s*/?>\s*', "", text, count=1, flags=re.IGNORECASE | re.DOTALL)
    return text


def patch_one(path: Path, title: str, description: str) -> bool:
    if not path.exists():
        print(f"SKIP missing: {path}")
        return False

    original = path.read_text(encoding="utf-8", errors="ignore")
    text = remove_existing_marketing_block(original)
    text = remove_basic_title_description(text)

    block = meta_block(title, description, path.name)

    lower = text.lower()
    if "<head" in lower:
        head_end = lower.find(">")
        insert_pos = head_end + 1
        text = text[:insert_pos] + "\n" + block + text[insert_pos:]
    else:
        text = block + text

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
    print("ASTRAA PUBLIC MARKETING METADATA PATCH")
    print("=" * 100)
    print("Mode: PATCH PUBLIC HTML METADATA ONLY")
    print("Backup directory:", BACKUP_DIR)

    changed = 0

    for file_name, meta in PAGE_META.items():
        for path in [Path(file_name), Path("frontend") / file_name]:
            if patch_one(path, meta["title"], meta["description"]):
                changed += 1

    print("\nChanged files:", changed)
    print("\nSafety confirmation:")
    print("- This script did not modify api.py.")
    print("- This script did not change backend/auth/payment logic.")
    print("- This script did not send marketing messages.")
    print("- This script did not post to social media.")
    print("- This script did not deploy Astraa.")


if __name__ == "__main__":
    main()
