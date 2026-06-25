from pathlib import Path
import py_compile

path = Path("arka_governor_dispatcher.py")
code = path.read_text(encoding="utf-8-sig")

identity_helpers = r'''

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
'''

if "def _is_identity_question(raw: str)" not in code:
    # Insert before dispatcher function if possible.
    marker = "def arka_governor_dispatch(raw: str, web_func=None) -> str:"
    if marker not in code:
        raise RuntimeError("Could not find arka_governor_dispatch function.")
    code = code.replace(marker, identity_helpers + "\n\n" + marker, 1)

# Add identity route at top of arka_governor_dispatch after raw empty check.
old = '''    # Specific business/system routes first.
    if _is_website_status(raw):
        return governor_website_status(raw)
'''

new = '''    # Identity / owner route must run before web/source fallback.
    if _is_identity_question(raw):
        return governor_identity_status(raw)

    # Specific business/system routes first.
    if _is_website_status(raw):
        return governor_website_status(raw)
'''

if old in code and "_is_identity_question(raw)" not in code.split("def arka_governor_dispatch", 1)[1]:
    code = code.replace(old, new, 1)

path.write_text(code, encoding="utf-8")
py_compile.compile(str(path), doraise=True)

print("[OK] Identity route added to Governor Dispatcher.")
print("[TEST] who am I?")
