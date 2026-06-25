from __future__ import annotations

import json
import os
import re
import sqlite3
import subprocess
import time
import urllib.parse
import urllib.request
from html import unescape
from pathlib import Path

DB_PATH = r"D:\ARKA_HQ\data\arka_core.db"
HQ_ROOT = Path(os.environ.get("ARKA_HQ_ROOT", r"D:\ARKA_HQ\repos\ardhanarishvara_git")).resolve()
ROOT = Path(__file__).parent
MEMORY_PATH = ROOT / "arka_memory.json"
MODULE_REGISTRY_PATH = ROOT / "arka_module_registry.json"

def _load_json(path, default):
    if path.exists():
        return json.loads(path.read_text(encoding="utf-8-sig"))
    return default

def _save_json(path, data):
    path.write_text(json.dumps(data, indent=2), encoding="utf-8")

def init_db():
    os.makedirs(os.path.dirname(DB_PATH), exist_ok=True)
    conn = sqlite3.connect(DB_PATH)
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

    conn.commit()
    conn.close()

def log_event(event_type, content):
    init_db()
    conn = sqlite3.connect(DB_PATH)
    conn.execute(
        "INSERT INTO arka_logs (timestamp, event_type, content) VALUES (?, ?, ?)",
        (time.strftime("%Y-%m-%dT%H:%M:%S"), event_type, content)
    )
    conn.commit()
    conn.close()

def lifecycle_insert(item_type, content, status="active", source="arka"):
    init_db()
    conn = sqlite3.connect(DB_PATH)
    conn.execute(
        "INSERT INTO lifecycle_store (timestamp, type, content, status, source) VALUES (?, ?, ?, ?, ?)",
        (time.strftime("%Y-%m-%dT%H:%M:%S"), item_type, content, status, source)
    )
    conn.commit()
    conn.close()

def save_active_memory(text, source="explicit_user_command"):
    text = text.strip()
    if not text:
        return "I need something to save."

    m = _load_json(MEMORY_PATH, {"memories": [], "pending_memories": [], "audit": []})

    entry = {
        "id": str(int(time.time() * 1000))[-8:],
        "type": "user_memory",
        "text": text,
        "source": source,
        "status": "active",
        "created_at": time.time()
    }

    m.setdefault("memories", []).insert(0, entry)
    m.setdefault("audit", []).insert(0, {
        "event": "memory_saved_active",
        "id": entry["id"],
        "created_at": time.time()
    })

    _save_json(MEMORY_PATH, m)
    lifecycle_insert("memory", text, status="active", source=source)
    log_event("memory_saved_active", text)

    return f"Saved. I'll remember: {text}"

def active_memories():
    m = _load_json(MEMORY_PATH, {"memories": []})
    return m.get("memories", [])

def recall_memory(term):
    term = (term or "").lower().strip()
    if not term:
        return []

    results = []
    for mem in active_memories():
        text = mem.get("text", "")
        if term in text.lower():
            results.append(text)
    return results[:10]

def extract_save_command(raw):
    patterns = [
        r"^arka[, ]+record this[: ]+(.*)$",
        r"^arka[, ]+save this[: ]+(.*)$",
        r"^arka[, ]+put this in memory[: ]+(.*)$",
        r"^put this in memory[: ]+(.*)$",
        r"^record this[: ]+(.*)$",
        r"^save this[: ]+(.*)$",
        r"^remember that[: ]*(.*)$",
        r"^remember[: ]+(.*)$"
    ]

    for pat in patterns:
        m = re.search(pat, raw.strip(), flags=re.I)
        if m:
            return m.group(1).strip()

    return ""

def web_search_sources(query, limit=5):
    """
    Lightweight web source discovery using DuckDuckGo HTML.
    This returns sources, titles, snippets when available.
    It does not claim structured facts unless visible in snippets.
    """
    q = urllib.parse.quote_plus(query)
    url = f"https://html.duckduckgo.com/html/?q={q}"

    headers = {
        "User-Agent": "Mozilla/5.0 ArkaHQ/0.5.2"
    }

    req = urllib.request.Request(url, headers=headers)

    try:
        with urllib.request.urlopen(req, timeout=10) as res:
            html = res.read().decode("utf-8", errors="ignore")
    except Exception as e:
        log_event("web_search_error", str(e))
        return []

    results = []

    # DuckDuckGo result blocks vary, so use tolerant regex.
    blocks = re.findall(r'<div class="result.*?</div>\s*</div>', html, flags=re.S)

    for block in blocks:
        if len(results) >= limit:
            break

        title_match = re.search(r'class="result__a"[^>]*href="([^"]+)"[^>]*>(.*?)</a>', block, flags=re.S)
        snippet_match = re.search(r'class="result__snippet"[^>]*>(.*?)</a>|class="result__snippet"[^>]*>(.*?)</div>', block, flags=re.S)

        if not title_match:
            continue

        href = unescape(title_match.group(1))
        title = re.sub(r"<.*?>", "", title_match.group(2), flags=re.S)
        title = unescape(title).strip()

        # DuckDuckGo sometimes wraps URLs in redirect param uddg.
        parsed = urllib.parse.urlparse(href)
        params = urllib.parse.parse_qs(parsed.query)
        if "uddg" in params:
            href = params["uddg"][0]

        snippet = ""
        if snippet_match:
            snippet_raw = snippet_match.group(1) or snippet_match.group(2) or ""
            snippet = re.sub(r"<.*?>", "", snippet_raw, flags=re.S)
            snippet = unescape(snippet).strip()

        results.append({
            "title": title,
            "url": href,
            "snippet": snippet
        })

    log_event("web_search", query)
    return results

def format_web_results(query, results):
    if not results:
        return (
            f"I tried searching for: {query}\n\n"
            "I could not pull reliable web results from the local connector. "
            "This may be a network, search-engine, or anti-scraping block."
        )

    lines = [f"Here is what I found for: {query}", ""]

    for i, r in enumerate(results, 1):
        lines.append(f"{i}. {r['title']}")
        if r.get("snippet"):
            lines.append(f"   {r['snippet']}")
        lines.append(f"   Source: {r['url']}")
        lines.append("")

    return "\n".join(lines).strip()

def flight_search(raw):
    query = raw.strip()

    if "from " not in query.lower():
        query = query + " from YVR"

    search_query = query + " flight prices official airline Google Flights Expedia Kayak Skyscanner"
    results = web_search_sources(search_query, limit=7)

    if not results:
        return (
            "I tried to find flight-price sources, but I could not pull reliable web results from the local connector. "
            "I will not invent prices."
        )

    lines = [
        "I found flight-price source pages to check. I will not invent prices or claim a hold.",
        "",
        "Use these sources to verify live fares:"
    ]

    for i, r in enumerate(results, 1):
        lines.append(f"{i}. {r['title']}")
        if r.get("snippet"):
            lines.append(f"   {r['snippet']}")
        lines.append(f"   Source: {r['url']}")
        lines.append("")

    lines.append("If a page snippet does not show a price, I cannot verify the fare from the source text alone.")
    log_event("flight_search", raw)

    return "\n".join(lines).strip()

def module_registry():
    return _load_json(MODULE_REGISTRY_PATH, {"modules": [], "updated_at": ""})

def save_module_registry(data):
    data["updated_at"] = time.strftime("%Y-%m-%dT%H:%M:%S")
    _save_json(MODULE_REGISTRY_PATH, data)

def discover_modules():
    roots = [
        HQ_ROOT / "ArdhanarishvaraOS",
        HQ_ROOT / "ardhanarishvara",
        HQ_ROOT / "arka_core",
        HQ_ROOT / "arka_system",
        HQ_ROOT / "aruhan",
        HQ_ROOT / "aruhan_runtime_loop.py",
        HQ_ROOT / "astraa_arka_bridge.py",
        HQ_ROOT / "lead_capture.py"
    ]

    allowed_ext = {".py", ".json", ".md", ".txt", ".yaml", ".yml"}
    keywords = [
        "module", "engine", "agent", "skill", "runtime", "loop",
        "core", "memory", "bridge", "os", "arka", "aruhan",
        "astraa", "autonomy", "approval", "permission"
    ]

    found = []

    for root in roots:
        try:
            if root.is_file() and root.suffix.lower() in allowed_ext:
                found.append({
                    "name": root.name,
                    "path": str(root),
                    "status": "discovered",
                    "auto_allowed": False,
                    "run_command": ""
                })
            elif root.is_dir():
                for p in root.rglob("*"):
                    if len(found) >= 150:
                        break
                    if not p.is_file():
                        continue
                    if p.suffix.lower() not in allowed_ext:
                        continue
                    low = str(p).lower()
                    if any(k in low for k in keywords):
                        found.append({
                            "name": p.name,
                            "path": str(p),
                            "status": "discovered",
                            "auto_allowed": False,
                            "run_command": ""
                        })
        except Exception as e:
            log_event("module_discovery_error", str(e))

    reg = module_registry()
    existing_paths = {m.get("path") for m in reg.get("modules", [])}

    for item in found:
        if item["path"] not in existing_paths:
            reg.setdefault("modules", []).append(item)

    save_module_registry(reg)
    log_event("module_discovery", f"found={len(found)}")

    return reg.get("modules", [])

def format_modules(modules, limit=12):
    if not modules:
        return "I checked the ecosystem module paths but did not find modules yet."

    lines = [
        f"I found {len(modules)} ecosystem module records.",
        "",
        "First modules:"
    ]

    for m in modules[:limit]:
        auto = "auto_allowed" if m.get("auto_allowed") else "not_auto_allowed"
        lines.append(f"- {m.get('name')} | {auto} | {m.get('path')}")

    lines.append("")
    lines.append("I can automatically run modules only after they are registered as auto_allowed with a run_command.")
    return "\n".join(lines)

def authorize_module_auto(module_name):
    reg = module_registry()
    name_low = module_name.lower().strip()
    matched = []

    for m in reg.get("modules", []):
        if name_low in m.get("name", "").lower() or name_low in m.get("path", "").lower():
            m["auto_allowed"] = True
            m["status"] = "auto_allowed"
            matched.append(m)

    save_module_registry(reg)

    if not matched:
        return f"I couldn't find a module matching: {module_name}"

    log_event("module_authorized_auto", module_name)
    return f"Authorized {len(matched)} module record(s) for automatic use. Add run_command before execution if needed."

def run_auto_allowed_modules():
    reg = module_registry()
    ran = []
    skipped = []

    for m in reg.get("modules", []):
        if not m.get("auto_allowed"):
            continue

        cmd = (m.get("run_command") or "").strip()
        if not cmd:
            skipped.append(m.get("name"))
            continue

        try:
            result = subprocess.run(
                cmd,
                cwd=str(HQ_ROOT),
                shell=True,
                text=True,
                capture_output=True,
                timeout=120
            )
            output = (result.stdout + result.stderr).strip()
            ran.append((m.get("name"), output[:1000]))
            log_event("module_auto_run", f"{m.get('name')} | {cmd}")
        except Exception as e:
            ran.append((m.get("name"), "ERROR: " + str(e)))
            log_event("module_auto_run_error", f"{m.get('name')} | {e}")

    lines = []

    if ran:
        lines.append("I ran the auto_allowed modules with run commands:")
        for name, output in ran:
            lines.append(f"- {name}: {output or 'completed with no output'}")

    if skipped:
        lines.append("")
        lines.append("These modules are auto_allowed but have no run_command yet:")
        for name in skipped:
            lines.append(f"- {name}")

    if not ran and not skipped:
        lines.append("No modules are currently configured for automatic execution.")

    return "\n".join(lines)

def arka_capability_router(raw):
    w = raw.lower().strip()

    # Natural greeting.
    if w in ["hi", "hey", "hello", "hi arka", "hey arka", "hello arka"]:
        return "Hi Keshanth, I'm here."

    # Explicit active save command.
    fact = extract_save_command(raw)
    if fact:
        return save_active_memory(fact)

    # Son name direct recall.
    if (
        "what is my son's name" in w
        or "what's my son's name" in w
        or "what is my sons name" in w
        or "do you remember my son's name" in w
    ):
        records = recall_memory("son")
        if not records:
            return "I don't have your son's name saved in active memory yet."

        for text in records:
            m = re.search(r"son'?s name is ([A-Za-z][A-Za-z .'-]{1,60})", text, flags=re.I)
            if m:
                return "Your son's name is " + m.group(1).strip(" .") + "."

        return "Here's what I remember about your son: " + "; ".join(records)

    # General memory recall.
    if "what do you remember about" in w:
        topic = w.split("what do you remember about", 1)[1].strip(" ?.").strip()
        records = recall_memory(topic)
        if records:
            return "Here's what I remember about " + topic + ":\n" + "\n".join("- " + r for r in records)
        return "I don't have active memory about " + topic + " yet."

    # Web search with sources.
    if w.startswith("search the web for ") or w.startswith("look up ") or w.startswith("google "):
        query = re.sub(r"^(search the web for|look up|google)\s*", "", raw, flags=re.I).strip()
        results = web_search_sources(query)
        return format_web_results(query, results)

    # Flight search with sources, no fake prices.
    if "flight" in w or "ticket" in w or "airfare" in w or "travel price" in w:
        return flight_search(raw)

    # Module discovery.
    if (
        "what modules" in w
        or "modules do you have" in w
        or "self modules" in w
        or "ardhanarishvara" in w
        or "adhanarishvara" in w
        or "library os" in w
    ):
        mods = discover_modules()
        return format_modules(mods)

    # Authorize auto module.
    if w.startswith("authorize module "):
        name = raw[len("authorize module "):].strip()
        return authorize_module_auto(name)

    # Run auto allowed modules.
    if (
        "run your modules" in w
        or "use your modules" in w
        or "better yourself" in w
        or "improve yourself" in w
        or "learn and evolve" in w
    ):
        discover_modules()
        auto_result = run_auto_allowed_modules()

        return (
            "I checked my ecosystem module registry and applied the auto_allowed rule.\n\n"
            + auto_result
            + "\n\nEverything is logged. Unknown modules are discovered first, then need registry configuration before execution."
        )

    return ""
