from __future__ import annotations

import json
import os
from pathlib import Path

REPORT_DIR = Path(os.getenv("ARKA_REPORT_DIR", "/mnt/d/ARKA_HQ/reports"))

def _latest_hygiene_report() -> Path | None:
    reports = sorted(
        REPORT_DIR.glob("ASTRAA_WEBSITE_FILE_HYGIENE_AUDIT_*.json"),
        key=lambda p: p.stat().st_mtime,
        reverse=True,
    )
    return reports[0] if reports else None

def _load_latest() -> dict | None:
    latest = _latest_hygiene_report()
    if not latest:
        return None
    try:
        return json.loads(latest.read_text(encoding="utf-8-sig"))
    except Exception:
        return None

def astraa_website_hygiene_answer(raw: str = "") -> str:
    data = _load_latest()

    if not data:
        return (
            "Astraa Website File Hygiene — Governor Route\n\n"
            "I routed this as an internal Astraa website hygiene question, not a web search.\n\n"
            "No latest hygiene audit report was found. Run `python3 astraa_website_file_hygiene_audit.py` from the repo root first."
        )

    counts = data.get("category_counts", {})
    total = data.get("total_web_like_files", 0)
    active_review = data.get("recommended_active_count", 0)
    excluded = data.get("recommended_excluded_count", 0)

    active_core = (
        counts.get("active_public_root", 0)
        + counts.get("active_public_tool_page", 0)
        + counts.get("active_public_asset_or_template", 0)
    )

    needs_review = (
        counts.get("needs_review_root_web_file", 0)
        + counts.get("needs_review_public_legacy", 0)
    )

    lines = [
        "Astraa Website File Hygiene — Governor Route",
        "",
        "I routed this as an internal Astraa website file hygiene question, not a web search.",
        "",
        "Current hygiene summary:",
        f"- Total web-like files found: {total}",
        f"- Active public/core files: {active_core}",
        f"- Needs human review: {needs_review}",
        f"- Recommended active/review count: {active_review}",
        f"- Recommended excluded count: {excluded}",
        "",
        "Category counts:",
    ]

    for key, value in sorted(counts.items(), key=lambda x: (-x[1], x[0])):
        lines.append(f"- {key}: {value}")

    lines.extend([
        "",
        "How to bring the count down properly:",
        "1. Do not delete files first.",
        "2. Count only active public root pages, active tool pages, and public assets as active website files.",
        "3. Review the 12 root review files and 4 public legacy files manually.",
        "4. Exclude internal/system/generated/runtime files from the public website count.",
        "5. Treat frontend duplicates and receipts as non-public unless intentionally promoted.",
        "",
        "Clean interpretation:",
        f"- Public/core active files: {active_core}",
        f"- Active plus review queue: {active_review}",
        f"- Excluded from public website count: {excluded}",
    ])

    return "\n".join(lines)
