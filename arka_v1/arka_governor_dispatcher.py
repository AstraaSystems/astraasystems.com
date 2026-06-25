from __future__ import annotations

import json
import os
import re
import sqlite3
import subprocess
import time
import urllib.request
from pathlib import Path
from urllib.parse import quote_plus

GOVERNOR_DISPATCHER_VERSION = "1.0"

ROOT = Path(os.getenv("ARKA_HQ_ROOT", r"D:\ARKA_HQ\repos\ardhanarishvara_git"))
ARKA_DIR = ROOT / "arka_v1"
DATA_DIR = Path(r"D:\ARKA_HQ\data")
DB_PATH = DATA_DIR / "arka_core.db"


def _run(cmd: str, timeout: int = 30) -> dict:
    try:
        p = subprocess.run(
            cmd,
            cwd=str(ROOT),
            shell=True,
            text=True,
            capture_output=True,
            timeout=timeout,
        )
        return {
            "ok": p.returncode == 0,
            "returncode": p.returncode,
            "stdout": (p.stdout or "").strip(),
            "stderr": (p.stderr or "").strip(),
        }
    except Exception as e:
        return {
            "ok": False,
            "returncode": -1,
            "stdout": "",
            "stderr": str(e),
        }


def _read_json(path: Path):
    try:
        return json.loads(path.read_text(encoding="utf-8-sig"))
    except Exception:
        return None


def _source_links(query: str) -> str:
    q = quote_plus(query or "")
    return (
        "- Bing search: https://www.bing.com/search?q=" + q + "\n"
        "- DuckDuckGo search: https://duckduckgo.com/?q=" + q + "\n"
        "- Google search: https://www.google.com/search?q=" + q
    )


def _is_exact_status(raw: str) -> bool:
    w = (raw or "").strip().lower()
    return w in {
        "status",
        "system status",
        "arka status",
        "current status",
        "show status",
        "show arka status",
    }


def _is_website_status(raw: str) -> bool:
    w = (raw or "").lower()
    website_terms = [
        "website",
        "site",
        "astraasystems.com",
        "www.astraasystems.com",
        "our website",
    ]
    status_terms = [
        "status",
        "activity",
        "activities",
        "traffic",
        "analytics",
        "visitors",
        "health",
        "run status",
        "current activates",
        "current activities",
    ]
    return any(a in w for a in website_terms) and any(b in w for b in status_terms)


def _is_leads_or_signups(raw: str) -> bool:
    w = (raw or "").lower()
    return any(x in w for x in [
        "lead",
        "leads",
        "signed up",
        "sign up",
        "signup",
        "signups",
        "registered",
        "registration",
        "anyone signed",
        "estimator signup",
        "estimator sign",
        "has astraa able to get any leads",
        "has anyone signed up for the estimator",
    ])


def _is_market_position(raw: str) -> bool:
    w = (raw or "").lower()
    return any(x in w for x in [
        "market position",
        "position in market",
        "current position in market",
        "product line up",
        "product lineup",
        "our product line",
        "competitive position",
    ])


def _is_current_external_question(raw: str) -> bool:
    w = (raw or "").lower()

    current_terms = [
        "weather",
        "today",
        "current",
        "latest",
        "new ",
        "newest",
        "priced",
        "price",
        "packages",
        "available",
        "market",
        "2027",
        "2028",
    ]

    external_entities = [
        "vw",
        "volkswagen",
        "id.4",
        "id 4",
        "ev",
        "vehicle",
        "car",
        "weather",
        "burnaby",
    ]

    if any(x in w for x in current_terms) and any(y in w for y in external_entities):
        return True

    # Product-code guard: ID.4 must never be treated as $4.00 math.
    if "id.4" in w or "id 4" in w:
        return True

    return False


def governor_system_status() -> str:
    git_head = _run("git log --oneline --decorate -1")
    git_tags = _run("git tag --points-at HEAD")
    git_status = _run("git status --short")

    required = [
        "arka_v1.py",
        "arka_math_os.py",
        "arka_memory.json",
        "arka_state.json",
        "start_arka_v1.ps1",
        "arka_capability_manifest.json",
    ]

    lines = [
        "Arka Governor Status",
        "",
        "Runtime:",
        "- Name: Arka V1",
        "- Mode: local",
        f"- Governor Dispatcher: {GOVERNOR_DISPATCHER_VERSION}",
        "",
        "Git:",
        "- HEAD: " + (git_head.get("stdout") or "unknown"),
        "- Tags at HEAD: " + ((git_tags.get("stdout") or "none").replace("\n", ", ")),
        "- Working tree: " + ("clean" if not git_status.get("stdout") else "has local changes"),
    ]

    if git_status.get("stdout"):
        lines.append("")
        lines.append("Git changes:")
        for line in git_status["stdout"].splitlines():
            lines.append("- " + line)

    lines.append("")
    lines.append("Required Arka files:")
    for item in required:
        p = ARKA_DIR / item
        lines.append(("- OK: " if p.exists() else "- MISSING: ") + item)

    state = _read_json(ARKA_DIR / "arka_state.json")
    memory = _read_json(ARKA_DIR / "arka_memory.json")

    lines.append("")
    lines.append("State summary:")
    if isinstance(state, dict):
        for k, v in list(state.items())[:12]:
            if isinstance(v, list):
                lines.append(f"- {k}: {len(v)} item(s)")
            elif isinstance(v, dict):
                lines.append(f"- {k}: {len(v.keys())} key(s)")
            else:
                lines.append(f"- {k}: {type(v).__name__}")
    else:
        lines.append("- arka_state.json not readable or empty")

    if isinstance(memory, dict):
        lines.append("")
        lines.append("Memory summary:")
        for k, v in list(memory.items())[:12]:
            if isinstance(v, list):
                lines.append(f"- {k}: {len(v)} item(s)")
            elif isinstance(v, dict):
                lines.append(f"- {k}: {len(v.keys())} key(s)")
            else:
                lines.append(f"- {k}: {type(v).__name__}")

    return "\n".join(lines)


def _http_check(url: str) -> dict:
    try:
        req = urllib.request.Request(
            url,
            headers={"User-Agent": "ArkaGovernor/1.0"},
            method="GET",
        )
        with urllib.request.urlopen(req, timeout=10) as r:
            body = r.read(200000)
            return {
                "ok": True,
                "url": url,
                "status": getattr(r, "status", None),
                "final_url": r.geturl(),
                "bytes_sampled": len(body),
            }
    except Exception as e:
        return {
            "ok": False,
            "url": url,
            "error": str(e),
        }


def governor_website_status(raw: str) -> str:
    checks = [
        _http_check("https://www.astraasystems.com"),
        _http_check("https://astraasystems.com"),
    ]

    lines = [
        "Astraa Website Status — Governor Route",
        "",
        "I routed this as an Astraa website/business status request, not a generic web search.",
        "",
        "Public website reachability:",
    ]

    for c in checks:
        if c.get("ok"):
            lines.append(f"- OK: {c.get('url')} -> HTTP {c.get('status')} | final: {c.get('final_url')} | sampled bytes: {c.get('bytes_sampled')}")
        else:
            lines.append(f"- FAIL: {c.get('url')} -> {c.get('error')}")

    local_signals = [
        "api.py",
        "wsgi.py",
        "lead_capture.py",
        "astraa_arka_bridge.py",
        "pricing.html",
        "estimator.html",
        "customer-portal.html",
        "workspace-internal.html",
    ]

    lines.append("")
    lines.append("Local Astraa file signals:")
    for name in local_signals:
        found = list(ROOT.rglob(name))
        found = [p for p in found if ".git" not in str(p) and ".venv" not in str(p)]
        if found:
            lines.append(f"- OK: {name}")
        else:
            lines.append(f"- MISSING/NOT FOUND: {name}")

    lines.append("")
    lines.append("Analytics/activity note:")
    lines.append("- I can check public reachability and local files now.")
    lines.append("- I cannot show true live visitor analytics unless a Netlify/analytics/server-log connector or exported activity file is available locally.")

    return "\n".join(lines)


def _summarize_json_file(path: Path) -> str:
    data = _read_json(path)
    if data is None:
        return f"{path.name}: not valid JSON or unreadable"

    if isinstance(data, list):
        return f"{path.name}: list with {len(data)} item(s)"

    if isinstance(data, dict):
        return f"{path.name}: dict with {len(data.keys())} key(s)"

    return f"{path.name}: {type(data).__name__}"


def _db_table_counts() -> list[str]:
    lines = []
    if not DB_PATH.exists():
        return ["Arka DB not found at D:\\ARKA_HQ\\data\\arka_core.db"]

    try:
        conn = sqlite3.connect(str(DB_PATH))
        cur = conn.cursor()
        cur.execute("SELECT name FROM sqlite_master WHERE type='table'")
        tables = [x[0] for x in cur.fetchall()]
        for table in tables:
            try:
                cur.execute(f"SELECT COUNT(*) FROM {table}")
                lines.append(f"{table}: {cur.fetchone()[0]} row(s)")
            except Exception as e:
                lines.append(f"{table}: count failed: {e}")
        conn.close()
    except Exception as e:
        lines.append(f"DB scan failed: {e}")

    return lines or ["No DB tables found"]


def governor_leads_status(raw: str) -> str:
    lines = [
        "Astraa Leads / Signups Status — Governor Route",
        "",
        "I routed this as an Astraa business-data question, not a web search.",
        "",
        "Local data sources checked:",
    ]

    candidate_patterns = [
        "*lead*.json",
        "*lead*.csv",
        "*signup*.json",
        "*signup*.csv",
        "*register*.json",
        "*registration*.json",
        "*usage*.json",
        "*payment*.json",
        "*session*.json",
        "*account*.json",
    ]

    seen = set()
    candidates = []

    for pat in candidate_patterns:
        for p in ROOT.rglob(pat):
            s = str(p)
            if ".git" in s or ".venv" in s or "__pycache__" in s:
                continue
            if str(p) not in seen:
                candidates.append(p)
                seen.add(str(p))

    if candidates:
        for p in candidates[:40]:
            if p.suffix.lower() == ".json":
                lines.append("- " + _summarize_json_file(p))
            else:
                try:
                    count = max(0, len(p.read_text(encoding="utf-8-sig", errors="ignore").splitlines()) - 1)
                    lines.append(f"- {p.name}: approx {count} data row(s)")
                except Exception:
                    lines.append(f"- {p.name}: found")
    else:
        lines.append("- No obvious local lead/signup JSON/CSV files found.")

    lines.append("")
    lines.append("SQLite/local DB signals:")
    for line in _db_table_counts():
        lines.append("- " + line)

    lines.append("")
    lines.append("Interpretation:")
    lines.append("- If leads/signups exist only in Netlify, email, Moneris, or production hosting analytics, Arka needs that connector/export available locally through Astraa safe access.")
    lines.append("- If lead capture writes to local JSON/DB, the counts above are the local evidence.")

    return "\n".join(lines)


def governor_market_position(raw: str, web_func=None) -> str:
    lines = [
        "Astraa Market / Product Position — Governor Route",
        "",
        "I routed this as an Astraa product-market question.",
        "",
        "Local product lineup context should be pulled from Astraa tools/pages/docs, then external market info should come through Astraa safe web access.",
        "",
        "Current local product-line signals to check:",
    ]

    product_terms = [
        "estimator",
        "finance",
        "operations",
        "expense",
        "commerce",
        "data",
        "inference",
        "distribution",
        "vault",
        "workspace",
        "pricing",
    ]

    for term in product_terms:
        matches = []
        for p in ROOT.rglob("*"):
            if not p.is_file():
                continue
            s = str(p)
            if ".git" in s or ".venv" in s or "__pycache__" in s:
                continue
            if term.lower() in p.name.lower():
                matches.append(p)
        lines.append(f"- {term}: {len(matches)} local file-name signal(s)")

    if web_func:
        try:
            web_result = web_func(raw)
            if web_result:
                lines.append("")
                lines.append("Astraa safe web/source access result:")
                lines.append(web_result)
                return "\n".join(lines)
        except Exception as e:
            lines.append("")
            lines.append("Astraa safe web/source access failed: " + str(e))

    lines.append("")
    lines.append("Source links for external market check:")
    lines.append(_source_links(raw))

    return "\n".join(lines)


def governor_safe_web(raw: str, web_func=None) -> str:
    lines = [
        "Astraa Safe Web Access — Governor Route",
        "",
        "This request needs current/external information, so I routed it through the Astraa safe access lane instead of Math OS or passive context.",
        "",
    ]

    if web_func:
        try:
            result = web_func(raw)
            if result:
                lines.append(result)
                return "\n".join(lines)
        except Exception as e:
            lines.append("The existing local web connector failed: " + str(e))
            lines.append("")

    lines.append("I could not access a richer live connector from this runtime, so here are source links:")
    lines.append(_source_links(raw))

    return "\n".join(lines)




def _is_identity_question(raw: str) -> bool:
    w = (raw or "").strip().lower()
    return w in {
        "who am i",
        "who am i?",
        "whoami",
        "who is the owner",
        "who owns arka",
        "who is arka built for",
        "who is the founder",
        "who is keshanth"
    }


def governor_identity_status(raw: str) -> str:
    memory = _read_json(ARKA_DIR / "arka_memory.json")
    state = _read_json(ARKA_DIR / "arka_state.json")

    owner = "Keshanth Sivayogampillai"
    email = "KeshanthSPillai@astraasystems.com"

    # Try to use local memory if owner is stored there.
    try:
        if isinstance(memory, dict):
            if memory.get("owner"):
                owner = str(memory.get("owner"))
            memories = memory.get("memories", [])
            if isinstance(memories, list):
                joined = " ".join(str(x) for x in memories).lower()
                if "keshanth" in joined and "astraa" in joined:
                    pass
    except Exception:
        pass

    lines = [
        "Identity / Owner — Governor Route",
        "",
        f"You are {owner}.",
        "",
        "In this ecosystem:",
        "- You are the external CEO/founder/operator.",
        "- Arka is your 90% local / 10% cloud personal AI governor, CEO/COO interface.",
        "- Astraa is the 10% local / 90% cloud business/web/public layer and safe access point.",
        "- Aruhan is the deep intelligence/security AI.",
        "- Ardhanarishvara OS is the governance/math/kernel layer.",
        "",
        "Known account signal:",
        f"- Primary ecosystem/M365 email: {email}",
        "",
        "I should answer identity questions from local owner/profile/memory context, not web search."
    ]

    if isinstance(state, dict):
        lines.append("")
        lines.append("Local Arka state detected:")
        for k in ["universal_context", "product_work_queue", "competitive_pricing_queue"]:
            if k in state:
                v = state.get(k)
                if isinstance(v, dict):
                    lines.append(f"- {k}: {len(v.keys())} key(s)")
                elif isinstance(v, list):
                    lines.append(f"- {k}: {len(v)} item(s)")

    return "\n".join(lines)


def arka_governor_dispatch(raw: str, web_func=None) -> str:
    raw = (raw or "").strip()
    if not raw:
        return ""

    # Identity / owner route must run before web/source fallback.
    if _is_identity_question(raw):
        return governor_identity_status(raw)

    # Specific business/system routes first.
    if _is_website_status(raw):
        return governor_website_status(raw)

    if _is_leads_or_signups(raw):
        return governor_leads_status(raw)

    if _is_market_position(raw):
        return governor_market_position(raw, web_func=web_func)

    if _is_exact_status(raw):
        return governor_system_status()

    # External/current info before Math OS so product names like ID.4 do not become math.
    if _is_current_external_question(raw):
        return governor_safe_web(raw, web_func=web_func)

    return ""
