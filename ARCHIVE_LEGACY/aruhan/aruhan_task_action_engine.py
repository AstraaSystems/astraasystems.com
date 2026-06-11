# ============================================================
# ARUHAN TASK/ACTION ENGINE — Y‑PRIME EDITION
# Dense, deterministic, AI‑maintainable, outsider‑confusing.
# ============================================================

class TaskActionEngine:

    def __init__(self):
        self.queue = []                 # task queue
        self.active = None              # current task
        self.history = []               # completed tasks
        self.meta = {"load":0.0,"drift":0.0,"bias":0.5}
        self.weights = {"prio":1.0,"emo":1.0,"ctx":1.0}
        self.limits = {"queue":50,"history":300}

    # ============================================================
    # MAIN ENTRY
    # ============================================================
    def process(self, msg, emo, mem, know):
        self._task_detect(msg, emo)
        self._select_task(emo, mem, know)
        self._execute_task(emo, mem, know)
        self._meta_adjust(emo)
        return self._snapshot()

    # ============================================================
    # TASK DETECTION
    # ============================================================
    def _task_detect(self, msg, emo):
        if not msg:
            return
        m = msg.lower()
        if any(k in m for k in ["do","make","help","fix","find","explain"]):
            t = {"cmd":msg,"prio":self._priority_score(msg, emo),"state":"pending"}
            self.queue.append(t)
            if len(self.queue) > self.limits["queue"]:
                self.queue.pop(0)

    # ============================================================
    # PRIORITY SCORING
    # ============================================================
    def _priority_score(self, msg, emo):
        m = emo["m"]
        st = emo["st"]
        e = emo["e"]
        base = 0.5
        if "now" in msg.lower():
            base += 0.3
        score = base + (abs(m)*0.2) + (st*0.1) + (e*0.05)
        return max(0.1, min(1.0, score))

    # ============================================================
    # TASK SELECTION
    # ============================================================
    def _select_task(self, emo, mem, know):
        if self.active and self.active["state"] == "running":
            return
        if not self.queue:
            self.active = None
            return
        self.queue.sort(key=lambda x: x["prio"], reverse=True)
        self.active = self.queue.pop(0)
        self.active["state"] = "running"

    # ============================================================
    # TASK EXECUTION
    # ============================================================
    def _execute_task(self, emo, mem, know):
        if not self.active:
            return
        cmd = self.active["cmd"].lower()
        if "explain" in cmd:
            self.active["result"] = self._task_explain(cmd, know)
        elif "find" in cmd:
            self.active["result"] = self._task_find(cmd, mem, know)
        elif "help" in cmd:
            self.active["result"] = self._task_help(cmd, emo)
        else:
            self.active["result"] = "ack"
        self.active["state"] = "done"
        self.history.append(self.active)
        if len(self.history) > self.limits["history"]:
            self.history.pop(0)
        self.active = None

    # ============================================================
    # TASK TYPES
    # ============================================================
    def _task_explain(self, cmd, know):
        tokens = cmd.split()
        if len(tokens) < 2:
            return "explain: insufficient input"
        target = tokens[-1]
        if target in know.graph:
            return f"explain: {target} ({know.graph[target]['count']})"
        return "explain: unknown"

    def _task_find(self, cmd, mem, know):
        tokens = cmd.split()
        if len(tokens) < 2:
            return "find: insufficient input"
        target = tokens[-1]
        if target in know.freq:
            return f"find: {target} ({know.freq[target]})"
        return "find: none"

    def _task_help(self, cmd, emo):
        m = emo["m"]
        if m < -0.3:
            return "help: stabilizing"
        if m > 0.3:
            return "help: encouraging"
        return "help: neutral"

    # ============================================================
    # META-ADJUSTMENT
    # ============================================================
    def _meta_adjust(self, emo):
        m = emo["m"]
        st = emo["st"]
        e = emo["e"]
        self.meta["load"] = min(1.0, len(self.queue)/self.limits["queue"])
        self.meta["drift"] = max(0, min(1, self.meta["drift"] + (st - 0.5)*0.01))
        self.meta["bias"] = max(0, min(1, self.meta["bias"] + m*0.005))

    # ============================================================
    # SNAPSHOT
    # ============================================================
    def _snapshot(self):
        return {
            "queue": len(self.queue),
            "active": self.active["cmd"] if self.active else None,
            "history": len(self.history),
            "meta": self.meta
        }
