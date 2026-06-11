# aruhan/os/predictive/predictive_cache.py

class PredictiveCache:
    """
    In-memory key-value store mapping state fingerprint keys directly
    to optimized, previously validated action-policy profiles.
    """
    def __init__(self):
        self.cache = {}

    def get(self, key):
        return self.cache.get(key)

    def set(self, key, value):
        self.cache[key] = value
