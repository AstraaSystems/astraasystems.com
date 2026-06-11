from .system_introspection import SystemIntrospection
from .collectors.collector import Collector

# Global introspection engine
introspect = SystemIntrospection()
collector = Collector()

__all__ = ["introspect", "collector", "SystemIntrospection"]
