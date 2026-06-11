#!/usr/bin/env python3
"""
ARKA Sovereign Ecosystem — Full System Test Harness (Extreme Edition)

This harness tests:
    - ArdhanarishvaraOS (OS Kernel)
    - ArkaUltimateSupervisor (Governance Layer)
    - AstraaTriVerticalSovEngine (Tri‑Vertical Sovereign Engine)
    - Business / Finance / Construction pipelines
    - Quantum bus routing
    - AST validation
    - Compute semaphore
    - Ledger writes
    - Cross‑domain event flow
"""

import asyncio
import json
import time

from arka_core.ardhanarishvara_os import ArdhanarishvaraOS
from arka_core.arka_ultimate_supervisor import ArkaUltimateSupervisor
from entities.astraa_trivertical_sovengine import Domain

async def run_full_system_test():
    print("\n==============================================================")
    print(" ARKA SOVEREIGN ECOSYSTEM — FULL SYSTEM TEST HARNESS")
    print("==============================================================\n")

    # ------------------------------------------------------------
    # 1. Initialize OS + Supervisor
    # ------------------------------------------------------------
    os_kernel = ArdhanarishvaraOS()
    supervisor = ArkaUltimateSupervisor(os_kernel)

    print("[+] OS Kernel Loaded")
    print("[+] Supervisor Loaded")
    print("[+] Astraa Sovereign Engine Mounted\n")

    # ------------------------------------------------------------
    # 2. Run multiple governance cycles
    # ------------------------------------------------------------
    for cycle in range(1, 4):
        print(f"\n--- GOVERNANCE CYCLE {cycle} ---")

        output = await supervisor.run_governance_cycle()

        print("Supervisor Output:")
        print(json.dumps(output, indent=4))

        print("Supervisor Telemetry:")
        print(json.dumps(supervisor.telemetry, indent=4))

        await asyncio.sleep(1)

    # ------------------------------------------------------------
    # 3. Direct Astraa Sovereign Engine Tests
    # ------------------------------------------------------------
    print("\n==============================================================")
    print(" ASTRAA SOVEREIGN ENGINE — DIRECT TRI‑VERTICAL TESTS")
    print("==============================================================\n")

    # BUSINESS
    business_out = await supervisor.astraa.run_vertical(
        Domain.BUSINESS,
        {"order": "B2B‑Workflow‑Test"}
    )
    print("[BUSINESS] Output:")
    print(json.dumps(business_out, indent=4))

    # FINANCE
    finance_out = await supervisor.astraa.run_vertical(
        Domain.FINANCE,
        {"invoice": 98765}
    )
    print("\n[FINANCE] Output:")
    print(json.dumps(finance_out, indent=4))

    # CONSTRUCTION
    construction_out = await supervisor.astraa.run_vertical(
        Domain.CONSTRUCTION,
        {"site": "Alpha‑Logistics‑Node"}
    )
    print("\n[CONSTRUCTION] Output:")
    print(json.dumps(construction_out, indent=4))

    # ------------------------------------------------------------
    # 4. OS Registry State Dump
    # ------------------------------------------------------------
    print("\n==============================================================")
    print(" ARDHANARISHVARA OS — REGISTRY STATE DUMP")
    print("==============================================================\n")

    for domain, reg in os_kernel.matrix_registry.items():
        print(f"Domain: {domain.name}")
        print(json.dumps(reg.retained_state_graph, indent=4))
        print("Checksum:", reg.cryptographic_checksum)
        print("Cycles:", reg.telemetry_cycles)
        print("--------------------------------------------------------------")

    print("\n==============================================================")
    print(" FULL SYSTEM TEST COMPLETE")
    print("==============================================================\n")


if __name__ == "__main__":
    asyncio.run(run_full_system_test())
