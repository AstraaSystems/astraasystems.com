#!/usr/bin/env python3
from __future__ import annotations

import json
import os
import subprocess
import time
import uuid
from dataclasses import dataclass, asdict
from http.server import BaseHTTPRequestHandler, HTTPServer
from pathlib import Path
from urllib.parse import parse_qs

APP_NAME = "Arka Personal AI"
ROOT = Path(__file__).parent

POLICY = json.loads((ROOT / "arka_policy.json").read_text(encoding="utf-8-sig"))
IDENTITY = json.loads((ROOT / POLICY.get("identity_file", "arka_identity.json")).read_text(encoding="utf-8-sig"))

MEMORY_FILE = ROOT / POLICY.get("memory_file", "arka_memory.json")
STATE_FILE = ROOT / "arka_runtime_state.json"

HQ_ROOT = Path(os.environ.get("ARKA_HQ_ROOT", r"D:\ARKA_HQ\repos\ardhanarishvara_git")).resolve()
APPROVAL_ENV = POLICY.get("approval_env_var", "ARKA_APPROVAL_KEY")

REMOTE_MODE = os.environ.get(POLICY.get("remote_mode_env_var", "ARKA_REMOTE_MODE"), "0") == "1"
HOST = "0.0.0.0" if REMOTE_MODE else POLICY.get("default_bind_host", "127.0.0.1")
PORT = int(os.environ.get("ARKA_HQ_PORT", POLICY.get("default_port", 8787)))

ALLOWLIST = set(POLICY.get("allowlisted_commands", []))

PNG_LOGO = ROOT / "assets" / "company_logo.png"
PNG_HEADER = ROOT / "assets" / "company_logo_header.png"
SVG_LOGO = ROOT / "assets" / "company_logo.svg"
SVG_HEADER = ROOT / "assets" / "company_logo_header.svg"

if PNG_LOGO.exists():
    LOGO_URL = "/assets/company_logo.png"
else:
    LOGO_URL = "/assets/company_logo.svg"

if PNG_HEADER.exists():
    HEADER_LOGO_URL = "/assets/company_logo_header.png"
else:
    HEADER_LOGO_URL = "/assets/company_logo_header.svg"


@dataclass
class Item:
    id: str
    created_at: float
    user_words: str
    kind: str
    status: str
    output: str
    command: str = ""


def load_json(path: Path, default):
    if path.exists():
        return json.loads(path.read_text(encoding="utf-8-sig"))
    return default


def save_json(path: Path, data):
    path.write_text(json.dumps(data, indent=2), encoding="utf-8")


def state():
    return load_json(STATE_FILE, {"items": []})


def memory():
    return load_json(MEMORY_FILE, {"memories": [], "pending_memories": [], "audit": []})


def esc(s):
    return (s or "").replace("&", "&amp;").replace("<", "&lt;").replace(">", "&gt;")


def add_item(words, kind, status, output, command=""):
    s = state()
    item = Item(
        id=str(uuid.uuid4())[:8],
        created_at=time.time(),
        user_words=words,
        kind=kind,
        status=status,
        output=output,
        command=command
    )
    s.setdefault("items", []).insert(0, asdict(item))
    save_json(STATE_FILE, s)
    return item


def draft_memory(text):
    m = memory()
    entry = {
        "id": str(uuid.uuid4())[:8],
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
    save_json(MEMORY_FILE, m)
    return entry


def approve_memory(mem_id, approval):
    expected = os.environ.get(APPROVAL_ENV, "")

    if not expected:
        return "BLOCKED: approval key is not set in this shell."

    if approval != expected:
        return "BLOCKED: approval key did not match."

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
            save_json(MEMORY_FILE, m)
            return "Memory approved and saved into Arka's active memory."

    return "Memory draft not found."


def run_command(cmd):
    if cmd not in ALLOWLIST:
        return "BLOCKED: command is not allowlisted: " + cmd

    if not HQ_ROOT.exists():
        return "BLOCKED: ARKA_HQ_ROOT does not exist: " + str(HQ_ROOT)

    try:
        p = subprocess.run(
            cmd,
            cwd=str(HQ_ROOT),
            shell=True,
            text=True,
            capture_output=True,
            timeout=60
        )
        return (p.stdout + p.stderr).strip() or "OK: command completed with no output."
    except Exception as e:
        return "ERROR: " + str(e)


def map_request(words):
    w = words.strip().lower()

    if not w:
        return add_item(words, "chat", "chat", "Say anything you want me to help with.")

    if w.startswith("remember that ") or w.startswith("remember ") or w.startswith("save preference"):
        text = words.split(" ", 1)[1] if " " in words else words
        mem = draft_memory(text)
        return add_item(
            words,
            "memory",
            "pending_approval",
            "I drafted this as a memory. Approve it if you want it to become part of my active memory. Memory ID: " + mem["id"]
        )

    if "what have you learned" in w or "show memory" in w or "memories" in w:
        m = memory()
        return add_item(
            words,
            "chat",
            "chat",
            f"I currently have {len(m.get('memories', []))} active memories and {len(m.get('pending_memories', []))} pending memory drafts."
        )

    if "who are you" in w or "personality" in w:
        return add_item(
            words,
            "chat",
            "chat",
            "Hey Keshanth - I am Arka. I am your personal AI and internal CEO support layer: friendly, easy-going, calm, direct, protective, and founder-aligned. I evolve through approved memories and skills, not silent self-modification."
        )

    if "evolve" in w or "evolution" in w:
        return add_item(
            words,
            "chat",
            "chat",
            "My evolution path is: personality, explicit memory, approved skills, and audited actions. I can learn preferences when you explicitly ask me to remember them, and I can propose new skills for your approval."
        )

    if any(x in w for x in ["flight", "book ticket", "book flight", "travel"]):
        return add_item(
            words,
            "chat",
            "chat",
            "I can collect travel preferences and prepare flight options once a travel research connector is added. In this build, I will not purchase tickets or submit payment automatically. Final booking stays behind your approval."
        )

    if any(x in w for x in ["website", "web", "connect to site"]):
        return add_item(
            words,
            "chat",
            "chat",
            "Website access should be added as a read-only connector first: allowlisted domains, source capture, and approval before form submissions or account actions."
        )

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
            status = "ready" if kind == "READ_ONLY" else "needs_approval"
            msg = "Ready." if status == "ready" else "Execution requires approval."
            return add_item(words, kind, status, msg, cmd)

    return add_item(
        words,
        "chat",
        "chat",
        "Got it. I can talk it through, draft a plan, or queue a safe task. If this becomes an action, I will ask for approval."
    )


def render_items():
    s = state()
    m = memory()

    blocks = []
    for item in s.get("items", [])[:30]:
        controls = ""

        if item["status"] == "ready":
            controls = f"""
            <form method="POST" action="/run">
                <input type="hidden" name="id" value="{esc(item['id'])}">
                <button class="mini primary">Run read-only</button>
            </form>
            """

        elif item["status"] == "needs_approval":
            controls = f"""
            <form method="POST" action="/run">
                <input type="hidden" name="id" value="{esc(item['id'])}">
                <input type="password" name="approval" placeholder="approval key">
                <button class="mini danger">Approve + run</button>
            </form>
            """

        blocks.append(f"""
        <article class="item">
            <div>
                <span class="item-id">{esc(item['id'])}</span>
                <span class="pill">{esc(item['status'])}</span>
                <span class="pill muted">{esc(item['kind'])}</span>
            </div>
            <p><b>You:</b> {esc(item['user_words'])}</p>
            <code>{esc(item.get('command') or 'conversation')}</code>
            {controls}
            <pre><b>Arka:</b> {esc(item['output'])}</pre>
        </article>
        """)

    pending = []
    for mem in m.get("pending_memories", [])[:10]:
        pending.append(f"""
        <article class="item pending">
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

    return (
        "".join(blocks) or "<p>No conversation yet. Talk to Arka.</p>",
        "".join(pending) or "<p>No pending memories.</p>",
        len(m.get("memories", [])),
        len(m.get("pending_memories", []))
    )


def page():
    items_html, pending_html, active_count, pending_count = render_items()
    mode = "REMOTE MODE" if REMOTE_MODE else "LOCAL MODE"

    css = """
    :root{
        --bg:#f5f7fb;--panel:#fff;--text:#07111f;--muted:#667085;
        --line:#d9e2f1;--blue:#1748d4;--navy:#071a44;
        --green:#47ff9a;--red:#ef4444;--shadow:0 24px 80px rgba(7,26,68,.14)
    }
    *{box-sizing:border-box}
    body{margin:0;background:var(--bg);color:var(--text);font-family:Inter,Segoe UI,Arial,sans-serif}
    .shell{max-width:1240px;margin:0 auto;padding:26px}
    .top{display:flex;justify-content:space-between;align-items:center;gap:18px;margin-bottom:22px}
    .brand{display:flex;align-items:center;gap:14px}
    .brand img{width:72px;height:72px;border-radius:18px;object-fit:cover;box-shadow:var(--shadow)}
    .kicker{font-size:12px;letter-spacing:.2em;text-transform:uppercase;color:var(--muted)}
    h1{font-size:34px;margin:2px 0 0;letter-spacing:-.04em}
    .toggle{border:1px solid var(--line);background:var(--panel);border-radius:999px;padding:6px;display:flex;gap:6px;box-shadow:var(--shadow)}
    .toggle button{border:0;border-radius:999px;padding:10px 14px;background:transparent;color:var(--muted);cursor:pointer}
    .toggle button.active{background:var(--navy);color:#fff}
    .grid{display:grid;grid-template-columns:1.15fr .85fr;gap:20px}
    .card{background:var(--panel);border:1px solid var(--line);border-radius:30px;box-shadow:var(--shadow);overflow:hidden}
    .hero{padding:28px}
    .hero-logo{width:100%;max-height:230px;object-fit:contain;background:#050505;border-radius:24px;padding:18px;margin-bottom:20px}
    .hero h2{font-size:44px;line-height:1;margin:8px 0 12px;letter-spacing:-.06em}
    .hero p{color:var(--muted);line-height:1.6}
    .metrics{display:grid;grid-template-columns:repeat(3,1fr);gap:12px;margin-top:20px}
    .metric{border:1px solid var(--line);border-radius:20px;padding:15px}
    .metric b{font-size:21px}
    .metric span{display:block;color:var(--muted);font-size:12px;margin-top:4px}
    .composer,.panel,.queue{padding:20px}
    textarea{width:100%;height:145px;border:1px solid var(--line);border-radius:22px;padding:17px;outline:none;resize:vertical;background:#fff;color:var(--text)}
    .send{margin-top:12px;width:100%;border:0;border-radius:18px;padding:15px;background:linear-gradient(135deg,var(--navy),var(--blue));color:#fff;font-weight:900;cursor:pointer}
    .item{border:1px solid var(--line);border-radius:22px;padding:15px;margin:12px 0;background:rgba(255,255,255,.72)}
    .item-id{font-weight:900;margin-right:8px}
    .pill{display:inline-flex;border:1px solid var(--line);border-radius:999px;padding:4px 8px;font-size:12px;margin-right:6px}
    .muted{color:var(--muted)}
    code{display:block;border-radius:14px;padding:10px;background:#f0f4ff;color:#13235c;overflow:auto}
    pre{white-space:pre-wrap;background:#0b1220;color:#dbeafe;border-radius:16px;padding:12px;overflow:auto}
    .mini{border:0;border-radius:12px;padding:9px 12px;margin-top:10px;margin-right:8px;cursor:pointer;font-weight:800}
    .mini.primary{background:var(--blue);color:white}
    .mini.danger{background:var(--red);color:white}
    input{border:1px solid var(--line);border-radius:12px;padding:10px;margin-top:10px}
    .side{display:grid;gap:20px}
    .cmd{border:1px solid var(--line);border-radius:16px;padding:12px;margin:9px 0}

    body.linux{
        --bg:#020403;--panel:#07100b;--text:#d8ffe8;--muted:#73a987;
        --line:#124b2b;--blue:#00d5ff;--navy:#06140d;
        --shadow:0 20px 80px rgba(0,255,128,.08);
        background:radial-gradient(circle at top left,rgba(0,255,128,.13),transparent 28%),#020403;
        font-family:Consolas,Cascadia Code,monospace
    }
    body.linux .card,body.linux .item,body.linux .metric,body.linux .cmd{background:rgba(3,18,10,.84);border-color:#17663b}
    body.linux textarea,body.linux input{background:#030906;color:var(--text);border-color:#17663b}
    body.linux code{background:#020806;color:#47ff9a;border:1px solid #17663b}
    body.linux pre{background:#000;color:#83ffb5;border:1px solid #17663b}
    body.linux .send,body.linux .toggle button.active{background:linear-gradient(135deg,#0d3b22,#00a86b);color:#eafff2}

    @media(max-width:940px){
        .grid{grid-template-columns:1fr}
        .top{align-items:flex-start;flex-direction:column}
        .metrics{grid-template-columns:1fr}
        .shell{padding:15px}
        .hero h2{font-size:34px}
    }
    """

    return f"""
    <!doctype html>
    <html>
    <head>
        <meta charset="utf-8">
        <meta name="viewport" content="width=device-width, initial-scale=1">
        <title>Arka Personal AI</title>
        <style>{css}</style>
    </head>
    <body class="portal">
        <div class="shell">
            <header class="top">
                <div class="brand">
                    {LOGO_URL}
                    <div>
                        <div class="kicker">Arka Personal AI / Evolution v0.4</div>
                        <h1>Founder Command Companion</h1>
                    </div>
                </div>
                <div class="toggle">
                    <button id="portalBtn" onclick="setTheme('portal')">Portal Prime</button>
                    <button id="linuxBtn" onclick="setTheme('linux')">Linux HQ</button>
                </div>
            </header>

            <main class="grid">
                <section class="card hero">
                    {HEADER_LOGO_URL}
                    <div class="kicker">{mode}</div>
                    <h2>Hey Keshanth - I am Arka.</h2>
                    <p>I am your personal AI foundation: friendly, easy-going, calm, direct, protective, and founder-aligned. I evolve through approved memories, reviewed preferences, and future skill modules.</p>
                    <div class="metrics">
                        <div class="metric"><b>{active_count}</b><span>active memories</span></div>
                        <div class="metric"><b>{pending_count}</b><span>pending memories</span></div>
                        <div class="metric"><b>{mode}</b><span>network mode</span></div>
                    </div>
                </section>

                <section class="card composer">
                    <form method="POST" action="/ask">
                        <div class="kicker">Talk to Arka</div>
                        <textarea name="words" placeholder="Example: Arka, who are you? / remember that I prefer morning focus blocks / what have you learned? / check repo status"></textarea>
                        <button class="send">Send to Arka</button>
                    </form>
                </section>

                <section class="card queue">
                    <h3>Conversation + Mission Queue</h3>
                    {items_html}
                </section>

                <aside class="side">
                    <section class="card panel">
                        <div class="kicker">Pending memories</div>
                        {pending_html}
                    </section>
                    <section class="card panel">
                        <div class="kicker">Evolution model</div>
                        <div class="cmd">Memory: explicit and approved</div>
                        <div class="cmd">Skills: future modules reviewed before use</div>
                        <div class="cmd">Actions: audited and approval-gated</div>
                        <div class="cmd">Payments/bookings: not automatic in this build</div>
                    </section>
                </aside>
            </main>
        </div>

        <script>
        function setTheme(t){{
            document.body.className=t;
            localStorage.setItem('arkaTheme',t);
            document.getElementById('portalBtn').classList.toggle('active',t==='portal');
            document.getElementById('linuxBtn').classList.toggle('active',t==='linux');
        }}
        setTheme(localStorage.getItem('arkaTheme')||'portal');
        </script>
    </body>
    </html>
    """


class Handler(BaseHTTPRequestHandler):
    def do_GET(self):
        clean = self.path.lstrip("/")

        file_map = {
            "assets/company_logo.png": PNG_LOGO,
            "assets/company_logo_header.png": PNG_HEADER,
            "assets/company_logo.svg": SVG_LOGO,
            "assets/company_logo_header.svg": SVG_HEADER,
        }

        if clean in file_map and file_map[clean].exists():
            path = file_map[clean]
            content_type = "image/png" if path.suffix.lower() == ".png" else "image/svg+xml"
            self.send_response(200)
            self.send_header("Content-Type", content_type)
            self.end_headers()
            self.wfile.write(path.read_bytes())
            return

        html = page()
        self.send_response(200)
        self.send_header("Content-Type", "text/html; charset=utf-8")
        self.end_headers()
        self.wfile.write(html.encode("utf-8"))

    def do_POST(self):
        data = parse_qs(self.rfile.read(int(self.headers.get("Content-Length", 0))).decode("utf-8"))

        if self.path == "/ask":
            map_request(data.get("words", [""])[0])

        elif self.path == "/approve_memory":
            result = approve_memory(data.get("id", [""])[0], data.get("approval", [""])[0])
            add_item("approve memory", "memory", "chat", result)

        elif self.path == "/run":
            s = state()
            item_id = data.get("id", [""])[0]
            approval = data.get("approval", [""])[0]

            for item in s.get("items", []):
                if item["id"] == item_id:
                    if item["kind"] == "LOCAL_EXEC":
                        expected = os.environ.get(APPROVAL_ENV, "")

                        if not expected:
                            item["status"] = "blocked"
                            item["output"] = "BLOCKED: approval key is not set."
                        elif approval != expected:
                            item["status"] = "blocked"
                            item["output"] = "BLOCKED: approval key did not match."
                        else:
                            item["status"] = "ran"
                            item["output"] = run_command(item.get("command", ""))
                    else:
                        item["status"] = "ran"
                        item["output"] = run_command(item.get("command", ""))

                    save_json(STATE_FILE, s)
                    break

        self.send_response(303)
        self.send_header("Location", "/")
        self.end_headers()


if __name__ == "__main__":
    print(APP_NAME, "v0.4 starting")
    print("HQ_ROOT:", HQ_ROOT)
    print("Mode:", "REMOTE" if REMOTE_MODE else "LOCAL")
    print("URL:", f"http://{HOST}:{PORT}")
    HTTPServer((HOST, PORT), Handler).serve_forever()
