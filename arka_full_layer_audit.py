from __future__ import annotations

import json
import re
import sqlite3
import subprocess
import time
from pathlib import Path

REPO = Path(r"D:\ARKA_HQ\repos\ardhanarishvara_git")
REPORT_DIR = Path(r"D:\ARKA_HQ\reports")
DATA_DIR = Path(r"D:\ARKA_HQ\data")
DB_PATH = DATA_DIR / "arka_core.db"

timestamp = time.strftime("%Y%m%d_%H%M%S")
REPORT_JSON = REPORT_DIR / f"ARKA_FULL_LAYER_AUDIT_{timestamp}.json"
REPORT_MD = REPORT_DIR / f"ARKA_FULL_LAYER_AUDIT_{timestamp}.md"

EXCLUDE = [".git", ".venv", "__pycache__", "node_modules"]

EXPECTED_ACTIVE = {
    "Arka V1 Runtime": [
        "arka_v1/arka_v1.py",
        "arka_v1/start_arka_v1.ps1"
    ],
    "Arka V1 Memory State": [
        "arka_v1/arka_memory.json",
        "arka_v1/arka_state.json",
        "arka_v1/arka_module_registry.json"
    ],
    "Arka Math OS": [
        "arka_v1/arka_math_os.py"
    ],
    "Arka Assets": [
        "arka_v1/assets/company_logo.svg"
    ],
    "Arka Personal AI Evolution": [
        "arka_personal_ai_v04_evolution/arka_personal_ai_v04.py",
        "arka_personal_ai_v04_evolution/arka_capabilities_v052.py",
        "arka_personal_ai_v04_evolution/ARKA_EVOLUTION_PROTOCOL.md",
        "arka_personal_ai_v04_evolution/arka_identity.json",
        "arka_personal_ai_v04_evolution/arka_policy.json",
        "arka_personal_ai_v04_evolution/arka_tone.json"
    ],
    "Arka Core / Supervisor": [
        "arka_core/ardhanarishvara_os.py",
        "arka_core/arka_ultimate_supervisor.py",
        "SupervisorCore.py",
        "SupervisorCore_DEPLOYED.py"
    ],
    "Arka Guards / Autonomy": [
        "arka_action_guard.py"
    ],
    "Arka Bridge": [
        "astraa_arka_bridge.py"
    ],
    "Arka Audit": [
        "ecosystem_gap_audit.py"
    ]
}

CAPABILITY_KEYWORDS = {
    "memory_active": ["save_active_memory", "active_memory_texts", "recall_memory", "arka_memory.json"],
    "conversation_journal": ["arka_conversation_journal", "record_journal", "show journal"],
    "context_brain": ["universal_context", "context brain", "show context brain"],
    "math_os": ["arka_math_os_router", "Math OS", "goal_breakdown", "revenue_customer_count"],
    "web_source_mode": ["web_search", "source links", "DuckDuckGo", "Bing search", "Google search"],
    "product_ceo_router": ["product_work_queue", "competitive_pricing_queue", "Product CEO"],
    "revenue_ai": ["Astraa Growth AI", "revenue_ai_plan", "lead_growth_queue"],
    "website_health": ["check website health", "Website health audit"],
    "approval_guard": ["ARKA_APPROVAL_KEY", "approval", "guard"],
    "bridge_layer": ["astraa_arka_bridge", "bridge", "Astraa"],
    "skill_registry": ["skill registry", "module_registry", "arka_module_registry"],
    "planner_kernel": ["planner", "brain kernel", "orchestrator", "executor", "validator"],
    "procedural_memory": ["procedural", "pattern", "generated_plans"],
    "remote_start": ["start_arka_v1.ps1", "ARKA_REMOTE_MODE"]
}

def should_skip(path: Path) -> bool:
    s = str(path)
    return any(x in s for x in EXCLUDE)

def rel(path: Path) -> str:
    try:
        return str(path.relative_to(REPO)).replace("\\", "/")
    except Exception:
        return str(path)

def safe_read(path: Path, limit=300000) -> str:
    try:
        return path.read_text(encoding="utf-8-sig", errors="ignore")[:limit]
    except Exception:
        return ""

def run_cmd(cmd: str):
    try:
        p = subprocess.run(cmd, cwd=str(REPO), shell=True, text=True, capture_output=True, timeout=120)
        return {
            "ok": p.returncode == 0,
            "returncode": p.returncode,
            "stdout": p.stdout.strip(),
            "stderr": p.stderr.strip()
        }
    except Exception as e:
        return {"ok": False, "returncode": -1, "stdout": "", "stderr": str(e)}

def list_files():
    files = []
    for p in REPO.rglob("*"):
        if should_skip(p):
            continue
        if p.is_file():
            files.append(p)
    return files

def arka_related_files(files):
    out = []
    terms = ["arka", "aruhan", "ardhanarishvara", "supervisor", "memory", "context", "brain"]
    for p in files:
        rp = rel(p).lower()
        if any(t in rp for t in terms):
            out.append(p)
            continue
        if p.suffix.lower() in [".py", ".md", ".json", ".txt", ".html", ".js"]:
            text = safe_read(p, limit=100000).lower()
            if "arka" in text:
                out.append(p)
    seen = set()
    clean = []
    for p in out:
        r = rel(p)
        if r not in seen:
            clean.append(p)
            seen.add(r)
    return clean

def expected_check():
    sections = {}
    for section, paths in EXPECTED_ACTIVE.items():
        rows = []
        for path in paths:
            p = REPO / path
            loose = p.exists()
            if not loose:
                frag = path.lower().replace("\\", "/")
                for item in REPO.rglob("*"):
                    if should_skip(item):
                        continue
                    if frag in rel(item).lower():
                        loose = True
                        break
            rows.append({
                "path": path,
                "exists": loose
            })
        sections[section] = rows
    return sections

def capability_scan(files):
    output = {}
    text_files = [p for p in files if p.suffix.lower() in [".py", ".md", ".json", ".txt", ".html", ".js", ".ps1"]]

    for cap, terms in CAPABILITY_KEYWORDS.items():
        matches = []
        matched_terms = set()

        for p in text_files:
            text = safe_read(p, limit=200000)
            lower = text.lower()
            rp = rel(p).lower()

            for term in terms:
                if term.lower() in lower or term.lower() in rp:
                    matches.append({
                        "term": term,
                        "file": rel(p)
                    })
                    matched_terms.add(term)
                    break

        output[cap] = {
            "matched_terms": sorted(list(matched_terms)),
            "required_terms": terms,
            "score": round((len(matched_terms) / len(terms)) * 100, 1) if terms else 0,
            "matches_sample": matches[:40]
        }

    return output

def python_syntax(files):
    issues = []
    for p in files:
        if p.suffix.lower() != ".py":
            continue
        try:
            compile(safe_read(p), str(p), "exec")
        except Exception as e:
            issues.append({"file": rel(p), "error": str(e)})
    return issues

def arka_state_summary():
    out = {}
    for path in [
        REPO / "arka_v1" / "arka_memory.json",
        REPO / "arka_v1" / "arka_state.json",
        REPO / "arka_v1" / "arka_module_registry.json",
        REPO / "arka_personal_ai_v04_evolution" / "arka_memory.json",
        REPO / "arka_personal_ai_v04_evolution" / "arka_identity.json",
        REPO / "arka_personal_ai_v04_evolution" / "arka_runtime_state.json"
    ]:
        key = rel(path)
        if not path.exists():
            out[key] = {"exists": False}
            continue
        try:
            data = json.loads(path.read_text(encoding="utf-8-sig"))
            summary = {"exists": True}
            if isinstance(data, dict):
                for k, v in data.items():
                    if isinstance(v, list):
                        summary[k] = len(v)
                    elif isinstance(v, dict):
                        summary[k] = len(v.keys())
                    else:
                        summary[k] = type(v).__name__
            out[key] = summary
        except Exception as e:
            out[key] = {"exists": True, "error": str(e)}
    return out

def db_summary():
    if not DB_PATH.exists():
        return {"exists": False}
    out = {"exists": True, "tables": {}}
    try:
        conn = sqlite3.connect(str(DB_PATH))
        cur = conn.cursor()
        cur.execute("SELECT name FROM sqlite_master WHERE type='table'")
        tables = [x[0] for x in cur.fetchall()]
        for t in tables:
            try:
                cur.execute(f"SELECT COUNT(*) FROM {t}")
                out["tables"][t] = cur.fetchone()[0]
            except Exception as e:
                out["tables"][t] = str(e)
        conn.close()
    except Exception as e:
        out["error"] = str(e)
    return out

def backup_clutter(files):
    rows = []
    for p in files:
        n = p.name.lower()
        if "backup" in n or n.startswith("patch_") or n.startswith("repair_") or n.startswith("hotfix_"):
            rows.append(rel(p))
    return rows

def recommendations(report):
    recs = []

    # Missing expected files
    for section, rows in report["expected"].items():
        missing = [x["path"] for x in rows if not x["exists"]]
        if missing:
            recs.append({
                "severity": "high",
                "area": section,
                "finding": "Missing expected Arka file(s): " + ", ".join(missing),
                "recommendation": "Restore or replace only these missing files if they are active. If they are legacy aliases, update audit map instead."
            })

    # Capability gaps
    for cap, item in report["capabilities"].items():
        if item["score"] < 50:
            recs.append({
                "severity": "medium",
                "area": cap,
                "finding": f"Capability evidence is weak: {item['score']}%.",
                "recommendation": "If this is required for V1, add documentation/manifest or route through V2 Brain Kernel. Do not patch blindly."
            })

    if report["syntax_issues"]:
        recs.append({
            "severity": "high",
            "area": "Python syntax",
            "finding": f"{len(report['syntax_issues'])} syntax issue(s) found in Arka-related files.",
            "recommendation": "Fix syntax before making more Arka changes."
        })

    clutter_count = len(report["backup_clutter"])
    if clutter_count > 15:
        recs.append({
            "severity": "medium",
            "area": "Arka cleanup",
            "finding": f"{clutter_count} backup/patch/repair files detected in Arka-related area.",
            "recommendation": "Archive repair scripts/backups outside active repo or document them as migration history."
        })

    # If no high/medium recs
    if not recs:
        recs.append({
            "severity": "info",
            "area": "Arka",
            "finding": "No major Arka gaps found.",
            "recommendation": "Freeze Arka V1 and move future intelligence into Arka V2 Brain Kernel / skill registry."
        })

    return recs

def score(report):
    checks = []

    def add(name, ok, note=""):
        checks.append({"name": name, "ok": bool(ok), "note": note})

    for section, rows in report["expected"].items():
        add(section, all(x["exists"] for x in rows), "Expected file section")

    for cap, item in report["capabilities"].items():
        add(f"Capability: {cap}", item["score"] >= 50, f"{item['score']}%")

    add("Python syntax", len(report["syntax_issues"]) == 0, f"{len(report['syntax_issues'])} issue(s)")
    add("Arka SQLite DB", report["db"].get("exists", False), "")
    add("Conversation journal", "arka_conversation_journal" in report["db"].get("tables", {}), "")

    ok = sum(1 for x in checks if x["ok"])
    total = len(checks)
    return {
        "ok": ok,
        "total": total,
        "percent": round((ok / total) * 100, 1) if total else 0,
        "checks": checks
    }

def write_md(report):
    lines = []
    lines.append("# Arka Full Layer Audit")
    lines.append("")
    lines.append(f"- Timestamp: `{report['timestamp']}`")
    lines.append(f"- Repo: `{report['repo']}`")
    lines.append(f"- Arka-related files detected: **{report['arka_file_count']}**")
    lines.append(f"- Arka readiness heuristic: **{report['readiness']['percent']}%**")
    lines.append("")

    lines.append("## Recommendations")
    for rec in report["recommendations"]:
        lines.append("")
        lines.append(f"### {rec['severity'].upper()} — {rec['area']}")
        lines.append(f"- Finding: {rec['finding']}")
        lines.append(f"- Recommendation: {rec['recommendation']}")

    lines.append("")
    lines.append("## Expected Arka Files")
    for section, rows in report["expected"].items():
        lines.append("")
        lines.append(f"### {section}")
        for row in rows:
            mark = "✅" if row["exists"] else "❌"
            lines.append(f"- {mark} `{row['path']}`")

    lines.append("")
    lines.append("## Capability Evidence")
    for cap, item in report["capabilities"].items():
        lines.append("")
        lines.append(f"### {cap} — {item['score']}%")
        lines.append(f"- Matched: {', '.join(item['matched_terms']) if item['matched_terms'] else 'None'}")
        for m in item["matches_sample"][:15]:
            lines.append(f"  - `{m['term']}` => `{m['file']}`")

    lines.append("")
    lines.append("## Syntax Issues")
    if not report["syntax_issues"]:
        lines.append("- ✅ No Arka-related Python syntax issues.")
    else:
        for issue in report["syntax_issues"]:
            lines.append(f"- ❌ `{issue['file']}` — {issue['error']}")

    lines.append("")
    lines.append("## State Summary")
    lines.append("```json")
    lines.append(json.dumps(report["state"], indent=2))
    lines.append("```")

    lines.append("")
    lines.append("## DB Summary")
    lines.append("```json")
    lines.append(json.dumps(report["db"], indent=2))
    lines.append("```")

    lines.append("")
    lines.append("## Backup / Patch Clutter")
    lines.append(f"- Count: `{len(report['backup_clutter'])}`")
    for item in report["backup_clutter"][:80]:
        lines.append(f"- `{item}`")

    REPORT_MD.write_text("\n".join(lines), encoding="utf-8")

def main():
    files = list_files()
    arka_files = arka_related_files(files)

    report = {
        "timestamp": timestamp,
        "repo": str(REPO),
        "arka_file_count": len(arka_files),
        "arka_files_sample": [rel(x) for x in arka_files[:300]],
        "expected": expected_check(),
        "capabilities": capability_scan(arka_files),
        "syntax_issues": python_syntax(arka_files),
        "state": arka_state_summary(),
        "db": db_summary(),
        "backup_clutter": backup_clutter(arka_files),
        "git_status": run_cmd("git status --short"),
        "recent_commits": run_cmd("git log --oneline -5")
    }

    report["readiness"] = score(report)
    report["recommendations"] = recommendations(report)

    REPORT_JSON.write_text(json.dumps(report, indent=2), encoding="utf-8")
    write_md(report)

    print("[OK] Arka full layer audit complete.")
    print("[JSON]", REPORT_JSON)
    print("[MD]", REPORT_MD)
    print("")
    print("Arka-related files:", report["arka_file_count"])
    print("Arka readiness heuristic:", str(report["readiness"]["percent"]) + "%")
    print("Python syntax issues:", len(report["syntax_issues"]))
    print("")
    print("Capability summary:")
    for cap, item in report["capabilities"].items():
        print("-", cap, str(item["score"]) + "%")
    print("")
    print("Recommendations:")
    for rec in report["recommendations"]:
        print("-", rec["severity"].upper(), rec["area"], "=>", rec["finding"])

if __name__ == "__main__":
    main()
