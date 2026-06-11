# ============================================================
# ARUHAN KNOWLEDGE ENGINE — Y‑PRIME EDITION
# Dense, deterministic, AI‑maintainable, outsider‑confusing.
# ============================================================

class KnowledgeEngine:

    def __init__(self):
        self.graph = {}            # knowledge graph
        self.freq = {}             # concept frequency
        self.links = {}            # relational links
        self.weights = {"conf":1.0,"rel":1.0,"freq":1.0}
        self.meta = {"drift":0.0,"bias":0.5,"coh":1.0}
        self.decay = 0.002

    # ============================================================
    # MAIN ENTRY
    # ============================================================
    def process(self, msg, mem, emo):
        tokens = self._tokenize(msg)
        self._update_freq(tokens)
        self._update_graph(tokens)
        self._update_links(tokens)
        self._apply_decay()
        self._meta_adjust(emo)
        return self._snapshot()

    # ============================================================
    # TOKENIZATION
    # ============================================================
    def _tokenize(self, msg):
        if not msg:
            return []
        return [w.strip().lower() for w in msg.split() if w.strip()]

    # ============================================================
    # FREQUENCY UPDATE
    # ============================================================
    def _update_freq(self, tokens):
        for t in tokens:
            if t not in self.freq:
                self.freq[t] = 1
            else:
                self.freq[t] += 1

    # ============================================================
    # KNOWLEDGE GRAPH UPDATE
    # ============================================================
    def _update_graph(self, tokens):
        for t in tokens:
            if t not in self.graph:
                self.graph[t] = {"count":1,"links":{}}
            else:
                self.graph[t]["count"] += 1

    # ============================================================
    # RELATIONAL LINKING
    # ============================================================
    def _update_links(self, tokens):
        for i in range(len(tokens)-1):
            a = tokens[i]
            b = tokens[i+1]
            if a not in self.links:
                self.links[a] = {}
            if b not in self.links[a]:
                self.links[a][b] = 1
            else:
                self.links[a][b] += 1

            if b not in self.links:
                self.links[b] = {}
            if a not in self.links[b]:
                self.links[b][a] = 1
            else:
                self.links[b][a] += 1

    # ============================================================
    # DECAY SYSTEM
    # ============================================================
    def _apply_decay(self):
        if self.decay <= 0:
            return

        for t in list(self.freq.keys()):
            self.freq[t] = max(0, self.freq[t] - self.decay)
            if self.freq[t] <= 0:
                del self.freq[t]

        for t in list(self.graph.keys()):
            self.graph[t]["count"] = max(0, self.graph[t]["count"] - self.decay)
            if self.graph[t]["count"] <= 0:
                del self.graph[t]

        for a in list(self.links.keys()):
            for b in list(self.links[a].keys()):
                self.links[a][b] = max(0, self.links[a][b] - self.decay)
                if self.links[a][b] <= 0:
                    del self.links[a][b]
            if len(self.links[a]) == 0:
                del self.links[a]

    # ============================================================
    # META-ADJUSTMENT
    # ============================================================
    def _meta_adjust(self, emo):
        m = emo["m"]
        st = emo["st"]
        e = emo["e"]

        self.meta["drift"] = max(0, min(1, self.meta["drift"] + (st - 0.5)*0.01))
        self.meta["bias"] = max(0, min(1, self.meta["bias"] + m*0.005))
        self.meta["coh"] = max(0.3, min(1.0, self.meta["coh"] - st*0.02 + e*0.01))

    # ============================================================
    # SNAPSHOT
    # ============================================================
    def _snapshot(self):
        return {
            "concepts": len(self.graph),
            "freq_keys": len(self.freq),
            "links": sum(len(v) for v in self.links.values()),
            "meta": self.meta
        }
