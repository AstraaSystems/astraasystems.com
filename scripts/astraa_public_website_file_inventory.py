#!/usr/bin/env python3
"""
Astraa Public Website File Inventory

READ-ONLY SCRIPT.

Purpose:
- Inventory public website files before marketing/public launch.
- Identify likely homepage/tool/pricing/legal/workspace pages.
- Scan for public wording risks and internal-name exposure risks.
- Scan local href references and report missing local targets.

Does NOT:
- modify website files
- deploy Astraa
- change backend behavior
- change auth/payment behavior
"""

from __future__ import annotations

from pathlib import Path
from datetime import datetime, timezone
from collections import Counter
import json
import re


ROOT = Path(".")
HTML_EXTENSIONS = {".html", ".htm"}

IGNORE_DIRS = {
    ".git",
    "venv",
    "__pycache__",
    "astraa_data",
    "SAFE_SNAPSHOTS",
    "deployment_templates",
}

PUBLIC_PAGE_KEYWORDS = {
    "homepage": ["index.html", "home"],
    "tools": ["tools", "estimator", "finance", "vault", "business", "commerce", "data", "inference", "distribution", "expense", "operations"],
    "pricing": ["pricing", "plans", "package"],
    "legal": ["privacy", "terms", "refund", "payment"],
    "workspace": ["workspace", "login", "register", "portal"],
    "contact": ["contact", "trial", "demo"],
}

PUBLIC_WORDING_RISK_TERMS = [
    "Arka",
    "Lux",
    "Aruhan",
    "Arkastra",
    "engine",
    "internal AI",
    "Oracle AI",
    "Arkastra AI",
    "Aruhan AI",
    "dev-login",
    "/api/auth/dev-login",
    "ASTRAA_ALLOW_DEV_LOGIN_PUBLIC_MODE",
    "ASTRAA_PUBLIC_LAUNCH_MODE",
    "localhost",
    "127.0.0.1",
]

REQUIRED_PUBLIC_AREAS = [
    "homepage",
    "tools",
    "pricing",
    "legal",
    "workspace",
    "contact",
]


HREF_RE = re.compile(r'href=["\']([^"\']+)["\']', re.IGNORECASE)


def section(title):
    print("\n" + "=" * 100)
    print(title)
    print("=" * 100)


def should_ignore(path: Path) -> bool:
    return any(part in IGNORE_DIRS for part in path.parts)


def html_files():
    files = []
    for path in ROOT.rglob("*"):
        if should_ignore(path):
            continue
        if path.is_file() and path.suffix.lower() in HTML_EXTENSIONS:
            files.append(path)
    return sorted(files)


def classify_page(path: Path):
    lower = str(path).lower()
    labels = []

    for label, terms in PUBLIC_PAGE_KEYWORDS.items():
        if any(term.lower() in lower for term in terms):
            labels.append(label)

    if path.name.lower() == "index.html":
        labels.append("homepage")

    return sorted(set(labels)) or ["unclassified"]


def scan_risk_terms(path: Path):
    text = path.read_text(encoding="utf-8", errors="ignore")
    hits = []

    for idx, line in enumerate(text.splitlines(), 1):
        matched = [term for term in PUBLIC_WORDING_RISK_TERMS if term.lower() in line.lower()]
        if matched:
            hits.append({
                "file": str(path),
                "line": idx,
                "matched": matched,
                "text": line.strip()[:300],
            })

    return hits


def extract_hrefs(path: Path):
    text = path.read_text(encoding="utf-8", errors="ignore")
    return HREF_RE.findall(text)


def is_external_href(href: str) -> bool:
    lower = href.lower()
    return (
        lower.startswith("http://")
        or lower.startswith("https://")
        or lower.startswith("mailto:")
        or lower.startswith("tel:")
        or lower.startswith("#")
        or lower.startswith("javascript:")
    )


def local_href_target(path: Path, href: str):
    clean = href.split("#", 1)[0].split("?", 1)[0].strip()

    if not clean:
        return None

    if clean.startswith("/"):
        return ROOT / clean.lstrip("/")

    return (path.parent / clean).resolve()


def scan_local_links(files):
    missing = []
    all_refs = []

    root_resolved = ROOT.resolve()

    for path in files:
        for href in extract_hrefs(path):
            all_refs.append({
                "file": str(path),
                "href": href,
            })

            if is_external_href(href):
                continue

            target = local_href_target(path, href)
            if target is None:
                continue

            try:
                target.relative_to(root_resolved)
            except Exception:
                continue

            if not target.exists():
                missing.append({
                    "file": str(path),
                    "href": href,
                    "expected_target": str(target),
                })

    return all_refs, missing


def main():
    section("ASTRAA PUBLIC WEBSITE FILE INVENTORY")
    print("Mode: READ ONLY")
    print("Time:", datetime.now(timezone.utc).isoformat().replace("+00:00", "Z"))
    print("Repository root:", ROOT.resolve())

    files = html_files()

    section("HTML FILES FOUND")
    print("HTML file count:", len(files))
    for path in files:
        print("-", path)

    section("PAGE CLASSIFICATION")
    coverage = Counter()
    page_records = []

    for path in files:
        labels = classify_page(path)
        for label in labels:
            coverage[label] += 1

        record = {
            "file": str(path),
            "labels": labels,
        }
        page_records.append(record)
        print(json.dumps(record, indent=2, sort_keys=True))

    section("PUBLIC AREA COVERAGE")
    for area in REQUIRED_PUBLIC_AREAS:
        print(f"{area}: {coverage.get(area, 0)}")

    section("PUBLIC WORDING / INTERNAL EXPOSURE RISK SCAN")
    all_risks = []
    for path in files:
        all_risks.extend(scan_risk_terms(path))

    if not all_risks:
        print("No risk terms found in HTML files.")
    else:
        print("Risk hits:", len(all_risks))
        for item in all_risks:
            print(json.dumps(item, indent=2, sort_keys=True))

    section("LOCAL HREF LINK CHECK")
    all_refs, missing = scan_local_links(files)

    print("Total href references:", len(all_refs))
    print("Missing local href targets:", len(missing))

    if missing:
        for item in missing:
            print(json.dumps(item, indent=2, sort_keys=True))
    else:
        print("No missing local href targets found.")

    section("QA NOTES")
    print("- Review risk hits manually. Some terms may be acceptable in legal/internal-only pages, but not public marketing pages.")
    print("- Public pages should avoid internal names and implementation details.")
    print("- Workspace links should remain controlled until production auth and managed DB are complete.")
    print("- External links are not validated by this script.")

    section("READ-ONLY CONFIRMATION")
    print("This script did not modify website files.")
    print("This script did not deploy Astraa.")
    print("This script did not change backend behavior.")
    print("This script did not change auth/payment behavior.")


if __name__ == "__main__":
    main()
