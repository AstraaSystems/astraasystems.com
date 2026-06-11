#!/usr/bin/env python3
#===============================================================================
#  ARDHANARISHVARA OS KERNEL MODULE
#  SovereignOS Identity & Access Engine — Auth, Roles, Permissions & Sessions
#  File: identity_access_engine.py
#===============================================================================

import time
import uuid
from typing import Dict, Any, Optional, List

class IdentityAccessEngine:
    """
    Provides:
      • identity registry (users, services, nodes)
      • authentication tokens
      • role-based access control (RBAC)
      • permission evaluation
      • session lifecycle
      • audit logging
    """

    def __init__(self, crypto_engine=None):
        self.identities: Dict[str, Dict[str, Any]] = {}
        self.roles: Dict[str, Dict[str, Any]] = {}
        self.sessions: Dict[str, Dict[str, Any]] = {}
        self.audit: Dict[str, Dict[str, Any]] = {}
        self.crypto = crypto_engine
        self.telemetry: Dict[str, Any] = {
            "identities_created": 0,
            "sessions_created": 0,
            "sessions_ended": 0,
            "auth_failures": 0,
            "access_denied": 0
        }

    #---------------------------------------------------------------------------
    #  CREATE IDENTITY
    #---------------------------------------------------------------------------
    def create_identity(self, name: str, secret: bytes, roles: List[str]) -> Dict[str, Any]:
        iid = f"ID-{uuid.uuid4().hex[:10].upper()}"
        self.identities[iid] = {
            "id": iid,
            "name": name,
            "secret": secret,
            "roles": roles,
            "created": time.time()
        }
        self.telemetry["identities_created"] += 1
        return self.identities[iid]

    #---------------------------------------------------------------------------
    #  DEFINE ROLE
    #---------------------------------------------------------------------------
    def define_role(self, name: str, permissions: List[str]):
        self.roles[name] = {
            "name": name,
            "permissions": permissions,
            "timestamp": time.time()
        }

    #---------------------------------------------------------------------------
    #  AUTHENTICATE
    #---------------------------------------------------------------------------
    def authenticate(self, identity_id: str, secret: bytes) -> Dict[str, Any]:
        if identity_id not in self.identities:
            self.telemetry["auth_failures"] += 1
            return {
                "auth_id": f"AUTH-{uuid.uuid4().hex[:10].upper()}",
                "status": "unknown_identity",
                "timestamp": time.time()
            }

        ident = self.identities[identity_id]

        if ident["secret"] != secret:
            self.telemetry["auth_failures"] += 1
            return {
                "auth_id": f"AUTH-{uuid.uuid4().hex[:10].upper()}",
                "status": "invalid_secret",
                "timestamp": time.time()
            }

        sid = f"SES-{uuid.uuid4().hex[:10].upper()}"
        token = uuid.uuid4().hex

        self.sessions[sid] = {
            "id": sid,
            "identity": identity_id,
            "token": token,
            "created": time.time(),
            "expires": time.time() + 3600
        }

        self.telemetry["sessions_created"] += 1

        return {
            "auth_id": f"AUTH-{uuid.uuid4().hex[:10].upper()}",
            "status": "authenticated",
            "session": sid,
            "token": token,
            "timestamp": time.time()
        }

    #---------------------------------------------------------------------------
    #  VALIDATE SESSION
    #---------------------------------------------------------------------------
    def validate(self, session_id: str, token: str) -> bool:
        ses = self.sessions.get(session_id)
        if not ses:
            return False
        if ses["token"] != token:
            return False
        if time.time() > ses["expires"]:
            return False
        return True

    #---------------------------------------------------------------------------
    #  CHECK PERMISSION
    #---------------------------------------------------------------------------
    def check(self, session_id: str, token: str, permission: str) -> bool:
        if not self.validate(session_id, token):
            self.telemetry["access_denied"] += 1
            return False

        ses = self.sessions[session_id]
        ident = self.identities[ses["identity"]]

        for role in ident["roles"]:
            perms = self.roles.get(role, {}).get("permissions", [])
            if permission in perms:
                return True

        self.telemetry["access_denied"] += 1
        return False

    #---------------------------------------------------------------------------
    #  END SESSION
    #---------------------------------------------------------------------------
    def end_session(self, session_id: str):
        if session_id in self.sessions:
            del self.sessions[session_id]
            self.telemetry["sessions_ended"] += 1

    #---------------------------------------------------------------------------
    #  AUDIT LOG
    #---------------------------------------------------------------------------
    def log(self, event: str, meta: Dict[str, Any]):
        lid = f"AUD-{uuid.uuid4().hex[:10].upper()}"
        self.audit[lid] = {
            "id": lid,
            "event": event,
            "meta": meta,
            "timestamp": time.time()
        }

    #---------------------------------------------------------------------------
    #  SNAPSHOT
    #---------------------------------------------------------------------------
    def snapshot(self) -> Dict[str, Any]:
        return {
            "snapshot_id": f"IAC-{uuid.uuid4().hex[:10].upper()}",
            "timestamp": time.time(),
            "identities": list(self.identities.keys()),
            "roles": self.roles,
            "sessions": list(self.sessions.keys()),
            "telemetry": self.telemetry
        }

#===============================================================================
#  END OF FILE — identity_access_engine.py
#===============================================================================
