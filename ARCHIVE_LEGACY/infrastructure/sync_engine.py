class ASTRASync:
    def __init__(self, astra, arka):
        self.astra = astra
        self.arka = arka

    def sync_heartbeat(self):
        hb = self.arka.os.health.heartbeat()
        self.astra_memory.save("arka_heartbeat", hb)
        return hb

    def sync_health(self):
        health = self.arka.os.health.health_score()
        self.astra_memory.save("arka_health", health)
        return health

    def attach_memory(self, memory_engine):
        self.astra_memory = memory_engine
