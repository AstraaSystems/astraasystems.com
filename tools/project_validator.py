# === PROJECT VALIDATOR (V17) ===

import os
import json
import importlib.util

BASE = "/home/keshanth/ARKA/ardhanarishvara"

REQUIRED_STRUCTURE = {
    "core": [
        "blackboard.py",
        "intent_engine.py",
        "kill_switch.py",
        "__init__.py"
    ],
    "agents": [
        "business_engine.py",
        "finance_engine.py",
        "operations_engine.py",
        "__init__.py"
    ],
    "tools": [
        "project_validator.py",
        "__init__.py"
    ]
}

def check_file_exists(path):
    return os.path.exists(path)

def check_importable(module_path):
    spec = importlib.util.spec_from_file_location("mod", module_path)
    if spec is None:
        return False
    try:
        mod = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(mod)
        return True
    except Exception:
        return False

def validate_structure():
    report = {
        "missing_files": [],
        "missing_init_files": [],
        "import_errors": [],
        "status": "OK"
    }

    for folder, files in REQUIRED_STRUCTURE.items():
        folder_path = os.path.join(BASE, folder)

        if not os.path.exists(folder_path):
            report["missing_files"].append(f"Missing folder: {folder_path}")
            continue

        for file in files:
            file_path = os.path.join(folder_path, file)

            if not check_file_exists(file_path):
                report["missing_files"].append(file_path)

            if file == "__init__.py" and not check_file_exists(file_path):
                report["missing_init_files"].append(file_path)

            if file.endswith(".py") and file != "__init__.py":
                if not check_importable(file_path):
                    report["import_errors"].append(file_path)

    if report["missing_files"] or report["import_errors"]:
        report["status"] = "ERROR"

    return report

def print_report(report):
    print("\n=== PROJECT VALIDATION REPORT ===\n")

    print("Status:", report["status"])
    print("\nMissing Files:")
    for f in report["missing_files"]:
        print(" -", f)

    print("\nMissing __init__.py:")
    for f in report["missing_init_files"]:
        print(" -", f)

    print("\nImport Errors:")
    for f in report["import_errors"]:
        print(" -", f)

    print("\n=================================\n")

if __name__ == "__main__":
    report = validate_structure()
    print_report(report)
