#!/usr/bin/env python3
"""
Astraa Patch: Dev Login Public-Mode Block

PATCH SCRIPT.

Purpose:
- Patch api.py so /api/auth/dev-login is blocked when:
  ASTRAA_PUBLIC_LAUNCH_MODE=true
  and ASTRAA_ALLOW_DEV_LOGIN_PUBLIC_MODE is not true.

Safety:
- Creates a timestamped backup of api.py.
- Only inserts a small guard inside /api/auth/dev-login.
- Does not touch payment, Estimator, Moneris, staging DB, storage, or Core OS logic.
- Idempotent: exits cleanly if marker already exists.
"""

from __future__ import annotations

from pathlib import Path
from datetime import datetime


API_PATH = Path("api.py")
MARKER = "ASTRAA_DEV_LOGIN_PUBLIC_MODE_BLOCK_V1"

ROUTE_MARKERS = [
    '@app.post("/api/auth/dev-login")',
    '@app.route("/api/auth/dev-login", methods=["POST"])',
    '@app.route("/api/auth/dev-login", methods=[\'POST\'])',
    "@app.post('/api/auth/dev-login')",
    "@app.route('/api/auth/dev-login', methods=['POST'])",
]

GUARD_LINES = [
    "    # ASTRAA_DEV_LOGIN_PUBLIC_MODE_BLOCK_V1",
    "    public_launch_mode = os.getenv(\"ASTRAA_PUBLIC_LAUNCH_MODE\", \"false\").strip().lower() == \"true\"",
    "    allow_dev_login_public_mode = os.getenv(\"ASTRAA_ALLOW_DEV_LOGIN_PUBLIC_MODE\", \"false\").strip().lower() == \"true\"",
    "",
    "    if public_launch_mode and not allow_dev_login_public_mode:",
    "        return jsonify({",
    "            \"gateway\": \"Astraa Gateway\",",
    "            \"status\": \"blocked\",",
    "            \"reason\": \"Development login is disabled in public launch mode.\",",
    "            \"review_note\": \"Set ASTRAA_ALLOW_DEV_LOGIN_PUBLIC_MODE=true only for intentional internal QA.\"",
    "        }), 403",
    "",
]

GUARD = "\n".join(GUARD_LINES) + "\n"


def find_route_position(text: str) -> tuple[int, str]:
    for marker in ROUTE_MARKERS:
        pos = text.find(marker)
        if pos != -1:
            return pos, marker
    return -1, ""


def main():
    if not API_PATH.exists():
        raise SystemExit("❌ api.py not found")

    text = API_PATH.read_text(encoding="utf-8", errors="ignore")

    if MARKER in text:
        print("✅ Dev-login production-mode block already exists")
        return

    route_pos, route_marker = find_route_position(text)

    if route_pos == -1:
        raise SystemExit("❌ Could not locate /api/auth/dev-login route decorator")

    def_pos = text.find("\ndef ", route_pos)

    if def_pos == -1:
        raise SystemExit("❌ Could not locate function definition after /api/auth/dev-login route")

    def_line_start = def_pos + 1
    def_line_end = text.find("\n", def_line_start)

    if def_line_end == -1:
        raise SystemExit("❌ Could not locate end of dev-login function definition line")

    def_line = text[def_line_start:def_line_end]

    backup = API_PATH.with_name(
        API_PATH.name + ".bak_dev_login_public_block_" + datetime.now().strftime("%Y%m%d_%H%M%S")
    )
    backup.write_text(text, encoding="utf-8")

    insert_pos = def_line_end + 1
    patched = text[:insert_pos] + GUARD + text[insert_pos:]

    API_PATH.write_text(patched, encoding="utf-8")

    print("✅ Added dev-login public-launch-mode block")
    print("Route marker:", route_marker)
    print("Function line:", def_line)
    print(f"Backup: {backup}")


if __name__ == "__main__":
    main()
