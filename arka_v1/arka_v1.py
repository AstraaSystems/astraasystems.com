#!/usr/bin/env python3
from __future__ import annotations

import json
import os
import re
import sqlite3
import subprocess
import time
import urllib.parse
import urllib.request
import uuid
from html import unescape
from http.server import BaseHTTPRequestHandler, HTTPServer
from pathlib import Path
from urllib.parse import parse_qs
from arka_math_os import arka_math_os_router
from arka_governor_dispatcher import arka_governor_dispatch

APP_NAME = "Arka V1"
VERSION = "1.0"
ROOT = Path(__file__).parent
REPO_ROOT = Path(os.environ.get("ARKA_HQ_ROOT", r"D:\ARKA_HQ\repos\ardhanarishvara_git")).resolve()
DATA_DIR = Path(r"D:\ARKA_HQ\data")
DB_PATH = DATA_DIR / "arka_core.db"

MEMORY_PATH = ROOT / "arka_memory.json"
STATE_PATH = ROOT / "arka_state.json"
MODULE_REGISTRY_PATH = ROOT / "arka_module_registry.json"

REMOTE_MODE = os.environ.get("ARKA_REMOTE_MODE", "0") == "1"
HOST = "0.0.0.0" if REMOTE_MODE else "127.0.0.1"
PORT = int(os.environ.get("ARKA_HQ_PORT", "8787"))
APPROVAL_KEY_ENV = "ARKA_APPROVAL_KEY"

LOGO_PNG = ROOT / "assets" / "company_logo.png"
HEADER_PNG = ROOT / "assets" / "company_logo_header.png"
LOGO_SVG = ROOT / "assets" / "company_logo.svg"

ALLOWLIST = {
    "python --version",
    "git --version",
    "git status --short",
    "git log --oneline -5",
    "dir",
    "Get-ChildItem",
    "pytest -q"
}

ASTRAA_TOOLS = [
    "Estimator",
    "Expense",
    "Finance",
    "Operations",
    "Commerce",
    "Data",
    "Inference",
    "Distribution",
    "Vault",
    "Workspace"
]

def uid():
    return str(uuid.uuid4())[:8]

def now():
    return time.strftime("%Y-%m-%dT%H:%M:%S")

def esc(s):
    return (s or "").replace("&", "&amp;").replace("<", "&lt;").replace(">", "&gt;")

def load_json(path: Path, default):
    if path.exists():
        try:
            return json.loads(path.read_text(encoding="utf-8-sig"))
        except Exception:
            return default
    return default

def save_json(path: Path, data):
    path.write_text(json.dumps(data, indent=2), encoding="utf-8")

def init():
    DATA_DIR.mkdir(parents=True, exist_ok=True)

    if not MEMORY_PATH.exists():
        save_json(MEMORY_PATH, {"schema": "arka_memory_v1", "memories": [], "audit": []})

    if not STATE_PATH.exists():
        save_json(STATE_PATH, {
            "chat": [],
            "tasks": [],
            "executive_log": [],
            "website_findings": [],
            "sales_snapshot": {},
            "marketing_plan": [],
            "tool_work_queue": [],
            "started_at": time.time()
        })

    if not MODULE_REGISTRY_PATH.exists():
        save_json(MODULE_REGISTRY_PATH, {"modules": [], "updated_at": ""})

    conn = sqlite3.connect(str(DB_PATH))
    cur = conn.cursor()

    cur.execute("""
        CREATE TABLE IF NOT EXISTS lifecycle_store (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            timestamp TEXT,
            type TEXT,
            content TEXT,
            status TEXT,
            source TEXT
        )
    """)

    cur.execute("""
        CREATE TABLE IF NOT EXISTS arka_logs (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            timestamp TEXT,
            event_type TEXT,
            content TEXT
        )
    """)

    cur.execute("""
        CREATE TABLE IF NOT EXISTS arka_business_events (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            timestamp TEXT,
            area TEXT,
            event_type TEXT,
            content TEXT,
            status TEXT
        )
    """)

    cur.execute("""
        CREATE TABLE IF NOT EXISTS arka_conversation_journal (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            timestamp TEXT,
            role TEXT,
            content TEXT
        )
    """)

    conn.commit()
    conn.close()

def state():
    s = load_json(STATE_PATH, {})
    s.setdefault("chat", [])
    s.setdefault("tasks", [])
    s.setdefault("executive_log", [])
    s.setdefault("website_findings", [])
    s.setdefault("sales_snapshot", {})
    s.setdefault("marketing_plan", [])
    s.setdefault("tool_work_queue", [])
    return s

def save_state(s):
    save_json(STATE_PATH, s)

def memory():
    m = load_json(MEMORY_PATH, {"memories": [], "audit": []})
    m.setdefault("memories", [])
    m.setdefault("audit", [])
    return m

def save_memory(m):
    save_json(MEMORY_PATH, m)

def log_event(event_type, content):
    init()
    conn = sqlite3.connect(str(DB_PATH))
    conn.execute(
        "INSERT INTO arka_logs (timestamp, event_type, content) VALUES (?, ?, ?)",
        (now(), event_type, str(content))
    )
    conn.commit()
    conn.close()

    s = state()
    s.setdefault("executive_log", []).insert(0, {
        "id": uid(),
        "timestamp": now(),
        "event_type": event_type,
        "content": str(content)
    })
    s["executive_log"] = s["executive_log"][:100]
    save_state(s)

def business_event(area, event_type, content, status="open"):
    init()
    conn = sqlite3.connect(str(DB_PATH))
    conn.execute(
        "INSERT INTO arka_business_events (timestamp, area, event_type, content, status) VALUES (?, ?, ?, ?, ?)",
        (now(), area, event_type, content, status)
    )
    conn.commit()
    conn.close()
    log_event("business_event", f"{area} | {event_type} | {content} | {status}")

def lifecycle_insert(item_type, content, status="active", source="arka_v1"):
    init()
    conn = sqlite3.connect(str(DB_PATH))
    conn.execute(
        "INSERT INTO lifecycle_store (timestamp, type, content, status, source) VALUES (?, ?, ?, ?, ?)",
        (now(), item_type, content, status, source)
    )
    conn.commit()
    conn.close()

def add_chat(role, text):
    s = state()
    s["chat"].append({"id": uid(), "role": role, "text": text, "created_at": time.time()})
    s["chat"] = s["chat"][-150:]
    save_state(s)

def add_task(user_words, kind, status, output, command="", area="general"):
    s = state()
    task = {
        "id": uid(),
        "created_at": time.time(),
        "area": area,
        "user_words": user_words,
        "kind": kind,
        "status": status,
        "output": output,
        "command": command
    }
    s["tasks"].insert(0, task)
    s["tasks"] = s["tasks"][:100]
    save_state(s)
    business_event(area, "task_added", user_words, status)
    return task

def save_active_memory(text):
    text = text.strip()
    if not text:
        return "I need something to save."

    m = memory()
    entry = {
        "id": uid(),
        "type": "user_memory",
        "text": text,
        "source": "explicit_user_command",
        "status": "active",
        "created_at": time.time()
    }

    m["memories"].insert(0, entry)
    m["audit"].insert(0, {"event": "memory_saved_active", "id": entry["id"], "created_at": time.time()})
    save_memory(m)

    lifecycle_insert("memory", text, "active", "explicit_user_command")
    log_event("memory_saved", text)
    return "Saved. I'll remember: " + text

def extract_save_command(raw):
    patterns = [
        r"^arka[, ]+remember this[: ]+(.*)$",
        r"^arka[, ]+remember[: ]+(.*)$",
        r"^record[: ]+(.*)$",
        r"^save[: ]+(.*)$",
        r"^memory[: ]+(.*)$",
        r"^add to memory[: ]+(.*)$",
        r"^put in memory[: ]+(.*)$",
        r"^arka[, ]+record this[: ]+(.*)$",
        r"^arka[, ]+save this[: ]+(.*)$",
        r"^arka[, ]+put this in memory[: ]+(.*)$",
        r"^record this[: ]+(.*)$",
        r"^save this[: ]+(.*)$",
        r"^put this in memory[: ]+(.*)$",
        r"^remember that[: ]*(.*)$",
        r"^remember[: ]+(.*)$"
    ]
    for pat in patterns:
        m = re.search(pat, raw.strip(), flags=re.I)
        if m:
            return m.group(1).strip()
    return ""

def active_memory_texts():
    return [x.get("text", "") for x in memory().get("memories", []) if x.get("text", "").strip()]

def recall_memory(term):
    term = (term or "").lower().strip()
    return [x for x in active_memory_texts() if term in x.lower()][:20]

def web_get(url):
    req = urllib.request.Request(url, headers={"User-Agent": "Mozilla/5.0 ArkaV1/1.0"})
    with urllib.request.urlopen(req, timeout=12) as res:
        return res.read().decode("utf-8", errors="ignore")

def web_search_sources(query, limit=6):
    q = urllib.parse.quote_plus(query)
    url = f"https://html.duckduckgo.com/html/?q={q}"

    try:
        html = web_get(url)
    except Exception as e:
        log_event("web_search_error", str(e))
        return []

    results = []
    blocks = re.findall(r'<div class="result.*?</div>\s*</div>', html, flags=re.S)

    for block in blocks:
        if len(results) >= limit:
            break

        title_match = re.search(r'class="result__a"[^>]*href="([^"]+)"[^>]*>(.*?)</a>', block, flags=re.S)
        if not title_match:
            continue

        href = unescape(title_match.group(1))
        title = re.sub(r"<.*?>", "", title_match.group(2), flags=re.S)
        title = unescape(title).strip()

        parsed = urllib.parse.urlparse(href)
        params = urllib.parse.parse_qs(parsed.query)
        if "uddg" in params:
            href = params["uddg"][0]

        snippet = ""
        snip = re.search(r'class="result__snippet"[^>]*>(.*?)</a>|class="result__snippet"[^>]*>(.*?)</div>', block, flags=re.S)
        if snip:
            raw_s = snip.group(1) or snip.group(2) or ""
            snippet = re.sub(r"<.*?>", "", raw_s, flags=re.S)
            snippet = unescape(snippet).strip()

        results.append({"title": title, "url": href, "snippet": snippet})

    log_event("web_search", query)
    return results

def format_web_results(query, results):
    if not results:
        return "I tried searching for: " + query + "\n\nI could not pull reliable web results from the local connector. I won't make anything up."

    lines = ["Here is what I found for: " + query, ""]
    for i, r in enumerate(results, 1):
        lines.append(f"{i}. {r['title']}")
        if r.get("snippet"):
            lines.append("   " + r["snippet"])
        lines.append("   Source: " + r["url"])
        lines.append("")
    return "\n".join(lines).strip()

def website_audit():
    findings = []

    public_text = ""
    try:
        public_text = web_get("https://astraasystems.com/")
        findings.append("Public site reachable from local connector.")
    except Exception as e:
        findings.append("Could not fetch public site from local connector: " + str(e))

    old_terms = [
        "Explore Engines",
        "Astraa Engines",
        "Full-Stack AI Automation",
        "Business Operation Engine",
        "Financial Engine",
        "Construction Engine",
        "Data Oracle Stream",
        "API Inference Layer"
    ]

    if public_text:
        plain = re.sub(r"<.*?>", " ", public_text, flags=re.S)
        for term in old_terms:
            if term.lower() in plain.lower():
                findings.append("Old public wording detected: " + term)

    website_files = []
    for ext in ["*.html", "*.css", "*.js", "*.py", "*.jinja", "*.jinja2"]:
        website_files.extend([p for p in REPO_ROOT.rglob(ext) if ".git" not in str(p) and ".venv" not in str(p) and "__pycache__" not in str(p)])

    findings.append(f"Local website/code file candidates found: {len(website_files)}")

    active_candidates = []
    for p in website_files[:1000]:
        try:
            text = p.read_text(encoding="utf-8", errors="ignore")
        except Exception:
            continue
        if "astraa" in text.lower() or "workspace" in text.lower() or "pricing" in text.lower() or "trial" in text.lower():
            active_candidates.append(str(p))

    findings.append(f"Likely Astraa website files found locally: {len(active_candidates)}")

    s = state()
    s["website_findings"] = [{"id": uid(), "timestamp": now(), "finding": x} for x in findings]
    save_state(s)

    for f in findings:
        business_event("website", "audit_finding", f, "open")

    lines = ["Website health audit completed.", ""]
    lines.extend("- " + f for f in findings)
    lines.append("")
    lines.append("CEO/COO recommendation: fix website positioning first, then lead capture, then pricing/trial conversion.")
    return "\n".join(lines)

def sales_status():
    init()
    conn = sqlite3.connect(str(DB_PATH))
    cur = conn.cursor()

    counts = {}
    for item_type in ["lead", "trial", "customer", "payment", "subscription", "memory", "web_research_request", "travel_research_request"]:
        cur.execute("SELECT COUNT(*) FROM lifecycle_store WHERE type=?", (item_type,))
        counts[item_type] = cur.fetchone()[0]

    conn.close()

    s = state()
    s["sales_snapshot"] = {"timestamp": now(), "counts": counts}
    save_state(s)

    lines = ["Sales / revenue status from connected local data:", ""]
    lines.append(f"- Leads: {counts.get('lead', 0)}")
    lines.append(f"- Trials: {counts.get('trial', 0)}")
    lines.append(f"- Customers: {counts.get('customer', 0)}")
    lines.append(f"- Payments: {counts.get('payment', 0)}")
    lines.append(f"- Subscriptions: {counts.get('subscription', 0)}")
    lines.append("")
    if counts.get("payment", 0) == 0 and counts.get("customer", 0) == 0:
        lines.append("I do not see connected customer/payment records in the local Arka DB yet. Connect Moneris/customer logs for real sales reporting.")
    return "\n".join(lines)

def marketing_plan():
    plan = [
        "Fix astraasystems.com homepage first: clean Tools/Workspace positioning, not old Engines language.",
        "Make Estimator, Finance, Operations, Expense, and Workspace pages clear and conversion-focused.",
        "Add strong calls to action: Start trial, View pricing, Contact Astraa, Login to Workspace.",
        "Create lead capture logging for every contact/trial request.",
        "Create industry landing pages for contractors, franchises, nonprofits, and regular businesses.",
        "Track each lead source and follow-up status.",
        "Use CASL-safe inbound follow-up only where consent exists."
    ]

    s = state()
    s["marketing_plan"] = [{"id": uid(), "status": "open", "item": x} for x in plan]
    save_state(s)

    for item in plan:
        business_event("marketing", "plan_item", item, "open")

    return "Astraa customer-growth plan:\n\n" + "\n".join(f"{i+1}. {x}" for i, x in enumerate(plan))

def build_tool_work_queue():
    queue = []
    for tool in ASTRAA_TOOLS:
        item = {
            "id": uid(),
            "tool": tool,
            "status": "open",
            "mission": f"Review and improve Astraa {tool} website/tool readiness."
        }
        queue.append(item)
        business_event("product_tools", "tool_work_assigned", item["mission"], "open")

    s = state()
    s["tool_work_queue"] = queue
    save_state(s)

    lines = ["Astraa tool work queue assigned:", ""]
    for item in queue:
        lines.append(f"- {item['tool']}: {item['mission']}")
    return "\n".join(lines)

def module_registry():
    return load_json(MODULE_REGISTRY_PATH, {"modules": [], "updated_at": ""})

def save_module_registry(reg):
    reg["updated_at"] = now()
    save_json(MODULE_REGISTRY_PATH, reg)

def discover_modules():
    roots = [
        REPO_ROOT / "ArdhanarishvaraOS",
        REPO_ROOT / "ardhanarishvara",
        REPO_ROOT / "arka_core",
        REPO_ROOT / "arka_system",
        REPO_ROOT / "aruhan",
        REPO_ROOT / "aruhan_runtime_loop.py",
        REPO_ROOT / "astraa_arka_bridge.py",
        REPO_ROOT / "lead_capture.py"
    ]

    allowed = {".py", ".json", ".md", ".txt", ".yaml", ".yml"}
    found = []

    for root in roots:
        try:
            if root.is_file() and root.suffix.lower() in allowed:
                found.append({"name": root.name, "path": str(root), "auto_allowed": False, "run_command": ""})
            elif root.is_dir():
                for p in root.rglob("*"):
                    if len(found) >= 200:
                        break
                    if p.is_file() and p.suffix.lower() in allowed:
                        found.append({"name": p.name, "path": str(p), "auto_allowed": False, "run_command": ""})
        except Exception as e:
            log_event("module_discovery_error", str(e))

    reg = module_registry()
    existing = {m.get("path") for m in reg.get("modules", [])}

    for item in found:
        if item["path"] not in existing:
            reg.setdefault("modules", []).append(item)

    save_module_registry(reg)
    log_event("module_discovery", f"found={len(found)}")
    return reg.get("modules", [])

def format_modules(mods):
    if not mods:
        return "I checked the ecosystem paths but did not find modules yet."

    lines = [f"I found {len(mods)} ecosystem module records.", "", "First modules:"]
    for m in mods[:15]:
        auto = "auto_allowed" if m.get("auto_allowed") else "not_auto_allowed"
        lines.append(f"- {m.get('name')} | {auto} | {m.get('path')}")
    return "\n".join(lines)

def classify_command(w):
    if w in ["status", "check status", "repo status", "git status"]:
        return "git status --short", "READ_ONLY"

    maps = [
        (["python version", "check python"], "python --version", "READ_ONLY"),
        (["git version"], "git --version", "READ_ONLY"),
        (["recent commits", "last commits", "git log"], "git log --oneline -5", "READ_ONLY"),
        (["list files", "show files", "folder"], "dir", "READ_ONLY"),
        (["run tests", "pytest", "test ecosystem"], "pytest -q", "LOCAL_EXEC")
    ]

    for keys, cmd, kind in maps:
        if any(k in w for k in keys):
            return cmd, kind

    return "", ""

def run_command(cmd):
    if cmd not in ALLOWLIST:
        return "Blocked. That command is not allowlisted: " + cmd

    try:
        p = subprocess.run(cmd, cwd=str(REPO_ROOT), shell=True, text=True, capture_output=True, timeout=90)
        output = (p.stdout + p.stderr).strip() or "Done. The command completed with no output."
        log_event("command_ran", cmd)
        return output
    except Exception as e:
        log_event("command_error", str(e))
        return "Error: " + str(e)


def extract_family_facts(raw):
    """
    Extract family facts from natural language, even if 'record/save/remember'
    appears at the end of the sentence.

    Examples:
    - Arka, My wife's name Thrilochana, and my first born son's name is Bhirav Aditya. record these
    - my wife's name is Thrilochana
    - my first-born son's name is Bhirav Aditya
    """
    text = (raw or "").strip()
    low = text.lower()

    facts = []

    # Only auto-save from natural sentence if user clearly asks to record/save/remember,
    # or if it begins with Arka and contains direct family name facts.
    has_save_intent = any(x in low for x in [
        "record", "save", "remember", "put this in memory", "add to memory"
    ])

    has_family_fact = any(x in low for x in [
        "wife", "son", "daughter", "child", "first born", "first-born"
    ]) and "name" in low

    if not (has_save_intent and has_family_fact):
        return []

    # Wife name patterns.
    wife_patterns = [
        r"wife'?s name is ([A-Za-z][A-Za-z .'-]{1,80})",
        r"wife'?s name ([A-Za-z][A-Za-z .'-]{1,80})(?:,|\.| and|$)",
        r"my wife name is ([A-Za-z][A-Za-z .'-]{1,80})",
        r"my wife name ([A-Za-z][A-Za-z .'-]{1,80})(?:,|\.| and|$)"
    ]

    for pat in wife_patterns:
        m = re.search(pat, text, flags=re.I)
        if m:
            name = m.group(1).strip(" .,'")
            # Trim trailing words from request phrases if accidentally captured.
            name = re.split(r"\b(record|save|remember|please)\b", name, flags=re.I)[0].strip(" .,'")
            if name:
                facts.append("my wife's name is " + name)

    # Son name patterns.
    son_patterns = [
        r"first[- ]born son'?s name is ([A-Za-z][A-Za-z .'-]{1,80})",
        r"first[- ]born son'?s name ([A-Za-z][A-Za-z .'-]{1,80})(?:,|\.| and|$)",
        r"son'?s name is ([A-Za-z][A-Za-z .'-]{1,80})",
        r"son'?s name ([A-Za-z][A-Za-z .'-]{1,80})(?:,|\.| and|$)",
        r"my son name is ([A-Za-z][A-Za-z .'-]{1,80})"
    ]

    for pat in son_patterns:
        m = re.search(pat, text, flags=re.I)
        if m:
            name = m.group(1).strip(" .,'")
            name = re.split(r"\b(record|save|remember|please)\b", name, flags=re.I)[0].strip(" .,'")
            if name:
                if "first" in pat:
                    facts.append("my first-born son's name is " + name)
                facts.append("my son's name is " + name)

    # Remove duplicates while preserving order.
    clean = []
    seen = set()
    for f in facts:
        key = f.lower()
        if key not in seen:
            clean.append(f)
            seen.add(key)

    return clean


def save_many_active_memories(facts):
    saved = []
    for fact in facts:
        result = save_active_memory(fact)
        saved.append(fact)
    if not saved:
        return ""
    if len(saved) == 1:
        return "Saved. I'll remember: " + saved[0]
    return "Saved. I'll remember:\n" + "\n".join("- " + f for f in saved)


def recall_name_from_memory(relation):
    relation = relation.lower().strip()

    if relation == "wife":
        terms = ["wife"]
        patterns = [
            r"wife'?s name is ([A-Za-z][A-Za-z .'-]{1,80})",
            r"wife name is ([A-Za-z][A-Za-z .'-]{1,80})"
        ]
    elif relation in ["son", "first-born son", "first born son"]:
        terms = ["son"]
        patterns = [
            r"first[- ]born son'?s name is ([A-Za-z][A-Za-z .'-]{1,80})",
            r"son'?s name is ([A-Za-z][A-Za-z .'-]{1,80})",
            r"son name is ([A-Za-z][A-Za-z .'-]{1,80})"
        ]
    else:
        terms = [relation]
        patterns = [rf"{re.escape(relation)}'?s name is ([A-Za-z][A-Za-z .'-]{{1,80}})"]

    # Active memory first.
    for text in active_memory_texts():
        low = text.lower()
        if any(t in low for t in terms) and "name" in low:
            for pat in patterns:
                m = re.search(pat, text, flags=re.I)
                if m:
                    return clean_extracted_name(m.group(1))

    # Journal fallback if available.
    try:
        rows = search_journal_user_only(terms[0], limit=30)
    except Exception:
        rows = []

    for ts, role, content in rows:
        low = content.lower()
        if "name" in low:
            for pat in patterns:
                m = re.search(pat, content, flags=re.I)
                if m:
                    return clean_extracted_name(m.group(1))

    return ""



def arka_encode_query(q):
    return urllib.parse.quote_plus((q or "").strip())


def arka_source_link_fallback(query):
    """
    If live scraping is blocked, return useful source/search links.
    This is better than a dead-end response and does not fake facts.
    """
    q = (query or "").strip()
    enc = arka_encode_query(q)

    links = [
        ("Bing search", "https://www.bing.com/search?q=" + enc),
        ("DuckDuckGo search", "https://duckduckgo.com/?q=" + enc),
        ("Google search", "https://www.google.com/search?q=" + enc)
    ]

    lines = [
        "I could not pull reliable live snippets from the local web connector.",
        "I won't make anything up, but here are source links you can open/check:",
        ""
    ]

    for name, url in links:
        lines.append("- " + name + ": " + url)

    log_event("web_source_fallback", q)
    return "\\n".join(lines)


def arka_search_or_sources(query):
    """
    Try Arka's live web search function if available.
    If it returns nothing, provide useful source links.
    """
    q = (query or "").strip()
    if not q:
        return "Tell me what you want me to search."

    results = []

    # Prefer strongest local search helper available.
    try:
        if "arka_web_search_v2" in globals():
            results = arka_web_search_v2(q, limit=8)
        elif "web_search_sources" in globals():
            results = web_search_sources(q, limit=8)
    except Exception as e:
        log_event("web_search_runtime_error", str(e))
        results = []

    if results:
        try:
            if "format_web_results_v2" in globals():
                return format_web_results_v2(q, results)
            return format_web_results(q, results)
        except Exception:
            lines = ["Here is what I found for: " + q, ""]
            for i, r in enumerate(results, 1):
                lines.append(str(i) + ". " + r.get("title", "Result"))
                if r.get("snippet"):
                    lines.append("   " + r.get("snippet"))
                lines.append("   Source: " + r.get("url", ""))
                lines.append("")
            return "\\n".join(lines).strip()

    return arka_source_link_fallback(q)


def arka_flight_source_fallback(raw):
    """
    Travel source mode. No fake prices. No ticket holds.
    Special handling for Vancouver/YVR to Hyderabad/HYD.
    """
    q = (raw or "").strip()
    low = q.lower()

    # Normalize likely route.
    from_yvr = any(x in low for x in ["vancouver", "yvr"])
    to_hyd = any(x in low for x in ["hyderabad", "hyd"])

    lines = [
        "I could not pull verified live fare snippets from the local connector.",
        "I won't invent prices and I won't claim ticket holds.",
        ""
    ]

    if from_yvr and to_hyd:
        lines.append("Best source pages for Vancouver/YVR to Hyderabad/HYD:")
        lines.append("- Google Flights route page: https://www.google.com/travel/flights/flights-from-vancouver-to-hyderabad.html")
        lines.append("- Skyscanner Canada route page: https://www.skyscanner.ca/routes/yvra/hyd/vancouver-to-hyderabad.html")
        lines.append("- Skyscanner YVR-HYD route page: https://www.skyscanner.com/routes/yvr/hyd/vancouver-international-to-hyderabad.html")
        lines.append("")
        lines.append("For December 2026, use the date grid / month view on those pages to verify live fares.")
    else:
        enc = arka_encode_query(q + " flight prices")
        lines.append("Flight search sources:")
        lines.append("- Google Flights: https://www.google.com/travel/flights")
        lines.append("- Bing travel search: https://www.bing.com/search?q=" + enc)
        lines.append("- DuckDuckGo travel search: https://duckduckgo.com/?q=" + enc)
        lines.append("- Skyscanner: https://www.skyscanner.ca/")
        lines.append("- Kayak: https://www.ca.kayak.com/flights")
        lines.append("- Expedia: https://www.expedia.ca/Flights")

    log_event("flight_source_fallback", q)
    return "\\n".join(lines)


def arka_is_general_question(raw):
    w = (raw or "").lower().strip()

    if not w:
        return False

    # Avoid routing personal memory or command phrases to web.
    blocked = [
        "what is my wife",
        "what's my wife",
        "what is my son",
        "what's my son",
        "what do you remember",
        "what did i say",
        "show memory",
        "show journal",
        "record this",
        "save this",
        "remember that",
        "check website",
        "how are sales",
        "marketing",
        "assign astraa"
    ]

    if any(b in w for b in blocked):
        return False

    starters = [
        "what ", "who ", "when ", "where ", "why ", "how ",
        "do ", "does ", "did ", "can ", "could ", "should ",
        "best ", "find ", "search ", "compare ", "price ", "prices ",
        "tell me about "
    ]

    return w.endswith("?") or any(w.startswith(s) for s in starters)


def arka_general_question_response(raw):
    """
    For unknown factual questions, do source mode rather than dead fallback.
    """
    q = (raw or "").strip()
    if not q:
        return "I'm here."

    # Flight/travel gets travel source handling.
    low = q.lower()
    if any(x in low for x in ["flight", "flights", "airfare", "ticket price", "ticket prices", "travel price"]):
        return arka_flight_source_fallback(q)

    return arka_search_or_sources(q)



def clean_extracted_name(name):
    """
    Cleans accidental captures like:
    - is Bhirav Aditya
    - name is Bhirav Aditya
    - Bhirav Aditya record this
    """
    name = (name or "").strip(" .,'")

    # Remove accidental leading words.
    name = re.sub(r"^(is|name is|called|named)\s+", "", name, flags=re.I).strip(" .,'")

    # Remove accidental trailing command/request words.
    name = re.split(r"\b(record|save|remember|please|important information)\b", name, flags=re.I)[0].strip(" .,'")

    return name


def clean_memory_line(text):
    """
    Prevent huge journal dumps and Arka's own previous responses from polluting recall.
    """
    text = (text or "").strip()

    # Keep active facts short and useful.
    if "Recent conversation journal:" in text:
        return ""

    if text.lower().startswith("here's what i remember"):
        return ""

    if text.lower().startswith("here's what i found"):
        return ""

    if text.lower().startswith("saved. i'll remember"):
        return ""

    if text.lower().startswith("yeah, i got you"):
        return ""

    # Avoid returning the user's exact recall question as a memory.
    if text.lower().startswith("what do you remember about"):
        return ""

    if text.lower().startswith("what did i say about"):
        return ""

    return text


def recall_topic_clean(topic, limit=6):
    """
    Active memory first, then clean user-only journal.
    """
    topic = (topic or "").strip()
    records = []

    # Active memory
    for mem in recall_memory(topic):
        clean = clean_memory_line(mem)
        if clean and clean not in [x[1] for x in records]:
            records.append(("Active memory", clean))

    # User-only journal
    try:
        rows = search_journal_user_only(topic, limit=20)
    except Exception:
        rows = []

    for ts, role, content in rows:
        clean = clean_memory_line(content)
        if clean and clean not in [x[1] for x in records]:
            records.append(("User said", clean))
        if len(records) >= limit:
            break

    return records[:limit]



PRODUCTS = ["Commerce", "Data", "Inference", "Distribution", "Vault"]

DEFAULT_PRICING_MAP = {
    "Commerce": {
        "competitive_reference": "Shopify / BigCommerce / WooCommerce-style commerce platforms",
        "source_notes": [
            "Shopify-style market references commonly show tiered pricing around Basic, Grow, Advanced, and Plus.",
            "Use official provider pages before final pricing."
        ],
        "starter_direction": "Astraa Commerce should likely be priced as a business tool, not a cheap widget. Start with Basic/Professional/Custom."
    },
    "Data": {
        "competitive_reference": "Snowflake / data cloud / warehouse / workspace tools",
        "source_notes": [
            "Snowflake uses consumption-based pricing with compute credits and storage pricing.",
            "Astraa Data should avoid uncontrolled usage costs for small businesses."
        ],
        "starter_direction": "Astraa Data should use packaged tiers with usage caps, then custom pricing for larger data volumes."
    },
    "Inference": {
        "competitive_reference": "OpenAI API / inference API / agent pricing",
        "source_notes": [
            "OpenAI API pricing is token-based and model-dependent.",
            "Astraa Inference should price by included usage plus overage or custom contract."
        ],
        "starter_direction": "Astraa Inference should be gated carefully with included requests/tokens and strict overage controls."
    },
    "Distribution": {
        "competitive_reference": "Shippo / ShipStation / shipping and logistics software",
        "source_notes": [
            "Shippo has Starter/Pro/Premier-style pricing with label and shipment volume considerations.",
            "Astraa Distribution should be priced by shipment/location/operation complexity."
        ],
        "starter_direction": "Astraa Distribution should start as Professional/Custom for logistics-heavy businesses."
    },
    "Vault": {
        "competitive_reference": "Dropbox Business / Box / secure file vault and document storage",
        "source_notes": [
            "Dropbox Business pricing uses per-user tiers for team storage and security features.",
            "Astraa Vault should include secure document storage, audit, retention, and client access controls."
        ],
        "starter_direction": "Astraa Vault can be bundled with other tools or sold as secure document/audit storage."
    }
}


def extract_products_from_text(raw):
    text = raw or ""
    found = []

    for product in PRODUCTS:
        if re.search(rf"\b{re.escape(product)}\b", text, flags=re.I):
            found.append(product)

    # If user says "other tools" but no list, include all five currently open tools.
    if not found and any(x in text.lower() for x in ["other tools", "these products", "these product", "products up and running"]):
        found = PRODUCTS[:]

    # preserve order
    ordered = []
    for p in PRODUCTS:
        if p in found:
            ordered.append(p)

    return ordered


def is_product_ceo_directive(raw):
    w = (raw or "").lower()

    product_words = any(p.lower() in w for p in PRODUCTS)
    directive_words = any(x in w for x in [
        "get astraa",
        "get these product",
        "get these products",
        "up and running",
        "fully running",
        "competitive pricing",
        "find competitive pricing",
        "product up",
        "tools up",
        "start working",
        "get them working"
    ])

    return product_words and directive_words


def ensure_product_state():
    s = state()
    s.setdefault("product_work_queue", [])
    s.setdefault("competitive_pricing_queue", [])
    s.setdefault("competitive_pricing_map", DEFAULT_PRICING_MAP)
    save_state(s)
    return s


def add_product_work(product, directive):
    s = ensure_product_state()

    existing = [
        x for x in s.get("product_work_queue", [])
        if x.get("product") == product and x.get("status") in ["open", "in_progress"]
    ]

    if existing:
        return existing[0]

    item = {
        "id": uid(),
        "timestamp": now(),
        "product": product,
        "status": "open",
        "priority": "high",
        "directive": directive,
        "mission": f"Get Astraa {product} up and running fully: product page, feature scope, pricing, lead path, and readiness checks.",
        "next_actions": [
            f"Audit local Astraa {product} files/pages/modules.",
            f"Create or update public website positioning for {product}.",
            f"Find competitive pricing references for {product}.",
            f"Prepare Basic / Professional / Custom packaging recommendation for {product}.",
            f"Log readiness gaps and action queue items for {product}."
        ]
    }

    s["product_work_queue"].insert(0, item)
    save_state(s)

    try:
        business_event("product_tools", "product_work_assigned", json.dumps(item), "open")
    except Exception:
        log_event("product_work_assigned", item)

    return item


def add_competitive_pricing_work(product):
    s = ensure_product_state()

    existing = [
        x for x in s.get("competitive_pricing_queue", [])
        if x.get("product") == product and x.get("status") in ["open", "in_progress"]
    ]

    if existing:
        return existing[0]

    pricing = DEFAULT_PRICING_MAP.get(product, {})

    item = {
        "id": uid(),
        "timestamp": now(),
        "product": product,
        "status": "open",
        "priority": "high",
        "mission": f"Find competitive pricing and package recommendation for Astraa {product}.",
        "competitive_reference": pricing.get("competitive_reference", ""),
        "starter_direction": pricing.get("starter_direction", ""),
        "research_sources_needed": [
            f"Official pricing pages for top {product} competitors",
            "Current monthly pricing",
            "Usage limits",
            "Free trial model",
            "Feature differences",
            "Best Astraa Basic / Professional / Custom fit"
        ]
    }

    s["competitive_pricing_queue"].insert(0, item)
    save_state(s)

    try:
        business_event("pricing", "competitive_pricing_assigned", json.dumps(item), "open")
    except Exception:
        log_event("competitive_pricing_assigned", item)

    return item


def handle_product_ceo_directive(raw):
    products = extract_products_from_text(raw)

    if not products:
        return "Tell me which Astraa products you want me to assign."

    # Save this directive as active memory too because this is CEO-level product direction.
    try:
        save_active_memory("CEO directive: " + raw.strip())
    except Exception:
        pass

    work_items = []
    pricing_items = []

    for product in products:
        work_items.append(add_product_work(product, raw.strip()))
        pricing_items.append(add_competitive_pricing_work(product))

    lines = [
        "Got it. I created CEO/COO product work assignments for Astraa.",
        "",
        "Products assigned:"
    ]

    for product in products:
        lines.append(f"- {product}: open → product readiness + website page + competitive pricing")

    lines.append("")
    lines.append("Immediate operating plan:")
    lines.append("1. Audit each product’s local files/pages/modules.")
    lines.append("2. Build or update website positioning for each product.")
    lines.append("3. Find competitive pricing references.")
    lines.append("4. Recommend Astraa Basic / Professional / Custom packaging.")
    lines.append("5. Log readiness gaps and next actions.")
    lines.append("")
    lines.append("Use: show product work queue")
    lines.append("Use: show competitive pricing")

    return "\n".join(lines)


def render_product_work_queue_text():
    s = ensure_product_state()
    queue = s.get("product_work_queue", [])

    if not queue:
        return "No Astraa product work items are open yet."

    lines = ["Astraa product work queue:"]
    for item in queue[:20]:
        lines.append("")
        lines.append(f"- {item.get('product')} | {item.get('status')} | {item.get('priority')}")
        lines.append(f"  Mission: {item.get('mission')}")
        for action in item.get("next_actions", [])[:5]:
            lines.append(f"  - {action}")

    return "\n".join(lines)


def render_competitive_pricing_text(product_filter=""):
    s = ensure_product_state()
    queue = s.get("competitive_pricing_queue", [])
    pricing_map = s.get("competitive_pricing_map", DEFAULT_PRICING_MAP)

    product_filter = (product_filter or "").strip().lower()

    if product_filter:
        queue = [x for x in queue if product_filter in x.get("product", "").lower()]

    if not queue:
        return "No competitive pricing work items are open yet."

    lines = ["Competitive pricing work queue:"]

    for item in queue[:20]:
        product = item.get("product", "")
        pricing = pricing_map.get(product, {})

        lines.append("")
        lines.append(f"- {product} | {item.get('status')} | {item.get('priority')}")
        lines.append(f"  Reference market: {item.get('competitive_reference')}")
        lines.append(f"  Starter direction: {item.get('starter_direction')}")

        notes = pricing.get("source_notes", [])
        if notes:
            lines.append("  Source notes:")
            for note in notes:
                lines.append("  - " + note)

    return "\n".join(lines)


def product_dashboard_html():
    s = state()
    product_queue = s.get("product_work_queue", [])
    pricing_queue = s.get("competitive_pricing_queue", [])

    html = []
    html.append("<h3>Astraa Product Command</h3>")

    if not product_queue:
        html.append("<p>No product work assigned yet.</p>")
    else:
        html.append("<p><b>Product work queue</b></p>")
        for item in product_queue[:8]:
            html.append("<p>• " + esc(item.get("product", "")) + ": " + esc(item.get("status", "")) + " — " + esc(item.get("mission", "")) + "</p>")

    if pricing_queue:
        html.append("<p><b>Competitive pricing queue</b></p>")
        for item in pricing_queue[:8]:
            html.append("<p>• " + esc(item.get("product", "")) + ": " + esc(item.get("status", "")) + " — " + esc(item.get("competitive_reference", "")) + "</p>")

    return "".join(html)



# ============================================================
# Arka Universal Processing Brain
# ============================================================

def normalize_key_name(key):
    key = (key or "").strip().lower()
    key = re.sub(r"[^a-z0-9]+", "_", key)
    key = key.strip("_")
    return key or "context"


def extract_key_value_context(raw):
    """
    Generic structured context parser.
    Handles:
    Platforms: DoorDash + Instacart
    EV charging: $20/week
    Goal: $50,000/year
    Work schedule: daily or 3 days/week
    """
    lines = [x.strip() for x in (raw or "").splitlines() if x.strip()]
    pairs = []

    for line in lines:
        # Remove bullets.
        clean = line.strip("•-–— ").strip()

        if ":" in clean:
            key, value = clean.split(":", 1)
            key = key.strip()
            value = value.strip()

            if key and value:
                pairs.append({
                    "key": normalize_key_name(key),
                    "label": key,
                    "value": value,
                    "raw": clean
                })

    return pairs


def is_structured_context(raw):
    pairs = extract_key_value_context(raw)
    return len(pairs) >= 2


def save_universal_context(raw):
    pairs = extract_key_value_context(raw)

    if not pairs:
        return ""

    s = state()
    s.setdefault("universal_context", {})
    s.setdefault("universal_context_log", [])

    saved_lines = []

    for pair in pairs:
        key = pair["key"]
        value = pair["value"]
        label = pair["label"]

        s["universal_context"][key] = {
            "label": label,
            "value": value,
            "source": "structured_user_context",
            "updated_at": now()
        }

        s["universal_context_log"].insert(0, {
            "id": uid(),
            "timestamp": now(),
            "key": key,
            "label": label,
            "value": value,
            "raw": pair["raw"]
        })

        # Save into active memory so other systems can reuse it.
        try:
            save_active_memory(f"Context - {label}: {value}")
        except Exception:
            pass

        saved_lines.append(f"- {label}: {value}")

    s["universal_context_log"] = s["universal_context_log"][:200]
    save_state(s)

    try:
        log_event("universal_context_saved", json.dumps(pairs))
    except Exception:
        pass

    return (
        "Got it. I updated my context brain with this information:\n\n"
        + "\n".join(saved_lines)
        + "\n\nI’ll use this context in future answers instead of treating every question from scratch."
    )


def extract_natural_context_fact(raw):
    """
    Captures natural contextual statements that are not exact memory commands.
    Examples:
    - I drive an EV...
    - I want to add Instacart...
    - I prefer short answers...
    - The website is our income source...
    """
    text = (raw or "").strip()
    w = text.lower()

    if not text:
        return ""

    # Avoid capturing questions.
    if "?" in text:
        return ""

    starters = [
        "i drive ",
        "i want ",
        "i prefer ",
        "i need ",
        "we need ",
        "our ",
        "the website ",
        "astraa ",
        "arka should ",
        "from now on ",
        "for future ",
        "use ",
        "include ",
        "add "
    ]

    if any(w.startswith(s) for s in starters):
        return text

    # Capture sentences with obvious persistent context words.
    context_words = [
        "ev", "charging", "platform", "schedule", "goal",
        "income", "website", "astraa", "arka", "preference",
        "customer", "pricing", "tool", "memory"
    ]

    if any(c in w for c in context_words) and any(v in w for v in [" is ", " are ", " should ", " will ", " want ", " need "]):
        return text

    return ""


def save_natural_context(raw):
    fact = extract_natural_context_fact(raw)

    if not fact:
        return ""

    s = state()
    s.setdefault("universal_context_notes", [])

    item = {
        "id": uid(),
        "timestamp": now(),
        "text": fact,
        "source": "natural_context"
    }

    s["universal_context_notes"].insert(0, item)
    s["universal_context_notes"] = s["universal_context_notes"][:200]
    save_state(s)

    try:
        save_active_memory("Context note: " + fact)
    except Exception:
        pass

    try:
        log_event("natural_context_saved", fact)
    except Exception:
        pass

    return (
        "Got it. I saved that as context, not just chat:\n\n"
        "- " + fact + "\n\n"
        "I’ll use it to adjust future answers."
    )


def get_universal_context_text():
    s = state()
    ctx = s.get("universal_context", {})
    notes = s.get("universal_context_notes", [])

    lines = []

    if ctx:
        lines.append("Structured context:")
        for key, item in ctx.items():
            lines.append(f"- {item.get('label', key)}: {item.get('value', '')}")

    if notes:
        lines.append("")
        lines.append("Context notes:")
        for item in notes[:10]:
            lines.append("- " + item.get("text", ""))

    return "\n".join(lines).strip()


def show_universal_context():
    text = get_universal_context_text()
    if not text:
        return "I don't have universal context saved yet."
    return "Here is my current context brain:\n\n" + text


def universal_work_item(raw):
    """
    Generic action/task creator for commands not caught by specialized routers.
    """
    text = (raw or "").strip()
    w = text.lower()

    action_starters = [
        "build ", "create ", "make ", "get ", "prepare ", "plan ",
        "analyze ", "audit ", "review ", "fix ", "improve ",
        "start ", "assign ", "find ", "research ", "compare "
    ]

    if not any(w.startswith(x) or ("arka, " + x) in w for x in action_starters):
        return ""

    # Avoid hijacking already-handled math/web/memory questions.
    if any(x in w for x in ["what is my", "what do you remember", "calculate "]):
        return ""

    s = state()
    s.setdefault("universal_work_queue", [])

    area = "general"

    if "astraa" in w or "website" in w or "customer" in w or "pricing" in w:
        area = "astraa_business"
    elif "arka" in w or "memory" in w or "brain" in w:
        area = "arka_system"
    elif "income" in w or "revenue" in w or "sales" in w:
        area = "revenue"
    elif "math" in w or "calculate" in w:
        area = "math"
    elif "web" in w or "search" in w:
        area = "web_research"

    item = {
        "id": uid(),
        "timestamp": now(),
        "area": area,
        "status": "open",
        "priority": "normal",
        "request": text,
        "next_step": "Review, classify, route to the right Arka skill/module, and log outcome."
    }

    s["universal_work_queue"].insert(0, item)
    s["universal_work_queue"] = s["universal_work_queue"][:200]
    save_state(s)

    try:
        business_event(area, "universal_work_item_created", json.dumps(item), "open")
    except Exception:
        log_event("universal_work_item_created", json.dumps(item))

    return (
        "Got it. I turned that into a universal Arka work item.\n\n"
        f"- Area: {area}\n"
        f"- Status: open\n"
        f"- Request: {text}\n\n"
        "Use: show universal work queue"
    )


def show_universal_work_queue():
    s = state()
    queue = s.get("universal_work_queue", [])

    if not queue:
        return "No universal work items are open."

    lines = ["Universal Arka work queue:"]
    for item in queue[:20]:
        lines.append("")
        lines.append(f"- {item.get('area')} | {item.get('status')} | {item.get('priority')}")
        lines.append("  Request: " + item.get("request", ""))
        lines.append("  Next step: " + item.get("next_step", ""))

    return "\n".join(lines)


def universal_brain_response(raw):
    """
    Last-resort intelligent fallback.
    Instead of 'Yeah, I got you', Arka explains what she can do next.
    """
    text = (raw or "").strip()

    if not text:
        return "I'm here."

    return (
        "I heard you. I don't have a specialized skill for that exact request yet, "
        "but I can still process it as context, a task, a calculation, web research, or an Astraa action.\n\n"
        "Try one of these forms:\n"
        "- record this: [important fact]\n"
        "- calculate [numbers]\n"
        "- search the web for [topic]\n"
        "- check website health\n"
        "- create plan for [goal]\n"
        "- show context brain\n"
        "- show universal work queue"
    )


def arka_reply(raw):
    raw = raw.strip()
    w = raw.lower()

    # Arka Governor Dispatcher: runtime routing above old patch routers.
    governor_result = arka_governor_dispatch(raw, web_func=globals().get("arka_search_or_sources"))
    # ARKA_RESPONSE_VALIDATOR_PHASE1
    # Validate governor output before it is returned to the owner.
    if governor_result:
        try:
            try:
                from arka_v1.core.response_validator import validate_response, ValidationStatus
                from arka_v1.core.response_repairer import repair_response
            except Exception:
                from core.response_validator import validate_response, ValidationStatus
                from core.response_repairer import repair_response

            validation = validate_response(
                prompt=raw,
                response=governor_result,
                context={
                    "owner_name": "Keshanth Sivayogampillai",
                    "requires_source": False,
                    "sources": [],
                    "verified_actions": [],
                },
                strict_mode=True,
            )

            if validation.status == ValidationStatus.FAIL:
                # ARKA_RESPONSE_REPAIRER_PHASE2
                # Attempt safe repair before blocking the answer.
                repair = repair_response(
                    prompt=raw,
                    response=governor_result,
                    issues=validation.issues,
                    context={
                        "owner_name": "Keshanth Sivayogampillai",
                        "requires_source": False,
                        "sources": [],
                        "verified_actions": [],
                    },
                    strict_mode=True,
                )

                if repair.repaired:
                    repaired_validation = validate_response(
                        prompt=raw,
                        response=repair.response,
                        context={
                            "owner_name": "Keshanth Sivayogampillai",
                            "requires_source": False,
                            "sources": [],
                            "verified_actions": [],
                        },
                        strict_mode=True,
                    )

                    if repaired_validation.status == ValidationStatus.PASS:
                        governor_result = repair.response
                    else:
                        issue_codes = ", ".join(issue.code for issue in repaired_validation.issues)
                        governor_result = (
                            "I attempted to repair the response, but the repaired response "
                            "did not pass Arka Phase 2 validation. "
                            f"Issues: {issue_codes}"
                        )
                else:
                    issue_codes = ", ".join(issue.code for issue in validation.issues)
                    governor_result = (
                        "I need to correct that before answering. "
                        "The response did not pass Arka Phase 1 validation, "
                        "and Phase 2 could not safely repair it. "
                        f"Issues: {issue_codes}"
                    )

        except Exception as validator_error:
            governor_result = (
                "I generated a response, but the Phase 1 response validator failed "
                f"before final output: {validator_error}"
            )

    if governor_result:
        try:
            log_event("governor_dispatch", raw)
        except Exception:
            pass
        return governor_result


    # Universal Processing Brain: structured context first.
    if is_structured_context(raw):
        return save_universal_context(raw)

    if w.startswith("show context brain") or w.startswith("show universal context"):
        return show_universal_context()

    if w.startswith("show universal work queue"):
        return show_universal_work_queue()

    # Natural context capture.
    natural_context_result = save_natural_context(raw)
    if natural_context_result:
        return natural_context_result

    # Generic work/action creation.
    universal_task_result = universal_work_item(raw)
    if universal_task_result:
        return universal_task_result


    # Full Math OS router: local calculations before web fallback.
    math_result = arka_math_os_router(raw)
    if math_result:
        try:
            log_event("math_os_calculation", raw)
        except Exception:
            pass
        return math_result


    # Product CEO/COO directive router.
    if is_product_ceo_directive(raw):
        return handle_product_ceo_directive(raw)

    if w.startswith("show product work queue") or w.startswith("show astraa product work"):
        return render_product_work_queue_text()

    if w.startswith("show competitive pricing") or w.startswith("show pricing queue"):
        return render_competitive_pricing_text()

    if w.startswith("competitive pricing for "):
        product = raw[len("competitive pricing for "):].strip()
        return render_competitive_pricing_text(product)


    # Clean topic recall, active memory first, no journal dumps.
    if "what do you remember about" in w:
        topic = w.split("what do you remember about", 1)[1].strip(" ?.").strip()

        if not topic:
            return "Tell me what topic you want me to recall."

        records = recall_topic_clean(topic)

        if records:
            lines = [f"Here's what I remember about {topic}:"]
            for label, content in records:
                lines.append(f"- {label}: {content}")
            return "\\n".join(lines)

        return "I don't have clean memory or user-journal context about " + topic + " yet."

    if (
        "what did i say about" in w
        or "what have i said about" in w
        or "what did i tell you about" in w
        or "what did we discuss about" in w
    ):
        topic = raw.lower()
        for phrase in [
            "what did i say about",
            "what have i said about",
            "what did i tell you about",
            "what did we discuss about"
        ]:
            topic = topic.replace(phrase, "")
        topic = topic.strip(" ?.:")

        if not topic:
            return "Tell me what topic you want me to search."

        records = recall_topic_clean(topic)

        if records:
            lines = [f"Here's what I found about {topic}:"]
            for label, content in records:
                lines.append(f"- {label}: {content}")
            return "\\n".join(lines)

        return f"I searched memory and your user journal, but I don't have anything clean about {topic} yet."


    # V1.1 web search and question fallback.
    if (
        w.startswith("search the web for ")
        or w.startswith("web search ")
        or w.startswith("search ")
        or w.startswith("look up ")
        or w.startswith("google ")
    ):
        q = raw.strip()
        for prefix in [
            "search the web for ",
            "web search ",
            "search ",
            "look up ",
            "google "
        ]:
            if q.lower().startswith(prefix):
                q = q[len(prefix):].strip()
                break
        return arka_search_or_sources(q)

    if any(x in w for x in [
        "flight price",
        "flight prices",
        "find flight",
        "best flight",
        "airfare",
        "ticket price",
        "ticket prices"
    ]):
        return arka_flight_source_fallback(raw)

    if arka_is_general_question(raw):
        return arka_general_question_response(raw)


    # Natural multi-fact family memory save.
    family_facts = extract_family_facts(raw)
    if family_facts:
        return save_many_active_memories(family_facts)

    # Family relationship recall.
    if (
        "what is my wife's name" in w
        or "what's my wife's name" in w
        or "what is my wifes name" in w
        or "do you remember my wife's name" in w
        or "do you remember my wifes name" in w
    ):
        name = recall_name_from_memory("wife")
        if name:
            return "Your wife's name is " + name + "."
        return "I don't have your wife's name saved yet. Say: Arka record this: my wife's name is [name]"

    if (
        "what is my son's name" in w
        or "what's my son's name" in w
        or "what is my sons name" in w
        or "what is my first born son's name" in w
        or "what is my first-born son's name" in w
        or "do you remember my son's name" in w
    ):
        name = recall_name_from_memory("son")
        if name:
            return "Your son's name is " + name + "."
        return "I don't have your son's name saved yet. Say: Arka record this: my son's name is [name]"


    # Persistent conversation journal recall.
    # This lets Arka answer: "what did I say about X?"
    if (
        "what did i say about" in w
        or "what have i said about" in w
        or "what did we say about" in w
        or "what did we discuss about" in w
        or "what did i tell you about" in w
    ):
        topic = raw.lower()
        for phrase in [
            "what did i say about",
            "what have i said about",
            "what did we say about",
            "what did we discuss about",
            "what did i tell you about"
        ]:
            topic = topic.replace(phrase, "")
        topic = topic.strip(" ?.:")

        if not topic:
            return "Tell me what topic you want me to look up in the conversation journal."

        records = combined_recall(topic)

        if records:
            lines = [f"Here's what I found about {topic}:"]
            for role, ts, content in records:
                label = "Active memory" if role == "active_memory" else role
                lines.append(f"- {label}: {content}")
            return "\\n".join(lines)

        return f"I searched my active memory and conversation journal, but I don't have anything recorded about {topic} yet."

    # Better memory recall: use both active memory and journal.
    if "what do you remember about" in w:
        topic = w.split("what do you remember about", 1)[1].strip(" ?.").strip()

        if not topic:
            return "Tell me what you want me to remember about."

        records = combined_recall(topic)

        if records:
            lines = [f"Here's what I remember about {topic}:"]
            for role, ts, content in records:
                label = "Active memory" if role == "active_memory" else role
                lines.append(f"- {label}: {content}")
            return "\\n".join(lines)

        return "I don't have active memory or journal context about " + topic + " yet."



    if not raw:
        return "I'm here."


    if w.startswith("show journal") or w.startswith("show conversation journal"):
        rows = search_journal("", limit=20)
        if not rows:
            return "The conversation journal is empty."
        lines = ["Recent conversation journal:"]
        for ts, role, content in rows:
            lines.append(f"- {ts} | {role}: {content}")
        return "\\n".join(lines)

    if w in ["hi", "hey", "hello", "hi arka", "hey arka", "hello arka"]:
        return "Hi Keshanth, I'm here."

    if w in ["thanks", "thank you", "ty"]:
        return "Anytime."

    fact = extract_save_command(raw)
    if fact:
        return save_active_memory(fact)

    if "what is my son's name" in w or "what's my son's name" in w or "what is my sons name" in w:
        for text in recall_memory("son"):
            m = re.search(r"son'?s name is ([A-Za-z][A-Za-z .'-]{1,60})", text, flags=re.I)
            if m:
                return "Your son's name is " + m.group(1).strip(" .") + "."
        return "I don't have your son's name saved yet. Say: Arka record this: my son's name is [name]"

    if "what do you remember about" in w:
        topic = w.split("what do you remember about", 1)[1].strip(" ?.").strip()
        records = recall_memory(topic)
        if records:
            return "Here's what I remember about " + topic + ":\n" + "\n".join("- " + r for r in records)
        return "I don't have active memory about " + topic + " yet."

    if w in ["memory", "memories", "show memory"] or "what have you learned" in w:
        records = active_memory_texts()
        if not records:
            return "I don't have active memories yet."
        return "Here's what I remember:\n" + "\n".join("- " + r for r in records[:15])

    if "website health" in w or "audit astraasystems.com" in w or "check website" in w or "site broken" in w or "website broken" in w:
        return website_audit()

    if "how are sales" in w or "sales status" in w or "revenue status" in w or "how is sale" in w:
        return sales_status()

    if "marketing" in w or "drive more customer" in w or "drive in more customer" in w or "get more customers" in w:
        return marketing_plan()

    if "start working on the other tools" in w or "assign astraa tools" in w or "tool work queue" in w or "what should astraa build next" in w:
        return build_tool_work_queue()

    if w.startswith("search the web for ") or w.startswith("look up ") or w.startswith("google "):
        q = re.sub(r"^(search the web for|look up|google)\s*", "", raw, flags=re.I).strip()
        return format_web_results(q, web_search_sources(q))

    if "flight" in w or "ticket" in w or "airfare" in w or "travel price" in w:
        q = raw
        results = web_search_sources(q + " flight prices official airline Google Flights Expedia Kayak Skyscanner", 8)
        if not results:
            return "I tried to find flight-price sources, but I could not pull reliable results. I won't invent prices or claim ticket holds."
        return "I found flight-price source pages to check. No fake prices. No ticket holds.\n\n" + format_web_results(q, results)

    if "what modules" in w or "modules do you have" in w or "ardhanarishvara" in w or "adhanarishvara" in w or "library os" in w:
        return format_modules(discover_modules())

    if "who are you" in w or "what are you" in w:
        return "I'm Arka V1 — your internal CEO/COO operating system for Arka HQ. I monitor Astraa, organize sales/marketing/product work, remember what you tell me, and log actions."

    cmd, kind = classify_command(w)
    if cmd:
        if kind == "READ_ONLY":
            add_task(raw, kind, "ready", "Prepared safe read-only task.", cmd)
            return "Got it. I put that in the Action Queue: " + cmd
        add_task(raw, kind, "needs_approval", "Needs approval before execution.", cmd)
        return "Got it. I queued it, but it needs approval before I run it: " + cmd

    
    if arka_is_general_question(raw):
        return arka_general_question_response(raw)

    
    return universal_brain_response(raw)




def record_journal(role, content):
    """
    Persistent conversation journal.
    This records every user/Arka turn so Arka can recall context later.
    This is separate from active memory.
    """
    try:
        init()
        conn = sqlite3.connect(str(DB_PATH))
        conn.execute("""
            CREATE TABLE IF NOT EXISTS arka_conversation_journal (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                timestamp TEXT,
                role TEXT,
                content TEXT
            )
        """)
        conn.execute(
            "INSERT INTO arka_conversation_journal (timestamp, role, content) VALUES (?, ?, ?)",
            (now(), role, content)
        )
        conn.commit()
        conn.close()
    except Exception as e:
        try:
            print("[JOURNAL ERROR]", e)
        except Exception:
            pass


def search_journal(term, limit=12):
    """
    Search previous conversation turns.
    """
    term = (term or "").strip()

    try:
        init()
        conn = sqlite3.connect(str(DB_PATH))
        conn.execute("""
            CREATE TABLE IF NOT EXISTS arka_conversation_journal (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                timestamp TEXT,
                role TEXT,
                content TEXT
            )
        """)
        cur = conn.cursor()
        if term:
            cur.execute(
                "SELECT timestamp, role, content FROM arka_conversation_journal WHERE content LIKE ? ORDER BY id DESC LIMIT ?",
                (f"%{term}%", limit)
            )
        else:
            cur.execute(
                "SELECT timestamp, role, content FROM arka_conversation_journal ORDER BY id DESC LIMIT ?",
                (limit,)
            )
        rows = cur.fetchall()
        conn.close()
        return rows
    except Exception:
        return []


def combined_recall(term, limit=12):
    """
    Return active memory first, then conversation journal.
    """
    found = []

    for mem_text in recall_memory(term):
        found.append(("active_memory", "", mem_text))

    for ts, role, content in search_journal(term, limit=limit):
        if content not in [x[2] for x in found]:
            found.append((role, ts, content))

    return found[:limit]


def handle_chat(raw):
    # Visible chat
    add_chat("user", raw)

    # Persistent journal: every user message
    record_journal("user", raw)

    # Arka response
    reply = arka_reply(raw)

    # Visible chat
    add_chat("arka", reply)

    # Persistent journal: every Arka reply
    record_journal("arka", reply)

    return reply

def render_chat():
    chat = state().get("chat", [])
    if not chat:
        return '<div class="empty"><b>Arka V1 is live.</b><p>Say hi, ask for website health, sales status, marketing plan, or tell me to record something.</p></div>'

    out = []
    for msg in chat[-120:]:
        role = msg.get("role", "arka")
        label = "You" if role == "user" else "Arka"
        out.append(f'''
        <div class="msg {esc(role)}">
          <div class="bubble">
            <div class="label">{label}</div>
            <div>{esc(msg.get("text", ""))}</div>
          </div>
        </div>
        ''')
    return "".join(out)

def render_tasks():
    tasks = state().get("tasks", [])
    if not tasks:
        return "<p>No action tasks yet.</p>"

    out = []
    for t in tasks[:30]:
        controls = ""
        if t["status"] == "ready":
            controls = f'''
            <form method="POST" action="/run">
              <input type="hidden" name="id" value="{esc(t["id"])}">
              <button class="mini primary">Run read-only</button>
            </form>
            '''
        elif t["status"] == "needs_approval":
            controls = f'''
            <form method="POST" action="/run">
              <input type="hidden" name="id" value="{esc(t["id"])}">
              <input type="password" name="approval" placeholder="approval key">
              <button class="mini danger">Approve + run</button>
            </form>
            '''

        out.append(f'''
        <article class="task">
          <div><b>{esc(t["id"])}</b> <span>{esc(t["status"])}</span> <span>{esc(t["kind"])}</span></div>
          <p>{esc(t["user_words"])}</p>
          <code>{esc(t.get("command", ""))}</code>
          {controls}
          <pre>{esc(t.get("output", ""))}</pre>
        </article>
        ''')
    return "".join(out)

def render_exec_panel():
    s = state()
    findings = s.get("website_findings", [])[:5]
    marketing = s.get("marketing_plan", [])[:5]
    tools = s.get("tool_work_queue", [])[:10]
    sales = s.get("sales_snapshot", {}).get("counts", {})

    html = []

    html.append("<h3>Astraa Revenue Command</h3>")
    html.append("<div class='mini-grid'>")
    html.append(f"<div class='metric'><b>{sales.get('lead', 0)}</b><span>Leads</span></div>")
    html.append(f"<div class='metric'><b>{sales.get('trial', 0)}</b><span>Trials</span></div>")
    html.append(f"<div class='metric'><b>{sales.get('customer', 0)}</b><span>Customers</span></div>")
    html.append(f"<div class='metric'><b>{sales.get('payment', 0)}</b><span>Payments</span></div>")
    html.append("</div>")

    html.append("<h3>Website Findings</h3>")
    if findings:
        for f in findings:
            html.append("<p>• " + esc(f.get("finding", "")) + "</p>")
    else:
        html.append("<p>No website audit run yet.</p>")

    html.append("<h3>Marketing Plan</h3>")
    if marketing:
        for m in marketing:
            html.append("<p>• " + esc(m.get("item", "")) + "</p>")
    else:
        html.append("<p>No marketing plan generated yet.</p>")

    html.append("<h3>Astraa Tool Work Queue</h3>")
    if tools:
        for t in tools:
            html.append("<p>• " + esc(t.get("tool", "")) + ": " + esc(t.get("status", "")) + "</p>")
    else:
        html.append("<p>No tool work queue assigned yet.</p>")

    return "".join(html)

def logo_small():
    if LOGO_PNG.exists():
        return '<img src="/assets/company_logo.png" alt="Astraa Systems logo">'
    if LOGO_SVG.exists():
        return '<img src="/assets/company_logo.svg" alt="Astraa Systems logo">'
    return '<div class="logo">A</div>'


def logo_header():
    if HEADER_PNG.exists():
        return '<img class="hero-logo" src="/assets/company_logo_header.png" alt="Astraa Systems logo">'
    if LOGO_PNG.exists():
        return '<img class="hero-logo" src="/assets/company_logo.png" alt="Astraa Systems logo">'
    if LOGO_SVG.exists():
        return '<img class="hero-logo" src="/assets/company_logo.svg" alt="Astraa Systems logo">'
    return ""

def page():
    mem_count = len(memory().get("memories", []))
    mode = "REMOTE MODE" if REMOTE_MODE else "LOCAL MODE"

    css = """
    :root{--bg:#f5f7fb;--panel:#fff;--text:#07111f;--muted:#667085;--line:#d9e2f1;--blue:#1748d4;--navy:#071a44;--red:#ef4444;--shadow:0 24px 80px rgba(7,26,68,.14)}
    *{box-sizing:border-box}
    body{margin:0;background:var(--bg);color:var(--text);font-family:Inter,Segoe UI,Arial,sans-serif}
    .shell{max-width:1440px;margin:0 auto;padding:22px}
    .top{display:flex;justify-content:space-between;align-items:center;margin-bottom:18px}
    .brand{display:flex;gap:14px;align-items:center}
    .brand img,.logo{width:72px;height:72px;border-radius:18px;object-fit:cover;background:#050505;box-shadow:var(--shadow)}
    .kicker{font-size:12px;letter-spacing:.2em;text-transform:uppercase;color:var(--muted)}
    h1{font-size:32px;margin:2px 0 0}
    .badge{border:1px solid var(--line);border-radius:999px;padding:10px 14px;background:#fff;box-shadow:var(--shadow);color:var(--muted)}
    .grid{display:grid;grid-template-columns:.8fr 1.05fr .95fr;gap:16px;align-items:start}
    .card{background:#fff;border:1px solid var(--line);border-radius:28px;box-shadow:var(--shadow);overflow:hidden}
    .hero,.panel{padding:22px}
    .hero-logo{width:100%;max-height:170px;object-fit:contain;background:#050505;border-radius:22px;padding:16px;margin-bottom:16px}
    .metric{border:1px solid var(--line);border-radius:18px;padding:13px;margin-top:10px}
    .mini-grid{display:grid;grid-template-columns:repeat(2,1fr);gap:8px}
    .chat-card{display:flex;flex-direction:column;height:calc(100vh - 135px);min-height:680px}
    .chat-head{padding:18px 20px;border-bottom:1px solid var(--line)}
    .chat-body{flex:1;overflow:auto;padding:20px;background:linear-gradient(180deg,#fff,#f8fbff)}
    .chat-input{border-top:1px solid var(--line);padding:16px;background:#fff}
    .chat-input form{display:flex;gap:10px}
    textarea{flex:1;height:58px;min-height:58px;max-height:140px;border:1px solid var(--line);border-radius:18px;padding:14px;outline:none;resize:vertical}
    .send{border:0;border-radius:18px;padding:0 22px;background:linear-gradient(135deg,var(--navy),var(--blue));color:#fff;font-weight:900;cursor:pointer}
    .msg{display:flex;margin:12px 0}
    .msg.user{justify-content:flex-end}
    .msg.arka{justify-content:flex-start}
    .bubble{max-width:82%;border-radius:22px;padding:13px 15px;line-height:1.45;white-space:pre-wrap}
    .user .bubble{background:linear-gradient(135deg,var(--navy),var(--blue));color:white;border-bottom-right-radius:6px}
    .arka .bubble{background:#eef4ff;border:1px solid #d9e2f1;border-bottom-left-radius:6px}
    .label{font-size:11px;text-transform:uppercase;letter-spacing:.14em;opacity:.7;margin-bottom:4px}
    .task{border:1px solid var(--line);border-radius:20px;padding:14px;margin:10px 0;background:rgba(255,255,255,.72)}
    code{display:block;border-radius:14px;padding:10px;background:#f0f4ff;color:#13235c;overflow:auto}
    pre{white-space:pre-wrap;background:#0b1220;color:#dbeafe;border-radius:16px;padding:12px;overflow:auto}
    .mini{border:0;border-radius:12px;padding:9px 12px;margin-top:10px;margin-right:8px;cursor:pointer;font-weight:800}
    .primary{background:var(--blue);color:white}
    .danger{background:var(--red);color:white}
    input{border:1px solid var(--line);border-radius:12px;padding:10px;margin-top:10px}
    @media(max-width:1150px){.grid{grid-template-columns:1fr}.chat-card{height:auto;min-height:620px}.top{align-items:flex-start;flex-direction:column;gap:12px}}
    """

    return f'''
    <!doctype html>
    <html>
    <head>
      <meta charset="utf-8">
      <meta name="viewport" content="width=device-width, initial-scale=1">
      <title>Arka V1 - Internal CEO COO</title>
      <style>{css}</style>
    </head>
    <body>
      <div class="shell">
        <header class="top">
          <div class="brand">
            {logo_small()}
            <div>
              <div class="kicker">Arka V1 / Internal CEO COO</div>
              <h1>Founder Command Operating System</h1>
            </div>
          </div>
          <div class="badge">V1 Full Stack Local Core</div>
        </header>

        <main class="grid">
          <section class="card hero">
            {logo_header()}
            <div class="kicker">{mode}</div>
            <h2>Hey Keshanth - Arka V1 is live.</h2>
            <p>I am the internal CEO/COO command layer for Arka HQ. Website, revenue, marketing, tools, memory, modules, and logs are managed from here.</p>
            <div class="metric"><b>{mem_count}</b> active memories</div>
            <div class="metric"><b>{mode}</b> network mode</div>
            <div class="metric"><b>Astraa</b><span> revenue front door monitored from this console</span></div>
          </section>

          <section class="card chat-card">
            <div class="chat-head">
              <div class="kicker">Conversation with Arka</div>
              <b>Ask naturally: website health, sales status, marketing plan, assign Astraa tools.</b>
            </div>
            <div class="chat-body" id="chatBody">{render_chat()}</div>
            <div class="chat-input">
              <form id="chatForm">
                <textarea id="words" name="words" placeholder="hi / check website health / how are sales / create marketing plan / assign Astraa tools / Arka record this: ..."></textarea>
                <button class="send" type="submit">Send</button>
              </form>
            </div>
          </section>

          <aside class="card panel">
            {render_exec_panel()}
            <hr>
            <h3>Action Queue</h3>
            <div id="tasks">{render_tasks()}</div>
          </aside>
        </main>
      </div>

      <script>
      async function refreshPanels(){{
        const r = await fetch('/api/state');
        const data = await r.json();
        document.getElementById('chatBody').innerHTML = data.chat;
        document.getElementById('tasks').innerHTML = data.tasks;
        document.getElementById('chatBody').scrollTop = document.getElementById('chatBody').scrollHeight;
      }}

      document.getElementById('chatForm').addEventListener('submit', async function(e){{
        e.preventDefault();
        const box = document.getElementById('words');
        const words = box.value.trim();
        if(!words) return;
        box.value = '';
        await fetch('/api/chat', {{
          method:'POST',
          headers:{{'Content-Type':'application/x-www-form-urlencoded'}},
          body:new URLSearchParams({{words: words}})
        }});
        location.reload();
      }});
      </script>
    </body>
    </html>
    '''

class Handler(BaseHTTPRequestHandler):
    def do_GET(self):
        clean = self.path.lstrip("/")

        file_map = {
            "assets/company_logo.png": LOGO_PNG,
            "assets/company_logo_header.png": HEADER_PNG,
            "assets/company_logo.svg": LOGO_SVG
        }

        if clean in file_map and file_map[clean].exists():
            p = file_map[clean]
            ctype = "image/png" if p.suffix.lower() == ".png" else "image/svg+xml"
            self.send_response(200)
            self.send_header("Content-Type", ctype)
            self.end_headers()
            self.wfile.write(p.read_bytes())
            return

        if self.path == "/api/state":
            payload = {"chat": render_chat(), "tasks": render_tasks()}
            self.send_response(200)
            self.send_header("Content-Type", "application/json; charset=utf-8")
            self.end_headers()
            self.wfile.write(json.dumps(payload).encode("utf-8"))
            return

        if self.path == "/health":
            payload = {"ok": True, "name": APP_NAME, "version": VERSION, "mode": "remote" if REMOTE_MODE else "local"}
            self.send_response(200)
            self.send_header("Content-Type", "application/json; charset=utf-8")
            self.end_headers()
            self.wfile.write(json.dumps(payload).encode("utf-8"))
            return

        html = page()
        self.send_response(200)
        self.send_header("Content-Type", "text/html; charset=utf-8")
        self.end_headers()
        self.wfile.write(html.encode("utf-8"))

    def do_POST(self):
        data = parse_qs(self.rfile.read(int(self.headers.get("Content-Length", 0))).decode("utf-8"))

        if self.path == "/api/chat":
            handle_chat(data.get("words", [""])[0])
            self.send_response(200)
            self.send_header("Content-Type", "application/json; charset=utf-8")
            self.end_headers()
            self.wfile.write(json.dumps({"ok": True}).encode("utf-8"))
            return

        if self.path == "/run":
            s = state()
            task_id = data.get("id", [""])[0]
            approval = data.get("approval", [""])[0]

            for t in s.get("tasks", []):
                if t["id"] == task_id:
                    if t["kind"] == "LOCAL_EXEC":
                        expected = os.environ.get(APPROVAL_KEY_ENV, "")
                        if not expected:
                            t["status"] = "blocked"
                            t["output"] = "Approval key is not set."
                        elif approval != expected:
                            t["status"] = "blocked"
                            t["output"] = "Approval key did not match."
                        else:
                            t["status"] = "ran"
                            t["output"] = run_command(t.get("command", ""))
                    else:
                        t["status"] = "ran"
                        t["output"] = run_command(t.get("command", ""))
                    save_state(s)
                    break

        self.send_response(303)
        self.send_header("Location", "/")
        self.end_headers()

if __name__ == "__main__":
    init()
    print(APP_NAME, "v" + VERSION, "starting")
    print("REPO_ROOT:", REPO_ROOT)
    print("Mode:", "REMOTE" if REMOTE_MODE else "LOCAL")
    print("URL:", f"http://{HOST}:{PORT}")
    print("Health:", f"http://{HOST}:{PORT}/health")
    HTTPServer((HOST, PORT), Handler).serve_forever()
