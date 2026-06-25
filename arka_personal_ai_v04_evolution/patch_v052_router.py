from pathlib import Path
import re
import py_compile

app = Path("arka_personal_ai_v04.py")
code = app.read_text(encoding="utf-8-sig")

# Add import after existing imports.
if "from arka_capabilities_v052 import arka_capability_router" not in code:
    marker = "from urllib.parse import parse_qs"
    if marker in code:
        code = code.replace(
            marker,
            marker + "\nfrom arka_capabilities_v052 import arka_capability_router",
            1
        )
    else:
        code = "from arka_capabilities_v052 import arka_capability_router\n" + code

# Inject router immediately after w = raw.lower()
if "ARKA v0.5.2 capability router" not in code:
    patterns = [
        "    w = raw.lower()",
        "    w=raw.lower()",
        "    w = raw.lower().strip()",
        "    w=raw.lower().strip()"
    ]

    patched = False

    for p in patterns:
        if p in code:
            code = code.replace(
                p,
                p + """
    # ARKA v0.5.2 capability router
    routed = arka_capability_router(raw)
    if routed:
        return routed
""",
                1
            )
            patched = True
            break

    if not patched:
        raise RuntimeError("Could not find arka_brain raw/w entry point to patch.")

app.write_text(code, encoding="utf-8")
py_compile.compile(str(app), doraise=True)

print("[OK] Main app patched with v0.5.2 capability router.")
