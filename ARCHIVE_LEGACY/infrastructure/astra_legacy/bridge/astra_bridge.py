class ASTRABridge:
    def __init__(self, astra, arka, sync_engine):
        self.astra = astra
        self.arka = arka
        self.sync = sync_engine

    def send_to_astra(self, text):
        result = self.arka.process(text)
        self.sync.astra_memory.save("last_message", result)
        return result

    def get_astra_memory(self):
        return self.sync.astra_memory.all()
