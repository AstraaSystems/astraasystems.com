from pathlib import Path
import json
import re
import time
import sqlite3
import py_compile

root = Path(".").resolve()
app = root / "arka_v1.py"
memory_path = root / "arka_memory.json"
db_path = Path(r"D:\ARKA_HQ\data\arka_core.db")

if not app.exists():
    raise FileNotFoundError("arka_v1.py not found. Run this inside D:\\ARKA_HQ\\repos\\ardhanarishvara_git\\arka_v1")

# ------------------------------------------------------------
# 1) Seed active memory immediately
# ------------------------------------------------------------
def load_json(path, default):
    if path.exists():
        try:
            return json.loads(path.read_text(encoding="utf-8-sig"))
        except Exception:
            return default
    return default

def save_json(path, data):
    path.write_text(json.dumps(data, indent=2), encoding="utf-8")

memory = load_json(memory_path, {
    "schema": "arka_memory_v1",
    "owner": "Keshanth Sivayogampillai",
    "memories": [],
    "audit": []
})

memory.setdefault("memories", [])
memory.setdefault("audit", [])

facts = [
    "my wife's name is Thrilochana",
    "my first-born son's name is Bhirav Aditya",
    "my first born son's name is Bhirav Aditya",
    "my son's name is Bhirav Aditya"
]

existing = {m.get("text", "").lower().strip() for m in memory["memories"]}

for fact in facts:
    if fact.lower() not in existing:
        entry = {
            "id": str(int(time.time() * 1000))[-8:],
            "type": "family_memory",
            "text": fact,
            "source": "explicit_user_command_hotfix",
            "status": "active",
            "created_at": time.time()
        }
        memory["memories"].insert(0, entry)
        memory["audit"].insert(0, {
            "event": "memory_seeded_family_hotfix",
            "text": fact,
            "created_at": time.time()
        })

save_json(memory_path, memory)

# ------------------------------------------------------------
# 2) Seed SQLite lifecycle_store too
# ------------------------------------------------------------
db_path.parent.mkdir(parents=True, exist_ok=True)
conn = sqlite3.connect(str(db_path))
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

for fact in facts:
    cur.execute(
        "INSERT INTO lifecycle_store (timestamp, type, content, status, source) VALUES (?, ?, ?, ?, ?)",
        (time.strftime("%Y-%m-%dT%H:%M:%S"), "memory", fact, "active", "explicit_user_command_hotfix")
    )
    cur.execute(
        "INSERT INTO arka_logs (timestamp, event_type, content) VALUES (?, ?, ?)",
        (time.strftime("%Y-%m-%dT%H:%M:%S"), "memory_seeded_family_hotfix", fact)
    )

conn.commit()
conn.close()

print("[OK] Seeded active family memory:")
for f in facts:
    print(" -", f)

# ------------------------------------------------------------
# 3) Patch Arka parser/recall logic
# ------------------------------------------------------------
code = app.read_text(encoding="utf-8-sig")

helpers = r'''
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
                    return m.group(1).strip(" .,'")

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
                    return m.group(1).strip(" .,'")

    return ""
'''

if "def extract_family_facts(raw):" not in code:
    code = code.replace("def arka_reply(raw):", helpers + "\n\ndef arka_reply(raw):", 1)

router = r'''
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
'''

if "Natural multi-fact family memory save." not in code:
    targets = ["    w = raw.lower()", "    w=raw.lower()"]
    patched = False
    for target in targets:
        if target in code:
            code = code.replace(target, target + "\n" + router, 1)
            patched = True
            break
    if not patched:
        raise RuntimeError("Could not find w = raw.lower() inside arka_reply.")

app.write_text(code, encoding="utf-8")
py_compile.compile(str(app), doraise=True)

print("[OK] Family memory parser and recall patched.")
print("[OK] Test: what is my wife's name?")
print("[OK] Test: what is my son's name?")
