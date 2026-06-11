#!/usr/bin/env python3
#===============================================================================
#  ARDHANARISHVARA OS KERNEL MODULE
#  SovereignOS Interrupt Controller — IRQ Routing, Vector Table & ISR Dispatch
#  File: interrupt_controller.py
#===============================================================================

import time
import uuid
from typing import Dict, Any, Callable, Optional

class InterruptController:
    """
    Provides:
      • interrupt vector table
      • IRQ registration & masking
      • ISR dispatch
      • priority-based interrupt handling
      • kernel-level interrupt telemetry
    """

    def __init__(self):
        self.vector_table: Dict[int, Dict[str, Any]] = {}
        self.masked: Dict[int, bool] = {}
        self.priority: Dict[int, int] = {}
        self.telemetry: Dict[str, Any] = {
            "handled": 0,
            "errors": 0,
            "last_irq": None
        }

    #---------------------------------------------------------------------------
    #  REGISTER INTERRUPT
    #---------------------------------------------------------------------------
    def register_irq(self, irq: int, handler: Callable[..., Any], priority: int = 1):
        self.vector_table[irq] = {
            "irq": irq,
            "handler": handler,
            "priority": priority,
            "timestamp": time.time()
        }
        self.masked[irq] = False
        self.priority[irq] = priority

    #---------------------------------------------------------------------------
    #  MASK INTERRUPT
    #---------------------------------------------------------------------------
    def mask(self, irq: int):
        if irq in self.masked:
            self.masked[irq] = True

    #---------------------------------------------------------------------------
    #  UNMASK INTERRUPT
    #---------------------------------------------------------------------------
    def unmask(self, irq: int):
        if irq in self.masked:
            self.masked[irq] = False

    #---------------------------------------------------------------------------
    #  DISPATCH INTERRUPT
    #---------------------------------------------------------------------------
    async def dispatch(self, irq: int, payload: Dict[str, Any]) -> Dict[str, Any]:
        if irq not in self.vector_table:
            self.telemetry["errors"] += 1
            return {
                "irq_id": f"IRQ-{uuid.uuid4().hex[:10].upper()}",
                "status": "unknown_irq",
                "timestamp": time.time()
            }

        if self.masked.get(irq, False):
            return {
                "irq_id": f"IRQ-{uuid.uuid4().hex[:10].upper()}",
                "status": "masked",
                "timestamp": time.time()
            }

        entry = self.vector_table[irq]
        handler = entry["handler"]

        try:
            result = await handler(payload)
            self.telemetry["handled"] += 1
            self.telemetry["last_irq"] = irq

            return {
                "irq_id": f"IRQ-{uuid.uuid4().hex[:10].upper()}",
                "status": "handled",
                "irq": irq,
                "result": result,
                "timestamp": time.time()
            }

        except Exception as e:
            self.telemetry["errors"] += 1
            return {
                "irq_id": f"IRQ-{uuid.uuid4().hex[:10].upper()}",
                "status": "handler_error",
                "irq": irq,
                "error": str(e),
                "timestamp": time.time()
            }

    #---------------------------------------------------------------------------
    #  GET HIGHEST PRIORITY IRQ
    #---------------------------------------------------------------------------
    def highest_priority_irq(self) -> Optional[int]:
        if not self.vector_table:
            return None
        return max(self.vector_table.keys(), key=lambda irq: self.priority.get(irq, 0))

    #---------------------------------------------------------------------------
    #  INTERRUPT SNAPSHOT
    #---------------------------------------------------------------------------
    def snapshot(self) -> Dict[str, Any]:
        return {
            "snapshot_id": f"INT-{uuid.uuid4().hex[:10].upper()}",
            "timestamp": time.time(),
            "vector_table": self.vector_table,
            "masked": self.masked,
            "priority": self.priority,
            "telemetry": self.telemetry
        }

#===============================================================================
#  END OF FILE — interrupt_controller.py
#===============================================================================
