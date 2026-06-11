#!/usr/bin/env python3
#===============================================================================
#  ARDHANARISHVARA OS KERNEL MODULE
#  SovereignOS Package Manager Engine — Repos, Dependencies, Install & Rollback
#  File: package_manager_engine.py
#===============================================================================

import time
import uuid
from typing import Dict, Any, List, Optional

class PackageManagerEngine:
    """
    Provides:
      • package repository registry
      • package metadata + versioning
      • dependency resolution
      • installation + removal
      • rollback snapshots
      • signature verification (via crypto engine)
    """

    def __init__(self, crypto_engine=None):
        self.repos: Dict[str, Dict[str, Any]] = {}
        self.installed: Dict[str, Dict[str, Any]] = {}
        self.snapshots: Dict[str, Dict[str, Any]] = {}
        self.crypto = crypto_engine
        self.telemetry: Dict[str, Any] = {
            "packages_installed": 0,
            "packages_removed": 0,
            "repos_added": 0,
            "errors": 0
        }

    #---------------------------------------------------------------------------
    #  ADD REPOSITORY
    #---------------------------------------------------------------------------
    def add_repo(self, name: str, url: str, packages: Dict[str, Any]) -> Dict[str, Any]:
        rid = f"REP-{uuid.uuid4().hex[:10].upper()}"
        self.repos[name] = {
            "id": rid,
            "name": name,
            "url": url,
            "packages": packages,
            "timestamp": time.time()
        }
        self.telemetry["repos_added"] += 1
        return self.repos[name]

    #---------------------------------------------------------------------------
    #  FETCH PACKAGE METADATA
    #---------------------------------------------------------------------------
    def metadata(self, repo: str, package: str) -> Optional[Dict[str, Any]]:
        if repo not in self.repos:
            return None
        return self.repos[repo]["packages"].get(package)

    #---------------------------------------------------------------------------
    #  VERIFY PACKAGE SIGNATURE
    #---------------------------------------------------------------------------
    def _verify_signature(self, pkg: Dict[str, Any]) -> bool:
        if not self.crypto:
            return True
        sig = pkg.get("signature")
        data = pkg.get("data", b"")
        key = pkg.get("key")
        if not sig or not key:
            return False
        return self.crypto.verify_hmac(key, data, sig)

    #---------------------------------------------------------------------------
    #  RESOLVE DEPENDENCIES
    #---------------------------------------------------------------------------
    def _resolve(self, repo: str, package: str) -> List[str]:
        meta = self.metadata(repo, package)
        if not meta:
            return []
        deps = meta.get("depends", [])
        resolved = []
        for d in deps:
            resolved.extend(self._resolve(repo, d))
            resolved.append(d)
        return list(dict.fromkeys(resolved))

    #---------------------------------------------------------------------------
    #  INSTALL PACKAGE
    #---------------------------------------------------------------------------
    def install(self, repo: str, package: str) -> Dict[str, Any]:
        meta = self.metadata(repo, package)
        if not meta:
            self.telemetry["errors"] += 1
            return {
                "install_id": f"PKG-{uuid.uuid4().hex[:10].upper()}",
                "status": "unknown_package",
                "timestamp": time.time()
            }

        if not self._verify_signature(meta):
            self.telemetry["errors"] += 1
            return {
                "install_id": f"PKG-{uuid.uuid4().hex[:10].upper()}",
                "status": "signature_invalid",
                "timestamp": time.time()
            }

        deps = self._resolve(repo, package)
        for d in deps:
            if d not in self.installed:
                self.installed[d] = {
                    "name": d,
                    "version": self.metadata(repo, d)["version"],
                    "timestamp": time.time()
                }

        self.installed[package] = {
            "name": package,
            "version": meta["version"],
            "timestamp": time.time()
        }

        self.telemetry["packages_installed"] += 1

        return {
            "install_id": f"PKG-{uuid.uuid4().hex[:10].upper()}",
            "status": "installed",
            "package": package,
            "dependencies": deps,
            "timestamp": time.time()
        }

    #---------------------------------------------------------------------------
    #  REMOVE PACKAGE
    #---------------------------------------------------------------------------
    def remove(self, package: str) -> Dict[str, Any]:
        if package not in self.installed:
            self.telemetry["errors"] += 1
            return {
                "remove_id": f"RMV-{uuid.uuid4().hex[:10].upper()}",
                "status": "not_installed",
                "timestamp": time.time()
            }

        del self.installed[package]
        self.telemetry["packages_removed"] += 1

        return {
            "remove_id": f"RMV-{uuid.uuid4().hex[:10].upper()}",
            "status": "removed",
            "package": package,
            "timestamp": time.time()
        }

    #---------------------------------------------------------------------------
    #  SNAPSHOT FOR ROLLBACK
    #---------------------------------------------------------------------------
    def snapshot(self) -> Dict[str, Any]:
        sid = f"SNP-{uuid.uuid4().hex[:10].upper()}"
        snap = {
            "id": sid,
            "timestamp": time.time(),
            "installed": self.installed.copy()
        }
        self.snapshots[sid] = snap
        return snap

    #---------------------------------------------------------------------------
    #  ROLLBACK
    #---------------------------------------------------------------------------
    def rollback(self, snapshot_id: str) -> Dict[str, Any]:
        if snapshot_id not in self.snapshots:
            self.telemetry["errors"] += 1
            return {
                "rollback_id": f"RLB-{uuid.uuid4().hex[:10].upper()}",
                "status": "unknown_snapshot",
                "timestamp": time.time()
            }

        snap = self.snapshots[snapshot_id]
        self.installed = snap["installed"].copy()

        return {
            "rollback_id": f"RLB-{uuid.uuid4().hex[:10].upper()}",
            "status": "restored",
            "snapshot": snapshot_id,
            "timestamp": time.time()
        }

#===============================================================================
#  END OF FILE — package_manager_engine.py
#===============================================================================
