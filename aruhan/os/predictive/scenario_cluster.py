# aruhan/os/predictive/scenario_cluster.py

class ScenarioCluster:
    """
    Scans the historical ledger to harvest clusters of past execution states
    that match the structural profile of the current system fingerprint.
    """
    def find_similar(self, fp, ledger_records, limit=100):
        similar = []
        # Scan recent history for contextual pattern matching
        for r in ledger_records[-limit:]:
            f = r.get("fusion")
            if not f:
                continue

            # Evaluate distance bounds across core spatial dimensions
            if abs(f.get("score", 0.0) - fp["score"]) < 0.2:
                if abs(f.get("instability", 0.0) - fp["instability"]) < 0.2:
                    if f.get("direction", "").strip() == fp["direction"]:
                        similar.append(r)
        return similar
