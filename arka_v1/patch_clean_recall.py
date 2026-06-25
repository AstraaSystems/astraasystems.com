from pathlib import Path
import re
import py_compile

app = Path("arka_v1.py")
if not app.exists():
    raise FileNotFoundError("arka_v1.py not found.")

code = app.read_text(encoding="utf-8-sig")

helpers = r'''
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
'''

if "def clean_extracted_name(name):" not in code:
    code = code.replace("def arka_reply(raw):", helpers + "\n\ndef arka_reply(raw):", 1)

# Patch recall_name_from_memory if present.
code = code.replace(
    'return m.group(1).strip(" .,\')"',
    'return clean_extracted_name(m.group(1))'
)

code = code.replace(
    'return m.group(1).strip(" .,\'")',
    'return clean_extracted_name(m.group(1))'
)

code = code.replace(
    'return m.group(1).strip(" .")',
    'return clean_extracted_name(m.group(1))'
)

# Add clean recall router early inside arka_reply.
router = r'''
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
'''

if "Clean topic recall, active memory first, no journal dumps." not in code:
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

print("[OK] Clean recall patch applied.")
print("[OK] Test: what is my son's name?")
print("[OK] Test: what do you remember about astraasystems.com?")
