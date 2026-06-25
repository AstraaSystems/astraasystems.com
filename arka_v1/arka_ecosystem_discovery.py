from __future__ import annotations

import ast
import json
import os
import re
import time
from pathlib import Path
from typing import Any, Dict, List

ROOT = Path(os.getenv("ARKA_HQ_ROOT", r"D:\ARKA_HQ\repos\ardhanarishvara_git"))
ARKA_DIR = ROOT / "arka_v1"

REGISTRY_OUT = ARKA_DIR / "arka_ecosystem_registry.generated.json"
CONTRACTS_OUT = ARKA_DIR / "arka_capability_contracts.generated.json"
MISSING_OUT = ARKA_DIR / "arka_missing_entrypoints_report.json"

SKIP_PARTS = [".git", ".venv", "__pycache__", "node_modules", ".pytest_cache"]
TEXT_SUFFIXES = {".py", ".md", ".json", ".txt", ".yaml", ".yml", ".html", ".js", ".css", ".ps1", ".toml"}

ENTITY_SEEDS = {
    "Arka": ["arka", "governor", "commander", "ceo", "coo", "hq", "personal ai"],
    "Aruhan": ["aruhan", "security", "intelligence", "risk", "audit", "guardian", "sentinel"],
    "Astraa": ["astraa", "astraasystems.com", "website", "workspace", "customer", "lead", "moneris"],
    "Ardhanarishvara OS": ["ardhanarishvara", "kernel", "governance", "policy", "signal", "fusion"],
    "Math OS": ["math os", "arka_math_os", "calculate", "goal", "margin", "compound", "loan"],
    "Lux": ["lux", "treasury", "compounding", "valuation", "ibkr", "yield"],
    "Arkastra": ["arkastra", "commerce", "order", "capital", "routing"],
    "Estimator": ["estimator", "estimate", "construction", "cost", "risk", "scenario"],
    "Oracle": ["oracle", "telemetry", "macro", "signal", "scan"],
    "Distribution": ["distribution", "logistics", "dispatch", "schedule", "flow"],
    "Bridge Layer": ["bridge", "astraa_arka_bridge", "sync", "execution router"],
}

ROLE_HINTS = [
    ("security_intelligence", ["security", "risk", "threat", "audit", "guardian", "sentinel"]),
    ("wealth_treasury", ["treasury", "lux", "compounding", "valuation", "ibkr", "yield"]),
    ("commerce", ["commerce", "order", "capital", "payment", "moneris"]),
    ("construction_estimator", ["estimator", "estimate", "construction", "cost"]),
    ("telemetry_oracle", ["oracle", "telemetry", "signal", "macro", "scan"]),
    ("logistics_distribution", ["distribution", "logistics", "dispatch", "schedule"]),
    ("governance_kernel", ["kernel", "governance", "policy", "ardhanarishvara"]),
    ("math_reasoning", ["math", "calculate", "goal", "margin", "compound"]),
    ("website_business", ["astraa", "website", "workspace", "lead", "customer"]),
    ("governor_interface", ["arka", "governor", "commander", "ceo", "coo"]),
]

APPROVAL_HINTS = [
    ("trading_or_capital", ["trade", "trading", "ibkr", "capital", "treasury"]),
    ("payment_or_customer", ["payment", "moneris", "customer", "email", "lead"]),
    ("public_website", ["publish", "website", "public", "deploy"]),
    ("destructive_file_action", ["delete", "remove", "overwrite", "archive"]),
]

def should_skip(path: Path) -> bool:
    s = str(path)
    return any(x in s for x in SKIP_PARTS)

def rel(path: Path) -> str:
    try:
        return str(path.relative_to(ROOT)).replace("\\", "/")
    except Exception:
        return str(path)

def safe_read(path: Path, limit: int = 250000) -> str:
    try:
        return path.read_text(encoding="utf-8-sig", errors="ignore")[:limit]
    except Exception:
        return ""

def list_files() -> List[Path]:
    files = []
    for p in ROOT.rglob("*"):
        if should_skip(p):
            continue
        if p.is_file() and p.suffix.lower() in TEXT_SUFFIXES:
            files.append(p)
    return files

def detect_functions_classes(path: Path) -> Dict[str, List[str]]:
    out = {"functions": [], "classes": []}
    if path.suffix.lower() != ".py":
        return out

    text = safe_read(path)
    try:
        tree = ast.parse(text)
    except Exception:
        return out

    for node in ast.walk(tree):
        if isinstance(node, ast.FunctionDef):
            out["functions"].append(node.name)
        elif isinstance(node, ast.ClassDef):
            out["classes"].append(node.name)

    return out

def score_entity(entity: str, keywords: List[str], path: Path, text: str) -> int:
    hay = (rel(path) + "\n" + text[:50000]).lower()
    score = 0
    for kw in keywords:
        k = kw.lower()
        if k in rel(path).lower():
            score += 5
        if k in hay:
            score += 2
    return score

def infer_role(text: str, path_text: str) -> str:
    hay = (path_text + "\n" + text[:50000]).lower()
    best = ("general", 0)
    for role, terms in ROLE_HINTS:
        score = sum(1 for t in terms if t in hay)
        if score > best[1]:
            best = (role, score)
    return best[0]

def infer_approval_required(text: str, path_text: str) -> List[str]:
    hay = (path_text + "\n" + text[:50000]).lower()
    approvals = []
    for approval, terms in APPROVAL_HINTS:
        if any(t in hay for t in terms):
            approvals.append(approval)
    return sorted(list(set(approvals)))

def discover() -> Dict[str, Any]:
    files = list_files()

    entities: Dict[str, Dict[str, Any]] = {}

    for entity, keywords in ENTITY_SEEDS.items():
        evidence = []
        total_score = 0
        role_votes = {}
        approval_set = set()
        entrypoints = []

        for p in files:
            text = safe_read(p)
            s = score_entity(entity, keywords, p, text)
            if s <= 0:
                continue

            total_score += s
            role = infer_role(text, rel(p))
            role_votes[role] = role_votes.get(role, 0) + 1

            for ap in infer_approval_required(text, rel(p)):
                approval_set.add(ap)

            fc = detect_functions_classes(p)
            callable_like = bool(fc["functions"] or fc["classes"])

            evidence.append({
                "path": rel(p),
                "score": s,
                "role_hint": role,
                "functions": fc["functions"][:20],
                "classes": fc["classes"][:20],
                "callable_like": callable_like,
                "preview": re.sub(r"\s+", " ", text[:500]).strip()
            })

            if callable_like:
                entrypoints.append({
                    "path": rel(p),
                    "functions": fc["functions"][:20],
                    "classes": fc["classes"][:20]
                })

        evidence.sort(key=lambda x: x["score"], reverse=True)

        detected_role = "general"
        if role_votes:
            detected_role = sorted(role_votes.items(), key=lambda x: x[1], reverse=True)[0][0]

        status = "present" if evidence else "not_detected"
        callable_status = "candidate_entrypoints_found" if entrypoints else "no_callable_entrypoint_detected"

        entities[entity] = {
            "name": entity,
            "status": status,
            "detected_role": detected_role,
            "confidence_score": total_score,
            "evidence_count": len(evidence),
            "top_evidence": evidence[:12],
            "callable_status": callable_status,
            "candidate_entrypoints": entrypoints[:10],
            "approval_required_for": sorted(list(approval_set)),
        }

    registry = {
        "version": "generated-1.0",
        "created_at": time.strftime("%Y-%m-%dT%H:%M:%S"),
        "root": str(ROOT),
        "purpose": "Generated ecosystem registry from local filesystem evidence. This is Arka's self-discovered map, not manually taught one-off answers.",
        "entities": list(entities.values()),
    }

    contracts = {
        "version": "generated-1.0",
        "created_at": time.strftime("%Y-%m-%dT%H:%M:%S"),
        "purpose": "Generated capability contracts. A capability is callable only when entrypoints are detected and safety/approval status is known.",
        "contracts": []
    }

    missing = {
        "version": "generated-1.0",
        "created_at": time.strftime("%Y-%m-%dT%H:%M:%S"),
        "missing_or_weak": []
    }

    for item in registry["entities"]:
        contract = {
            "name": item["name"],
            "detected_role": item["detected_role"],
            "status": item["status"],
            "callable_status": item["callable_status"],
            "candidate_entrypoints": item["candidate_entrypoints"],
            "approval_required_for": item["approval_required_for"],
            "safe_read_only_use": item["status"] == "present",
            "safe_execute_use": item["callable_status"] == "candidate_entrypoints_found" and not item["approval_required_for"],
            "input_schema": "not_declared",
            "output_schema": "not_declared",
            "notes": "Generated from filesystem evidence. Promote to explicit contract before autonomous execution."
        }
        contracts["contracts"].append(contract)

        if item["status"] != "present" or item["callable_status"] != "candidate_entrypoints_found":
            missing["missing_or_weak"].append({
                "name": item["name"],
                "status": item["status"],
                "callable_status": item["callable_status"],
                "recommendation": "Add or promote explicit capability contract/entrypoint if this entity should be executable by Arka."
            })

    REGISTRY_OUT.write_text(json.dumps(registry, indent=2), encoding="utf-8")
    CONTRACTS_OUT.write_text(json.dumps(contracts, indent=2), encoding="utf-8")
    MISSING_OUT.write_text(json.dumps(missing, indent=2), encoding="utf-8")

    return {
        "registry": str(REGISTRY_OUT),
        "contracts": str(CONTRACTS_OUT),
        "missing": str(MISSING_OUT),
        "entity_count": len(registry["entities"]),
        "present_count": sum(1 for x in registry["entities"] if x["status"] == "present"),
        "callable_candidates": sum(1 for x in registry["entities"] if x["callable_status"] == "candidate_entrypoints_found")
    }

def main():
    result = discover()
    print("[OK] Arka ecosystem self-discovery complete.")
    print("[REGISTRY]", result["registry"])
    print("[CONTRACTS]", result["contracts"])
    print("[MISSING]", result["missing"])
    print("Entities:", result["entity_count"])
    print("Present:", result["present_count"])
    print("Callable candidates:", result["callable_candidates"])

if __name__ == "__main__":
    main()
