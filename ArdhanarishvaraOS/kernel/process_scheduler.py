#!/usr/bin/env python3
#===============================================================================
#  ARDHANARISHVARA OS KERNEL MODULE
#  SovereignOS Process Scheduler — Task Queue, Priority Engine & Time Slice Core
#  File: process_scheduler.py
#===============================================================================

import time
import uuid
import asyncio
from typing import Dict, Any, Optional, Callable, List

class ProcessScheduler:
    """
    Provides:
      • process registration
      • priority-based scheduling
      • round-robin time slicing
      • async task execution
      • kernel-level process state tracking
    """

    def __init__(self):
        self.processes: Dict[str, Dict[str, Any]] = {}
        self.ready_queue: List[str] = []
        self.running: Optional[str] = None
        self.time_slice = 0.05  # 50ms default slice

    #---------------------------------------------------------------------------
    #  REGISTER PROCESS
    #---------------------------------------------------------------------------
    def register(self, name: str, priority: int, handler: Callable[..., Any]):
        pid = f"PRC-{uuid.uuid4().hex[:10].upper()}"
        self.processes[pid] = {
            "id": pid,
            "name": name,
            "priority": priority,
            "handler": handler,
            "state": "ready",
            "last_run": None,
            "created": time.time()
        }
        self.ready_queue.append(pid)
        self.ready_queue.sort(key=lambda p: self.processes[p]["priority"], reverse=True)
        return pid

    #---------------------------------------------------------------------------
    #  SCHEDULE NEXT PROCESS
    #---------------------------------------------------------------------------
    def _next_process(self) -> Optional[str]:
        if not self.ready_queue:
            return None
        return self.ready_queue.pop(0)

    #---------------------------------------------------------------------------
    #  RUN SCHEDULER LOOP
    #---------------------------------------------------------------------------
    async def run(self):
        while True:
            pid = self._next_process()
            if not pid:
                await asyncio.sleep(0.01)
                continue

            proc = self.processes[pid]
            self.running = pid
            proc["state"] = "running"
            proc["last_run"] = time.time()

            try:
                task = asyncio.create_task(proc["handler"]())
                await asyncio.wait_for(task, timeout=self.time_slice)
            except asyncio.TimeoutError:
                proc["state"] = "ready"
                self.ready_queue.append(pid)
                self.ready_queue.sort(key=lambda p: self.processes[p]["priority"], reverse=True)
            except Exception as e:
                proc["state"] = "error"
                proc["error"] = str(e)
            finally:
                self.running = None

    #---------------------------------------------------------------------------
    #  KILL PROCESS
    #---------------------------------------------------------------------------
    def kill(self, pid: str) -> Dict[str, Any]:
        if pid not in self.processes:
            return {
                "kill_id": f"KIL-{uuid.uuid4().hex[:10].upper()}",
                "status": "unknown_process",
                "timestamp": time.time()
            }

        if pid in self.ready_queue:
            self.ready_queue.remove(pid)

        del self.processes[pid]

        return {
            "kill_id": f"KIL-{uuid.uuid4().hex[:10].upper()}",
            "status": "terminated",
            "process": pid,
            "timestamp": time.time()
        }

    #---------------------------------------------------------------------------
    #  SNAPSHOT
    #---------------------------------------------------------------------------
    def snapshot(self) -> Dict[str, Any]:
        return {
            "snapshot_id": f"PSC-{uuid.uuid4().hex[:10].upper()}",
            "timestamp": time.time(),
            "running": self.running,
            "ready_queue": self.ready_queue,
            "processes": self.processes
        }

#===============================================================================
#  END OF FILE — process_scheduler.py
#===============================================================================
