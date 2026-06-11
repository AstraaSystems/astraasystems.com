#!/usr/bin/env python3
#===============================================================================
#  ARDHANARISHVARA OS KERNEL MODULE
#  SovereignOS Package Manager — Registry, Dependency Resolver & Installer Core
#  File: package_manager.py
#===============================================================================

import time
import uuid
import hashlib
from typing import Dict, Any, List, Optional

class PackageManager:
    """
    Provides:
      • package registry
      • dependency resolution
      • installation & removal
      • integrity verification
      • version comparison
      • kernel-level package orchestration
    """

    def __init__(self):
        self.registry: Dict[str, Dict[str, Any]] = {}
        self.installed: Dict[str, Dict[str, Any]] = {}

    #---------------------------------------------------------------------------
    #  REGISTER PACKAGE
    #---------------------------------------------------------------------------
    def register(self, manifest: Dict[str, Any]) -> Dict[str, Any]:
        pkg_id = manifest.get("id")
        if not pkg_id:
            return {
                "pkg_id": None,
                "status": "invalid_manifest",
                "timestamp": time.time()
            }

        self.registry[pkg_id] = manifest

        return {
            "pkg_id": pkg_id,
            "status": "registered",
            "timestamp": time.time()
        }

    #---------------------------------------------------------------------------
    #  VERSION COMPARISON
    #---------------------------------------------------------------------------
    def _version_tuple(self, v: str):
        return tuple(int(x) for x in v.split("."))

    def newer(self, v1: str, v2: str) -> bool:
        return self._version_tuple(v1) > self._version_tuple(v2)

    #---------------------------------------------------------------------------
    #  DEPENDENCY RESOLUTION
    #---------------------------------------------------------------------------
    def resolve(self, pkg_id: str) -> List[str]:
        if pkg_id not in self.registry:
            return []

        deps = self.registry[pkg_id].get("dependencies", [])
        resolved = []

        for d in deps:
            resolved.extend(self.resolve(d))
            resolved.append(d)

        return list(dict.fromkeys(resolved))

    #---------------------------------------------------------------------------
    #  INTEGRITY CHECK
    #---------------------------------------------------------------------------
    def verify(self, pkg_id: str, data: bytes) -> bool:
        manifest = self.registry.get(pkg_id)
        if not manifest:
            return False

        expected = manifest.get("checksum")
        if not expected:
            return False

        actual = hashlib.sha256(data).hexdigest()
        return actual == expected

    #---------------------------------------------------------------------------
    #  INSTALL PACKAGE
    #---------------------------------------------------------------------------
    def install(self, pkg_id: str, data: bytes) -> Dict[str, Any]:
        if pkg_id not in self.registry:
            return {
                "install_id": f"PKG-{uuid.uuid4().hex[:10].upper()}",
                "status": "unknown_package",
                "timestamp": time.time()
            }

        if not self.verify(pkg_id, data):
            return {
                "install_id": f"PKG-{uuid.uuid4().hex[:10].upper()}",
                "status": "integrity_failed",
                "timestamp": time.time()
            }

        deps = self.resolve(pkg_id)
        for d in deps:
            if d not in self.installed:
                self.installed[d] = {
                    "id": d,
                    "version": self.registry[d]["version"],
                    "timestamp": time.time()
                }

        self.installed[pkg_id] = {
            "id": pkg_id,
            "version": self.registry[pkg_id]["version"],
            "timestamp": time.time()
        }

        return {
            "install_id": f"PKG-{uuid.uuid4().hex[:10].upper()}",
            "status": "installed",
            "package": pkg_id,
            "dependencies": deps,
            "timestamp": time.time()
        }

    #---------------------------------------------------------------------------
    #  REMOVE PACKAGE
    #---------------------------------------------------------------------------
    def remove(self, pkg_id: str) -> Dict[str, Any]:
        if pkg_id not in self.installed:
            return {
                "remove_id": f"RMV-{uuid.uuid4().hex[:10].upper()}",
                "status": "not_installed",
                "timestamp": time.time()
            }

        del self.installed[pkg_id]

        return {
            "remove_id": f"RMV-{uuid.uuid4().hex[:10].upper()}",
            "status": "removed",
            "package": pkg_id,
            "timestamp": time.time()
        }

    #---------------------------------------------------------------------------
    #  SNAPSHOT
    #---------------------------------------------------------------------------
    def snapshot(self) -> Dict[str, Any]:
        return {
            "snapshot_id": f"PKS-{uuid.uuid4().hex[:10].upper()}",
            "timestamp": time.time(),
            "installed": self.installed,
            "registry": self.registry
        }

#===============================================================================
#  END OF FILE — package_manager.py
#===============================================================================
