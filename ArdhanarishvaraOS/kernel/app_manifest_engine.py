#!/usr/bin/env python3
#===============================================================================
#  ARDHANARISHVARA OS KERNEL MODULE
#  App Manifest Engine — SovereignOS Application Metadata, Permissions & Schema
#  File: app_manifest_engine.py
#===============================================================================

import time
import uuid
import json
from typing import Dict, Any, Optional

class AppManifestEngine:
    """
    Provides:
      • manifest validation
      • permission schema enforcement
      • metadata parsing
      • versioning & capability checks
      • kernel-level app registration
    """

    def __init__(self):
        self.manifests: Dict[str, Dict[str, Any]] = {}
        self.schema = {
            "id": str,
            "name": str,
            "version": str,
            "entrypoint": str,
            "permissions": list,
            "capabilities": list,
            "metadata": dict
        }

    #---------------------------------------------------------------------------
    #  VALIDATE MANIFEST
    #---------------------------------------------------------------------------
    def validate(self, manifest: Dict[str, Any]) -> bool:
        for key, t in self.schema.items():
            if key not in manifest:
                return False
            if not isinstance(manifest[key], t):
                return False
        return True

    #---------------------------------------------------------------------------
    #  REGISTER MANIFEST
    #---------------------------------------------------------------------------
    def register(self, manifest: Dict[str, Any]) -> Dict[str, Any]:
        if not self.validate(manifest):
            return {
                "manifest_id": f"MNF-{uuid.uuid4().hex[:10].upper()}",
                "status": "invalid_manifest",
                "timestamp": time.time()
            }

        app_id = manifest["id"]
        self.manifests[app_id] = manifest

        return {
            "manifest_id": f"MNF-{uuid.uuid4().hex[:10].upper()}",
            "status": "registered",
            "app_id": app_id,
            "timestamp": time.time()
        }

    #---------------------------------------------------------------------------
    #  GET MANIFEST
    #---------------------------------------------------------------------------
    def get(self, app_id: str) -> Optional[Dict[str, Any]]:
        return self.manifests.get(app_id)

    #---------------------------------------------------------------------------
    #  LIST ALL MANIFESTS
    #---------------------------------------------------------------------------
    def list(self) -> Dict[str, Dict[str, Any]]:
        return self.manifests

    #---------------------------------------------------------------------------
    #  CHECK PERMISSIONS
    #---------------------------------------------------------------------------
    def check_permission(self, app_id: str, permission: str) -> bool:
        m = self.manifests.get(app_id)
        if not m:
            return False
        return permission in m.get("permissions", [])

    #---------------------------------------------------------------------------
    #  EXPORT MANIFEST
    #---------------------------------------------------------------------------
    def export(self, app_id: str) -> Dict[str, Any]:
        m = self.manifests.get(app_id)
        if not m:
            return {}

        return {
            "export_id": f"EXP-{uuid.uuid4().hex[:10].upper()}",
            "timestamp": time.time(),
            "manifest": json.dumps(m)
        }

#===============================================================================
#  END OF FILE — app_manifest_engine.py
#===============================================================================
