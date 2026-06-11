#!/usr/bin/env python3
#===============================================================================
#  ARDHANARISHVARA OS KERNEL MODULE
#  SovereignOS Kernel Panic Handler — Crash Capture, Stack Trace & Safe Mode
#  File: kernel_panic_handler.py
#===============================================================================

import time
import uuid
import traceback
from typing import Dict, Any, Optional

class KernelPanicHandler:
    """
    Provides:
      • panic event capture
      • stack trace extraction
      • subsystem fault metadata
      • crash signature generation
      • safe-mode escalation
      • persistent panic log registry
    """

    def __init__(self):
        self.panics: Dict[str, Dict[str, Any]] = {}
        self.last_panic: Optional[str] = None
        self.safe_mode = False

    #---------------------------------------------------------------------------
    #  TRIGGER PANIC
    #---------------------------------------------------------------------------
    def panic(self, subsystem: str, message: str, meta: Dict[str, Any]) -> Dict[str, Any]:
        pid = f"PNC-{uuid.uuid4().hex[:10].upper()}"
        trace = traceback.format_stack()

        entry = {
            "id": pid,
            "subsystem": subsystem,
            "message": message,
            "meta": meta,
            "stack": trace,
            "timestamp": time.time(),
            "signature": self._signature(subsystem, message)
        }

        self.panics[pid] = entry
        self.last_panic = pid
        self.safe_mode = True

        return {
            "panic_id": pid,
            "status": "captured",
            "safe_mode": True,
            "timestamp": time.time()
        }

    #---------------------------------------------------------------------------
    #  INTERNAL: GENERATE CRASH SIGNATURE
    #---------------------------------------------------------------------------
    def _signature(self, subsystem: str, message: str) -> str:
        raw = f"{subsystem}:{message}:{time.time()}"
        return uuid.uuid5(uuid.NAMESPACE_DNS, raw).hex.upper()

    #---------------------------------------------------------------------------
    #  CLEAR PANIC STATE
    #---------------------------------------------------------------------------
    def clear(self) -> Dict[str, Any]:
        self.safe_mode = False
        return {
            "clear_id": f"CLR-{uuid.uuid4().hex[:10].upper()}",
            "status": "cleared",
            "timestamp": time.time()
        }

    #---------------------------------------------------------------------------
    #  GET LAST PANIC
    #---------------------------------------------------------------------------
    def last(self) -> Optional[Dict[str, Any]]:
        if not self.last_panic:
            return None
        return self.panics.get(self.last_panic)

    #---------------------------------------------------------------------------
    #  SNAPSHOT
    #---------------------------------------------------------------------------
    def snapshot(self) -> Dict[str, Any]:
        return {
            "snapshot_id": f"PAN-{uuid.uuid4().hex[:10].upper()}",
            "timestamp": time.time(),
            "safe_mode": self.safe_mode,
            "last_panic": self.last_panic,
            "panic_count": len(self.panics)
        }

#===============================================================================
#  END OF FILE — kernel_panic_handler.py
#===============================================================================
