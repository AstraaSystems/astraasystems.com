#!/usr/bin/env python3
#===============================================================================
#  ARDHANARISHVARA OS KERNEL MODULE
#  Sovereign Payment Gateway Engine — Moneris + Stripe Unified Processor
#  File: payment_gateways.py
#===============================================================================

import time
import uuid
import json
import hmac
import hashlib
import random
import aiohttp
from typing import Dict, Any, Optional

class SovereignPaymentGateways:
    """
    Unified async payment processor for Moneris + Stripe.
    """

    def __init__(self, moneris_key: str, moneris_store: str, stripe_key: str):
        self.moneris_key = moneris_key
        self.moneris_store = moneris_store
        self.stripe_key = stripe_key
        self.session: Optional[aiohttp.ClientSession] = None

    #---------------------------------------------------------------------------
    #  SESSION MANAGEMENT
    #---------------------------------------------------------------------------
    async def _ensure_session(self):
        if self.session is None or self.session.closed:
            self.session = aiohttp.ClientSession(
                timeout=aiohttp.ClientTimeout(total=15),
                headers={"User-Agent": f"ARKA-Payments/{random.randint(1000,9999)}"}
            )

    #---------------------------------------------------------------------------
    #  MONERIS HASH GENERATION
    #---------------------------------------------------------------------------
    def _moneris_hash(self, order_id: str, amount: float) -> str:
        raw = f"{self.moneris_key}{order_id}{amount}"
        return hashlib.sha256(raw.encode()).hexdigest()

    #---------------------------------------------------------------------------
    #  STRIPE SIGNATURE
    #---------------------------------------------------------------------------
    def _stripe_sig(self, payload: Dict[str, Any]) -> str:
        body = json.dumps(payload, separators=(",", ":"))
        return hmac.new(
            self.stripe_key.encode(),
            body.encode(),
            hashlib.sha256
        ).hexdigest()

    #---------------------------------------------------------------------------
    #  MONERIS CHARGE
    #---------------------------------------------------------------------------
    async def moneris_charge(self, amount: float, card: Dict[str, str]) -> Dict[str, Any]:
        await self._ensure_session()

        order_id = f"MON-{uuid.uuid4().hex[:10].upper()}"
        payload = {
            "store_id": self.moneris_store,
            "api_token": self.moneris_key,
            "order_id": order_id,
            "amount": f"{amount:.2f}",
            "pan": card["number"],
            "expdate": card["exp"],
            "crypt_type": "7",
            "dynamic_descriptor": "ARKA"
        }

        try:
            async with self.session.post(
                "https://api.moneris.com/HPPDP/index.php",
                json=payload
            ) as resp:
                text = await resp.text()
                return {
                    "gateway": "moneris",
                    "order_id": order_id,
                    "status": resp.status,
                    "response": text,
                    "timestamp": time.time()
                }
        except Exception as e:
            return {
                "gateway": "moneris",
                "order_id": order_id,
                "status": 0,
                "error": str(e),
                "timestamp": time.time()
            }

    #---------------------------------------------------------------------------
    #  STRIPE CHARGE
    #---------------------------------------------------------------------------
    async def stripe_charge(self, amount: float, token: str) -> Dict[str, Any]:
        await self._ensure_session()

        payload = {
            "amount": int(amount * 100),
            "currency": "cad",
            "source": token,
            "description": "ARKA Sovereign Charge"
        }

        headers = {
            "Authorization": f"Bearer {self.stripe_key}",
            "Stripe-Signature": self._stripe_sig(payload)
        }

        try:
            async with self.session.post(
                "https://api.stripe.com/v1/charges",
                data=payload,
                headers=headers
            ) as resp:
                text = await resp.text()
                return {
                    "gateway": "stripe",
                    "status": resp.status,
                    "response": text,
                    "timestamp": time.time()
                }
        except Exception as e:
            return {
                "gateway": "stripe",
                "status": 0,
                "error": str(e),
                "timestamp": time.time()
            }

    #---------------------------------------------------------------------------
    #  UNIFIED PAYMENT ROUTER
    #---------------------------------------------------------------------------
    async def charge(self, engine: str, amount: float, payload: Dict[str, Any]) -> Dict[str, Any]:
        if engine.lower() == "moneris":
            return await self.moneris_charge(amount, payload)
        if engine.lower() == "stripe":
            return await self.stripe_charge(amount, payload["token"])
        return {"error": "unknown_gateway", "timestamp": time.time()}

    #---------------------------------------------------------------------------
    #  CLEANUP
    #---------------------------------------------------------------------------
    async def close(self):
        if self.session and not self.session.closed:
            await self.session.close()

#===============================================================================
#  END OF FILE — payment_gateways.py
#===============================================================================
