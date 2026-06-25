from __future__ import annotations

import json
from pathlib import Path

REPORT_DIR = Path("/mnt/d/ARKA_HQ/reports")

reports = sorted(
    REPORT_DIR.glob("ASTRAA_WEBSITE_FILE_HYGIENE_AUDIT_*.json"),
    key=lambda p: p.stat().st_mtime,
    reverse=True,
)

if not reports:
    raise SystemExit("No ASTRAA_WEBSITE_FILE_HYGIENE_AUDIT JSON report found.")

latest = reports[0]
data = json.loads(latest.read_text(encoding="utf-8-sig"))

print("[REPORT]", latest)
print("Total web-like files:", data.get("total_web_like_files"))
print("Recommended active/review count:", data.get("recommended_active_count"))
print("Recommended excluded count:", data.get("recommended_excluded_count"))
print()

rows = data.get("rows", [])

def show(category: str, limit: int = 200):
    selected = [r for r in rows if r.get("category") == category]
    print(f"================ {category} ({len(selected)}) ================")
    for r in selected[:limit]:
        print(f"- {r.get('path')}  [{r.get('reason')}]")
    print()

for category in [
    "active_public_root",
    "active_public_tool_page",
    "active_public_asset_or_template",
    "needs_review_root_web_file",
    "needs_review_public_legacy",
    "unknown_review",
    "internal_or_non_public",
    "generated_runtime_or_patch",
]:
    show(category)
