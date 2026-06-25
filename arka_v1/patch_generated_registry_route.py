from pathlib import Path
import py_compile

path = Path("arka_governor_dispatcher.py")
code = path.read_text(encoding="utf-8-sig")

helpers = r'''

def _load_generated_registry() -> dict:
    path = ARKA_DIR / "arka_ecosystem_registry.generated.json"
    try:
        return json.loads(path.read_text(encoding="utf-8-sig"))
    except Exception:
        return {"entities": []}


def _generated_entity_lookup(name: str):
    reg = _load_generated_registry()
    wanted = (name or "").strip().lower()
    wanted = re.sub(r"\s+([?.!])", r"\1", wanted)
    wanted = re.sub(r"[?.!]+$", "", wanted).strip()

    for item in reg.get("entities", []):
        if item.get("name", "").lower() == wanted:
            return item

    for item in reg.get("entities", []):
        n = item.get("name", "").lower()
        if wanted in n or n in wanted:
            return item

    return None


def _is_generated_ecosystem_question(raw: str) -> bool:
    w = (raw or "").strip().lower()
    w = re.sub(r"\s+([?.!])", r"\1", w)

    list_triggers = [
        "name all the ai",
        "name all ai",
        "all ai inside",
        "ai inside our ecosystem",
        "what ai are inside",
        "list ai",
        "list all ai",
        "what engines do we have",
        "name all engines",
        "ecosystem ai",
        "ecosystem engines",
        "show ecosystem registry",
        "show ai council"
    ]

    if any(x in w for x in list_triggers):
        return True

    if w.startswith(("who is ", "what is ", "what's ")):
        target = (
            w.replace("who is ", "", 1)
             .replace("what is ", "", 1)
             .replace("what's ", "", 1)
             .replace("?", "")
             .strip()
        )
        return _generated_entity_lookup(target) is not None

    return False


def governor_generated_ecosystem_registry(raw: str) -> str:
    reg = _load_generated_registry()
    w = (raw or "").strip().lower()

    if w.startswith(("who is ", "what is ", "what's ")):
        target = (
            w.replace("who is ", "", 1)
             .replace("what is ", "", 1)
             .replace("what's ", "", 1)
             .replace("?", "")
             .strip()
        )
        item = _generated_entity_lookup(target)
        if item:
            lines = [
                f"{item.get('name')} — Self-Discovered Ecosystem Registry",
                "",
                f"Detected role: {item.get('detected_role')}",
                f"Status: {item.get('status')}",
                f"Evidence count: {item.get('evidence_count')}",
                f"Callable status: {item.get('callable_status')}",
                "",
                "Top local evidence:"
            ]

            for e in item.get("top_evidence", [])[:5]:
                lines.append(f"- {e.get('path')} | score {e.get('score')} | role hint {e.get('role_hint')}")

            if item.get("approval_required_for"):
                lines.append("")
                lines.append("Approval-sensitive areas detected:")
                for a in item.get("approval_required_for", []):
                    lines.append(f"- {a}")

            lines.append("")
            lines.append("Note: This answer comes from Arka's generated local ecosystem discovery, not web search.")

            return "\n".join(lines)

    lines = [
        "AI / Agents / Engines inside the Arka-Astraa ecosystem",
        "",
        "Generated from local ecosystem self-discovery:"
    ]

    for item in reg.get("entities", []):
        lines.append("")
        lines.append(f"- {item.get('name')}")
        lines.append(f"  Detected role: {item.get('detected_role')}")
        lines.append(f"  Status: {item.get('status')}")
        lines.append(f"  Evidence count: {item.get('evidence_count')}")
        lines.append(f"  Callable status: {item.get('callable_status')}")

    lines.append("")
    lines.append("Note: This registry is generated from local files. If files change, run ecosystem self-discovery again.")

    return "\n".join(lines)
'''

if "def _load_generated_registry()" not in code:
    marker = "def arka_governor_dispatch(raw: str, web_func=None) -> str:"
    if marker not in code:
        raise RuntimeError("Could not find arka_governor_dispatch.")
    code = code.replace(marker, helpers + "\n\n" + marker, 1)

old = '''    # Identity / owner route must run before web/source fallback.
    if _is_identity_question(raw):
        return governor_identity_status(raw)

    # Specific business/system routes first.
'''

new = '''    # Identity / owner route must run before web/source fallback.
    if _is_identity_question(raw):
        return governor_identity_status(raw)

    # Generated ecosystem registry route: self-discovered internal AIs/agents/engines before web fallback.
    if _is_generated_ecosystem_question(raw):
        return governor_generated_ecosystem_registry(raw)

    # Specific business/system routes first.
'''

if old in code and "_is_generated_ecosystem_question(raw)" not in code.split("def arka_governor_dispatch", 1)[1]:
    code = code.replace(old, new, 1)

path.write_text(code, encoding="utf-8")
py_compile.compile(str(path), doraise=True)

print("[OK] Generated registry route installed.")
