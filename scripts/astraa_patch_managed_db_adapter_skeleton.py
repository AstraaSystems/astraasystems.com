#!/usr/bin/env python3
"""
Astraa Patch: Managed DB Adapter Skeleton

PATCH SCRIPT.

Purpose:
- Add managed DB adapter skeleton helpers to api.py.
- Prepare storage wrappers for future managed DB backend support.
- Keep JSON/local storage as the default.
- Keep managed DB mode fail-closed until real adapter implementation exists.

Does NOT:
- connect to managed DB
- create tables
- create indexes
- import data
- migrate data
- change route behavior
- change auth/payment behavior
- open customer access
- deploy Astraa
"""

from __future__ import annotations

from pathlib import Path
from datetime import datetime


ROOT = Path(".")
TARGET = ROOT / "api.py"
STAMP = datetime.now().strftime("%Y%m%d_%H%M%S")
BACKUP_DIR = ROOT / "SAFE_SNAPSHOTS" / f"managed_db_adapter_skeleton_{STAMP}"

START = "# ASTRAA_MANAGED_DB_ADAPTER_SKELETON_V1_START"
END = "# ASTRAA_MANAGED_DB_ADAPTER_SKELETON_V1_END"

INSERT_BEFORE = "def astraa_storage_load_sessions_db():"


SKELETON = r'''
# ASTRAA_MANAGED_DB_ADAPTER_SKELETON_V1_START
def astraa_storage_backend():
    """
    Return configured storage backend.

    Safe default:
    - json

    Future backend:
    - managed_db

    This helper does not connect to a database.
    """
    return os.getenv("ASTRAA_STORAGE_BACKEND", "json").strip().lower()


def astraa_managed_db_adapter_selected():
    """
    Return whether managed DB backend is explicitly selected.

    Selecting managed_db does not mean it is implemented or safe to use yet.
    """
    return astraa_storage_backend() in {"managed_db", "postgres", "postgresql"}


def astraa_managed_db_required_env():
    """
    Required environment names for future managed DB adapter use.

    Presence checks must never print secret values.
    """
    return [
        "ASTRAA_STORAGE_BACKEND",
        "ASTRAA_MANAGED_DB_ENGINE",
        "ASTRAA_MANAGED_DB_URL",
    ]


def astraa_managed_db_config_status():
    """
    Return managed DB configuration status without exposing secret values.

    This is a safe presence/shape check only.
    It does not connect to managed DB.
    It does not create tables.
    It does not migrate data.
    """
    backend = astraa_storage_backend()
    engine = os.getenv("ASTRAA_MANAGED_DB_ENGINE", "").strip().lower()
    has_url = bool(os.getenv("ASTRAA_MANAGED_DB_URL", "").strip())

    missing = []

    if backend in {"managed_db", "postgres", "postgresql"}:
        if not engine:
            missing.append("ASTRAA_MANAGED_DB_ENGINE")
        if engine in {"postgres", "postgresql", "managed_db"} and not has_url:
            missing.append("ASTRAA_MANAGED_DB_URL")

    return {
        "storage_backend": backend,
        "managed_db_selected": backend in {"managed_db", "postgres", "postgresql"},
        "engine": engine or None,
        "configured": not missing if backend in {"managed_db", "postgres", "postgresql"} else False,
        "missing": missing,
        "secret_values_exposed": False,
    }


def astraa_managed_db_adapter_blocked(operation, store_name):
    """
    Return a standard fail-closed managed DB adapter response.

    Future adapter implementation should replace this only after:
    - managed staging DB proof exists
    - schema/index proof exists
    - import/reconcile proof exists
    - production secrets are secure
    """
    status = astraa_managed_db_config_status()

    return {
        "status": "blocked",
        "storage_backend": status.get("storage_backend"),
        "managed_db_selected": status.get("managed_db_selected"),
        "engine": status.get("engine"),
        "configured": status.get("configured"),
        "missing": status.get("missing"),
        "operation": operation,
        "store_name": store_name,
        "reason": (
            "Managed DB adapter skeleton is present but real managed DB storage "
            "operations are not implemented yet. JSON/local storage remains the safe default."
        ),
    }


def astraa_managed_db_load_store_stub(store_name):
    """
    Fail-closed placeholder for future managed DB load operations.

    Does not connect to a database.
    """
    raise RuntimeError(str(astraa_managed_db_adapter_blocked("load", store_name)))


def astraa_managed_db_save_store_stub(store_name, data):
    """
    Fail-closed placeholder for future managed DB save operations.

    Does not connect to a database.
    """
    raise RuntimeError(str(astraa_managed_db_adapter_blocked("save", store_name)))
# ASTRAA_MANAGED_DB_ADAPTER_SKELETON_V1_END

'''.lstrip()


def main():
    print("=" * 100)
    print("ASTRAA MANAGED DB ADAPTER SKELETON PATCH")
    print("=" * 100)
    print("Mode: PATCH api.py")
    print("Target:", TARGET)
    print("Backup directory:", BACKUP_DIR)

    if not TARGET.exists():
        raise SystemExit("Missing api.py")

    original = TARGET.read_text(encoding="utf-8", errors="ignore")

    if START in original and END in original:
        print("Managed DB adapter skeleton already exists. No changes made.")
        return

    idx = original.find(INSERT_BEFORE)
    if idx == -1:
        raise SystemExit("Could not locate storage wrapper insertion point.")

    text = original[:idx] + SKELETON + original[idx:]

    backup_path = BACKUP_DIR / TARGET
    backup_path.parent.mkdir(parents=True, exist_ok=True)
    backup_path.write_text(original, encoding="utf-8")

    TARGET.write_text(text, encoding="utf-8")

    print("PATCHED:", TARGET)
    print("")
    print("Safety confirmation:")
    print("- This patch did not connect to managed DB.")
    print("- This patch did not create tables.")
    print("- This patch did not create indexes.")
    print("- This patch did not import data.")
    print("- This patch did not migrate data.")
    print("- This patch did not change route behavior.")
    print("- This patch did not change auth/payment behavior.")
    print("- This patch did not open customer access.")
    print("- This patch did not deploy Astraa.")


if __name__ == "__main__":
    main()
