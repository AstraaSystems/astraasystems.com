#!/usr/bin/env python3
"""
Astraa Integration Wrapper — Extreme Complexity Edition
Role: Bridge between Astraa Kernel and Tri‑Vertical HyperEngine
Security: AST‑Validated Envelope Routing, Async Compute Locks
"""

import asyncio
import time
import uuid
from dataclasses import asdict

from entities.astraa_trivertical_hyperengine import (
    AstraaTriVerticalHyperEngine,
    Envelope,
    Domain
)

class AstraaIntegrationWrapper:
    """
    This wrapper mounts the Tri‑Vertical HyperEngine inside Astraa and exposes
    a clean API for Astraa to run Business / Finance / Construction verticals.
    """

    def __init__(self, astraa_kernel):
        self.astraa = astraa_kernel
        self.hyper = AstraaTriVerticalHyperEngine()

        # Attach telemetry space inside Astraa
        self.astraa.trivertical_telemetry = {
            "last_domain": None,
            "last_envelope": None,
            "last_output": None,
            "cycles": 0,
            "last_runtime": 0.0
        }

    # ------------------------------------------------------------
    # Create envelope helper
    # ------------------------------------------------------------
    def _build_envelope(self, context: dict, mutation_ast: str = "") -> Envelope:
        return Envelope(
            tx_id=uuid.uuid4().hex[:8].upper(),
            epoch=time.time(),
            entropy="ASTRAA_TRIVERTICAL",
            mutation_ast=mutation_ast,
            context=context or {}
        )

    # ------------------------------------------------------------
    # Public API — Astraa calls this
    # ------------------------------------------------------------
    async def run_vertical(self, domain: Domain, context: dict, mutation_ast: str = ""):
        """
        domain: Domain.BUSINESS / FINANCE / CONSTRUCTION
        context: dict payload Astraa wants to send
        mutation_ast: optional AST mutation block
        """

        env = self._build_envelope(context, mutation_ast)

        # Execute through HyperEngine
        output = await self.hyper.run_vertical(domain, env)

        # Update Astraa telemetry
        self.astraa.trivertical_telemetry.update({
            "last_domain": domain.value,
            "last_envelope": asdict(env),
            "last_output": output,
            "cycles": self.astraa.trivertical_telemetry["cycles"] + 1,
            "last_runtime": time.time()
        })

        return output
