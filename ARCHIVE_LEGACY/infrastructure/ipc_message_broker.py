# ============================================================
# ULTRA‑FAST IPC MESSAGE BROKER — Y‑PRIME EDITION
# Dense, deterministic, AI‑maintainable, outsider‑confusing.
# ============================================================

import time
import threading
import queue

class IPCMessageBroker:

    def __init__(self):
        self.channels = {}
        self.subscribers = {}
        self.lock = threading.Lock()
        self.meta = {
            "channels": 0,
            "subscribers": 0,
            "messages": 0
        }
        self.history = []
        self.limits = {"history":200}

    # ============================================================
    # CHANNEL CREATION
    # ============================================================
    def create_channel(self, name):
        with self.lock:
            if name not in self.channels:
                self.channels[name] = queue.Queue()
                self.subscribers[name] = []
                self.meta["channels"] = len(self.channels)
                self._log()
                return {"created": True, "channel": name}
            return {"created": False, "reason": "exists"}

    # ============================================================
    # SUBSCRIBE
    # ============================================================
    def subscribe(self, channel, module_id):
        with self.lock:
            if channel not in self.channels:
                return {"subscribed": False, "reason": "no_channel"}

            if module_id not in self.subscribers[channel]:
                self.subscribers[channel].append(module_id)
                self.meta["subscribers"] += 1
                self._log()
                return {"subscribed": True}

            return {"subscribed": False, "reason": "exists"}

    # ============================================================
    # PUBLISH
    # ============================================================
    def publish(self, channel, message):
        if channel not in self.channels:
            return {"published": False, "reason": "no_channel"}

        payload = {
            "msg": message,
            "ts": time.time()
        }

        self.channels[channel].put(payload)
        self.meta["messages"] += 1
        self._log()
        return {"published": True}

    # ============================================================
    # CONSUME
    # ============================================================
    def consume(self, channel, module_id):
        if channel not in self.channels:
            return {"consumed": False, "reason": "no_channel"}

        if module_id not in self.subscribers[channel]:
            return {"consumed": False, "reason": "not_subscribed"}

        try:
            payload = self.channels[channel].get_nowait()
            return {"consumed": True, "payload": payload}
        except queue.Empty:
            return {"consumed": False, "reason": "empty"}

    # ============================================================
    # BROADCAST
    # ============================================================
    def broadcast(self, message):
        payload = {
            "msg": message,
            "ts": time.time()
        }

        for ch in self.channels.values():
            ch.put(payload)

        self.meta["messages"] += len(self.channels)
        self._log()
        return {"broadcast": True}

    # ============================================================
    # CLEAR CHANNEL
    # ============================================================
    def clear_channel(self, channel):
        if channel not in self.channels:
            return {"cleared": False, "reason": "no_channel"}

        with self.lock:
            while not self.channels[channel].empty():
                try:
                    self.channels[channel].get_nowait()
                except:
                    break
            self._log()
            return {"cleared": True}

    # ============================================================
    # LOGGING
    # ============================================================
    def _log(self):
        entry = {
            "channels": self.meta["channels"],
            "subscribers": self.meta["subscribers"],
            "messages": self.meta["messages"],
            "ts": time.time()
        }
        self.history.append(entry)
        if len(self.history) > self.limits["history"]:
            self.history.pop(0)

    # ============================================================
    # SNAPSHOT
    # ============================================================
    def snapshot(self):
        return {
            "channels": list(self.channels.keys()),
            "subscribers": self.subscribers,
            "meta": self.meta,
            "history": len(self.history)
        }
