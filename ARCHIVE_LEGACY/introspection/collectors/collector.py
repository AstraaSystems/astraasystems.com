"""
Collector Wrapper
-----------------
Provides a simple interface for collecting system snapshots.
"""

from ..system_introspection import SystemIntrospection


class Collector:
    def __init__(self):
        self.engine = SystemIntrospection()

    def collect(self):
        return self.engine.system_overview()
