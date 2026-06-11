class ASTRAKnowledge:
    def __init__(self):
        self.knowledge = []

    def add(self, item):
        self.knowledge.append(item)
        return {"added": item}

    def all(self):
        return self.knowledge
