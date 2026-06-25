import json
from pathlib import Path

base = Path(r"D:\ARKA_HQ\repos\ardhanarishvara_git\arka_v1")
reg = json.loads((base / "arka_ecosystem_registry.generated.json").read_text(encoding="utf-8-sig"))
contracts = json.loads((base / "arka_capability_contracts.generated.json").read_text(encoding="utf-8-sig"))
missing = json.loads((base / "arka_missing_entrypoints_report.json").read_text(encoding="utf-8-sig"))

print("Registry:", base / "arka_ecosystem_registry.generated.json")
print("Contracts:", base / "arka_capability_contracts.generated.json")
print("Missing:", base / "arka_missing_entrypoints_report.json")
print("Entities:", len(reg.get("entities", [])))
print("Present:", sum(1 for x in reg.get("entities", []) if x.get("status") == "present"))
print("Callable candidates:", sum(1 for x in reg.get("entities", []) if x.get("callable_status") == "candidate_entrypoints_found"))
print("")
print("Entities:")
for item in reg.get("entities", []):
    print("-", item.get("name"), "|", item.get("status"), "|", item.get("detected_role"), "|", item.get("callable_status"), "| evidence:", item.get("evidence_count"))
print("")
print("Missing/weak:")
for item in missing.get("missing_or_weak", []):
    print("-", item.get("name"), "|", item.get("status"), "|", item.get("callable_status"))
