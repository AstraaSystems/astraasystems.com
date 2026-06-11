#!/usr/bin/env python3
"""
ArdhanarishvaraOS — Standalone Test Harness (Extreme Edition)
Purpose:
    - Validate OS boot
    - Validate async event bus
    - Validate AST validator
    - Validate compute semaphore
    - Validate ledger writes
"""

import asyncio
import json
from arka_core.ardhanarishvara_os import ArdhanarishvaraOS
from entities.astraa_trivertical_sovengine import Envelope, Domain

async def run_os_test():
    print("\n===============================================")
    print(" ARDHANARISHVARA OS — STANDALONE TEST HARNESS")
    print("===============================================\n")

    os_kernel = ArdhanarishvaraOS()

    # Build a test envelope
    env = Envelope(
        tx_id="TEST1234",
        epoch=0.0,
        entropy="OS_TEST",
        mutation_ast="x = 1 + 1",
        context={"test": "os_event"}
    )

    # Inject into FINANCE domain
    await os_kernel.inject_monadic_vector(
        Domain.FINANCE,
        Domain.BUSINESS,
        env
    )

    # Process queue
    while not os_kernel.backbone.quantum_bus.empty():
        pkt = await os_kernel.backbone.quantum_bus.get()
        await os_kernel._process_vector_execution(pkt)
        os_kernel.backbone.quantum_bus.task_done()

    print("\n=== OS REGISTRY STATE ===")
    for domain, reg in os_kernel.matrix_registry.items():
        print(domain.name, json.dumps(reg.retained_state_graph, indent=4))

    print("\n=== OS TEST COMPLETE ===")

if __name__ == "__main__":
    asyncio.run(run_os_test())
