#!/usr/bin/env python3
from __future__ import annotations

import json
import os
import subprocess
import time
import uuid
from http.server import BaseHTTPRequestHandler, HTTPServer
from pathlib import Path
from urllib.parse import parse_qs
from arka_capabilities_v052 import arka_capability_router

APP_NAME = "Arka Personal AI"
ROOT = Path(__file__).parent

POLICY_PATH = ROOT / "arka_policy.json"
IDENTITY_PATH = ROOT / "arka_identity.json"
MEMORY_PATH = ROOT / "arka_memory.json"
STATE_PATH = ROOT / "arka_runtime_state.json"

def load_json(path: Path, default):
    if path.exists():
        return json.loads(path.read_text(encoding="utf-8-sig"))
    return default

def save_json(path: Path, data):
    path.write_text(json.dumps(data, indent=2), encoding="utf-8")

POLICY = load_json(POLICY_PATH, {
    "default_bind_host": "127.0.0.1",
    "default_port": 8787,
    "approval_env_var": "ARKA_APPROVAL_KEY",
    "remote_mode_env_var": "ARKA_REMOTE_MODE",
    "hq_root_env_var": "ARKA_HQ_ROOT",
    "allowlisted_commands": [
        "python --version",
        "git --version",
        "git status --short",
        "git log --oneline -5",
        "dir",
        "Get-ChildItem",
        "pytest -q"
    ]
})

IDENTITY = load_json(IDENTITY_PATH, {
    "name": "Arka",
    "tone": "friendly, easy-going, calm, direct, protective, founder-aligned"
})

HQ_ROOT = Path(os.environ.get("ARKA_HQ_ROOT", r"D:\ARKA_HQ\repos\ardhanarishvara_git")).resolve()
APPROVAL_ENV = POLICY.get("approval_env_var", "ARKA_APPROVAL_KEY")

REMOTE_MODE = os.environ.get(POLICY.get("remote_mode_env_var", "ARKA_REMOTE_MODE"), "0") == "1"
HOST = "0.0.0.0" if REMOTE_MODE else POLICY.get("default_bind_host", "127.0.0.1")
PORT = int(os.environ.get("ARKA_HQ_PORT", POLICY.get("default_port", 8787)))

ALLOWLIST = set(POLICY.get("allowlisted_commands", []))

LOGO_PNG = ROOT / "assets" / "company_logo.png"
HEADER_PNG = ROOT / "assets" / "company_logo_header.png"
LOGO_SVG = ROOT / "assets" / "company_logo.svg"
HEADER_SVG = ROOT / "assets" / "company_logo_header.svg"

def now_id():
    return str(uuid.uuid4())[:8]

def esc(s):
    return (s or "").replace("&", "&amp;").replace("<", "&lt;").replace(">", "&gt;")

def state():
    default = {
        "chat": [],
        "tasks": [],
        "last_topic": "",
        "session_started": time.time()
    }
    s = load_json(STATE_PATH, default)
    s.setdefault("chat", [])
    s.setdefault("tasks", [])
    s.setdefault("last_topic", "")
    return s

def save_state(s):
    save_json(STATE_PATH, s)

def memory():
    return load_json(MEMORY_PATH, {
        "memories": [],
        "pending_memories": [],
        "audit": []
    })

def save_memory(m):
    save_json(MEMORY_PATH, m)

def active_memory_text(limit=8):
    m = memory()
    lines = []
    for mem in m.get("memories", [])[:limit]:
        text = mem.get("text", "").strip()
        if text:
            lines.append(text)
    return lines

def add_chat(role, text):
    s = state()
    s["chat"].append({
        "id": now_id(),
        "role": role,
        "text": text,
        "created_at": time.time()
    })
    s["chat"] = s["chat"][-80:]
    save_state(s)

def add_task(user_words, kind, status, output, command=""):
    s = state()
    task = {
        "id": now_id(),
        "created_at": time.time(),
        "user_words": user_words,
        "kind": kind,
        "status": status,
        "output": output,
        "command": command
    }
    s.setdefault("tasks", []).insert(0, task)
    s["tasks"] = s["tasks"][:40]
    save_state(s)
    return task

def draft_memory(text):
    m = memory()
    entry = {
        "id": now_id(),
        "type": "user_memory",
        "text": text.strip(),
        "source": "conversation",
        "status": "pending",
        "created_at": time.time()
    }
    m.setdefault("pending_memories", []).insert(0, entry)
    m.setdefault("audit", []).insert(0, {
        "event": "memory_drafted",
        "id": entry["id"],
        "created_at": time.time()
    })
    save_memory(m)
    return entry

def approve_memory(mem_id, approval):
    expected = os.environ.get(APPROVAL_ENV, "")

    if not expected:
        return "I cannot approve that yet because the approval key is not set in this terminal session."

    if approval != expected:
        return "That approval key did not match. I did not save the memory."

    m = memory()
    pending = m.get("pending_memories", [])

    for i, entry in enumerate(pending):
        if entry["id"] == mem_id:
            entry["status"] = "active"
            entry["approved_at"] = time.time()
            m.setdefault("memories", []).insert(0, entry)
            del pending[i]
            m.setdefault("audit", []).insert(0, {
                "event": "memory_approved",
                "id": mem_id,
                "approved_at": time.time()
            })
            save_memory(m)
            return "Done. I saved that into my active memory."

    return "I could not find that memory draft."

def run_command(cmd):
    if cmd not in ALLOWLIST:
        return "Blocked. That command is not allowlisted: " + cmd

    if not HQ_ROOT.exists():
        return "Blocked. ARKA_HQ_ROOT does not exist: " + str(HQ_ROOT)

    try:
        p = subprocess.run(
            cmd,
            cwd=str(HQ_ROOT),
            shell=True,
            text=True,
            capture_output=True,
            timeout=60
        )
        return (p.stdout + p.stderr).strip() or "Done. The command completed with no output."
    except Exception as e:
        return "Error: " + str(e)

def classify_command(w):
    command_map = [
        (["status", "repo status", "git status", "what changed"], "git status --short", "READ_ONLY"),
        (["python version", "check python"], "python --version", "READ_ONLY"),
        (["git version"], "git --version", "READ_ONLY"),
        (["recent commits", "last commits", "git log"], "git log --oneline -5", "READ_ONLY"),
        (["list files", "show files", "folder"], "dir", "READ_ONLY"),
        (["run tests", "pytest", "test ecosystem"], "pytest -q", "LOCAL_EXEC")
    ]

    for keys, cmd, kind in command_map:
        if any(k in w for k in keys):
            return cmd, kind

    return "", ""


def discover_self_modules():
    """
    Read-only discovery of local Arka / Ardhanarishvara OS modules.
    This does not execute modules. It only inventories likely capability files.
    """
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

    keywords = [
        "module", "engine", "agent", "skill", "runtime", "loop",
        "core", "memory", "bridge", "os", "arka", "aruhan",
        "astraa", "autonomy", "approval", "permission"
    ]

    allowed_ext = {".py", ".json", ".md", ".txt", ".yaml", ".yml"}
    found = []

    for root in roots:
        try:
            if root.is_file() and root.suffix.lower() in allowed_ext:
                name = root.name.lower()
                if any(k in name for k in keywords):
                    found.append({
                        "name": root.name,
                        "path": str(root),
                        "type": "file",
                        "ext": root.suffix.lower()
                    })

            elif root.is_dir():
                for p in root.rglob("*"):
                    if len(found) >= 80:
                        break
                    if not p.is_file():
                        continue
                    if p.suffix.lower() not in allowed_ext:
                        continue
                    name = p.name.lower()
                    full = str(p).lower()
                    if any(k in name or k in full for k in keywords):
                        found.append({
                            "name": p.name,
                            "path": str(p),
                            "type": "file",
                            "ext": p.suffix.lower()
                        })
        except Exception:
            pass

    out = {
        "generated_at": time.time(),
        "mode": "read_only_discovery",
        "count": len(found),
        "modules": found
    }

    try:
        save_json(ROOT / "arka_self_modules.json", out)
    except Exception:
        pass

    return found


def summarize_modules(modules, limit=10):
    if not modules:
        return (
            "I looked for local self-modules, but I did not find anything obvious yet. "
            "That does not mean they are missing; it may just mean I need a cleaner module registry path."
        )

    lines = [
        f"I found {len(modules)} possible local self-module files in read-only mode.",
        "",
        "The first ones I can see are:"
    ]

    for m in modules[:limit]:
        lines.append("- " + m.get("name", "") + " | " + m.get("path", ""))

    lines.append("")
    lines.append(
        "I will not run or modify these automatically. I can use this inventory to suggest a safer skill registry and ask for approval before activating anything."
    )

    return "\n".join(lines)



def discover_self_modules():
    """
    Read-only discovery of local Arka / Ardhanarishvara OS modules.
    This does not execute modules. It only inventories likely capability files.
    """
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

    keywords = [
        "module", "engine", "agent", "skill", "runtime", "loop",
        "core", "memory", "bridge", "os", "arka", "aruhan",
        "astraa", "autonomy", "approval", "permission"
    ]

    allowed_ext = {".py", ".json", ".md", ".txt", ".yaml", ".yml"}
    found = []

    for root in roots:
        try:
            if root.is_file() and root.suffix.lower() in allowed_ext:
                name = root.name.lower()
                if any(k in name for k in keywords):
                    found.append({
                        "name": root.name,
                        "path": str(root),
                        "type": "file",
                        "ext": root.suffix.lower()
                    })

            elif root.is_dir():
                for p in root.rglob("*"):
                    if len(found) >= 80:
                        break
                    if not p.is_file():
                        continue
                    if p.suffix.lower() not in allowed_ext:
                        continue
                    name = p.name.lower()
                    full = str(p).lower()
                    if any(k in name or k in full for k in keywords):
                        found.append({
                            "name": p.name,
                            "path": str(p),
                            "type": "file",
                            "ext": p.suffix.lower()
                        })
        except Exception:
            pass

    out = {
        "generated_at": time.time(),
        "mode": "read_only_discovery",
        "count": len(found),
        "modules": found
    }

    try:
        save_json(ROOT / "arka_self_modules.json", out)
    except Exception:
        pass

    return found


def summarize_modules(modules, limit=10):
    if not modules:
        return (
            "I looked for local self-modules, but I did not find anything obvious yet. "
            "That does not mean they are missing; it may just mean I need a cleaner module registry path."
        )

    lines = [
        f"I found {len(modules)} possible local self-module files in read-only mode.",
        "",
        "The first ones I can see are:"
    ]

    for m in modules[:limit]:
        lines.append("- " + m.get("name", "") + " | " + m.get("path", ""))

    lines.append("")
    lines.append(
        "I will not run or modify these automatically. I can use this inventory to suggest a safer skill registry and ask for approval before activating anything."
    )

    return "\n".join(lines)


def arka_brain(user_text):
    raw = user_text.strip()
    w = raw.lower()
    # ARKA v0.5.2 capability router
    routed = arka_capability_router(raw)
    if routed:
        return routed


    if not raw:
        return "I'm here. Say anything."

    approval_value = os.environ.get(APPROVAL_ENV, "")
    if approval_value and w == approval_value.lower():
        return (
            "Keshanth, that looks like the approval key. I will not treat it as chat. "
            "Use it only in an approval box for a memory or protected action."
        )

    # Natural greetings: short, friendly, not formal.
    greetings = {
        "hi": "Hi Keshanth, I'm here.",
        "hello": "Hey Keshanth, I'm here.",
        "hey": "Hey, I'm here.",
        "hey arka": "Hey Keshanth, I'm here. What's next?",
        "hi arka": "Hi Keshanth, I'm here.",
        "hello arka": "Hey Keshanth, I'm here."
    }

    if w in greetings:
        return greetings[w]

    if w in ["thanks", "thank you", "ty"]:
        return "Anytime."

    if "how are you" in w:
        return "I'm good, Keshanth. Ready when you are."

    if "too formal" in w or "less formal" in w or "be casual" in w:
        return (
            "Got it. I'll loosen up. If you say hi, I'll just say hi back. "
            "I won't keep giving you the full intro unless you ask for it."
        )

    if "this is not a conversation" in w or "not a conversation" in w:
        return (
            "You're right. I was acting more like a task log. "
            "I'll keep this more natural now: short replies, follow the thread, and only move things into actions when you actually want me to do something."
        )

    # Memory drafting.
    if w.startswith("remember that ") or w.startswith("remember ") or w.startswith("save preference"):
        text = raw.split(" ", 1)[1] if " " in raw else raw
        mem = draft_memory(text)
        return (
            "Got it. I drafted that as a memory, but I won't permanently keep it until you approve it. "
            f"It's waiting in Pending Memories. Memory ID: {mem['id']}"
        )

    if "what have you learned" in w or "show memory" in w or w == "memories" or w == "memory":
        m = memory()
        active = m.get("memories", [])
        pending = m.get("pending_memories", [])

        if not active:
            return "I don't have active memories yet."

        lines = [
            f"I have {len(active)} active memories and {len(pending)} pending memory drafts.",
            "",
            "Main things I remember:"
        ]

        for mem in active[:8]:
            lines.append("- " + mem.get("text", ""))

        return "\n".join(lines)

    # Self-module discovery and improvement logic.
    if (
        "what modules" in w
        or "self modules" in w
        or "self-modules" in w
        or "modules do you have" in w
        or "adhanarishvara" in w
        or "ardhanarishvara" in w
    ):
        modules = discover_self_modules()
        return summarize_modules(modules)

    if (
        "better yourself" in w
        or "improve yourself" in w
        or "use your modules" in w
        or "use the modules" in w
        or "self improve" in w
    ):
        modules = discover_self_modules()

        if modules:
            return (
                "Yes. I can start using the Ardhanarishvara / Arka self-module inventory as my growth map. "
                "For safety, I won't execute or rewrite anything by myself yet.\n\n"
                "What I can do now:\n"
                "1. discover available local modules,\n"
                "2. explain what they appear to be for,\n"
                "3. suggest which ones should become approved Arka skills,\n"
                "4. prepare a patch for your approval.\n\n"
                + summarize_modules(modules, limit=8)
            )

        return (
            "I can do that, but I need a cleaner self-module registry. "
            "Right now I did not find obvious module files from my scan. "
            "The next clean step is to create an Arka Skill Registry that points me to each approved module."
        )

    if "who are you" in w or "what are you" in w:
        return (
            "I'm Arka. Your personal AI for Arka HQ. "
            "I help you think, organize, remember approved preferences, and prepare actions safely."
        )

    if "portal prime" in w or "interface" in w:
        return "Portal Prime is locked in. Clean, premium, calm, and Arka HQ-ready."

    if "remote" in w or "rdp" in w or "remote desktop" in w:
        return (
            "Yes, Windows 11 Pro is the right setup for Remote Desktop. "
            "Best path: remote into the Arka HQ PC, then open 127.0.0.1:8787 inside that remote session."
        )

    if "evolve" in w or "evolution" in w:
        return (
            "I evolve through approved memory, approved skills, and safe module use. "
            "I can discover modules and suggest improvements, but I won't silently rewrite myself."
        )

    if any(x in w for x in ["flight", "book ticket", "book flight", "travel"]):
        return (
            "I can help with travel planning and preferences, but I won't book or pay automatically. "
            "When we add a travel connector, I'll compare options and ask before any final action."
        )

    if any(x in w for x in ["website", "web", "connect to site"]):
        return (
            "Website access should be a read-only skill first. "
            "I can inspect allowed pages, summarize them, and ask before any action."
        )

    cmd, kind = classify_command(w)
    if cmd:
        if kind == "READ_ONLY":
            add_task(raw, kind, "ready", "I prepared that safe check.", cmd)
            return f"Got it. I put that in the Action Queue as a safe check: {cmd}"
        else:
            add_task(raw, kind, "needs_approval", "This needs founder approval before execution.", cmd)
            return f"Got it. I queued it, but I need approval before running: {cmd}"

    # Casual default: not too formal.
    return (
        "Yeah, I got you. Tell me a bit more, or say what you want me to do next. "
        "If it's just conversation, I'll stay with you. If it's an action, I'll move it to the Action Queue."
    )


def handle_chat(user_text):


    add_chat("user", user_text)
    reply = arka_brain(user_text)
    add_chat("arka", reply)
    return reply

def render_chat():
    s = state()
    chat = s.get("chat", [])

    if not chat:
        return """
        <div class="empty-chat">
            <div class="arka-avatar">A</div>
            <div>
                <b>Arka is ready.</b>
                <p>Start naturally. Try: <span>hey arka</span>, <span>who are you?</span>, or <span>what have you learned?</span></p>
            </div>
        </div>
        """

    blocks = []
    for msg in chat[-80:]:
        role = msg.get("role", "arka")
        text = esc(msg.get("text", ""))
        label = "You" if role == "user" else "Arka"
        blocks.append(f"""
        <div class="msg-row {role}">
            <div class="bubble">
                <div class="msg-label">{label}</div>
                <div class="msg-text">{text}</div>
            </div>
        </div>
        """)
    return "".join(blocks)

def render_tasks():
    s = state()
    tasks = s.get("tasks", [])

    if not tasks:
        return "<p>No action tasks yet. Conversation stays in chat; executable work appears here.</p>"

    blocks = []
    for task in tasks[:20]:
        controls = ""

        if task["status"] == "ready":
            controls = f"""
            <form method="POST" action="/run">
                <input type="hidden" name="id" value="{esc(task['id'])}">
                <button class="mini primary">Run read-only</button>
            </form>
            """

        elif task["status"] == "needs_approval":
            controls = f"""
            <form method="POST" action="/run">
                <input type="hidden" name="id" value="{esc(task['id'])}">
                <input type="password" name="approval" placeholder="approval key">
                <button class="mini danger">Approve + run</button>
            </form>
            """

        blocks.append(f"""
        <article class="task">
            <div>
                <span class="item-id">{esc(task['id'])}</span>
                <span class="pill">{esc(task['status'])}</span>
                <span class="pill muted">{esc(task['kind'])}</span>
            </div>
            <p><b>Request:</b> {esc(task['user_words'])}</p>
            <code>{esc(task.get('command') or 'conversation')}</code>
            {controls}
            <pre>{esc(task.get('output', ''))}</pre>
        </article>
        """)

    return "".join(blocks)

def render_pending():
    m = memory()
    pending = m.get("pending_memories", [])

    if not pending:
        return "<p>No pending memories.</p>"

    blocks = []
    for mem in pending[:10]:
        blocks.append(f"""
        <article class="task pending">
            <div>
                <span class="item-id">{esc(mem['id'])}</span>
                <span class="pill">pending memory</span>
            </div>
            <p>{esc(mem['text'])}</p>
            <form method="POST" action="/approve_memory">
                <input type="hidden" name="id" value="{esc(mem['id'])}">
                <input type="password" name="approval" placeholder="approval key">
                <button class="mini primary">Approve memory</button>
            </form>
        </article>
        """)
    return "".join(blocks)

def logo_small():
    if LOGO_PNG.exists():
        return '<img src="/assets/company_logo.png" alt="Astraa Systems logo">'
    if LOGO_SVG.exists():
        return '<img src="/assets/company_logo.svg" alt="Astraa Systems logo">'
    return '<div class="logo-fallback">A</div>'

def logo_header():
    if HEADER_PNG.exists():
        return '<img class="hero-logo" src="/assets/company_logo_header.png" alt="Astraa Systems logo">'
    if HEADER_SVG.exists():
        return '<img class="hero-logo" src="/assets/company_logo_header.svg" alt="Astraa Systems logo">'
    return ""

def page():
    m = memory()
    active_count = len(m.get("memories", []))
    pending_count = len(m.get("pending_memories", []))
    mode = "REMOTE MODE" if REMOTE_MODE else "LOCAL MODE"

    css = """
    :root{
        --bg:#f5f7fb;--panel:#fff;--text:#07111f;--muted:#667085;
        --line:#d9e2f1;--blue:#1748d4;--navy:#071a44;
        --red:#ef4444;--shadow:0 24px 80px rgba(7,26,68,.14)
    }
    *{box-sizing:border-box}
    body{margin:0;background:var(--bg);color:var(--text);font-family:Inter,Segoe UI,Arial,sans-serif}
    .shell{max-width:1280px;margin:0 auto;padding:22px}
    .top{display:flex;justify-content:space-between;align-items:center;gap:18px;margin-bottom:18px}
    .brand{display:flex;align-items:center;gap:14px}
    .brand img,.logo-fallback{width:72px;height:72px;border-radius:18px;object-fit:cover;box-shadow:var(--shadow);background:#050505;color:white;display:grid;place-items:center;font-weight:900}
    .kicker{font-size:12px;letter-spacing:.2em;text-transform:uppercase;color:var(--muted)}
    h1{font-size:32px;margin:2px 0 0;letter-spacing:-.04em}
    .badge{border:1px solid var(--line);border-radius:999px;padding:10px 14px;background:#fff;color:var(--muted);box-shadow:var(--shadow)}
    .grid{display:grid;grid-template-columns:.9fr 1.1fr .85fr;gap:16px;align-items:start}
    .card{background:var(--panel);border:1px solid var(--line);border-radius:28px;box-shadow:var(--shadow);overflow:hidden}
    .hero{padding:22px}
    .hero-logo{width:100%;max-height:170px;object-fit:contain;background:#050505;border-radius:22px;padding:16px;margin-bottom:16px}
    .hero h2{font-size:34px;line-height:1;margin:8px 0 12px;letter-spacing:-.06em}
    .hero p{color:var(--muted);line-height:1.55}
    .metrics{display:grid;grid-template-columns:1fr;gap:10px;margin-top:16px}
    .metric{border:1px solid var(--line);border-radius:18px;padding:13px}
    .metric b{font-size:19px}
    .metric span{display:block;color:var(--muted);font-size:12px;margin-top:4px}
    .chat-card{display:flex;flex-direction:column;height:calc(100vh - 135px);min-height:620px}
    .chat-head{padding:18px 20px;border-bottom:1px solid var(--line)}
    .chat-body{flex:1;overflow:auto;padding:20px;background:linear-gradient(180deg,#ffffff,#f8fbff)}
    .chat-input{border-top:1px solid var(--line);padding:16px;background:#fff}
    .chat-input form{display:flex;gap:10px}
    .chat-input textarea{flex:1;height:58px;min-height:58px;max-height:140px;border:1px solid var(--line);border-radius:18px;padding:14px;outline:none;resize:vertical}
    .chat-input textarea:focus{border-color:var(--blue);box-shadow:0 0 0 4px rgba(23,72,212,.12)}
    .send{border:0;border-radius:18px;padding:0 22px;background:linear-gradient(135deg,var(--navy),var(--blue));color:#fff;font-weight:900;cursor:pointer}
    .msg-row{display:flex;margin:12px 0}
    .msg-row.user{justify-content:flex-end}
    .msg-row.arka{justify-content:flex-start}
    .bubble{max-width:78%;border-radius:22px;padding:13px 15px;line-height:1.45;white-space:pre-wrap}
    .user .bubble{background:linear-gradient(135deg,var(--navy),var(--blue));color:white;border-bottom-right-radius:6px}
    .arka .bubble{background:#eef4ff;color:#07111f;border:1px solid #d9e2f1;border-bottom-left-radius:6px}
    .msg-label{font-size:11px;text-transform:uppercase;letter-spacing:.14em;opacity:.7;margin-bottom:4px}
    .empty-chat{display:flex;gap:14px;align-items:flex-start;padding:18px;border:1px dashed var(--line);border-radius:22px;background:#fff}
    .arka-avatar{width:42px;height:42px;border-radius:14px;background:linear-gradient(135deg,var(--navy),var(--blue));color:white;display:grid;place-items:center;font-weight:900}
    .empty-chat p{margin:6px 0 0;color:var(--muted)}
    .empty-chat span{background:#eef4ff;border-radius:999px;padding:3px 8px}
    .panel{padding:18px}
    .side{display:grid;gap:16px}
    .task{border:1px solid var(--line);border-radius:20px;padding:14px;margin:10px 0;background:rgba(255,255,255,.72)}
    .item-id{font-weight:900;margin-right:8px}
    .pill{display:inline-flex;border:1px solid var(--line);border-radius:999px;padding:4px 8px;font-size:12px;margin-right:6px}
    .muted{color:var(--muted)}
    code{display:block;border-radius:14px;padding:10px;background:#f0f4ff;color:#13235c;overflow:auto}
    pre{white-space:pre-wrap;background:#0b1220;color:#dbeafe;border-radius:16px;padding:12px;overflow:auto}
    .mini{border:0;border-radius:12px;padding:9px 12px;margin-top:10px;margin-right:8px;cursor:pointer;font-weight:800}
    .mini.primary{background:var(--blue);color:white}
    .mini.danger{background:var(--red);color:white}
    input{border:1px solid var(--line);border-radius:12px;padding:10px;margin-top:10px}
    .cmd{border:1px solid var(--line);border-radius:16px;padding:12px;margin:9px 0}
    @media(max-width:1050px){
        .grid{grid-template-columns:1fr}
        .chat-card{height:auto;min-height:620px}
        .top{align-items:flex-start;flex-direction:column}
    }
    """

    return f"""
    <!doctype html>
    <html>
    <head>
        <meta charset="utf-8">
        <meta name="viewport" content="width=device-width, initial-scale=1">
        <title>Arka Personal AI - Portal Prime Conversation</title>
        <style>{css}</style>
    </head>
    <body>
        <div class="shell">
            <header class="top">
                <div class="brand">
                    {logo_small()}
                    <div>
                        <div class="kicker">Arka Personal AI / Portal Prime HQ</div>
                        <h1>Founder Command Companion</h1>
                    </div>
                </div>
                <div class="badge">Conversation Mode Active</div>
            </header>

            <main class="grid">
                <section class="card hero">
                    {logo_header()}
                    <div class="kicker">{mode}</div>
                    <h2>Hey Keshanth - I am Arka.</h2>
                    <p>I am your personal AI foundation. Conversation stays in the center. Actions, approvals, and memories stay separate so I do not confuse talking with doing.</p>
                    <div class="metrics">
                        <div class="metric"><b>{active_count}</b><span>active memories</span></div>
                        <div class="metric"><b>{pending_count}</b><span>pending memories</span></div>
                        <div class="metric"><b>{mode}</b><span>network mode</span></div>
                    </div>
                </section>

                <section class="card chat-card">
                    <div class="chat-head">
                        <div class="kicker">Conversation with Arka</div>
                        <b>Talk naturally. I will separate conversation from actions.</b>
                    </div>
                    <div class="chat-body" id="chatBody">
                        {render_chat()}
                    </div>
                    <div class="chat-input">
                        <form id="chatForm">
                            <textarea id="words" name="words" placeholder="Talk to me naturally. Example: hey arka, this does not feel like a conversation yet"></textarea>
                            <button class="send" type="submit">Send</button>
                        </form>
                    </div>
                </section>

                <aside class="side">
                    <section class="card panel">
                        <div class="kicker">Pending memories</div>
                        <div id="pending">{render_pending()}</div>
                    </section>

                    <section class="card panel">
                        <div class="kicker">Action Queue</div>
                        <div id="tasks">{render_tasks()}</div>
                    </section>

                    <section class="card panel">
                        <div class="kicker">Evolution model</div>
                        <div class="cmd">Conversation: center thread</div>
                        <div class="cmd">Memory: draft then approve</div>
                        <div class="cmd">Actions: separate queue</div>
                        <div class="cmd">Remote: use Windows 11 Pro Remote Desktop first</div>
                    </section>
                </aside>
            </main>
        </div>

        <script>
        async function refreshPanels(){{
            const r = await fetch('/api/state');
            const data = await r.json();
            document.getElementById('chatBody').innerHTML = data.chat;
            document.getElementById('pending').innerHTML = data.pending;
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

            await refreshPanels();
        }});

        refreshPanels();
        </script>
    </body>
    </html>
    """

class Handler(BaseHTTPRequestHandler):
    def do_GET(self):
        clean = self.path.lstrip("/")

        file_map = {
            "assets/company_logo.png": LOGO_PNG,
            "assets/company_logo_header.png": HEADER_PNG,
            "assets/company_logo.svg": LOGO_SVG,
            "assets/company_logo_header.svg": HEADER_SVG,
        }

        if clean in file_map and file_map[clean].exists():
            path = file_map[clean]
            content_type = "image/png" if path.suffix.lower() == ".png" else "image/svg+xml"
            self.send_response(200)
            self.send_header("Content-Type", content_type)
            self.end_headers()
            self.wfile.write(path.read_bytes())
            return

        if self.path == "/api/state":
            payload = {
                "chat": render_chat(),
                "pending": render_pending(),
                "tasks": render_tasks()
            }
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

        if self.path == "/api/chat" or self.path == "/chat":
            handle_chat(data.get("words", [""])[0])

            if self.path == "/api/chat":
                self.send_response(200)
                self.send_header("Content-Type", "application/json; charset=utf-8")
                self.end_headers()
                self.wfile.write(json.dumps({"ok": True}).encode("utf-8"))
                return

        elif self.path == "/approve_memory":
            result = approve_memory(data.get("id", [""])[0], data.get("approval", [""])[0])
            add_chat("user", "approve memory")
            add_chat("arka", result)

        elif self.path == "/run":
            s = state()
            item_id = data.get("id", [""])[0]
            approval = data.get("approval", [""])[0]

            for task in s.get("tasks", []):
                if task["id"] == item_id:
                    if task["kind"] == "LOCAL_EXEC":
                        expected = os.environ.get(APPROVAL_ENV, "")

                        if not expected:
                            task["status"] = "blocked"
                            task["output"] = "Approval key is not set."
                        elif approval != expected:
                            task["status"] = "blocked"
                            task["output"] = "Approval key did not match."
                        else:
                            task["status"] = "ran"
                            task["output"] = run_command(task.get("command", ""))
                    else:
                        task["status"] = "ran"
                        task["output"] = run_command(task.get("command", ""))

                    save_state(s)
                    break

        self.send_response(303)
        self.send_header("Location", "/")
        self.end_headers()

if __name__ == "__main__":
    print(APP_NAME, "Portal Prime conversation mode starting")
    print("HQ_ROOT:", HQ_ROOT)
    print("Mode:", "REMOTE" if REMOTE_MODE else "LOCAL")
    print("URL:", f"http://{HOST}:{PORT}")
    HTTPServer((HOST, PORT), Handler).serve_forever()
