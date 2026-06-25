from pathlib import Path
import re
import json
import py_compile

app = Path("arka_v1.py")
if not app.exists():
    raise FileNotFoundError("arka_v1.py not found. Run inside D:\\ARKA_HQ\\repos\\ardhanarishvara_git\\arka_v1")

code = app.read_text(encoding="utf-8-sig")

helpers = r'''
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
'''

if "def save_universal_context(raw):" not in code:
    code = code.replace("def arka_reply(raw):", helpers + "\n\ndef arka_reply(raw):", 1)

router = r'''
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
'''

if "Universal Processing Brain: structured context first." not in code:
    targets = ["    w = raw.lower()", "    w=raw.lower()"]
    patched = False

    for target in targets:
        if target in code:
            code = code.replace(target, target + "\n" + router, 1)
            patched = True
            break

    if not patched:
        raise RuntimeError("Could not find w = raw.lower() inside arka_reply.")

# Replace generic dead fallback if present.
fallbacks = [
    'return "I’m with you. Tell me if you want me to record it, research it, check Astraa, or turn it into an action."',
    'return "I’m with you. Tell me if you want me to record it, research it, check Astraa, or turn it into an action."',
    'return "Yeah, I got you. Tell me what you want me to do next."'
]

new_fallback = '''
    return universal_brain_response(raw)
'''

for old in fallbacks:
    if old in code:
        code = code.replace(old, new_fallback, 1)

app.write_text(code, encoding="utf-8")
py_compile.compile(str(app), doraise=True)

print("[OK] Arka Universal Processing Brain installed.")
print("[OK] Test: structured context block")
print("[OK] Test: show context brain")
print("[OK] Test: build a plan for something new")
