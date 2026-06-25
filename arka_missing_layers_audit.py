from __future__ import annotations

import ast
import json
import os
import re
import sqlite3
import subprocess
import time
from pathlib import Path

REPO = Path(r"D:\ARKA_HQ\repos\ardhanarishvara_git")
ARKA = REPO / "arka_v1"
REPORT_DIR = Path(r"D:\ARKA_HQ\reports")
DATA_DIR = Path(r"D:\ARKA_HQ\data")
DB_PATH = DATA_DIR / "arka_core.db"

timestamp = time.strftime("%Y%m%d_%H%M%S")
REPORT_JSON = REPORT_DIR / f"ARKA_MISSING_LAYERS_AUDIT_{timestamp}.json"
REPORT_MD = REPORT_DIR / f"ARKA_MISSING_LAYERS_AUDIT_{timestamp}.md"

EXCLUDE = [".git", ".venv", "__pycache__", "node_modules"]

EXPECTED_LAYERS = {
    "governor_dispatcher": {
        "required": True,
        "description": "Runtime router above old patch routers.",
        "evidence_files": [
            "arka_v1/arka_governor_dispatcher.py"
        ],
        "keywords": [
            "arka_governor_dispatch",
            "governor_system_status",
            "governor_website_status",
            "governor_leads_status",
            "governor_safe_web"
        ]
    },
    "identity_owner_route": {
        "required": True,
        "description": "Who am I / owner/profile route from local memory/profile.",
        "evidence_files": [
            "arka_v1/arka_governor_dispatcher.py"
        ],
        "keywords": [
            "_is_identity_question",
            "governor_identity_status"
        ]
    },
    "ecosystem_self_discovery": {
        "required": True,
        "description": "Arka scans local ecosystem and generates its own registry instead of being manually taught.",
        "evidence_files": [
            "arka_v1/arka_ecosystem_discovery.py",
            "arka_v1/arka_ecosystem_registry.generated.json",
            "arka_v1/arka_capability_contracts.generated.json"
        ],
        "keywords": [
            "self_discovery",
            "capability_contract",
            "generated registry",
            "entrypoint",
            "callable"
        ]
    },
    "ecosystem_registry_runtime": {
        "required": True,
        "description": "Runtime route for internal AI/agent/engine questions.",
        "evidence_files": [
            "arka_v1/arka_ecosystem_registry.json",
            "arka_v1/arka_governor_dispatcher.py"
        ],
        "keywords": [
            "_is_ecosystem_registry_question",
            "governor_ecosystem_registry",
            "arka_ecosystem_registry"
        ]
    },
    "capability_contracts": {
        "required": True,
        "description": "Machine-readable contracts for what each AI/engine/tool can do, how to call it, and what approvals are needed.",
        "evidence_files": [
            "arka_v1/arka_capability_contracts.generated.json",
            "arka_v1/skills",
            "arka_v1/capabilities"
        ],
        "keywords": [
            "input_schema",
            "output_schema",
            "approval_required",
            "safe_actions",
            "entrypoint"
        ]
    },
    "astraa_safe_access_contract": {
        "required": True,
        "description": "Defines Arka 90/10 and Astraa 10/90 safe access bridge.",
        "evidence_files": [
            "astraa_access/arka_astraa_safe_access_manifest.json",
            "arka_v1/docs/ARKA_GOVERNOR_ASTRAA_SAFE_ACCESS_CANON.md"
        ],
        "keywords": [
            "safe access",
            "90 local",
            "10 cloud",
            "astraasystems.com",
            "governor"
        ]
    },
    "astraa_tool_catalog": {
        "required": True,
        "description": "Catalog of Astraa website/tools available through Astraa safe access.",
        "evidence_files": [
            "astraa_access/astraa_tool_catalog.json",
            "arka_v1/astraa_tool_catalog.generated.json"
        ],
        "keywords": [
            "tool_catalog",
            "astraa tools",
            "finance",
            "operations",
            "estimator",
            "workspace",
            "vault"
        ]
    },
    "astraa_web_source_connector": {
        "required": True,
        "description": "Connector/source extractor for current web/cloud info via Astraa safe access.",
        "evidence_files": [
            "astraa_access/astraa_web_connector.py",
            "arka_v1/astraa_safe_web_connector.py"
        ],
        "keywords": [
            "search",
            "source extractor",
            "web connector",
            "citation",
            "live snippets",
            "safe web"
        ]
    },
    "website_activity_connector": {
        "required": False,
        "description": "Connector for true website activity/analytics if available.",
        "evidence_files": [
            "astraa_access/netlify_analytics_connector.py",
            "astraa_access/website_activity_connector.py",
            "logs",
            "analytics"
        ],
        "keywords": [
            "netlify",
            "analytics",
            "visitors",
            "traffic",
            "activity",
            "events"
        ]
    },
    "lead_signup_connector": {
        "required": True,
        "description": "Connector to local/backend lead capture, estimator signup, usage/account data.",
        "evidence_files": [
            "lead_capture.py",
            "astraa_access/lead_signup_connector.py",
            "api.py"
        ],
        "keywords": [
            "lead",
            "signup",
            "register",
            "registration",
            "usage_db",
            "sessions_db",
            "payment_db"
        ]
    },
    "intent_classifier": {
        "required": True,
        "description": "General classifier above old routers: identity, ecosystem, math, web, business, status, memory.",
        "evidence_files": [
            "arka_v1/intent_classifier.py",
            "arka_v1/arka_governor_dispatcher.py"
        ],
        "keywords": [
            "classify",
            "intent",
            "route",
            "domain",
            "question"
        ]
    },
    "math_guardrails": {
        "required": True,
        "description": "Prevents product names like ID.4 from being treated as money/math.",
        "evidence_files": [
            "arka_v1/arka_math_os.py",
            "arka_v1/arka_governor_dispatcher.py"
        ],
        "keywords": [
            "ID.4",
            "math",
            "looks_like_arithmetic",
            "safe_eval",
            "product-code"
        ]
    },
    "response_validator": {
        "required": True,
        "description": "Checks answer before final response: did it answer, use right source, avoid fabrication?",
        "evidence_files": [
            "arka_v1/response_validator.py",
            "arka_v1/validator.py"
        ],
        "keywords": [
            "validate",
            "validator",
            "grounded",
            "source required",
            "approval"
        ]
    },
    "memory_policy": {
        "required": True,
        "description": "Controls what gets saved as memory/context and prevents questions from being saved as facts.",
        "evidence_files": [
            "arka_v1/arka_memory.json",
            "arka_v1/arka_v1.py",
            "arka_v1/arka_capability_manifest.json"
        ],
        "keywords": [
            "is_question_like",
            "natural_context",
            "save_active_memory",
            "context brain",
            "memory policy"
        ]
    },
    "approval_policy": {
        "required": True,
        "description": "Approval-only autonomy guard for risky actions.",
        "evidence_files": [
            "arka_action_guard.py",
            "arka_v1/arka_governor_dispatcher.py"
        ],
        "keywords": [
            "approval",
            "ARKA_APPROVAL_KEY",
            "external commitments",
            "trades",
            "payments"
        ]
    },
    "smoke_tests": {
        "required": True,
        "description": "Regression tests for identity, status, website, leads, ecosystem, math, web routing.",
        "evidence_files": [
            "arka_v1/tests",
            "arka_v1/smoke_tests.py",
            "tests"
        ],
        "keywords": [
            "who am i",
            "status",
            "who is lux",
            "website status",
            "estimator signup",
            "ID.4"
        ]
    }
}

def rel(path: Path) -> str:
    try:
        return str(path.relative_to(REPO)).replace("\\", "/")
    except Exception:
        return str(path)

def should_skip(path: Path) -> bool:
    s = str(path)
    return any(x in s for x in EXCLUDE)

def safe_read(path: Path, limit=250000) -> str:
    try:
        return path.read_text(encoding="utf-8-sig", errors="ignore")[:limit]
    except Exception:
        return ""

def run_cmd(cmd: str, timeout=90) -> dict:
    try:
        p = subprocess.run(cmd, cwd=str(REPO), shell=True, text=True, capture_output=True, timeout=timeout)
        return {
            "ok": p.returncode == 0,
            "returncode": p.returncode,
            "stdout": (p.stdout or "").strip(),
            "stderr": (p.stderr or "").strip()
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

def exists_loose(candidate: str, files) -> bool:
    p = REPO / candidate
    if p.exists():
        return True
    c = candidate.lower().replace("\\", "/")
    for f in files:
        if c in rel(f).lower():
            return True
    return False

def keyword_hits(keywords, files):
    hits = []
    kwords = [k.lower() for k in keywords]
    text_suffixes = {".py", ".md", ".json", ".txt", ".yaml", ".yml", ".ps1", ".html", ".js", ".css", ".toml"}

    for f in files:
        rp = rel(f).lower()
        path_hit = [k for k in kwords if k in rp]
        if path_hit:
            hits.append({"file": rel(f), "term": path_hit[0], "where": "path"})
            continue

        if f.suffix.lower() not in text_suffixes:
            continue

        text = safe_read(f).lower()
        for k in kwords:
            if k in text:
                hits.append({"file": rel(f), "term": k, "where": "content"})
                break

    return hits[:80]

def layer_check(layer_name, spec, files):
    evidence_rows = []
    for candidate in spec["evidence_files"]:
        evidence_rows.append({
            "candidate": candidate,
            "exists_or_loose_match": exists_loose(candidate, files)
        })

    hits = keyword_hits(spec["keywords"], files)

    evidence_score = sum(1 for x in evidence_rows if x["exists_or_loose_match"]) / max(1, len(evidence_rows))
    keyword_score = len(set(h["term"] for h in hits)) / max(1, len(spec["keywords"]))

    score = round((evidence_score * 0.65 + keyword_score * 0.35) * 100, 1)

    if score >= 75:
        status = "present"
    elif score >= 35:
        status = "partial"
    else:
        status = "missing"

    return {
        "layer": layer_name,
        "required": spec["required"],
        "description": spec["description"],
        "status": status,
        "score": score,
        "evidence": evidence_rows,
        "matched_keywords": sorted(list(set(h["term"] for h in hits))),
        "hits_sample": hits[:30]
    }

def python_syntax(files):
    issues = []
    for f in files:
        if f.suffix.lower() != ".py":
            continue
        try:
            compile(safe_read(f), str(f), "exec")
        except Exception as e:
            issues.append({"file": rel(f), "error": str(e)})
    return issues

def ast_routes_summary():
    dispatcher = ARKA / "arka_governor_dispatcher.py"
    if not dispatcher.exists():
        return {"exists": False}

    text = safe_read(dispatcher)
    funcs = []
    try:
        tree = ast.parse(text)
        for node in ast.walk(tree):
            if isinstance(node, ast.FunctionDef):
                funcs.append(node.name)
    except Exception as e:
        return {"exists": True, "parse_error": str(e), "functions": []}

    return {"exists": True, "functions": sorted(funcs)}

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

def recommendations(report):
    recs = []

    for layer in report["layers"]:
        if layer["required"] and layer["status"] == "missing":
            recs.append({
                "severity": "high",
                "layer": layer["layer"],
                "finding": f"Required layer is missing ({layer['score']}%).",
                "recommendation": "Build this as architecture, not a scenario patch."
            })
        elif layer["required"] and layer["status"] == "partial":
            recs.append({
                "severity": "medium",
                "layer": layer["layer"],
                "finding": f"Required layer is partial ({layer['score']}%).",
                "recommendation": "Strengthen this layer or add generated contracts/tests before more V1 behavior changes."
            })
        elif (not layer["required"]) and layer["status"] == "missing":
            recs.append({
                "severity": "info",
                "layer": layer["layer"],
                "finding": f"Optional layer is missing ({layer['score']}%).",
                "recommendation": "Only build if needed for travel readiness or business operation."
            })

    if report["python_syntax_issues"]:
        recs.insert(0, {
            "severity": "high",
            "layer": "python_syntax",
            "finding": f"{len(report['python_syntax_issues'])} Python syntax issue(s) found.",
            "recommendation": "Fix syntax before building further."
        })

    return recs

def write_md(report):
    lines = []
    lines.append("# Arka Missing Layers Audit")
    lines.append("")
    lines.append(f"- Timestamp: `{report['timestamp']}`")
    lines.append(f"- Repo: `{report['repo']}`")
    lines.append(f"- Files scanned: **{report['file_count']}**")
    lines.append(f"- Overall architecture score: **{report['overall_score']}%**")
    lines.append(f"- Python syntax issues: **{len(report['python_syntax_issues'])}**")
    lines.append("")

    lines.append("## Layer Summary")
    for layer in report["layers"]:
        icon = "✅" if layer["status"] == "present" else "⚠️" if layer["status"] == "partial" else "❌"
        req = "required" if layer["required"] else "optional"
        lines.append(f"- {icon} **{layer['layer']}** — {layer['status']} — {layer['score']}% — {req}")

    lines.append("")
    lines.append("## Recommendations")
    for rec in report["recommendations"]:
        lines.append("")
        lines.append(f"### {rec['severity'].upper()} — {rec['layer']}")
        lines.append(f"- Finding: {rec['finding']}")
        lines.append(f"- Recommendation: {rec['recommendation']}")

    lines.append("")
    lines.append("## Detailed Layers")
    for layer in report["layers"]:
        lines.append("")
        lines.append(f"### {layer['layer']} — {layer['status']} — {layer['score']}%")
        lines.append(f"- Description: {layer['description']}")
        lines.append("- Evidence files:")
        for e in layer["evidence"]:
            mark = "✅" if e["exists_or_loose_match"] else "❌"
            lines.append(f"  - {mark} `{e['candidate']}`")
        lines.append(f"- Matched keywords: {', '.join(layer['matched_keywords']) if layer['matched_keywords'] else 'None'}")
        if layer["hits_sample"]:
            lines.append("- Evidence sample:")
            for h in layer["hits_sample"][:10]:
                lines.append(f"  - `{h['term']}` in `{h['file']}` ({h['where']})")

    lines.append("")
    lines.append("## Governor Dispatcher Functions")
    lines.append("```json")
    lines.append(json.dumps(report["governor_dispatcher"], indent=2))
    lines.append("```")

    lines.append("")
    lines.append("## DB Summary")
    lines.append("```json")
    lines.append(json.dumps(report["db"], indent=2))
    lines.append("```")

    if report["python_syntax_issues"]:
        lines.append("")
        lines.append("## Python Syntax Issues")
        for issue in report["python_syntax_issues"]:
            lines.append(f"- `{issue['file']}` — {issue['error']}")

    REPORT_MD.write_text("\n".join(lines), encoding="utf-8")

def main():
    files = list_files()
    layers = [layer_check(name, spec, files) for name, spec in EXPECTED_LAYERS.items()]
    syntax = python_syntax(files)

    overall = round(sum(l["score"] for l in layers) / max(1, len(layers)), 1)

    report = {
        "timestamp": timestamp,
        "repo": str(REPO),
        "file_count": len(files),
        "overall_score": overall,
        "layers": layers,
        "python_syntax_issues": syntax,
        "governor_dispatcher": ast_routes_summary(),
        "db": db_summary(),
        "git_status": run_cmd("git status --short"),
        "recent_commits": run_cmd("git log --oneline --decorate -8")
    }

    report["recommendations"] = recommendations(report)

    REPORT_JSON.write_text(json.dumps(report, indent=2), encoding="utf-8")
    write_md(report)

    print("[OK] Arka missing layers audit complete.")
    print("[JSON]", REPORT_JSON)
    print("[MD]", REPORT_MD)
    print("")
    print("Overall architecture score:", str(overall) + "%")
    print("Python syntax issues:", len(syntax))
    print("")
    print("Layer summary:")
    for layer in layers:
        print("-", layer["status"].upper(), layer["layer"], str(layer["score"]) + "%", "(required)" if layer["required"] else "(optional)")
    print("")
    print("Recommendations:")
    for rec in report["recommendations"]:
        print("-", rec["severity"].upper(), rec["layer"], "=>", rec["finding"])

if __name__ == "__main__":
    main()
