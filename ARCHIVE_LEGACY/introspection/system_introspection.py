"""
ARKA System Introspection Engine
--------------------------------
Provides system-level diagnostics and telemetry for:
- ARKA Core
- Astra
- Aruhan
- Multi-agent coordination

Collects:
- CPU usage
- Memory usage
- Disk usage
- Process info
- ARKA health
"""

import psutil
import platform
from datetime import datetime
from .utils.snapshot import Snapshot


class SystemIntrospection:
    def __init__(self):
        pass

    def system_overview(self):
        return Snapshot(
            timestamp=datetime.utcnow().isoformat() + "Z",
            cpu=self.cpu_usage(),
            memory=self.memory_usage(),
            disk=self.disk_usage(),
            process=self.process_info(),
            platform=self.platform_info(),
            health=self.health_status()
        ).to_dict()

    # -----------------------------
    # CPU
    # -----------------------------
    def cpu_usage(self):
        return {
            "percent": psutil.cpu_percent(interval=0.2),
            "cores": psutil.cpu_count(logical=True),
            "physical_cores": psutil.cpu_count(logical=False)
        }

    # -----------------------------
    # Memory
    # -----------------------------
    def memory_usage(self):
        mem = psutil.virtual_memory()
        return {
            "total": mem.total,
            "available": mem.available,
            "used": mem.used,
            "percent": mem.percent
        }

    # -----------------------------
    # Disk
    # -----------------------------
    def disk_usage(self):
        disk = psutil.disk_usage("/")
        return {
            "total": disk.total,
            "used": disk.used,
            "free": disk.free,
            "percent": disk.percent
        }

    # -----------------------------
    # Process Info
    # -----------------------------
    def process_info(self):
        p = psutil.Process()
        return {
            "pid": p.pid,
            "cpu_percent": p.cpu_percent(interval=0.1),
            "memory_percent": p.memory_percent(),
            "threads": p.num_threads()
        }

    # -----------------------------
    # Platform Info
    # -----------------------------
    def platform_info(self):
        return {
            "system": platform.system(),
            "release": platform.release(),
            "version": platform.version(),
            "machine": platform.machine(),
            "processor": platform.processor()
        }

    # -----------------------------
    # Health Status
    # -----------------------------
    def health_status(self):
        cpu = psutil.cpu_percent(interval=0.1)
        mem = psutil.virtual_memory().percent

        if cpu < 80 and mem < 80:
            return "healthy"
        elif cpu < 95 and mem < 95:
            return "degraded"
        else:
            return "critical"
