# aruhan/governance/fusion/adaptive_trust_learner.py

from aruhan.os.memory.json_ledger import JsonLedger

class AdaptiveTrustLearner:
    """
    Upgraded Arka Trust Learner. Distinctly grades directional tracking nodes 
    vs structural governance nodes to guarantee balanced ecosystem evaluation.
    """
    def __init__(self, max_lookback=300):
        self.ledger = JsonLedger()
        self.max_lookback = max_lookback

    def _score_record(self, source_name, source_entry, record):
        sig_val = source_entry.get("value", 0.0)
        global_innovation = record.get("innovation", 0.0)
        
        # Guard against older structural ledger entries with raw uniform values
        if source_name in ["estimator", "dataoracle"]:
            node_error = abs(sig_val - global_innovation)
            return max(0.0, 1.0 - node_error)
        else:
            # Normalize structural nodes (temporal/reflection) based on state correlation
            system_error = abs(record.get("prediction", 0.0) - record.get("measurement", 0.0))
            if system_error > 0.5:
                return 1.0 if abs(sig_val) > 0.3 else 0.4
            else:
                return 1.0 if abs(sig_val) <= 0.3 else 0.6

    def source_reliability(self, source_name, current_signal=None):
        records = self.ledger.read_all()
        if len(records) < 30:
            return 1.0

        recent = records[-self.max_lookback:]
        matched = []

        for r in recent:
            if "signals" not in r:
                continue

            source_entry = None
            for s in r["signals"]:
                if s.get("source") == source_name:
                    source_entry = s
                    break

            if source_entry is None:
                continue

            if current_signal is not None:
                if source_entry.get("trend") != current_signal.trend:
                    continue
                if source_entry.get("regime") != current_signal.regime:
                    continue

            matched.append(self._score_record(source_name, source_entry, r))

        if len(matched) < 5:
            return 1.0

        return max(0.4, min(sum(matched) / len(matched), 1.05))

    def source_summary(self, source_name):
        records = self.ledger.read_all()
        matched = []
        for r in records[-self.max_lookback:]:
            if "signals" not in r:
                continue

            source_entry = None
            for s in r["signals"]:
                if s.get("source") == source_name:
                    source_entry = s
                    break

            if source_entry is None:
                continue

            matched.append(self._score_record(source_name, source_entry, r))

        if not matched:
            return {"source": source_name, "samples": 0, "avg_score": 0.0}

        return {
            "source": source_name, 
            "samples": len(matched), 
            "avg_score": round(sum(matched) / len(matched), 4)
        }
