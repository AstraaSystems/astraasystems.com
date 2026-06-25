from pathlib import Path
import json
import py_compile

root = Path(".").resolve()
print(f"[ARKA FIX] Repairing folder: {root}")

# ------------------------------------------------------------
# 1) Remove UTF-8 BOM from JSON files
# ------------------------------------------------------------
json_files = [
    root / "arka_policy.json",
    root / "arka_identity.json",
    root / "arka_memory.json",
]

for path in json_files:
    if path.exists():
        text = path.read_text(encoding="utf-8-sig")
        data = json.loads(text)
        path.write_text(json.dumps(data, indent=2), encoding="utf-8")
        print(f"[OK] Rewritten without BOM: {path.name}")
    else:
        print(f"[WARN] Missing JSON file: {path.name}")

# ------------------------------------------------------------
# 2) Patch Python app to tolerate BOM forever
# ------------------------------------------------------------
app = root / "arka_personal_ai_v04.py"

if not app.exists():
    raise FileNotFoundError("arka_personal_ai_v04.py was not found in this folder.")

code = app.read_text(encoding="utf-8-sig")

code = code.replace('read_text(encoding="utf-8")', 'read_text(encoding="utf-8-sig")')
code = code.replace("read_text(encoding='utf-8')", "read_text(encoding='utf-8-sig')")

# ------------------------------------------------------------
# 3) Fix form tags if previous terminal paste stripped them
# ------------------------------------------------------------
code = code.replace(
    '            /run\n                <input',
    '            <form method="POST" action="/run">\n                <input'
)

code = code.replace(
    '            /approve_memory\n                <input',
    '            <form method="POST" action="/approve_memory">\n                <input'
)

code = code.replace(
    '                    /ask\n                        <div',
    '                    <form method="POST" action="/ask">\n                        <div'
)

# Also handle spacing variants
code = code.replace(
    '            /run\r\n                <input',
    '            <form method="POST" action="/run">\r\n                <input'
)

code = code.replace(
    '            /approve_memory\r\n                <input',
    '            <form method="POST" action="/approve_memory">\r\n                <input'
)

code = code.replace(
    '                    /ask\r\n                        <div',
    '                    <form method="POST" action="/ask">\r\n                        <div'
)

app.write_text(code, encoding="utf-8")
print("[OK] Patched arka_personal_ai_v04.py")

# ------------------------------------------------------------
# 4) Validate JSON again
# ------------------------------------------------------------
for path in json_files:
    if path.exists():
        json.loads(path.read_text(encoding="utf-8-sig"))
        print(f"[OK] JSON validated: {path.name}")

# ------------------------------------------------------------
# 5) Validate Python syntax
# ------------------------------------------------------------
py_compile.compile(str(app), doraise=True)
print("[OK] Python syntax validated")

print("")
print("[ARKA FIX] Repair complete. Start Arka with:")
print("python .\\arka_personal_ai_v04.py")
