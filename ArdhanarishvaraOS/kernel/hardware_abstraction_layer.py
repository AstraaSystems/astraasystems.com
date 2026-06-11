#!/usr/bin/env python3
#===============================================================================
#  ARDHANARISHVARA OS KERNEL MODULE
#  SovereignOS Hardware Abstraction Layer — Device Registry, Drivers & IO Core
#  File: hardware_abstraction_layer.py
#===============================================================================

import time
import uuid
from typing import Dict, Any, Optional, Callable

class HardwareAbstractionLayer:
    """
    Provides:
      • device registration
      • driver binding
      • hardware capability mapping
      • IO request dispatch
      • kernel-level hardware event routing
    """

    def __init__(self):
        self.devices: Dict[str, Dict[str, Any]] = {}
        self.drivers: Dict[str, Dict[str, Any]] = {}
        self.io_handlers: Dict[str, Callable[..., Any]] = {}

    #---------------------------------------------------------------------------
    #  REGISTER DEVICE
    #---------------------------------------------------------------------------
    def register_device(self, name: str, type: str, capabilities: Dict[str, Any]):
        did = f"DEV-{uuid.uuid4().hex[:10].upper()}"
        self.devices[did] = {
            "id": did,
            "name": name,
            "type": type,
            "capabilities": capabilities,
            "driver": None,
            "timestamp": time.time()
        }
        return did

    #---------------------------------------------------------------------------
    #  REGISTER DRIVER
    #---------------------------------------------------------------------------
    def register_driver(self, name: str, device_type: str, handler: Callable[..., Any]):
        self.drivers[name] = {
            "name": name,
            "device_type": device_type,
            "handler": handler,
            "timestamp": time.time()
        }

    #---------------------------------------------------------------------------
    #  BIND DRIVER TO DEVICE
    #---------------------------------------------------------------------------
    def bind(self, device_id: str, driver_name: str) -> Dict[str, Any]:
        if device_id not in self.devices:
            return {
                "bind_id": f"HAL-{uuid.uuid4().hex[:10].upper()}",
                "status": "unknown_device",
                "timestamp": time.time()
            }

        if driver_name not in self.drivers:
            return {
                "bind_id": f"HAL-{uuid.uuid4().hex[:10].upper()}",
                "status": "unknown_driver",
                "timestamp": time.time()
            }

        dev = self.devices[device_id]
        drv = self.drivers[driver_name]

        if dev["type"] != drv["device_type"]:
            return {
                "bind_id": f"HAL-{uuid.uuid4().hex[:10].upper()}",
                "status": "type_mismatch",
                "timestamp": time.time()
            }

        dev["driver"] = driver_name
        return {
            "bind_id": f"HAL-{uuid.uuid4().hex[:10].upper()}",
            "status": "bound",
            "device": device_id,
            "driver": driver_name,
            "timestamp": time.time()
        }

    #---------------------------------------------------------------------------
    #  REGISTER IO HANDLER
    #---------------------------------------------------------------------------
    def register_io(self, device_type: str, handler: Callable[..., Any]):
        self.io_handlers[device_type] = handler

    #---------------------------------------------------------------------------
    #  IO REQUEST
    #---------------------------------------------------------------------------
    async def io(self, device_id: str, payload: Dict[str, Any]) -> Dict[str, Any]:
        if device_id not in self.devices:
            return {
                "io_id": f"IO-{uuid.uuid4().hex[:10].upper()}",
                "status": "unknown_device",
                "timestamp": time.time()
            }

        dev = self.devices[device_id]
        dtype = dev["type"]

        if dtype not in self.io_handlers:
            return {
                "io_id": f"IO-{uuid.uuid4().hex[:10].upper()}",
                "status": "no_handler",
                "timestamp": time.time()
            }

        try:
            result = await self.io_handlers[dtype](payload)
            return {
                "io_id": f"IO-{uuid.uuid4().hex[:10].upper()}",
                "status": "ok",
                "device": device_id,
                "result": result,
                "timestamp": time.time()
            }
        except Exception as e:
            return {
                "io_id": f"IO-{uuid.uuid4().hex[:10].upper()}",
                "status": "io_error",
                "device": device_id,
                "error": str(e),
                "timestamp": time.time()
            }

    #---------------------------------------------------------------------------
    #  HAL SNAPSHOT
    #---------------------------------------------------------------------------
    def snapshot(self) -> Dict[str, Any]:
        return {
            "snapshot_id": f"HAL-{uuid.uuid4().hex[:10].upper()}",
            "timestamp": time.time(),
            "devices": self.devices,
            "drivers": self.drivers,
            "io_handlers": list(self.io_handlers.keys())
        }

#===============================================================================
#  END OF FILE — hardware_abstraction_layer.py
#===============================================================================
