class ASTRAMemory:
    def __init__(self):
        self.store = {}

    def save(self, key, value):
        self.store[key] = value
        return {"saved": key}

    def load(self, key):
        return self.store.get(key, None)

    def all(self):
        return self.store
