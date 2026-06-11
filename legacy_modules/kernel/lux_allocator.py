#!/usr/bin/env python3
# ============================================================
#  LUX ALLOCATOR v17 — Arka Pillai Holdings Ltd
#  Automatically allocates 20% of profit to Lux account
# ============================================================

class LuxAllocator:

    def allocate(self, total_profit: float) -> dict:
        lux_share = round(total_profit * 0.20, 2)
        retained = round(total_profit - lux_share, 2)

        return {
            "lux_allocation": lux_share,
            "retained_profit": retained
        }
