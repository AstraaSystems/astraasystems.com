from ardhanarishvara.memory.long_term_memory import LongTermMemory

class AruhanMemoryBridge:
    def __init__(self):
        self.shared = LongTermMemory()

    def write(self, data):
        self.shared.store(data)

    def read(self):
        return self.shared.retrieve()
