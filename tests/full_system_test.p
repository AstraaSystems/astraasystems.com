#!/usr/bin/env python3

import asyncio
from arka_core.ardhanarishvara_os import ArdhanarishvaraOS
from arka_core.arka_ultimate_supervisor import ArkaUltimateSupervisor

async def run_test():
    os_kernel = ArdhanarishvaraOS()
    supervisor = ArkaUltimateSupervisor(os_kernel)

    print("\n=== FULL SYSTEM TEST START ===")

    for _ in range(3):
        out = await supervisor.run_governance_cycle()
        print("Supervisor Output:", out)
        await asyncio.sleep(1)

    print("\n=== FULL SYSTEM TEST COMPLETE ===")

if __name__ == "__main__":
    asyncio.run(run_test())
