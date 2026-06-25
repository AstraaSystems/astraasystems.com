from pathlib import Path
import re
import py_compile

app = Path("arka_v1.py")

if not app.exists():
    raise FileNotFoundError("arka_v1.py not found. Run this inside D:\\ARKA_HQ\\repos\\ardhanarishvara_git\\arka_v1")

code = app.read_text(encoding="utf-8-sig")

# ------------------------------------------------------------
# 1) Make sure DB init creates conversation journal table
# ------------------------------------------------------------
if "CREATE TABLE IF NOT EXISTS arka_conversation_journal" not in code:
    anchor = '''    cur.execute("""
        CREATE TABLE IF NOT EXISTS arka_business_events (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            timestamp TEXT,
            area TEXT,
            event_type TEXT,
            content TEXT,
            status TEXT
        )
    """)
'''
    insert = anchor + '''
    cur.execute("""
        CREATE TABLE IF NOT EXISTS arka_conversation_journal (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            timestamp TEXT,
            role TEXT,
            content TEXT
        )
    """)
'''
    if anchor in code:
        code = code.replace(anchor, insert, 1)
    else:
        print("[WARN] Could not find DB anchor. Journal table will be created inside record_journal().")

# ------------------------------------------------------------
# 2) Add journal + recall helpers before handle_chat()
# ------------------------------------------------------------
helpers = r'''
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
    if not term:
        return []

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
        cur.execute(
            "SELECT timestamp, role, content FROM arka_conversation_journal WHERE content LIKE ? ORDER BY id DESC LIMIT ?",
            (f"%{term}%", limit)
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
'''

if "def record_journal(role, content):" not in code:
    code = code.replace("def handle_chat(raw):", helpers + "\n\ndef handle_chat(raw):", 1)

# ------------------------------------------------------------
# 3) Replace handle_chat so every turn is journaled
# ------------------------------------------------------------
handle_pattern = r'''def handle_chat\(raw\):
    add_chat\("user", raw\)
    reply = arka_reply\(raw\)
    add_chat\("arka", reply\)
    return reply
'''

handle_new = '''def handle_chat(raw):
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
'''

code, count = re.subn(handle_pattern, handle_new, code)

if count != 1:
    print("[WARN] Could not replace handle_chat using exact pattern. Trying looser replacement.")
    loose = r"def handle_chat\(raw\):.*?return reply"
    code, count2 = re.subn(loose, handle_new.strip(), code, count=1, flags=re.S)
    if count2 != 1:
        print("[WARN] handle_chat was not replaced. Check file manually if journal does not work.")

# ------------------------------------------------------------
# 4) Expand save/record command patterns
# ------------------------------------------------------------
extra_patterns = [
    r'        r"^arka[, ]+remember this[: ]+(.*)$",',
    r'        r"^arka[, ]+remember[: ]+(.*)$",',
    r'        r"^record[: ]+(.*)$",',
    r'        r"^save[: ]+(.*)$",',
    r'        r"^memory[: ]+(.*)$",',
    r'        r"^add to memory[: ]+(.*)$",',
    r'        r"^put in memory[: ]+(.*)$",'
]

if 'r"^arka[, ]+remember this[: ]+(.*)$"' not in code:
    code = code.replace("    patterns = [", "    patterns = [\n" + "\n".join(extra_patterns), 1)

# ------------------------------------------------------------
# 5) Add journal recall routing inside arka_reply after w = raw.lower()
# ------------------------------------------------------------
journal_router = r'''
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

'''

if "Persistent conversation journal recall." not in code:
    targets = ["    w = raw.lower()", "    w=raw.lower()"]
    patched = False
    for target in targets:
        if target in code:
            code = code.replace(target, target + "\n" + journal_router, 1)
            patched = True
            break
    if not patched:
        print("[WARN] Could not find arka_reply lower-case line to inject journal router.")

# ------------------------------------------------------------
# 6) Fix logo functions returning text paths instead of img tags
# ------------------------------------------------------------
logo_block_pattern = r'''def logo_small\(\):
    .*?def logo_header\(\):
    .*?return ""
'''

logo_block_new = r'''def logo_small():
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
'''

code, logo_count = re.subn(logo_block_pattern, logo_block_new, code, count=1, flags=re.S)

if logo_count != 1:
    print("[WARN] Logo functions were not replaced. If logo still shows as text, check logo_small/logo_header manually.")

# ------------------------------------------------------------
# 7) Fix action queue form rendering
# ------------------------------------------------------------
code = code.replace(
    '            /run\n              <input',
    '            <form method="POST" action="/run">\n              <input'
)
code = code.replace(
    '            /run\r\n              <input',
    '            <form method="POST" action="/run">\r\n              <input'
)

# ------------------------------------------------------------
# 8) Add quick journal command: show journal
# ------------------------------------------------------------
show_journal_router = r'''
    if w.startswith("show journal") or w.startswith("show conversation journal"):
        rows = search_journal("", limit=20)
        if not rows:
            return "The conversation journal is empty."
        lines = ["Recent conversation journal:"]
        for ts, role, content in rows:
            lines.append(f"- {ts} | {role}: {content}")
        return "\\n".join(lines)
'''

# Instead of empty search issue, define search_journal all rows if empty
code = code.replace(
'''def search_journal(term, limit=12):
    """
    Search previous conversation turns.
    """
    term = (term or "").strip()
    if not term:
        return []
''',
'''def search_journal(term, limit=12):
    """
    Search previous conversation turns.
    """
    term = (term or "").strip()
'''
)

code = code.replace(
'''        cur.execute(
            "SELECT timestamp, role, content FROM arka_conversation_journal WHERE content LIKE ? ORDER BY id DESC LIMIT ?",
            (f"%{term}%", limit)
        )
''',
'''        if term:
            cur.execute(
                "SELECT timestamp, role, content FROM arka_conversation_journal WHERE content LIKE ? ORDER BY id DESC LIMIT ?",
                (f"%{term}%", limit)
            )
        else:
            cur.execute(
                "SELECT timestamp, role, content FROM arka_conversation_journal ORDER BY id DESC LIMIT ?",
                (limit,)
            )
'''
)

if "Recent conversation journal:" not in code:
    for target in ["    if w in [\"hi\", \"hey\", \"hello\", \"hi arka\", \"hey arka\", \"hello arka\"]:", "    if w in ['hi', 'hey', 'hello', 'hi arka', 'hey arka', 'hello arka']:"]:
        if target in code:
            code = code.replace(target, show_journal_router + "\n" + target, 1)
            break

# ------------------------------------------------------------
# 9) Save, compile
# ------------------------------------------------------------
app.write_text(code, encoding="utf-8")
py_compile.compile(str(app), doraise=True)

print("[OK] Arka V1 recording reliability repair applied.")
print("[OK] Every chat turn now records to arka_conversation_journal.")
print("[OK] Explicit record/save/remember still saves active memory.")
print("[OK] Use: what did I say about website")
print("[OK] Use: what do you remember about website")
print("[OK] Use: show journal")
