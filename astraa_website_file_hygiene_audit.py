from __future__ import annotations

import csv
import json
import os
import time
from pathlib import Path

ROOT = Path(os.getenv("ARKA_HQ_ROOT", "/mnt/d/ARKA_HQ/repos/ardhanarishvara_git"))
REPORT_DIR = Path(os.getenv("ARKA_REPORT_DIR", "/mnt/d/ARKA_HQ/reports"))
REPORT_DIR.mkdir(parents=True, exist_ok=True)

stamp = time.strftime("%Y%m%d_%H%M%S")
REPORT_JSON = REPORT_DIR / f"ASTRAA_WEBSITE_FILE_HYGIENE_AUDIT_{stamp}.json"
REPORT_CSV = REPORT_DIR / f"ASTRAA_WEBSITE_FILE_HYGIENE_AUDIT_{stamp}.csv"
REPORT_MD = REPORT_DIR / f"ASTRAA_WEBSITE_FILE_HYGIENE_AUDIT_{stamp}.md"

WEB_SUFFIXES = {".html", ".css", ".js", ".json", ".svg", ".png", ".jpg", ".jpeg", ".webp", ".ico", ".txt", ".xml"}

SKIP_ALWAYS = {
    ".git",
    ".venv",
    ".venv_win",
    ".venv_wsl",
    "__pycache__",
    "node_modules",
    ".pytest_cache",
}

ACTIVE_PUBLIC_HINTS = {
    "index.html",
    "about.html",
    "contact.html",
    "pricing.html",
    "privacy.html",
    "terms.html",
    "register.html",
    "login.html",
    "customer-portal.html",
    "workspace-internal.html",
    "payment.html",
    "payment-success.html",
    "estimator-faq.html",
    "faq.html",
    "trial.html",
    "trial-terms.html",
    "tools.html",
}

ACTIVE_TOOL_PAGE_HINTS = {
    "tool-estimator.html",
    "tool-finance.html",
    "tool-operations.html",
    "tool-commerce.html",
    "tool-data.html",
    "tool-inference.html",
    "tool-distribution.html",
    "tool-vault.html",
    "tool-expense.html",
}

PUBLIC_DIR_HINTS = {
    "public",
    "static",
    "assets",
    "templates",
    "netlify",
    "functions",
}

INTERNAL_DIR_HINTS = {
    "arka_v1",
    "arka_personal_ai_v04_evolution",
    "ArdhanarishvaraOS",
    "aruhan_intelligence",
    "astraa_access",
    "legal",
    "ARCHIVE_LEGACY",
    "reports",
    "docs",
    "tests",
    "scripts",
    "audit",
    "logs",
    "context",
    "reflection",
    "governance",
    "infrastructure",
    "entities",
    "agents",
    "autonomy",
}

GENERATED_OR_RUNTIME_HINTS = {
    "generated",
    "runtime",
    "state",
    "memory",
    "ledger",
    "audit",
    "report",
    "backup",
    "patch",
    "repair",
    "hotfix",
}

OLD_PUBLIC_LANGUAGE_HINTS = {
    "engines.html",
    "tool-inference.html",
    "workspace-internal.html",
}

def rel(p: Path) -> str:
    try:
        return str(p.relative_to(ROOT)).replace("\\", "/")
    except Exception:
        return str(p)

def should_skip(p: Path) -> bool:
    parts = set(p.parts)
    return bool(parts & SKIP_ALWAYS)

def classify(p: Path) -> tuple[str, str]:
    r = rel(p)
    lower = r.lower()
    name = p.name

    # exact active root pages
    if "/" not in r and name in ACTIVE_PUBLIC_HINTS:
        return "active_public_root", "known public root page"

    if "/" not in r and name in ACTIVE_TOOL_PAGE_HINTS:
        return "active_public_tool_page", "known public tool page"

    # active public directories
    first = r.split("/", 1)[0]
    if first in PUBLIC_DIR_HINTS:
        return "active_public_asset_or_template", f"under public-style folder: {first}"

    # likely backend web/business support
    if name in {"api.py", "wsgi.py", "lead_capture.py", "astraa_arka_bridge.py", "netlify.toml"}:
        return "website_backend_support", "backend/deployment support file"

    # internal/system folders
    if first in INTERNAL_DIR_HINTS:
        return "internal_or_non_public", f"under internal/system folder: {first}"

    # generated/runtime/patch/backup
    if any(h in lower for h in GENERATED_OR_RUNTIME_HINTS):
        return "generated_runtime_or_patch", "generated/runtime/patch/backup naming"

    # old public pages that need human review
    if name in OLD_PUBLIC_LANGUAGE_HINTS:
        return "needs_review_public_legacy", "public-ish legacy/current page needs review"

    # root web file not known active
    if "/" not in r and p.suffix.lower() in WEB_SUFFIXES:
        return "needs_review_root_web_file", "root web file not in active canon list"

    return "unknown_review", "not clearly classified"

def main():
    rows = []
    for p in ROOT.rglob("*"):
        if should_skip(p):
            continue
        if not p.is_file():
            continue
        if p.suffix.lower() not in WEB_SUFFIXES:
            continue

        category, reason = classify(p)
        rows.append({
            "path": rel(p),
            "name": p.name,
            "suffix": p.suffix.lower(),
            "category": category,
            "reason": reason,
            "size": p.stat().st_size,
        })

    counts = {}
    for row in rows:
        counts[row["category"]] = counts.get(row["category"], 0) + 1

    report = {
        "timestamp": stamp,
        "root": str(ROOT),
        "total_web_like_files": len(rows),
        "category_counts": dict(sorted(counts.items(), key=lambda x: (-x[1], x[0]))),
        "rows": rows,
        "recommended_active_count": sum(
            1 for r in rows
            if r["category"] in {
                "active_public_root",
                "active_public_tool_page",
                "active_public_asset_or_template",
                "website_backend_support",
                "needs_review_public_legacy",
                "needs_review_root_web_file",
            }
        ),
        "recommended_excluded_count": sum(
            1 for r in rows
            if r["category"] in {
                "internal_or_non_public",
                "generated_runtime_or_patch",
                "unknown_review",
            }
        ),
    }

    REPORT_JSON.write_text(json.dumps(report, indent=2), encoding="utf-8")

    with REPORT_CSV.open("w", encoding="utf-8", newline="") as f:
        writer = csv.DictWriter(f, fieldnames=["path", "name", "suffix", "category", "reason", "size"])
        writer.writeheader()
        writer.writerows(rows)

    lines = []
    lines.append("# Astraa Website File Hygiene Audit")
    lines.append("")
    lines.append(f"- Total web-like files: **{report['total_web_like_files']}**")
    lines.append(f"- Recommended active/review count: **{report['recommended_active_count']}**")
    lines.append(f"- Recommended excluded count: **{report['recommended_excluded_count']}**")
    lines.append("")
    lines.append("## Category Counts")
    for k, v in report["category_counts"].items():
        lines.append(f"- `{k}`: {v}")

    lines.append("")
    lines.append("## Recommended Interpretation")
    lines.append("- Do not delete files from this report directly.")
    lines.append("- Reduce the website count by updating the website audit to count only active/review categories.")
    lines.append("- Internal/system/generated/patch files should not count as Astraa public website files.")
    lines.append("- Review root legacy pages before archiving.")

    lines.append("")
    lines.append("## Needs Review")
    for row in rows:
        if row["category"].startswith("needs_review"):
            lines.append(f"- `{row['path']}` — {row['reason']}")

    REPORT_MD.write_text("\n".join(lines), encoding="utf-8")

    print("[OK] Astraa website file hygiene audit complete.")
    print("[JSON]", REPORT_JSON)
    print("[CSV]", REPORT_CSV)
    print("[MD]", REPORT_MD)
    print("")
    print("Total web-like files:", report["total_web_like_files"])
    print("Recommended active/review count:", report["recommended_active_count"])
    print("Recommended excluded count:", report["recommended_excluded_count"])
    print("")
    print("Category counts:")
    for k, v in report["category_counts"].items():
        print("-", k, v)

if __name__ == "__main__":
    main()
