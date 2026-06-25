from pathlib import Path
import py_compile

app = Path("arka_v1.py")
code = app.read_text(encoding="utf-8-sig")

# Add import
if "from arka_math_os import arka_math_os_router" not in code:
    marker = "from urllib.parse import parse_qs"
    if marker in code:
        code = code.replace(marker, marker + "\nfrom arka_math_os import arka_math_os_router", 1)
    else:
        code = "from arka_math_os import arka_math_os_router\n" + code

# Inject router early inside arka_reply, after w = raw.lower()
router = '''
    # Full Math OS router: local calculations before web fallback.
    math_result = arka_math_os_router(raw)
    if math_result:
        try:
            log_event("math_os_calculation", raw)
        except Exception:
            pass
        return math_result
'''

if "Full Math OS router: local calculations before web fallback." not in code:
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
py_compile.compile("arka_math_os.py", doraise=True)
py_compile.compile(str(app), doraise=True)

print("[OK] Full Math OS installed and connected to Arka V1.")
