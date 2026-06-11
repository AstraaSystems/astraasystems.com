#!/usr/bin/env python3
"""
ARKA Sovereign Ecosystem — Import Validator (Extreme Edition)
Purpose:
    - Validate all engine imports
    - Validate OS + Supervisor
    - Validate Astraa TriVertical Sovereign Engine
    - Validate folder structure
    - Validate class existence
    - Validate file integrity (SHA-256)
"""

import os
import sys
import importlib
import hashlib
import json
from typing import Dict, Any, List

# ============================================================
# 1. EXPECTED FILES + MODULES
# ============================================================

EXPECTED_MODULES = {
    "arka_core.ardhanarishvara_os": "ArdhanarishvaraOS",
    "arka_core.arka_ultimate_supervisor": "ArkaUltimateSupervisor",

    "entities.aruhan": "AruhanAgent",
    "entities.astraa": "AstraaAgent",
    "entities.arkastra": "ArkastraAgent",
    "entities.lux": "LuxAgent",
    "entities.disturition": "DisturitionAgent",

    "entities.astraa_trivertical_sovengine": "AstraaTriVerticalSovEngine",
}

# ============================================================
# 2. FILE INTEGRITY CHECK
# ============================================================

def sha256_file(path: str) -> str:
    if not os.path.exists(path):
        return "MISSING"
    h = hashlib.sha256()
    with open(path, "rb") as f:
        for chunk in iter(lambda: f.read(4096), b""):
            h.update(chunk)
    return h.hexdigest().upper()

# ============================================================
# 3. MODULE IMPORT CHECK
# ============================================================

def validate_import(module_path: str, class_name: str) -> Dict[str, Any]:
    result = {
        "module": module_path,
        "class": class_name,
        "import_success": False,
        "class_exists": False,
        "error": None
    }

    try:
        module = importlib.import_module(module_path)
        result["import_success"] = True

        if hasattr(module, class_name):
            result["class_exists"] = True
        else:
            result["error"] = f"Class '{class_name}' not found in module."

    except Exception as e:
        result["error"] = str(e)

    return result

# ============================================================
# 4. FOLDER STRUCTURE VALIDATION
# ============================================================

EXPECTED_FOLDERS = [
    "arka_core",
    "entities",
    "execution",
    "support_docs",
    ".astraa_vault",
    ".ardhanarishvara_vault"
]

def validate_folders() -> Dict[str, bool]:
    return {folder: os.path.exists(folder) for folder in EXPECTED_FOLDERS}

# ============================================================
# 5. RUN VALIDATION
# ============================================================

def run_validator():
    print("\n===============================================")
    print(" ARKA SOVEREIGN ECOSYSTEM — IMPORT VALIDATOR")
    print("===============================================\n")

    report = {
        "folders": validate_folders(),
        "modules": {},
        "integrity": {}
    }

    # Validate modules
    for module_path, class_name in EXPECTED_MODULES.items():
        result = validate_import(module_path, class_name)
        report["modules"][module_path] = result

    # Validate file integrity
    for module_path in EXPECTED_MODULES.keys():
        file_path = module_path.replace(".", "/") + ".py"
        report["integrity"][file_path] = sha256_file(file_path)

    print(json.dumps(report, indent=4))

    print("\n===============================================")
    print(" VALIDATION COMPLETE")
    print("===============================================\n")

    return report

# ============================================================
# 6. MAIN
# ============================================================

if __name__ == "__main__":
    run_validator()
