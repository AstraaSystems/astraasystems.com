from pathlib import Path
import py_compile

app = Path("arka_v1.py")
code = app.read_text(encoding="utf-8-sig")

import_line = "from arka_governor_dispatcher import arka_governor_dispatch"

if import_line not in code:
    # Prefer placing after existing imports if possible.
    if "from arka_math_os import" in code:
        code = code.replace(
            "from arka_math_os import arka_math_os_router",
            "from arka_math_os import arka_math_os_router\n" + import_line,
            1
        )
    else:
        code = import_line + "\n" + code

router = '''
    # Arka Governor Dispatcher: runtime routing above old patch routers.
    governor_result = arka_governor_dispatch(raw, web_func=globals().get("arka_search_or_sources"))
    if governor_result:
        try:
            log_event("governor_dispatch", raw)
        except Exception:
            pass
        return governor_result
'''

if "Arka Governor Dispatcher: runtime routing above old patch routers." not in code:
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

py_compile.compile("arka_governor_dispatcher.py", doraise=True)
py_compile.compile(str(app), doraise=True)

print("[OK] Governor Dispatcher installed into Arka V1.")
