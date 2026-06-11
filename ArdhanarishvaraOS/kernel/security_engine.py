#!/usr/bin/env python3
#===============================================================================
#  ARDHANARISHVARA OS KERNEL MODULE
#  SovereignOS Security Engine — Auth, Crypto, Audit & Threat Model Core
#  File: security_engine.py
#===============================================================================

import time
import uuid
import hashlib
import hmac
import secrets
from typing import Dict, Any, Optional, List

class SecurityEngine:
    """
    Provides:
      • authentication tokens
      • cryptographic hashing & HMAC
      • permission enforcement
      • audit logging
      • threat event classification
    """

    def __init__(self):
        self.tokens: Dict[str, Dict[str, Any]] = {}
        self.audit_log: List[Dict[str, Any]] = []
        self.permissions: Dict[str, List[str]] = {}
        self.threat_levels = ["low", "medium", "high", "critical"]

    #---------------------------------------------------------------------------
    #  GENERATE AUTH TOKEN
    #---------------------------------------------------------------------------
    def generate_token(self, subject: str, ttl: int = 3600) -> str:
        token = secrets.token_hex(32)
        self.tokens[token] = {
            "subject": subject,
            "expires": time.time() + ttl,
            "issued": time.time()
        }
        return token

    #---------------------------------------------------------------------------
    #  VALIDATE TOKEN
    #---------------------------------------------------------------------------
    def validate_token(self, token: str) -> bool:
        if token not in self.tokens:
            return False
        return time.time() < self.tokens[token]["expires"]

    #---------------------------------------------------------------------------
    #  HASH DATA
    #---------------------------------------------------------------------------
    def hash(self, data: bytes) -> str:
        return hashlib.sha256(data).hexdigest()

    #---------------------------------------------------------------------------
    #  HMAC SIGNATURE
    #---------------------------------------------------------------------------
    def sign(self, key: bytes, data: bytes) -> str:
        return hmac.new(key, data, hashlib.sha256).hexdigest()

    #---------------------------------------------------------------------------
    #  REGISTER PERMISSIONS FOR SUBJECT
    #---------------------------------------------------------------------------
    def register_permissions(self, subject: str, perms: List[str]):
        self.permissions[subject] = perms

    #---------------------------------------------------------------------------
    #  CHECK PERMISSION
    #---------------------------------------------------------------------------
    def check_permission(self, subject: str, perm: str) -> bool:
        allowed = self.permissions.get(subject, [])
        return perm in allowed

    #---------------------------------------------------------------------------
    #  AUDIT EVENT
    #---------------------------------------------------------------------------
    def audit(self, subject: str, action: str, meta: Dict[str, Any]):
        entry = {
            "audit_id": f"AUD-{uuid.uuid4().hex[:10].upper()}",
            "subject": subject,
            "action": action,
            "meta": meta,
            "timestamp": time.time()
        }
        self.audit_log.append(entry)

    #---------------------------------------------------------------------------
    #  THREAT CLASSIFICATION
    #---------------------------------------------------------------------------
    def classify_threat(self, event: Dict[str, Any]) -> str:
        score = 0

        if event.get("unauthorized"):
            score += 2
        if event.get("integrity_failure"):
            score += 3
        if event.get("rate_limit_exceeded"):
            score += 1
        if event.get("sandbox_violation"):
            score += 4

        if score >= 6:
            return "critical"
        if score >= 4:
            return "high"
        if score >= 2:
            return "medium"
        return "low"

    #---------------------------------------------------------------------------
    #  SECURITY SNAPSHOT
    #---------------------------------------------------------------------------
    def snapshot(self) -> Dict[str, Any]:
        return {
            "snapshot_id": f"SEC-{uuid.uuid4().hex[:10].upper()}",
            "timestamp": time.time(),
            "tokens": list(self.tokens.keys()),
            "permissions": self.permissions,
            "audit_count": len(self.audit_log)
        }

#===============================================================================
#  END OF FILE — security_engine.py
#===============================================================================
