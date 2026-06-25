from __future__ import annotations

import json
import os
import re
import sqlite3
import subprocess
import sys
import time
from pathlib import Path

REPO = Path(r"D:\ARKA_HQ\repos\ardhanarishvara_git")
REPORT_DIR = Path(r"D:\ARKA_HQ\reports")
DATA_DIR = Path(r"D:\ARKA_HQ\data")
DB_PATH = DATA_DIR / "arka_core.db"

REPORT_DIR.mkdir(parents=True, exist_ok=True)

timestamp = time.strftime("%Y%m%d_%H%M%S")

REPORT_JSON = REPORT_DIR / f"ARKA_ECOSYSTEM_GAP_AUDIT_{timestamp}.json"
REPORT_MD = REPORT_DIR / f"ARKA_ECOSYSTEM_GAP_AUDIT_{timestamp}.md"

EXPECTED = {
    "Arka V1 Core": [
        "arka_v1/arka_v1.py",
        "arka_v1/start_arka_v1.ps1",
        "arka_v1/arka_memory.json",
        "arka_v1/arka_state.json",
    ],
    "Math OS": [
        "arka_v1/arka_math_os.py",
    ],
    "Arka Live Legacy": [
        "arka_live_v06/arka_live.py",
        "arka_live_v06/start_arka_live.ps1",
    ],
    "Astraa Bridge / Leads": [
        "astraa_arka_bridge.py",
        "lead_capture.py",
    ],
    "Runtime / API": [
        "api.py",
        "wsgi.py",
    ],
    "Aruhan / Autonomy": [
        "aruhan_runtime_loop.py",
    ],
    "Estimator / Tools": [
        "elite_estimator_module.py",
        "elite_estimator_v2.py",
        "arka_ardhanarishvara_estimator_integration.py",
    ],
    "Readiness / Audit": [
        "audit_state.py",
    ],
}

KEYWORDS = {
    "Astraa Website": [
        "astraa",
        "workspace",
        "pricing",
        "trial",
        "tools",
        "estimator",
        "finance",
        "operations",
        "commerce",
        "vault",
    ],
    "Old Website Language": [
        "Explore Engines",
        "Astraa Engines",
        "Full-Stack AI Automation",
        "Business Operation Engine",
        "Financial Engine",
        "Construction Engine",
        "Data Oracle Stream",
        "API Inference Layer",
    ],
    "Arka Brain": [
        "universal_context",
        "context brain",
        "Math OS",
        "Product CEO",
        "Revenue AI",
        "Astraa Growth AI",
        "skill registry",
        "brain kernel",
    ],
}

PY_EXCLUDE = [
    ".git",
    ".venv",
    "__pycache__",
    "node_modules",
    "migration_backups",
]

def rel(path: Path) -> str:
    try:
        return str(path.relative_to(REPO)).replace("\\", "/")
    except Exception:
        return str(path)

def exists_rel(p: str) -> bool:
    return (REPO / p).exists()

def run_cmd(cmd: str):
    try:
        p = subprocess.run(
            cmd,
            cwd=str(REPO),
            shell=True,
            text=True,
            capture_output=True,
            timeout=90,
        )
        return {
            "ok": p.returncode == 0,
            "returncode": p.returncode,
            "stdout": p.stdout.strip(),
            "stderr": p.stderr.strip(),
        }
    except Exception as e:
        return {
            "ok": False,
            "returncode": -1,
            "stdout": "",
            "stderr": str(e),
        }

def safe_read(path: Path, limit=300000):
    try:
        text = path.read_text(encoding="utf-8-sig", errors="ignore")
        return text[:limit]
    except Exception:
        return ""

def should_skip(path: Path) -> bool:
    s = str(path)
    return any(x in s for x in PY_EXCLUDE)

def list_files():
    files = []
    for p in REPO.rglob("*"):
        if should_skip(p):
            continue
        if p.is_file():
            files.append(p)
    return files

def python_files(files):
    return [p for p in files if p.suffix.lower() == ".py"]

def site_files(files):
    allowed = {".html", ".css", ".js", ".py", ".jinja", ".jinja2", ".json"}
    return [p for p in files if p.suffix.lower() in allowed]

def syntax_check(py_files):
    results = []
    for p in py_files:
        try:
            code = compile(safe_read(p), str(p), "exec")
            results.append({"file": rel(p), "ok": True, "error": ""})
        except Exception as e:
            results.append({"file": rel(p), "ok": False, "error": str(e)})
    return results

def expected_check():
    sections = {}
    for section, paths in EXPECTED.items():
        rows = []
        for p in paths:
            rows.append({
                "path": p,
                "exists": exists_rel(p),
            })
        sections[section] = rows
    return sections

def keyword_scan(files):
    output = {}
    candidates = site_files(files)

    for category, terms in KEYWORDS.items():
        matches = []
        for p in candidates:
            text = safe_read(p)
            if not text:
                continue

            for term in terms:
                if term.lower() in text.lower():
                    matches.append({
                        "file": rel(p),
                        "term": term,
                    })
                    break

        output[category] = matches[:200]

    return output

def arka_state_scan():
    arka_dir = REPO / "arka_v1"
    state_path = arka_dir / "arka_state.json"
    memory_path = arka_dir / "arka_memory.json"
    registry_path = arka_dir / "arka_module_registry.json"

    out = {}

    for name, path in [
        ("state", state_path),
        ("memory", memory_path),
        ("module_registry", registry_path),
    ]:
        if not path.exists():
            out[name] = {"exists": False}
            continue

        try:
            data = json.loads(path.read_text(encoding="utf-8-sig"))
            summary = {"exists": True}

            if isinstance(data, dict):
                for key, value in data.items():
                    if isinstance(value, list):
                        summary[key] = len(value)
                    elif isinstance(value, dict):
                        summary[key] = len(value.keys())
                    else:
                        summary[key] = type(value).__name__

            out[name] = summary
        except Exception as e:
            out[name] = {"exists": True, "error": str(e)}

    return out

def db_scan():
    if not DB_PATH.exists():
        return {"exists": False}

    out = {"exists": True, "tables": {}}

    try:
        conn = sqlite3.connect(str(DB_PATH))
        cur = conn.cursor()

        cur.execute("SELECT name FROM sqlite_master WHERE type='table'")
        tables = [x[0] for x in cur.fetchall()]

        for table in tables:
            try:
                cur.execute(f"SELECT COUNT(*) FROM {table}")
                count = cur.fetchone()[0]
                out["tables"][table] = count
            except Exception as e:
                out["tables"][table] = str(e)

        conn.close()
    except Exception as e:
        out["error"] = str(e)

    return out

def duplicate_patch_scan(files):
    backups = []
    patches = []
    for p in files:
        name = p.name.lower()
        if "backup" in name or ".backup" in name:
            backups.append(rel(p))
        if name.startswith("patch_") or name.startswith("repair_") or name.startswith("hotfix_"):
            patches.append(rel(p))
    return {
        "backup_files": backups[:300],
        "backup_count": len(backups),
        "patch_files": patches[:300],
        "patch_count": len(patches),
    }

def readiness_score(report):
    """
    This is a heuristic checklist, not a certified score.
    """
    checks = []

    def add(name, ok, note=""):
        checks.append({"name": name, "ok": bool(ok), "note": note})

    expected = report["expected_files"]

    for section, rows in expected.items():
        missing = [r["path"] for r in rows if not r["exists"]]
        add(f"Expected files: {section}", not missing, "Missing: " + ", ".join(missing) if missing else "")

    syntax_failures = [x for x in report["python_syntax"] if not x["ok"]]
    add("Python syntax health", len(syntax_failures) == 0, f"{len(syntax_failures)} syntax issue(s)")

    state = report["arka_state"]
    add("Arka state file", state.get("state", {}).get("exists", False), "")
    add("Arka memory file", state.get("memory", {}).get("exists", False), "")
    add("Arka module registry", state.get("module_registry", {}).get("exists", False), "")

    db = report["database"]
    add("Arka SQLite DB", db.get("exists", False), "")
    add("Conversation/journal table present", "arka_conversation_journal" in db.get("tables", {}), "")
    add("Logs table present", "arka_logs" in db.get("tables", {}), "")

    old_lang_count = len(report["keyword_scan"].get("Old Website Language", []))
    add("Old website language cleared", old_lang_count == 0, f"{old_lang_count} match(es) found")

    backup_count = report["duplicates"]["backup_count"]
    add("Patch/backups clutter controlled", backup_count < 25, f"{backup_count} backup file(s) found")

    ok_count = sum(1 for c in checks if c["ok"])
    total = len(checks)

    return {
        "checks": checks,
        "ok_count": ok_count,
        "total": total,
        "heuristic_percent": round((ok_count / total) * 100, 1) if total else 0,
    }

def gap_recommendations(report):
    recs = []

    for section, rows in report["expected_files"].items():
        missing = [r["path"] for r in rows if not r["exists"]]
        if missing:
            recs.append({
                "area": section,
                "severity": "high",
                "finding": "Missing expected file(s): " + ", ".join(missing),
                "recommendation": "Restore or rebuild only the missing file(s), not the whole ecosystem.",
            })

    syntax_failures = [x for x in report["python_syntax"] if not x["ok"]]
    for fail in syntax_failures[:20]:
        recs.append({
            "area": "Python syntax",
            "severity": "high",
            "finding": f"{fail['file']} has syntax error: {fail['error']}",
            "recommendation": "Fix syntax before adding new features.",
        })

    old_lang = report["keyword_scan"].get("Old Website Language", [])
    if old_lang:
        recs.append({
            "area": "Astraa website",
            "severity": "medium",
            "finding": f"Old engine/positioning language found in {len(old_lang)} file match(es).",
            "recommendation": "Update public wording from old engine language to current Tools / Workspace positioning.",
        })

    if not report["database"].get("exists"):
        recs.append({
            "area": "Data/logging",
            "severity": "high",
            "finding": "Arka SQLite database not found.",
            "recommendation": "Start Arka once or initialize DB so logs/memory/journal can persist.",
        })

    duplicates = report["duplicates"]
    if duplicates["backup_count"] >= 25:
        recs.append({
            "area": "Repository hygiene",
            "severity": "medium",
            "finding": f"{duplicates['backup_count']} backup files found.",
            "recommendation": "Move old backup/patch files into an archive folder after verifying current stable state.",
        })

    if not recs:
        recs.append({
            "area": "Overall",
            "severity": "info",
            "finding": "No major missing blanks detected by this audit.",
            "recommendation": "Freeze current state and move to V2 Brain Kernel / skill registry design.",
        })

    return recs

def write_markdown(report):
    lines = []

    lines.append("# ARKA / ASTRAA Local Ecosystem Gap Audit")
    lines.append("")
    lines.append(f"- Timestamp: `{report['timestamp']}`")
    lines.append(f"- Repo: `{report['repo']}`")
    lines.append("")

    lines.append("## Readiness Snapshot")
    readiness = report["readiness"]
    lines.append(f"- Heuristic readiness: **{readiness['heuristic_percent']}%**")
    lines.append(f"- Checks passed: **{readiness['ok_count']} / {readiness['total']}**")
    lines.append("")
    for check in readiness["checks"]:
        mark = "✅" if check["ok"] else "⚠️"
        note = f" — {check['note']}" if check.get("note") else ""
        lines.append(f"- {mark} {check['name']}{note}")

    lines.append("")
    lines.append("## Missing / Gap Recommendations")
    for rec in report["recommendations"]:
        lines.append("")
        lines.append(f"### {rec['area']} — {rec['severity']}")
        lines.append(f"- Finding: {rec['finding']}")
        lines.append(f"- Recommendation: {rec['recommendation']}")

    lines.append("")
    lines.append("## Expected Files")
    for section, rows in report["expected_files"].items():
        lines.append("")
        lines.append(f"### {section}")
        for row in rows:
            mark = "✅" if row["exists"] else "❌"
            lines.append(f"- {mark} `{row['path']}`")

    lines.append("")
    lines.append("## Python Syntax Issues")
    fails = [x for x in report["python_syntax"] if not x["ok"]]
    if not fails:
        lines.append("- ✅ No Python syntax issues detected.")
    else:
        for fail in fails:
            lines.append(f"- ❌ `{fail['file']}` — {fail['error']}")

    lines.append("")
    lines.append("## Arka State Summary")
    lines.append("```json")
    lines.append(json.dumps(report["arka_state"], indent=2))
    lines.append("```")

    lines.append("")
    lines.append("## Database Summary")
    lines.append("```json")
    lines.append(json.dumps(report["database"], indent=2))
    lines.append("```")

    lines.append("")
    lines.append("## Website / Keyword Signals")
    for category, rows in report["keyword_scan"].items():
        lines.append("")
        lines.append(f"### {category}")
        if not rows:
            lines.append("- No matches found.")
        else:
            for row in rows[:50]:
                lines.append(f"- `{row['file']}` — `{row['term']}`")

    lines.append("")
    lines.append("## Repository Hygiene")
    lines.append(f"- Backup file count: `{report['duplicates']['backup_count']}`")
    lines.append(f"- Patch/repair/hotfix file count: `{report['duplicates']['patch_count']}`")

    REPORT_MD.write_text("\n".join(lines), encoding="utf-8")

def main():
    if not REPO.exists():
        raise SystemExit(f"Repo does not exist: {REPO}")

    files = list_files()
    py_files = python_files(files)

    report = {
        "timestamp": timestamp,
        "repo": str(REPO),
        "file_count": len(files),
        "python_file_count": len(py_files),
        "git_status": run_cmd("git status --short"),
        "recent_commits": run_cmd("git log --oneline -5"),
        "expected_files": expected_check(),
        "python_syntax": syntax_check(py_files),
        "keyword_scan": keyword_scan(files),
        "arka_state": arka_state_scan(),
        "database": db_scan(),
        "duplicates": duplicate_patch_scan(files),
    }

    report["readiness"] = readiness_score(report)
    report["recommendations"] = gap_recommendations(report)

    REPORT_JSON.write_text(json.dumps(report, indent=2), encoding="utf-8")
    write_markdown(report)

    print("[OK] Ecosystem gap audit complete.")
    print("[JSON]", REPORT_JSON)
    print("[MD]", REPORT_MD)
    print("")
    print("Readiness:", report["readiness"]["heuristic_percent"], "%")
    print("Recommendations:")
    for rec in report["recommendations"]:
        print("-", rec["severity"].upper(), rec["area"], "=>", rec["finding"])

if __name__ == "__main__":
    main()
