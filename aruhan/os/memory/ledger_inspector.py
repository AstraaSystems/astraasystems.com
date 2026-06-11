import json
from pathlib import Path

def audit_ledger():
    ledger_path = Path("aruhan_ledger.jsonl")
    if not ledger_path.exists():
        print("❌ Inspector Error: Target ledger footprint does not exist on disk.")
        return

    nominal_errors = []
    stress_errors = []
    defensive_count = 0
    total_samples = 0
    
    with ledger_path.open("r") as f:
        for line in f:
            record = json.loads(line)
            actual = record['measurement']
            pred = record['prediction']
            decision = record['decision']
            
            error = abs(actual - pred)
            total_samples += 1
            
            if decision == "ACT DEFENSIVE":
                stress_errors.append(error)
                defensive_count += 1
            else:
                nominal_errors.append(error)

    # Calculate MAD (Mean Absolute Deviation)
    nom_mad = sum(nominal_errors) / len(nominal_errors) if nominal_errors else 0
    stress_mad = sum(stress_errors) / len(stress_errors) if stress_errors else 0

    print("=========================================================================")
    print("🛡️  ARUHAN INTEGRITY & GOVERNANCE LEDGER AUDIT REPORT")
    print("=========================================================================")
    print(f"📈 Total Historical Lifetime Cycles Accounted: {total_samples}")
    print(f"\n🧠 REGIME-SPECIFIC PERFORMANCE MATRIX (MEAN ERROR)")
    print(f"   ├─ NOMINAL      : {nom_mad:.4f} Mean Absolute Deviation (MAD)")
    print(f"   ├─ HIGH_STRESS  : {stress_mad:.4f} Mean Absolute Deviation (MAD)")
    print(f"   └─ Gate Interventions : {defensive_count} DEFENSIVE triggers fired.")
    print("=========================================================================")

if __name__ == "__main__":
    audit_ledger()
