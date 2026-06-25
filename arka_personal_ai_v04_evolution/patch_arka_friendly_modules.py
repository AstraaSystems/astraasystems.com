from pathlib import Path
import re
import py_compile

app = Path("arka_personal_ai_v04.py")
if not app.exists():
    raise FileNotFoundError("arka_personal_ai_v04.py not found. Run this inside arka_personal_ai_v04_evolution.")

code = app.read_text(encoding="utf-8-sig")

new_block = r'''
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

    return "\\n".join(lines)


def arka_brain(user_text):
    raw = user_text.strip()
    w = raw.lower()

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

        return "\\n".join(lines)

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
                "For safety, I won't execute or rewrite anything by myself yet.\\n\\n"
                "What I can do now:\\n"
                "1. discover available local modules,\\n"
                "2. explain what they appear to be for,\\n"
                "3. suggest which ones should become approved Arka skills,\\n"
                "4. prepare a patch for your approval.\\n\\n"
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
'''

pattern = r"def arka_brain\(user_text\):.*?\ndef handle_chat\(user_text\):"
new_code, count = re.subn(pattern, new_block, code, flags=re.S)

if count != 1:
    raise RuntimeError(
        "Could not patch arka_brain cleanly. The current file structure is different than expected."
    )

app.write_text(new_code, encoding="utf-8")
py_compile.compile(str(app), doraise=True)

print("[OK] Arka v0.4.3 friendly conversation + self-module discovery patch applied.")
